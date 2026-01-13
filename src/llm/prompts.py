"""
Prompt Templates for LLM Response Generation

Builds prompts for synthetic respondents based on personas and concepts.
"""

from typing import Dict, Any
from ..persona.generator import Persona


class PromptBuilder:
    """Builds prompts for LLM-based synthetic respondents"""

    @staticmethod
    def build_system_prompt(persona: Persona) -> str:
        """
        Build system prompt that conditions the LLM on persona attributes.

        Args:
            persona: The persona to embody

        Returns:
            System prompt string
        """
        description = persona.to_description()

        system_prompt = f"""You are a consumer participating in a market research survey about scratchcard products.

Your profile: You are {description}.

When answering questions:
- Respond naturally and authentically as this specific person would
- Base your opinions on your demographic and psychographic characteristics
- Be honest, specific, and DECISIVE in your responses - don't hedge or be overly cautious
- Express STRONG genuine opinions when you feel them, both positive and negative
- Vary your language naturally (don't be repetitive)
- Use enthusiastic language when you genuinely like something
- Keep responses concise (1-3 sentences typically)

Remember: You are not an AI assistant - you are a real consumer with real, often strong, opinions about products. Real people express clear preferences and enthusiasm or disappointment - you should too!"""

        return system_prompt

    @staticmethod
    def build_purchase_intent_prompt(concept_description: str) -> str:
        """Build prompt for purchase intent question"""
        return f"""Here is a scratchcard product concept:

{concept_description}

Question: How likely would you be to buy this scratchcard at this price?

Please explain your purchase intent clearly and decisively. Would you definitely buy it, probably buy it, or not? Be direct and specific about your commitment level."""

    @staticmethod
    def build_uniqueness_prompt(concept_description: str) -> str:
        """Build prompt for uniqueness question"""
        return f"""Concept:

{concept_description}

Question: How new and different is this scratchcard compared to others you've seen?

Be direct about how innovative this feels. Is it genuinely groundbreaking, or just another standard option?"""

    @staticmethod
    def build_value_prompt(concept_description: str, price: str) -> str:
        """Build prompt for value for money question"""
        return f"""Concept:

{concept_description}

The price is {price}.

Question: Do you think this scratchcard is worth the price? Is it good value for money?

Please explain whether you think the price is fair, too high, or too low for what you're getting."""

    @staticmethod
    def build_likeability_prompt(concept_description: str) -> str:
        """Build prompt for likeability question"""
        return f"""Concept:

{concept_description}

Question: Overall, how much do you like or dislike this scratchcard concept?

Express your genuine feelings clearly. Do you love it, like it, feel neutral, or dislike it? Be direct about your reaction."""

    @staticmethod
    def build_relevance_prompt(concept_description: str) -> str:
        """Build prompt for relevance question"""
        return f"""Concept:

{concept_description}

Question: How relevant is this scratchcard to you personally? Does it fit your interests and preferences?

Please explain how well this product matches your personal interests."""

    @staticmethod
    def build_playfulness_prompt(concept_description: str) -> str:
        """Build prompt for playfulness question"""
        return f"""Concept:

{concept_description}

Question: Would you play this with family or friends?

Please share whether you'd enjoy this as a social activity with others."""

    @staticmethod
    def build_excitement_prompt(concept_description: str) -> str:
        """Build prompt for excitement question"""
        return f"""Concept:

{concept_description}

Question: How exciting is this scratchcard to you?

Be direct about your excitement level. Are you genuinely thrilled, somewhat interested, or completely bored by this?"""

    @staticmethod
    def build_understanding_prompt(concept_description: str) -> str:
        """Build prompt for understanding question"""
        return f"""Concept:

{concept_description}

Question: How well do you understand what to expect from this scratchcard? Is it clear what you'd get, or confusing?

Please explain how clear or unclear this concept is to you."""

    @staticmethod
    def build_believability_prompt(concept_description: str) -> str:
        """Build prompt for believability question"""
        return f"""Concept:

{concept_description}

Question: How believable is this scratchcard concept? Does it seem realistic or too good to be true?

Be direct about your confidence in this. Is it completely believable, somewhat credible, or totally unrealistic?"""

    @staticmethod
    def build_gift_intent_prompt(concept_description: str) -> str:
        """Build prompt for gift purchase intent question"""
        return f"""Concept:

{concept_description}

Question: Would you buy this scratchcard as a gift for someone?

Please explain whether you think this would make a good gift."""

    @staticmethod
    def build_gift_satisfaction_prompt(concept_description: str) -> str:
        """Build prompt for gift satisfaction question"""
        return f"""Concept:

{concept_description}

Question: How pleased would you be if you received this scratchcard as a gift?

Please share how you'd feel if someone gave this to you as a present."""

    @staticmethod
    def build_increment_prompt(concept_description: str) -> str:
        """Build prompt for incrementality question"""
        return f"""Concept:

{concept_description}

Question: If this scratchcard wasn't available, what would you do?

Would you buy a different scratchcard instead, or would you not buy a scratchcard at all?"""

    @staticmethod
    def build_likes_prompt(concept_description: str) -> str:
        """Build prompt for likes question (B15)"""
        return f"""Concept:

{concept_description}

Question: What do you like most about this product?

Think about what appeals to you. If there is something you genuinely like, explain it briefly. If you truly don't like anything about this concept, simply respond with "Nothing" - that's a perfectly acceptable answer. Be honest - don't invent positives if you don't feel any."""

    @staticmethod
    def build_dislikes_prompt(concept_description: str) -> str:
        """Build prompt for dislikes question (B16)"""
        return f"""Concept:

{concept_description}

Question: What do you like least about this product?

Think about what concerns you or what you dislike. If there are genuine concerns, explain them briefly. If you truly have no concerns or dislikes about this concept, simply respond with "Nothing" - that's a perfectly acceptable answer. Be honest - don't invent negatives if you don't feel any."""

    @staticmethod
    def build_generic_prompt(question_text: str, concept_description: str) -> str:
        """Build a generic prompt for any question"""
        return f"""Concept:

{concept_description}

Question: {question_text}

Please provide your honest answer."""
