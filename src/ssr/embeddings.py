"""
Embedding Service

Wrapper for text embedding models (OpenAI API).
"""

from typing import List
import numpy as np
from openai import OpenAI
import time
import os


class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self, model_id: str = "text-embedding-3-small", api_key: str = None):
        """
        Initialize the embedding service.

        Args:
            model_id: OpenAI embedding model ID
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
        """
        self.model_id = model_id
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY env var")

        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        if not texts:
            return np.array([])

        # Clean texts (remove empty strings, strip whitespace)
        cleaned_texts = [str(text).strip() for text in texts if text]

        if not cleaned_texts:
            return np.array([])

        # Call OpenAI API with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    input=cleaned_texts,
                    model=self.model_id
                )

                # Extract embeddings from response
                embeddings = [item.embedding for item in response.data]

                return np.array(embeddings)

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Embedding attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise Exception(f"Failed to generate embeddings after {self.max_retries} attempts: {e}")

    def embed_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            numpy array of shape (embedding_dim,)
        """
        embeddings = self.embed_texts([text])
        return embeddings[0] if len(embeddings) > 0 else np.array([])

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for this model.

        Returns:
            Embedding dimension
        """
        # Known dimensions for OpenAI models
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }

        return dimensions.get(self.model_id, 1536)  # Default to 1536
