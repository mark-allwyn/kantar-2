"""
Conditional Logic Engine

Handles survey flow logic, skip patterns, and question dependencies.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable
from enum import Enum


class Operator(Enum):
    """Comparison operators for conditions"""
    EQUALS = "=="
    NOT_EQUALS = "!="
    IN = "in"
    NOT_IN = "not_in"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    BETWEEN = "between"
    CONTAINS = "contains"


@dataclass
class ConditionalRule:
    """A rule that determines if a question should be asked"""
    question_id: str  # The question this rule applies to
    source_question: str  # The question whose answer we check
    operator: Operator
    values: List[Any]
    logic_type: str = "AND"  # "AND" or "OR" for compound conditions

    def evaluate(self, responses: Dict[str, Any]) -> bool:
        """Evaluate if this condition is met based on responses"""
        # Get the source question's response
        if self.source_question not in responses:
            return False  # Can't ask if dependency not answered

        response = responses[self.source_question]

        # Handle different operators
        if self.operator == Operator.EQUALS:
            return response == self.values[0]

        elif self.operator == Operator.NOT_EQUALS:
            return response != self.values[0]

        elif self.operator == Operator.IN:
            # Check if response matches any of the values
            if isinstance(response, (list, tuple)):
                return any(r in self.values for r in response)
            return response in self.values

        elif self.operator == Operator.NOT_IN:
            if isinstance(response, (list, tuple)):
                return all(r not in self.values for r in response)
            return response not in self.values

        elif self.operator == Operator.LESS_THAN:
            return response < self.values[0]

        elif self.operator == Operator.GREATER_THAN:
            return response > self.values[0]

        elif self.operator == Operator.LESS_EQUAL:
            return response <= self.values[0]

        elif self.operator == Operator.GREATER_EQUAL:
            return response >= self.values[0]

        elif self.operator == Operator.BETWEEN:
            return self.values[0] <= response <= self.values[1]

        elif self.operator == Operator.CONTAINS:
            if isinstance(response, str):
                return any(str(v) in response for v in self.values)
            return False

        return False


@dataclass
class ScreeningRule:
    """A rule that screens out respondents"""
    description: str
    condition: ConditionalRule

    def should_screen_out(self, persona_attrs: Dict[str, Any]) -> bool:
        """Check if persona should be screened out"""
        return self.condition.evaluate(persona_attrs)


class SurveyLogic:
    """Manages survey flow logic and conditional questioning"""

    def __init__(self):
        self.rules: Dict[str, List[ConditionalRule]] = {}
        self.screening_rules: List[ScreeningRule] = []
        self.question_order: List[str] = []

    def add_rule(self, rule: ConditionalRule):
        """Add a conditional rule for a question"""
        if rule.question_id not in self.rules:
            self.rules[rule.question_id] = []
        self.rules[rule.question_id].append(rule)

    def add_screening_rule(self, rule: ScreeningRule):
        """Add a screening rule"""
        self.screening_rules.append(rule)

    def set_question_order(self, order: List[str]):
        """Set the default question order"""
        self.question_order = order

    def should_ask_question(self, question_id: str, responses: Dict[str, Any]) -> bool:
        """Determine if a question should be asked based on prior responses"""
        # If no rules, always ask
        if question_id not in self.rules:
            return True

        # Evaluate all rules for this question
        rules = self.rules[question_id]

        # If multiple rules, check logic type
        if len(rules) == 1:
            return rules[0].evaluate(responses)

        # For multiple rules, apply AND/OR logic
        logic_type = rules[0].logic_type

        if logic_type == "AND":
            return all(rule.evaluate(responses) for rule in rules)
        else:  # OR
            return any(rule.evaluate(responses) for rule in rules)

    def apply_screening(self, persona_attrs: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Apply screening rules to a persona.

        Returns:
            (should_include, reason) - (True, None) if passes, (False, reason) if screened
        """
        # Apply standard screening rules
        for screening_rule in self.screening_rules:
            if screening_rule.should_screen_out(persona_attrs):
                return False, screening_rule.description

        # S4 compound screening: If age 56-75 AND doesn't buy paper scratchcards -> screen out
        # Rule: "If S2_3=2,3 and S4 does not contain (3) -> Screen Out"
        age = persona_attrs.get('age', 0)
        category_buyer = persona_attrs.get('category_buyer', [])

        if age >= 56 and age <= 75:  # Age band 56-75 (S2_3)
            # Check if they buy paper scratchcards (option 3 in S4)
            if isinstance(category_buyer, list):
                has_paper_scratchcards = 'Paper scratchcards bought in person' in category_buyer
            else:
                has_paper_scratchcards = 'Paper scratchcards bought in person' in str(category_buyer)

            if not has_paper_scratchcards:
                return False, "Age 56-75 but doesn't buy paper scratchcards (S4 screening)"

        # S5 screening: If they would NEVER spend money on paper scratchcards -> screen out
        # Rule: "If S5 contains 'Paper scratchcards bought in person' -> Screen Out"
        category_non_rejector = persona_attrs.get('category_non_rejector', [])

        if isinstance(category_non_rejector, list):
            rejects_paper_scratchcards = 'Paper scratchcards bought in person' in category_non_rejector
        else:
            rejects_paper_scratchcards = 'Paper scratchcards bought in person' in str(category_non_rejector)

        if rejects_paper_scratchcards:
            return False, "Would never spend money on paper scratchcards (S5 screening)"

        return True, None

    def get_next_questions(self, current_responses: Dict[str, Any],
                           all_questions: List[str] = None) -> List[str]:
        """
        Get the next questions to ask based on current response state.

        Args:
            current_responses: Dict of question_id -> response
            all_questions: Optional list of all questions (uses question_order if not provided)

        Returns:
            List of question IDs that should be asked next
        """
        if all_questions is None:
            all_questions = self.question_order

        # Find questions not yet answered
        unanswered = [q for q in all_questions if q not in current_responses]

        # Filter by conditional logic
        to_ask = []
        for question_id in unanswered:
            if self.should_ask_question(question_id, current_responses):
                to_ask.append(question_id)

        return to_ask

    def trace_path(self, persona_attrs: Dict[str, Any], all_questions: List[str]) -> List[str]:
        """
        Trace the expected path through the survey for a given persona.

        Useful for debugging and validation.

        Returns:
            List of question IDs that would be asked
        """
        # Check screening first
        passes, reason = self.apply_screening(persona_attrs)
        if not passes:
            return []  # Screened out

        responses = dict(persona_attrs)  # Start with persona attributes
        asked_questions = []

        for question_id in all_questions:
            if self.should_ask_question(question_id, responses):
                asked_questions.append(question_id)
                # Simulate a response (for tracing purposes, we don't need actual values)
                responses[question_id] = None

        return asked_questions


def create_standard_survey_logic() -> SurveyLogic:
    """
    Create the standard survey logic for the Board Games questionnaire.

    This includes all the conditional rules from the questionnaire.
    """
    logic = SurveyLogic()

    # Screening rules
    logic.add_screening_rule(ScreeningRule(
        description="Works in excluded occupation",
        condition=ConditionalRule(
            question_id="SCREENER",
            source_question="occupation",
            operator=Operator.IN,
            values=['Advertising/PR', 'Marketing/Market Research',
                   'Lottery sales/distribution', 'Tobacco shop salesperson']
        )
    ))

    logic.add_screening_rule(ScreeningRule(
        description="Age out of range",
        condition=ConditionalRule(
            question_id="SCREENER",
            source_question="age",
            operator=Operator.NOT_IN,
            values=list(range(18, 76))  # 18-75 inclusive
        )
    ))

    # S4 screening: If age band 56-75 AND doesn't buy paper scratchcards -> screen out
    # This is implemented as a custom check in the screening logic
    # Rule: "If S2_3=2,3 and S4 does not contain (3) -> Screen Out"
    # Meaning: If in age band 56-75 and category_buyer doesn't include "Paper scratchcards bought in person"

    # Conditional question rules (from questionnaire analysis)

    # B21: Barriers - only if low purchase intent (4 or 5)
    logic.add_rule(ConditionalRule(
        question_id="B21",
        source_question="B2",
        operator=Operator.IN,
        values=[4, 5]
    ))

    # B8: Portfolio incrementality - only if would buy different scratchcard
    logic.add_rule(ConditionalRule(
        question_id="B8",
        source_question="B7",
        operator=Operator.EQUALS,
        values=[1]  # Code for "Would buy different scratchcard"
    ))

    # B22: Would buy as gift - only if some purchase intent (1, 2, or 3)
    logic.add_rule(ConditionalRule(
        question_id="B22",
        source_question="B2",
        operator=Operator.IN,
        values=[1, 2, 3]
    ))

    # B23: Occasions - only if would buy as gift
    logic.add_rule(ConditionalRule(
        question_id="B23",
        source_question="B22",
        operator=Operator.IN,
        values=[1, 2, 3]  # Any positive gift intent
    ))

    # B24: Pleased with gift - NO CONDITIONS (always show)

    # Set default question order (concept test section)
    concept_questions = [
        "B2",   # Purchase intent
        "B21",  # Barriers (conditional)
        "B3",   # Uniqueness
        "B4",   # Value for money
        "B6",   # Likeability
        "B7",   # Increment
        "B8",   # Portfolio incrementality (conditional)
        "B11",  # Relevance
        "B11a", # Playfulness
        "B12",  # Excitement
        "B13",  # Understanding
        "B14",  # Believability
        "B15",  # Likes open
        "B16",  # Dislikes open
        "B17",  # Highlighter drivers
        "B18",  # Highlighter barriers
        "B20",  # Imagery
        "B22",  # Would buy as gift (conditional)
        "B23",  # Occasions (conditional)
        "B24",  # Pleased with gift (no conditions)
    ]

    logic.set_question_order(concept_questions)

    return logic
