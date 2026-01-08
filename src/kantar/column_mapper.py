"""
Column mapper for matching Kantar Excel format.

Maps between current system column names and Kantar ground truth format,
handling concept name variations and question ID patterns.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ColumnMapping:
    """Mapping between system and Kantar column formats."""
    system_column: str
    kantar_column: str
    question_id: str
    concept_name: Optional[str] = None


class ColumnMapper:
    """
    Maps between system and Kantar column naming conventions.

    The Kantar format uses patterns like:
    "(UNPURINT) UNPRICED PURCHASE INTENT - Concept Name"

    The system format may vary, so this mapper provides flexible matching.
    """

    # Question ID mappings (system -> Kantar)
    QUESTION_MAPPINGS = {
        'PRPURINT': 'UNPURINT',  # Priced vs Unpriced purchase intent
        'UNPURINT': 'UNPURINT',
        'UNIQNESS': 'UNIQNESS',
        'UNPRICEP': 'UNPRICEP',
        'LIKBILTY': 'LIKBILTY',
        'INCREMNT': 'INCREMNT',
        'RELVANCE': 'RELVANCE',
        'PLAYFLNS': 'PLAYFLNS',
        'EXCITMENT': 'EXCITMENT',
        'BELVBLTY': 'BELVBLTY',
        'LIKES_STD': 'LIKES_STD',
        'DISLIKES': 'DISLIKES',
        'GIFT': 'WOULD BUY AS GIFT',
        'OCCASIONS': 'OCCASIONS',
        'GIFT_SATISFACTION': 'PLEASED WITH GIFT',
        'BARRIERS': 'BARRIERS'
    }

    # Full question text mapping
    QUESTION_TEXT = {
        'UNPURINT': 'UNPRICED PURCHASE INTENT',
        'UNIQNESS': 'UNIQUENESS',
        'UNPRICEP': 'EXPECTED PRICE COMPARISON',
        'LIKBILTY': 'LIKEABILITY',
        'INCREMNT': 'BUY INSTEAD IF NOT AVAILABLE',
        'RELVANCE': 'RELEVANCE',
        'PLAYFLNS': 'PLAYFULNESS',
        'EXCITMENT': 'EXCITEMENT',
        'BELVBLTY': 'BELIEVEABILITY',
        'LIKES_STD': 'LIKES',
        'DISLIKES': 'DISLIKES',
    }

    def __init__(self):
        """Initialize the column mapper."""
        pass

    def build_kantar_column_name(self, question_id: str, concept_name: str) -> str:
        """
        Build a Kantar-format column name.

        Args:
            question_id: Question ID (e.g., 'UNPURINT')
            concept_name: Concept name (e.g., 'US Pulse Play')

        Returns:
            Kantar format column name
        """
        # Map system question ID to Kantar ID
        kantar_id = self.QUESTION_MAPPINGS.get(question_id, question_id)

        # Get question text
        question_text = self.QUESTION_TEXT.get(kantar_id, kantar_id.replace('_', ' ').upper())

        # Build full column name
        # Format: "(ID) QUESTION TEXT - Concept Name  "
        # Note: Kantar format sometimes has trailing spaces
        column_name = f"({kantar_id}) {question_text} - {concept_name}  "

        return column_name

    def parse_kantar_column(self, column_name: str) -> Optional[Tuple[str, str]]:
        """
        Parse a Kantar column name to extract question ID and concept name.

        Args:
            column_name: Kantar format column name

        Returns:
            Tuple of (question_id, concept_name) or None if not a question column
        """
        # Pattern: "(ID) Text - Concept Name"
        pattern = r'\(([A-Z_]+)\)\s+.+?\s+-\s+(.+?)\s*$'
        match = re.match(pattern, column_name)

        if match:
            question_id = match.group(1)
            concept_name = match.group(2).strip()
            return (question_id, concept_name)

        return None

    def match_concept_names(self,
                          extracted_concepts: List[str],
                          ground_truth_concepts: List[str]) -> Dict[str, str]:
        """
        Match extracted concept names to ground truth concept names.

        Handles variations like:
        - "Pulse Play" vs "US Pulse Play"
        - "Pulse Play" vs "Codes - US Pulse Play"

        Args:
            extracted_concepts: Concepts extracted from PPTX
            ground_truth_concepts: Concepts from ground truth Excel

        Returns:
            Mapping from extracted -> ground truth concept names
        """
        mapping = {}

        for extracted in extracted_concepts:
            best_match = None
            best_score = 0

            for gt in ground_truth_concepts:
                score = self._concept_similarity(extracted, gt)
                if score > best_score:
                    best_score = score
                    best_match = gt

            if best_match and best_score > 0.5:
                mapping[extracted] = best_match
                logger.info(f"Matched '{extracted}' -> '{best_match}' (score: {best_score:.2f})")
            else:
                logger.warning(f"No match found for concept: '{extracted}'")

        return mapping

    def _concept_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity score between two concept names.

        Args:
            name1: First concept name
            name2: Second concept name

        Returns:
            Similarity score (0-1)
        """
        # Normalize
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()

        # Exact match
        if n1 == n2:
            return 1.0

        # Check if one contains the other
        if n1 in n2 or n2 in n1:
            return 0.9

        # Remove common prefixes/suffixes
        prefixes = ['codes - ', 'us ', 'uk ', 'at ', 'cz ', 'gr ']
        for prefix in prefixes:
            n1 = n1.replace(prefix, '')
            n2 = n2.replace(prefix, '')

        # Check again after cleanup
        if n1 == n2:
            return 0.95

        if n1 in n2 or n2 in n1:
            return 0.85

        # Word overlap
        words1 = set(n1.split())
        words2 = set(n2.split())
        overlap = len(words1 & words2)
        total = len(words1 | words2)

        if total == 0:
            return 0.0

        return overlap / total


def main():
    """CLI entry point for testing the mapper."""
    logging.basicConfig(level=logging.INFO)

    mapper = ColumnMapper()

    # Test column name building
    print("=== Column Name Building ===")
    test_cases = [
        ('UNPURINT', 'US Pulse Play'),
        ('UNIQNESS', 'US Standard Or VIP Mode'),
        ('LIKBILTY', 'US Happy Hour'),
    ]

    for question_id, concept in test_cases:
        kantar_col = mapper.build_kantar_column_name(question_id, concept)
        print(f"{question_id} + '{concept}'")
        print(f"  -> '{kantar_col}'")
        print()

    # Test parsing
    print("\n=== Column Name Parsing ===")
    test_columns = [
        "(UNPURINT) UNPRICED PURCHASE INTENT - US Pulse Play  ",
        "(UNIQNESS) UNIQUENESS - US Standard Or VIP Mode  "
    ]

    for col in test_columns:
        result = mapper.parse_kantar_column(col)
        print(f"'{col}'")
        print(f"  -> {result}")
        print()

    # Test concept matching
    print("\n=== Concept Matching ===")
    extracted = ["Pulse Play", "Standard or VIP Mode", "Happy Hour"]
    ground_truth = [
        "US Pulse Play",
        "US Standard Or VIP Mode",
        "US Happy Hour",
        "Codes - US Pulse Play"
    ]

    matches = mapper.match_concept_names(extracted, ground_truth)
    print(f"Matches: {matches}")


if __name__ == "__main__":
    main()
