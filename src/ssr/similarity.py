"""
Similarity and Normalization Engine

Computes cosine similarity and converts to probability distributions.
"""

import numpy as np
from typing import List


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity value between -1 and 1
    """
    # Handle zero vectors
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return np.dot(vec1, vec2) / (norm1 * norm2)


def compute_similarities(answer_vector: np.ndarray, anchor_vectors: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarities between an answer and multiple anchors.

    Args:
        answer_vector: Vector for the answer (shape: embedding_dim)
        anchor_vectors: Vectors for anchors (shape: n_anchors × embedding_dim)

    Returns:
        Array of similarity scores (shape: n_anchors)
    """
    similarities = np.array([
        cosine_similarity(answer_vector, anchor_vec)
        for anchor_vec in anchor_vectors
    ])

    return similarities


def softmax_with_temperature(similarities: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    """
    Convert similarity scores to probability distribution using softmax.

    Args:
        similarities: Array of similarity scores
        temperature: Temperature parameter for softmax
                    - Lower T (e.g., 0.5): More confident, peaked distribution
                    - Higher T (e.g., 2.0): More uncertain, spread distribution
                    - T = 1.0: Standard softmax

    Returns:
        Probability distribution (sums to 1)
    """
    if temperature <= 0:
        raise ValueError("Temperature must be positive")

    # Scale by temperature
    scaled = similarities / temperature

    # Subtract max for numerical stability
    scaled = scaled - np.max(scaled)

    # Compute exponentials
    exp_scaled = np.exp(scaled)

    # Normalize to probabilities
    probabilities = exp_scaled / np.sum(exp_scaled)

    return probabilities


def linear_normalization(similarities: np.ndarray, epsilon: float = 0.0) -> np.ndarray:
    """
    Convert similarity scores to probability distribution using linear scaling.

    Alternative to softmax that preserves relative differences more directly.

    Args:
        similarities: Array of similarity scores
        epsilon: Minimum similarity value (default 0.0)

    Returns:
        Probability distribution (sums to 1)
    """
    # Ensure non-negative by shifting and adding epsilon
    shifted = similarities - np.min(similarities) + epsilon

    # Normalize to sum to 1
    if np.sum(shifted) == 0:
        # If all zeros, use uniform distribution
        return np.ones_like(similarities) / len(similarities)

    probabilities = shifted / np.sum(shifted)

    return probabilities


def normalize_to_probabilities(similarities: np.ndarray,
                               method: str = "softmax",
                               temperature: float = 1.0,
                               epsilon: float = 0.0) -> np.ndarray:
    """
    Convert similarity scores to probability distribution.

    Args:
        similarities: Array of similarity scores
        method: Normalization method ("softmax" or "linear")
        temperature: Temperature for softmax
        epsilon: Epsilon for linear normalization

    Returns:
        Probability distribution (sums to 1)
    """
    if method == "softmax":
        return softmax_with_temperature(similarities, temperature)
    elif method == "linear":
        return linear_normalization(similarities, epsilon)
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def select_level(probabilities: np.ndarray, method: str = "argmax") -> int:
    """
    Select a level based on probabilities.

    Args:
        probabilities: Probability distribution over levels
        method: Selection method
               - "argmax": Choose level with highest probability (deterministic)
               - "sample": Sample from distribution (stochastic)

    Returns:
        Index of selected level
    """
    if method == "argmax":
        return int(np.argmax(probabilities))
    elif method == "sample":
        return int(np.random.choice(len(probabilities), p=probabilities))
    else:
        raise ValueError(f"Unknown selection method: {method}")


def average_pmfs(pmfs: List[np.ndarray]) -> np.ndarray:
    """
    Average multiple probability mass functions.

    Implementation follows the paper's approach of averaging PMFs from multiple
    reference sets (Equation 8, Appendix A.4.3).

    Args:
        pmfs: List of probability distributions (each sums to 1)

    Returns:
        Averaged probability distribution (sums to 1)

    Raises:
        ValueError: If pmfs list is empty or distributions have different lengths
    """
    if len(pmfs) == 0:
        raise ValueError("Cannot average empty list of PMFs")

    if len(pmfs) == 1:
        return pmfs[0]

    # Check all PMFs have same length
    pmf_length = len(pmfs[0])
    if not all(len(pmf) == pmf_length for pmf in pmfs):
        raise ValueError("All PMFs must have the same length")

    # Arithmetic mean across all PMFs (as per paper)
    averaged = np.mean(pmfs, axis=0)

    # Ensure it's 1D (flatten if needed)
    averaged = np.asarray(averaged).flatten()

    # Ensure it still sums to 1 (numerical stability)
    sum_averaged = np.sum(averaged)
    if sum_averaged > 0:
        averaged = averaged / sum_averaged

    return averaged
