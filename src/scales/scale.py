"""
Scale Data Structures

Defines scale types and their properties for the SSR system.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ScaleType(Enum):
    """Types of rating scales"""
    LIKERT_4 = "likert_4"
    LIKERT_5 = "likert_5"
    LIKERT_6 = "likert_6"
    SLIDER_7 = "slider_7"
    SLIDER_9 = "slider_9"
    BINARY = "binary"
    MULTI_SELECT = "multi_select"
    CUSTOM = "custom"


@dataclass
class Scale:
    """
    A measurement scale with anchor statements for SSR.

    Attributes:
        id: Unique identifier (e.g., "likert5_purchase_intent_v1")
        name: Human-readable name
        scale_type: Type of scale
        num_levels: Number of scale points
        level_values: Actual values (e.g., [1,2,3,4,5] or ["No","Yes"])
        level_labels: Human-readable labels for each level
        anchor_texts: Primary anchor statements for SSR (one per level)
        anchor_text_sets: Optional multiple reference sets for averaging (6 sets per paper)
        num_reference_sets: Number of reference sets (1 for single set, 6 for paper's approach)
        description: What this scale measures
        language: Language code (e.g., "en")
        version: Version string (e.g., "v1")
        is_deprecated: Whether this scale version is deprecated
        is_reversed_polarity: Whether level 1 represents the most positive response
            (True for scales like UNIQUENESS where 1="Extremely new" is positive,
             False for standard scales where 1 is negative/low and 5 is positive/high)
    """
    id: str
    name: str
    scale_type: ScaleType
    num_levels: int
    level_values: List[any]
    level_labels: List[str]
    anchor_texts: List[str]
    description: str
    language: str = "en"
    version: str = "v1"
    is_deprecated: bool = False
    is_reversed_polarity: bool = False
    metadata: dict = field(default_factory=dict)
    anchor_text_sets: Optional[List[List[str]]] = None
    num_reference_sets: int = 1

    def __post_init__(self):
        """Validate scale consistency"""
        if not (len(self.level_values) == len(self.level_labels) == len(self.anchor_texts) == self.num_levels):
            raise ValueError(
                f"Scale {self.id}: Inconsistent lengths - "
                f"num_levels={self.num_levels}, "
                f"level_values={len(self.level_values)}, "
                f"level_labels={len(self.level_labels)}, "
                f"anchor_texts={len(self.anchor_texts)}"
            )

        # Check for duplicate values
        if len(set(self.level_values)) != len(self.level_values):
            raise ValueError(f"Scale {self.id}: Duplicate level values")

        # Validate multiple reference sets if provided
        if self.anchor_text_sets is not None:
            if len(self.anchor_text_sets) != self.num_reference_sets:
                raise ValueError(
                    f"Scale {self.id}: Expected {self.num_reference_sets} reference sets, "
                    f"got {len(self.anchor_text_sets)}"
                )

            for i, ref_set in enumerate(self.anchor_text_sets):
                if len(ref_set) != self.num_levels:
                    raise ValueError(
                        f"Scale {self.id}: Reference set {i} has {len(ref_set)} anchors, "
                        f"expected {self.num_levels}"
                    )

    def get_level_by_value(self, value: any) -> Optional[int]:
        """Get the index of a level by its value"""
        try:
            return self.level_values.index(value)
        except ValueError:
            return None

    def get_level_by_label(self, label: str) -> Optional[int]:
        """Get the index of a level by its label"""
        try:
            return self.level_labels.index(label)
        except ValueError:
            return None


@dataclass
class RatingResult:
    """Result of an SSR rating"""
    chosen_level_value: any
    chosen_level_index: int
    chosen_level_label: str
    probabilities: List[float]
    raw_similarities: List[float]
    scale_id: str
    scale_version: str
    embedding_model_id: str
    timestamp: str
    debug_info: dict = field(default_factory=dict)

    def to_formatted_response(self) -> str:
        """
        Format the response in the Excel format: "(code) label"

        Example: "(1) Definitely would"
        """
        return f"({self.chosen_level_value}) {self.chosen_level_label}"
