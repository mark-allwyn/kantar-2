"""
Questionnaire Parser Module

Extracts questions, scales, conditions, and dimension variables from the DOCX questionnaire.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import re
from docx import Document


class QuestionType(Enum):
    """Types of questions in the survey"""
    SINGLE_CODED = "single_coded"
    MULTI_CODED = "multi_coded"
    NUMERIC = "numeric"
    SLIDER = "slider"
    OPEN_TEXT = "open_text"
    MATRIX = "matrix"


class ScaleType(Enum):
    """Types of rating scales"""
    LIKERT_4 = "likert_4"
    LIKERT_5 = "likert_5"
    LIKERT_6 = "likert_6"
    SLIDER_7 = "slider_7"
    SLIDER_9 = "slider_9"
    BINARY = "binary"
    CUSTOM = "custom"


@dataclass
class Option:
    """A response option for a question"""
    code: Optional[int] = None
    text: str = ""
    is_exclusive: bool = False


@dataclass
class Condition:
    """A conditional logic rule"""
    source_question: str  # e.g., "B2"
    operator: str  # e.g., "==", "in", "not_in"
    values: List[Any]  # e.g., [4, 5]
    logic_type: str = "AND"  # "AND" or "OR"


@dataclass
class Question:
    """A survey question with all metadata"""
    id: str  # e.g., "B2", "S1"
    text: str
    question_type: QuestionType
    scale_type: Optional[ScaleType] = None
    options: List[Option] = field(default_factory=list)
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    conditions: List[Condition] = field(default_factory=list)  # When to ask this question
    is_quota: bool = False
    is_screening: bool = False
    is_derived: bool = False
    randomize_options: bool = False
    section: str = ""  # "Screener" or "Concept Test"
    notes: str = ""


@dataclass
class DimensionVariable:
    """A demographic or psychographic variable that defines personas"""
    name: str
    question_id: str
    values: List[str]
    is_demographic: bool = True
    is_quota: bool = False


@dataclass
class Questionnaire:
    """Complete questionnaire structure"""
    questions: Dict[str, Question] = field(default_factory=dict)
    dimensions: List[DimensionVariable] = field(default_factory=list)
    screening_rules: List[Condition] = field(default_factory=list)
    quota_rules: Dict[str, Any] = field(default_factory=dict)
    version_info: Dict[str, Any] = field(default_factory=dict)


class QuestionnaireParser:
    """Parser for DOCX questionnaire files"""

    def __init__(self, docx_path: str):
        self.docx_path = docx_path
        self.doc = None

    def parse(self) -> Questionnaire:
        """Main parsing method"""
        self.doc = Document(self.docx_path)
        questionnaire = Questionnaire()

        # Parse document structure
        current_section = ""
        current_question = None

        for para in self.doc.paragraphs:
            text = para.text.strip()

            if not text:
                continue

            # Detect sections
            if "SCREENER" in text.upper():
                current_section = "Screener"
                continue
            elif "CONCEPT TEST" in text.upper() or "MAIN QUESTIONNAIRE" in text.upper():
                current_section = "Concept Test"
                continue

            # Detect question IDs (e.g., S1., B2., etc.)
            question_match = re.match(r'^([SB]\d+[a-z]?)[\.\)]?\s*(.*)', text, re.IGNORECASE)
            if question_match:
                q_id = question_match.group(1).upper()
                q_text = question_match.group(2)

                if current_question:
                    questionnaire.questions[current_question.id] = current_question

                current_question = Question(
                    id=q_id,
                    text=q_text,
                    question_type=QuestionType.SINGLE_CODED,  # Default, will refine
                    section=current_section
                )
                continue

            # Parse options (numbered lists)
            if current_question:
                option_match = re.match(r'^(\d+)[\.\)]\s*(.*)', text)
                if option_match:
                    code = int(option_match.group(1))
                    option_text = option_match.group(2)

                    is_exclusive = any(keyword in option_text.lower()
                                     for keyword in ['none', 'prefer not', 'exclusive'])

                    current_question.options.append(Option(
                        code=code,
                        text=option_text,
                        is_exclusive=is_exclusive
                    ))

        # Add last question
        if current_question:
            questionnaire.questions[current_question.id] = current_question

        # Post-process: identify question types and scales
        self._identify_question_types(questionnaire)

        # Extract dimension variables
        self._extract_dimensions(questionnaire)

        # Parse conditional logic
        self._parse_conditions(questionnaire)

        return questionnaire

    def _identify_question_types(self, questionnaire: Questionnaire):
        """Identify question types based on content and structure"""

        for q_id, question in questionnaire.questions.items():
            text_lower = question.text.lower()
            num_options = len(question.options)

            # Identify scale types based on options
            if num_options == 5:
                if any(keyword in text_lower for keyword in ['intent', 'would', 'likely']):
                    question.scale_type = ScaleType.LIKERT_5
                    question.question_type = QuestionType.SINGLE_CODED
                elif any(keyword in text_lower for keyword in ['unique', 'new', 'different']):
                    question.scale_type = ScaleType.LIKERT_5
                elif any(keyword in text_lower for keyword in ['relevant', 'important']):
                    question.scale_type = ScaleType.LIKERT_5

            elif num_options == 4:
                if any(keyword in text_lower for keyword in ['exciting', 'excitement']):
                    question.scale_type = ScaleType.LIKERT_4
                elif any(keyword in text_lower for keyword in ['believable', 'believability']):
                    question.scale_type = ScaleType.LIKERT_4

            elif num_options == 6:
                if any(keyword in text_lower for keyword in ['like', 'dislike', 'likeability']):
                    question.scale_type = ScaleType.LIKERT_6

            elif num_options == 2:
                question.scale_type = ScaleType.BINARY

            # Identify sliders
            if 'slider' in text_lower or '1-7' in question.text or '1-9' in question.text:
                question.question_type = QuestionType.SLIDER
                if '1-9' in question.text:
                    question.scale_type = ScaleType.SLIDER_9
                    question.min_value = 1
                    question.max_value = 9
                elif '1-7' in question.text:
                    question.scale_type = ScaleType.SLIDER_7
                    question.min_value = 1
                    question.max_value = 7

            # Identify multi-coded
            if 'select all' in text_lower or 'multi' in text_lower or 'multiple' in text_lower:
                question.question_type = QuestionType.MULTI_CODED

            # Identify open text
            if 'open' in text_lower or 'explain' in text_lower or 'describe' in text_lower:
                question.question_type = QuestionType.OPEN_TEXT

            # Identify matrix
            if 'matrix' in text_lower or 'grid' in text_lower:
                question.question_type = QuestionType.MATRIX

    def _extract_dimensions(self, questionnaire: Questionnaire):
        """Extract dimension variables that define personas"""

        # Define which questions are dimensions
        dimension_questions = {
            'S1': ('gender', True, True),  # (name, is_demographic, is_quota)
            'S2': ('age', True, True),
            'S3': ('occupation', True, False),
            'S4': ('category_buyer', False, False),
            'S5': ('category_non_rejector', False, False),
            'S7': ('target_group', False, True),
            'S8': ('sc_players', False, False),
            'S9': ('brand_buyers', False, False),
            'I1': ('inertia', False, False),
        }

        for q_id, (name, is_demo, is_quota) in dimension_questions.items():
            if q_id in questionnaire.questions:
                question = questionnaire.questions[q_id]

                # Extract possible values
                if question.question_type == QuestionType.SLIDER:
                    values = [str(i) for i in range(question.min_value, question.max_value + 1)]
                else:
                    values = [opt.text for opt in question.options]

                questionnaire.dimensions.append(DimensionVariable(
                    name=name,
                    question_id=q_id,
                    values=values,
                    is_demographic=is_demo,
                    is_quota=is_quota
                ))

                question.is_quota = is_quota

    def _parse_conditions(self, questionnaire: Questionnaire):
        """Parse conditional logic from question text and notes"""

        # Hardcode known conditions from the questionnaire
        conditional_rules = {
            'B21': Condition(
                source_question='B2',
                operator='in',
                values=[4, 5]  # Asked if "probably would not" or "definitely would not"
            ),
            'B8': Condition(
                source_question='B7',
                operator='==',
                values=['Would buy different scratchcard']  # Simplified
            ),
            'B22': Condition(
                source_question='B2',
                operator='in',
                values=[1, 2, 3]  # Asked if some level of purchase intent
            ),
            'B23': Condition(
                source_question='B22',
                operator='!=',
                values=['Definitely would not']  # If would buy as gift
            ),
        }

        for q_id, condition in conditional_rules.items():
            if q_id in questionnaire.questions:
                questionnaire.questions[q_id].conditions.append(condition)

        # Add screening conditions
        questionnaire.screening_rules.extend([
            Condition(
                source_question='S3',
                operator='not_in',
                values=['Advertising/PR', 'Marketing/Market Research',
                       'Lottery sales/distribution', 'Tobacco shop salesperson']
            ),
            Condition(
                source_question='S2',
                operator='between',
                values=[18, 75]
            )
        ])

    def to_dict(self, questionnaire: Questionnaire) -> Dict:
        """Convert questionnaire to dictionary for JSON serialization"""
        return {
            'questions': {
                q_id: {
                    'id': q.id,
                    'text': q.text,
                    'type': q.question_type.value,
                    'scale_type': q.scale_type.value if q.scale_type else None,
                    'options': [{'code': opt.code, 'text': opt.text, 'is_exclusive': opt.is_exclusive}
                               for opt in q.options],
                    'min_value': q.min_value,
                    'max_value': q.max_value,
                    'conditions': [{'source': c.source_question, 'operator': c.operator, 'values': c.values}
                                  for c in q.conditions],
                    'is_quota': q.is_quota,
                    'is_screening': q.is_screening,
                    'section': q.section
                }
                for q_id, q in questionnaire.questions.items()
            },
            'dimensions': [
                {
                    'name': d.name,
                    'question_id': d.question_id,
                    'values': d.values,
                    'is_demographic': d.is_demographic,
                    'is_quota': d.is_quota
                }
                for d in questionnaire.dimensions
            ]
        }
