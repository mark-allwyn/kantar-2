"""
Question Handler

Handles different question types and generates appropriate responses.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..persona.generator import Persona
from ..llm.client import LLMClient
from ..llm.prompts import PromptBuilder
from ..ssr.rating_engine import RatingEngine
from ..scales.scale import RatingResult


@dataclass
class QuestionResponse:
    """Response to a survey question"""
    question_id: str
    question_type: str
    raw_response: str  # Free-text from LLM
    formatted_response: Any  # Formatted for output
    rating_result: Optional[RatingResult] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class QuestionHandler:
    """Handles question answering for different question types"""

    def __init__(self,
                 llm_client: LLMClient,
                 rating_engine: RatingEngine,
                 prompt_builder: PromptBuilder = None):
        """
        Initialize question handler.

        Args:
            llm_client: LLM client for generating responses
            rating_engine: SSR engine for rating responses
            prompt_builder: Prompt builder (uses default if None)
        """
        self.llm_client = llm_client
        self.rating_engine = rating_engine
        self.prompt_builder = prompt_builder or PromptBuilder()

    def handle_question(self,
                       question_id: str,
                       question_type: str,
                       persona: Persona,
                       concept_description: str,
                       question_text: str = "",
                       scale_id: Optional[str] = None,
                       options: Optional[List[str]] = None,
                       **kwargs) -> QuestionResponse:
        """
        Handle a question based on its type.

        Args:
            question_id: Question ID (e.g., "B2")
            question_type: Type of question
            persona: Respondent persona
            concept_description: Product concept description
            question_text: Optional question text
            scale_id: Scale ID for SSR (if applicable)
            options: Response options (for multi-coded)
            **kwargs: Additional question-specific parameters

        Returns:
            QuestionResponse
        """
        # Build system prompt (same for all)
        system_prompt = self.prompt_builder.build_system_prompt(persona)

        # Route to appropriate handler
        if question_type == "single_coded" and scale_id:
            return self._handle_likert_question(
                question_id, system_prompt, concept_description,
                question_text, scale_id, **kwargs
            )
        elif question_type == "binary" and scale_id:
            return self._handle_binary_question(
                question_id, system_prompt, concept_description,
                question_text, scale_id, **kwargs
            )
        elif question_type == "slider" and scale_id:
            return self._handle_slider_question(
                question_id, system_prompt, concept_description,
                question_text, scale_id, **kwargs
            )
        elif question_type == "multi_coded":
            return self._handle_multi_coded_question(
                question_id, system_prompt, concept_description,
                question_text, options, **kwargs
            )
        elif question_type == "open_text":
            return self._handle_open_text_question(
                question_id, system_prompt, concept_description,
                question_text, **kwargs
            )
        else:
            # Default: treat as open text
            return self._handle_open_text_question(
                question_id, system_prompt, concept_description,
                question_text, **kwargs
            )

    def _handle_likert_question(self,
                               question_id: str,
                               system_prompt: str,
                               concept_description: str,
                               question_text: str,
                               scale_id: str,
                               **kwargs) -> QuestionResponse:
        """Handle Likert-scale question using SSR"""

        # Build appropriate prompt based on question ID
        prompt_map = {
            'B2': self.prompt_builder.build_purchase_intent_prompt,
            'B3': self.prompt_builder.build_uniqueness_prompt,
            'B4': self.prompt_builder.build_value_prompt,
            'B6': self.prompt_builder.build_likeability_prompt,
            'B11': self.prompt_builder.build_relevance_prompt,
            'B11a': self.prompt_builder.build_playfulness_prompt,
            'B12': self.prompt_builder.build_excitement_prompt,
            'B14': self.prompt_builder.build_believability_prompt,
            'B22': self.prompt_builder.build_gift_intent_prompt,
            'B24': self.prompt_builder.build_gift_satisfaction_prompt,
        }

        if question_id in prompt_map:
            if question_id == 'B4' and 'price' in kwargs:
                user_prompt = prompt_map[question_id](concept_description, kwargs['price'])
            else:
                user_prompt = prompt_map[question_id](concept_description)
        else:
            user_prompt = self.prompt_builder.build_generic_prompt(
                question_text, concept_description
            )

        # Generate LLM response
        raw_response = self.llm_client.generate_response(system_prompt, user_prompt)

        # Rate using SSR (use default parameters from rating_engine for paper-compliant SSR)
        rating_result = self.rating_engine.rate_answer(
            raw_response,
            scale_id=scale_id
        )

        # Format for output
        formatted_response = rating_result.to_formatted_response()

        return QuestionResponse(
            question_id=question_id,
            question_type="likert",
            raw_response=raw_response,
            formatted_response=formatted_response,
            rating_result=rating_result,
            metadata={
                'scale_id': scale_id,
                'confidence': rating_result.probabilities[rating_result.chosen_level_index]
            }
        )

    def _handle_binary_question(self,
                               question_id: str,
                               system_prompt: str,
                               concept_description: str,
                               question_text: str,
                               scale_id: str,
                               **kwargs) -> QuestionResponse:
        """Handle binary (Yes/No) question using SSR"""

        # Build prompt
        if question_id == 'B7':
            user_prompt = self.prompt_builder.build_increment_prompt(concept_description)
        else:
            user_prompt = self.prompt_builder.build_generic_prompt(
                question_text, concept_description
            )

        # Generate and rate
        raw_response = self.llm_client.generate_response(system_prompt, user_prompt)
        rating_result = self.rating_engine.rate_answer(
            raw_response,
            scale_id=scale_id,
            temperature=kwargs.get('temperature', 0.5)
        )

        formatted_response = rating_result.to_formatted_response()

        return QuestionResponse(
            question_id=question_id,
            question_type="binary",
            raw_response=raw_response,
            formatted_response=formatted_response,
            rating_result=rating_result
        )

    def _handle_slider_question(self,
                               question_id: str,
                               system_prompt: str,
                               concept_description: str,
                               question_text: str,
                               scale_id: str,
                               **kwargs) -> QuestionResponse:
        """Handle slider question using SSR"""

        # Build prompt
        if question_id == 'B13':
            user_prompt = self.prompt_builder.build_understanding_prompt(concept_description)
        else:
            user_prompt = self.prompt_builder.build_generic_prompt(
                question_text, concept_description
            )

        # Generate and rate
        raw_response = self.llm_client.generate_response(system_prompt, user_prompt)
        rating_result = self.rating_engine.rate_answer(
            raw_response,
            scale_id=scale_id,
            temperature=kwargs.get('temperature', 0.5)
        )

        # For sliders, format as "(value) value"
        formatted_response = f"({rating_result.chosen_level_value}) {rating_result.chosen_level_value}"

        return QuestionResponse(
            question_id=question_id,
            question_type="slider",
            raw_response=raw_response,
            formatted_response=formatted_response,
            rating_result=rating_result
        )

    def _handle_multi_coded_question(self,
                                    question_id: str,
                                    system_prompt: str,
                                    concept_description: str,
                                    question_text: str,
                                    options: List[str],
                                    **kwargs) -> QuestionResponse:
        """Handle multi-coded question (simplified: ask LLM to select from options)"""

        # Build prompt with options
        options_text = "\n".join([f"- {opt}" for opt in options])
        user_prompt = f"""{concept_description}

Question: {question_text}

Please select all that apply from the following options:
{options_text}

Which of these apply? List all relevant options."""

        # Generate response
        raw_response = self.llm_client.generate_response(system_prompt, user_prompt)

        # Simple parsing: look for option text in response
        selected = []
        for opt in options:
            # Check if option mentioned in response
            if opt.lower() in raw_response.lower():
                selected.append(opt)

        # If nothing selected, pick first option as fallback
        if not selected:
            selected = [options[0]]

        # Format as comma-separated
        formatted_response = ", ".join(selected)

        return QuestionResponse(
            question_id=question_id,
            question_type="multi_coded",
            raw_response=raw_response,
            formatted_response=formatted_response,
            metadata={'selected_options': selected}
        )

    def _handle_open_text_question(self,
                                  question_id: str,
                                  system_prompt: str,
                                  concept_description: str,
                                  question_text: str,
                                  **kwargs) -> QuestionResponse:
        """Handle open-ended text question"""

        # Build prompt - use specific prompts for B15/B16
        if question_id == 'B15':
            user_prompt = self.prompt_builder.build_likes_prompt(concept_description)
        elif question_id == 'B16':
            user_prompt = self.prompt_builder.build_dislikes_prompt(concept_description)
        else:
            user_prompt = self.prompt_builder.build_generic_prompt(
                question_text, concept_description
            )

        # Generate response (this is the final output)
        raw_response = self.llm_client.generate_response(system_prompt, user_prompt)

        # Post-process: Handle minimal/"nothing" responses
        formatted_response = self._process_open_text_response(raw_response, question_id)

        return QuestionResponse(
            question_id=question_id,
            question_type="open_text",
            raw_response=raw_response,
            formatted_response=formatted_response
        )

    def _process_open_text_response(self, raw_response: str, question_id: str) -> str:
        """
        Process open-text response to handle blank/"nothing" cases.

        Args:
            raw_response: Raw LLM response
            question_id: Question identifier

        Returns:
            Processed response (may be empty string for "nothing")
        """
        response = raw_response.strip()

        # Check for common "nothing" variants (case insensitive)
        nothing_variants = [
            'nothing',
            'nothing.',
            'none',
            'none.',
            'n/a',
            'not applicable',
            'nothing specific',
            'nothing in particular',
            'i don\'t like anything',
            'i don\'t dislike anything',
            'no concerns',
            'no issues',
            'nothing comes to mind',
        ]

        response_lower = response.lower()

        # If response is very short and matches "nothing" pattern, return empty or "Nothing"
        if len(response) < 30 and any(variant in response_lower for variant in nothing_variants):
            # Return empty string for truly blank responses
            return ""

        return response


# Question metadata mapping
QUESTION_METADATA = {
    'B2': {'type': 'single_coded', 'scale_id': 'likert5_purchase_intent_v1'},
    'B21': {'type': 'multi_coded', 'scale_id': 'multiselect_barriers_v1'},
    'B3': {'type': 'single_coded', 'scale_id': 'likert5_uniqueness_v1'},
    'B4': {'type': 'single_coded', 'scale_id': 'likert5_value_v1'},
    'B6': {'type': 'single_coded', 'scale_id': 'likert6_likeability_v1'},
    'B7': {'type': 'binary', 'scale_id': 'binary_increment_v1'},
    'B11': {'type': 'single_coded', 'scale_id': 'likert5_relevance_v1'},
    'B11a': {'type': 'single_coded', 'scale_id': 'likert5_playfulness_v1'},
    'B12': {'type': 'single_coded', 'scale_id': 'likert4_excitement_v1'},
    'B13': {'type': 'slider', 'scale_id': 'slider9_understanding_v1'},
    'B14': {'type': 'single_coded', 'scale_id': 'likert4_believability_v1'},
    'B15': {'type': 'open_text'},
    'B16': {'type': 'open_text'},
    'B22': {'type': 'single_coded', 'scale_id': 'likert5_gift_v1'},
    'B23': {'type': 'multi_coded', 'scale_id': 'multiselect_occasions_v1'},
    'B24': {'type': 'single_coded', 'scale_id': 'likert5_pleased_v1'},
}
