"""
LLM Client

Wrapper for OpenAI GPT-4o API to generate synthetic respondent answers.
"""

from typing import Optional, List, Dict
import time
import os
from openai import OpenAI


class LLMClient:
    """Client for generating LLM responses"""

    def __init__(self,
                 model: str = "gpt-4o",
                 api_key: Optional[str] = None,
                 temperature: float = 0.5,
                 max_tokens: int = 500):
        """
        Initialize the LLM client.

        Args:
            model: OpenAI model ID (default: gpt-4o)
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            temperature: Sampling temperature (default: 0.5 per paper)
            max_tokens: Maximum tokens in response
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY env var")

        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def generate_response(self,
                         system_prompt: str,
                         user_prompt: str,
                         temperature: Optional[float] = None) -> str:
        """
        Generate a response from the LLM.

        Args:
            system_prompt: System message (persona conditioning)
            user_prompt: User message (question)
            temperature: Override default temperature

        Returns:
            Generated response text
        """
        temp = temperature if temperature is not None else self.temperature

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=self.max_tokens,
                    top_p=0.9  # As mentioned in the paper
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"LLM attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise Exception(f"Failed to generate response after {self.max_retries} attempts: {e}")

    def generate_batch(self,
                      system_prompt: str,
                      user_prompts: List[str],
                      temperature: Optional[float] = None) -> List[str]:
        """
        Generate multiple responses.

        Args:
            system_prompt: System message (same for all)
            user_prompts: List of user messages
            temperature: Override default temperature

        Returns:
            List of generated responses
        """
        return [
            self.generate_response(system_prompt, prompt, temperature)
            for prompt in user_prompts
        ]
