"""
Survey Engine

Orchestrates the complete survey process for synthetic respondents.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import random
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from ..persona.generator import Persona, PersonaGenerator
from ..logic.conditional_logic import SurveyLogic, create_standard_survey_logic
from .question_handler import QuestionHandler, QuestionResponse, QUESTION_METADATA


@dataclass
class ConceptResponse:
    """Responses for a single concept"""
    concept_id: str
    concept_name: str
    position: int  # Order shown to respondent
    responses: Dict[str, QuestionResponse] = field(default_factory=dict)


@dataclass
class RespondentData:
    """Complete data for one respondent"""
    respondent_id: str
    persona: Persona
    concept_responses: List[ConceptResponse] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class SurveyEngine:
    """Main survey orchestration engine"""

    def __init__(self,
                 question_handler: QuestionHandler,
                 survey_logic: Optional[SurveyLogic] = None,
                 concepts: Optional[List[Dict]] = None):
        """
        Initialize survey engine.

        Args:
            question_handler: Handler for question processing
            survey_logic: Survey logic engine (uses default if None)
            concepts: List of concept dictionaries
        """
        self.question_handler = question_handler
        self.survey_logic = survey_logic or create_standard_survey_logic()
        self.concepts = concepts or []

    def run_survey_for_respondent(self,
                                  persona: Persona,
                                  concepts_to_test: Optional[List[Dict]] = None,
                                  randomize_concepts: bool = True,
                                  questions_to_ask: Optional[List[str]] = None,
                                  num_concepts_per_respondent: int = 3) -> RespondentData:
        """
        Run complete survey for a single respondent across randomly selected concepts.

        Args:
            persona: The respondent persona
            concepts_to_test: Concepts to test (uses self.concepts if None)
            randomize_concepts: Whether to randomize concept order
            questions_to_ask: Specific questions to ask (None = all)
            num_concepts_per_respondent: Number of concepts to randomly assign (default=3)

        Returns:
            RespondentData with all responses
        """
        concepts = concepts_to_test or self.concepts
        if not concepts:
            raise ValueError("No concepts provided")

        # Check screening
        passes, reason = self.survey_logic.apply_screening(persona.get_all_attributes())
        if not passes:
            return RespondentData(
                respondent_id=persona.id,
                persona=persona,
                metadata={'screened_out': True, 'reason': reason}
            )

        # Randomly select N concepts for this respondent
        num_to_select = min(num_concepts_per_respondent, len(concepts))
        selected_indices = random.sample(range(len(concepts)), num_to_select)

        # Optionally randomize the order they're shown
        if randomize_concepts:
            random.shuffle(selected_indices)

        respondent_data = RespondentData(
            respondent_id=persona.id,
            persona=persona,
            metadata={'selected_concept_indices': selected_indices}
        )

        # Test each selected concept
        for position, concept_idx in enumerate(selected_indices, start=1):
            concept = concepts[concept_idx]

            concept_response = self._run_concept_test(
                persona=persona,
                concept=concept,
                position=position,
                questions_to_ask=questions_to_ask
            )

            respondent_data.concept_responses.append(concept_response)

        return respondent_data

    def _run_concept_test(self,
                         persona: Persona,
                         concept: Dict,
                         position: int,
                         questions_to_ask: Optional[List[str]] = None) -> ConceptResponse:
        """
        Run survey for a single concept.

        Args:
            persona: Respondent persona
            concept: Concept dictionary
            position: Position in rotation
            questions_to_ask: Questions to ask (None = all from logic)

        Returns:
            ConceptResponse
        """
        concept_response = ConceptResponse(
            concept_id=concept.get('id', f"Concept {position}"),
            concept_name=concept.get('name', ''),
            position=position
        )

        # Get concept description
        concept_description = concept.get('description', concept.get('full_text', ''))

        # Track responses for conditional logic
        response_state = dict(persona.get_all_attributes())

        # Determine which questions to ask
        if questions_to_ask is None:
            questions_to_ask = self.survey_logic.question_order

        # Ask each question
        for question_id in questions_to_ask:
            # Check if we should ask this question
            if not self.survey_logic.should_ask_question(question_id, response_state):
                continue

            # Get question metadata
            q_meta = QUESTION_METADATA.get(question_id, {})
            q_type = q_meta.get('type', 'open_text')
            scale_id = q_meta.get('scale_id')

            # Get options for multi-coded questions
            options = None
            if q_type == 'multi_coded' and scale_id:
                scale = self.question_handler.rating_engine.scale_registry.get_scale(scale_id)
                if scale:
                    options = scale.level_labels

            # Ask the question
            try:
                response = self.question_handler.handle_question(
                    question_id=question_id,
                    question_type=q_type,
                    persona=persona,
                    concept_description=concept_description,
                    scale_id=scale_id,
                    options=options,
                    price=concept.get('price', '')
                )

                concept_response.responses[question_id] = response

                # Update response state for conditional logic
                if response.rating_result:
                    response_state[question_id] = response.rating_result.chosen_level_value
                else:
                    response_state[question_id] = response.formatted_response

            except Exception as e:
                print(f"Error processing {question_id}: {e}")
                continue

        return concept_response

    def run_full_study(self,
                      n_respondents: int,
                      persona_generator: PersonaGenerator,
                      concepts: Optional[List[Dict]] = None,
                      questions_to_ask: Optional[List[str]] = None,
                      randomize_concepts: bool = True,
                      num_concepts_per_respondent: int = 3,
                      show_progress: bool = True,
                      max_workers: int = 1) -> List[RespondentData]:
        """
        Run complete study with N synthetic respondents.

        Args:
            n_respondents: Number of respondents to generate
            persona_generator: PersonaGenerator instance
            concepts: Concepts to test
            questions_to_ask: Questions to ask (None = all)
            randomize_concepts: Randomize concept order per respondent
            num_concepts_per_respondent: Number of concepts per respondent (default=3)
            show_progress: Show progress bar
            max_workers: Number of parallel workers (default=1 for sequential)

        Returns:
            List of RespondentData
        """
        concepts = concepts or self.concepts

        # Generate personas
        print(f"Generating {n_respondents} personas...")
        personas = persona_generator.generate_batch(n_respondents, apply_screening=True)

        # Run survey with optional parallelization
        if max_workers > 1:
            return self._run_parallel(
                personas, concepts, questions_to_ask, randomize_concepts,
                num_concepts_per_respondent, show_progress, max_workers
            )
        else:
            return self._run_sequential(
                personas, concepts, questions_to_ask, randomize_concepts,
                num_concepts_per_respondent, show_progress
            )

    def _run_sequential(self, personas, concepts, questions_to_ask,
                       randomize_concepts, num_concepts_per_respondent,
                       show_progress) -> List[RespondentData]:
        """Run survey sequentially (original behavior)"""
        all_respondent_data = []
        iterator = tqdm(personas, desc="Running survey") if show_progress else personas

        for persona in iterator:
            respondent_data = self.run_survey_for_respondent(
                persona=persona,
                concepts_to_test=concepts,
                randomize_concepts=randomize_concepts,
                questions_to_ask=questions_to_ask,
                num_concepts_per_respondent=num_concepts_per_respondent
            )
            all_respondent_data.append(respondent_data)

        return all_respondent_data

    def _run_parallel(self, personas, concepts, questions_to_ask,
                     randomize_concepts, num_concepts_per_respondent,
                     show_progress, max_workers) -> List[RespondentData]:
        """Run survey in parallel using ThreadPoolExecutor"""
        all_respondent_data = []

        def process_persona(persona):
            """Process single persona (thread-safe)"""
            return self.run_survey_for_respondent(
                persona=persona,
                concepts_to_test=concepts,
                randomize_concepts=randomize_concepts,
                questions_to_ask=questions_to_ask,
                num_concepts_per_respondent=num_concepts_per_respondent
            )

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_persona = {
                executor.submit(process_persona, persona): persona
                for persona in personas
            }

            # Collect results with progress bar
            if show_progress:
                with tqdm(total=len(personas), desc="Running survey") as pbar:
                    for future in as_completed(future_to_persona):
                        respondent_data = future.result()
                        all_respondent_data.append(respondent_data)
                        pbar.update(1)
            else:
                for future in as_completed(future_to_persona):
                    respondent_data = future.result()
                    all_respondent_data.append(respondent_data)

        return all_respondent_data
