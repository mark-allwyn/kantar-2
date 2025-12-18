"""
SSR Rating Engine

Main orchestration for Semantic Similarity Rating.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import numpy as np

from ..scales.scale import Scale, RatingResult
from ..scales.registry import ScaleRegistry
from .embeddings import EmbeddingService
from .similarity import compute_similarities, normalize_to_probabilities, select_level, average_pmfs


class RatingEngine:
    """Semantic Similarity Rating (SSR) engine"""

    def __init__(self,
                 scale_registry: ScaleRegistry,
                 embedding_service: EmbeddingService):
        """
        Initialize the rating engine.

        Args:
            scale_registry: Registry containing all scale definitions
            embedding_service: Service for generating text embeddings
        """
        self.scale_registry = scale_registry
        self.embedding_service = embedding_service

        # Cache for anchor embeddings (to avoid re-embedding)
        self._anchor_cache: Dict[str, np.ndarray] = {}

    def rate_answer(self,
                   answer_text: str,
                   scale_id: str,
                   temperature: float = 1.0,
                   normalization_method: str = "linear",
                   selection_method: str = "sample",
                   use_multiple_reference_sets: bool = True,
                   return_debug_info: bool = False) -> RatingResult:
        """
        Rate a free-text answer using SSR (Semantic Similarity Rating).

        Implementation follows the paper "LLMs Reproduce Human Purchase Intent
        via Semantic Similarity Elicitation of Likert Ratings" (2510.08338v2).

        Args:
            answer_text: The free-text response to rate
            scale_id: ID of the scale to use
            temperature: Temperature for probability normalization (default 1.0 per paper)
            normalization_method: "softmax" or "linear" (default "linear" per Equation 8 in paper)
            selection_method: "argmax" or "sample" (default "sample" to preserve distributions)
            use_multiple_reference_sets: Whether to use multiple reference sets (6) and average PMFs (default True per paper)
            return_debug_info: Whether to include debug information

        Returns:
            RatingResult with chosen level and probabilities
        """
        # Get scale
        scale = self.scale_registry.get_scale(scale_id)
        if scale is None:
            raise ValueError(f"Scale {scale_id} not found in registry")

        # Get anchor embeddings (use cache if available)
        # Cache stores list of embedding arrays (one per reference set)
        if scale_id not in self._anchor_cache:
            if use_multiple_reference_sets and scale.anchor_text_sets is not None and scale.num_reference_sets > 1:
                # Cache embeddings for all reference sets
                all_anchor_embeddings = [
                    self.embedding_service.embed_texts(anchor_set)
                    for anchor_set in scale.anchor_text_sets
                ]
                self._anchor_cache[scale_id] = all_anchor_embeddings
            else:
                # Backward compatible: single set
                anchor_embeddings = self.embedding_service.embed_texts(scale.anchor_texts)
                self._anchor_cache[scale_id] = [anchor_embeddings]  # Wrap in list for consistency

        anchor_embeddings_list = self._anchor_cache[scale_id]

        # Embed the answer once
        answer_embedding = self.embedding_service.embed_single(answer_text)

        # Compute PMF for each reference set
        pmfs = []
        all_similarities = []  # For debug info

        for anchor_embeddings in anchor_embeddings_list:
            # Compute similarities for this reference set
            similarities = compute_similarities(answer_embedding, anchor_embeddings)
            all_similarities.append(similarities)

            # Normalize to probabilities for this reference set
            pmf = normalize_to_probabilities(
                similarities,
                method=normalization_method,
                temperature=temperature
            )
            pmfs.append(pmf)

        # Average the PMFs (key step from paper's Appendix A.4.3)
        if len(pmfs) > 1:
            probabilities = average_pmfs(pmfs)
            # Use first reference set's similarities for debug (or could average these too)
            similarities = all_similarities[0]
        else:
            probabilities = pmfs[0]
            similarities = all_similarities[0]

        # Select level
        chosen_index = select_level(probabilities, method=selection_method)

        # Get level details
        # Note: The anchor_texts are always ordered to match level_labels and level_values,
        # regardless of polarity. So chosen_index directly maps to the correct level.
        chosen_value = scale.level_values[chosen_index]
        chosen_label = scale.level_labels[chosen_index]

        # Build debug info
        debug_info = {}
        if return_debug_info:
            debug_info = {
                "temperature": temperature,
                "normalization_method": normalization_method,
                "selection_method": selection_method,
                "answer_text": answer_text,
                "anchor_texts": scale.anchor_texts,
                "num_reference_sets": len(pmfs),
                "use_multiple_reference_sets": use_multiple_reference_sets and len(pmfs) > 1,
                "similarity_stats": {
                    "min": float(np.min(similarities)),
                    "max": float(np.max(similarities)),
                    "mean": float(np.mean(similarities)),
                    "std": float(np.std(similarities))
                },
                "probability_stats": {
                    "entropy": float(-np.sum(probabilities * np.log(probabilities + 1e-10))),
                    "max_prob": float(np.max(probabilities)),
                    "confidence": float(probabilities[chosen_index]),
                    "chosen_index": chosen_index
                }
            }

            # Add individual PMFs if using multiple reference sets
            if len(pmfs) > 1:
                debug_info["individual_pmfs"] = [pmf.tolist() for pmf in pmfs]
                debug_info["averaged_pmf"] = probabilities.tolist()

        # Create result
        result = RatingResult(
            chosen_level_value=chosen_value,
            chosen_level_index=chosen_index,
            chosen_level_label=chosen_label,
            probabilities=probabilities.tolist(),
            raw_similarities=similarities.tolist(),
            scale_id=scale.id,
            scale_version=scale.version,
            embedding_model_id=self.embedding_service.model_id,
            timestamp=datetime.now().isoformat(),
            debug_info=debug_info
        )

        return result

    def rate_batch(self,
                  answers: list[str],
                  scale_id: str,
                  **kwargs) -> list[RatingResult]:
        """
        Rate multiple answers using the same scale.

        Args:
            answers: List of free-text responses
            scale_id: ID of the scale to use
            **kwargs: Additional arguments passed to rate_answer

        Returns:
            List of RatingResults
        """
        return [self.rate_answer(answer, scale_id, **kwargs) for answer in answers]

    def clear_cache(self):
        """Clear the anchor embedding cache"""
        self._anchor_cache.clear()

    def preload_scales(self, scale_ids: list[str] = None):
        """
        Preload anchor embeddings for specified scales.

        Args:
            scale_ids: List of scale IDs to preload (if None, preloads all)
        """
        if scale_ids is None:
            scale_ids = list(self.scale_registry.scales.keys())

        for scale_id in scale_ids:
            if scale_id not in self._anchor_cache:
                scale = self.scale_registry.get_scale(scale_id)
                if scale:
                    if scale.anchor_text_sets is not None and scale.num_reference_sets > 1:
                        # Cache embeddings for all reference sets
                        all_anchor_embeddings = [
                            self.embedding_service.embed_texts(anchor_set)
                            for anchor_set in scale.anchor_text_sets
                        ]
                        self._anchor_cache[scale_id] = all_anchor_embeddings
                    else:
                        # Backward compatible: single set (wrap in list)
                        anchor_embeddings = self.embedding_service.embed_texts(scale.anchor_texts)
                        self._anchor_cache[scale_id] = [anchor_embeddings]
