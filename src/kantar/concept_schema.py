"""
Concept schema validation for synthetic survey generation.

Provides validation and helper functions for concept dictionaries.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


# Required concept fields
REQUIRED_FIELDS = ['id', 'name', 'description']

# Optional concept fields with defaults
OPTIONAL_FIELDS = {
    'full_text': None,
    'price': None,
    'features': [],
    'occasion': None
}


def validate_concept(concept: Dict[str, Any], strict: bool = True) -> bool:
    """
    Validate a single concept dictionary.

    Args:
        concept: Concept dictionary to validate
        strict: If True, raise ValueError on invalid. If False, log warning and return False.

    Returns:
        True if valid

    Raises:
        ValueError: If concept invalid and strict=True
    """
    # Check type
    if not isinstance(concept, dict):
        error_msg = f"Concept must be a dictionary, got {type(concept)}"
        if strict:
            raise ValueError(error_msg)
        logger.warning(error_msg)
        return False

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in concept:
            error_msg = f"Concept missing required field: '{field}'. Concept keys: {list(concept.keys())}"
            if strict:
                raise ValueError(error_msg)
            logger.warning(error_msg)
            return False

    # Check field types
    if not isinstance(concept['id'], str) or not concept['id'].strip():
        error_msg = f"Concept 'id' must be a non-empty string, got: {concept['id']}"
        if strict:
            raise ValueError(error_msg)
        logger.warning(error_msg)
        return False

    if not isinstance(concept['name'], str) or not concept['name'].strip():
        error_msg = f"Concept 'name' must be a non-empty string, got: {concept['name']}"
        if strict:
            raise ValueError(error_msg)
        logger.warning(error_msg)
        return False

    if not isinstance(concept['description'], str) or not concept['description'].strip():
        error_msg = f"Concept 'description' must be a non-empty string, got: {concept['description']}"
        if strict:
            raise ValueError(error_msg)
        logger.warning(error_msg)
        return False

    # Validate optional fields if present
    if 'features' in concept and not isinstance(concept['features'], list):
        error_msg = f"Concept 'features' must be a list, got: {type(concept['features'])}"
        if strict:
            raise ValueError(error_msg)
        logger.warning(error_msg)
        return False

    return True


def validate_concepts(concepts: List[Dict[str, Any]], strict: bool = True) -> bool:
    """
    Validate a list of concept dictionaries.

    Args:
        concepts: List of concept dictionaries
        strict: If True, raise ValueError on invalid. If False, log warnings.

    Returns:
        True if all valid

    Raises:
        ValueError: If concepts invalid and strict=True
    """
    if not isinstance(concepts, list):
        error_msg = f"Concepts must be a list, got {type(concepts)}"
        if strict:
            raise ValueError(error_msg)
        logger.warning(error_msg)
        return False

    if len(concepts) == 0:
        error_msg = "Concepts list is empty"
        if strict:
            raise ValueError(error_msg)
        logger.warning(error_msg)
        return False

    # Validate each concept
    for i, concept in enumerate(concepts):
        try:
            if not validate_concept(concept, strict=strict):
                if not strict:
                    logger.warning(f"Concept {i} failed validation")
                    return False
        except ValueError as e:
            if strict:
                raise ValueError(f"Concept {i} validation failed: {e}")
            logger.warning(f"Concept {i} validation failed: {e}")
            return False

    # Check for duplicate IDs
    concept_ids = [c['id'] for c in concepts]
    if len(concept_ids) != len(set(concept_ids)):
        duplicates = [id for id in concept_ids if concept_ids.count(id) > 1]
        error_msg = f"Duplicate concept IDs found: {set(duplicates)}"
        if strict:
            raise ValueError(error_msg)
        logger.warning(error_msg)
        return False

    return True


def fill_concept_defaults(concept: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fill in default values for optional concept fields.

    Args:
        concept: Concept dictionary (will be modified in place)

    Returns:
        Modified concept dictionary
    """
    for field, default_value in OPTIONAL_FIELDS.items():
        if field not in concept:
            concept[field] = default_value

    # Special handling for full_text
    if concept.get('full_text') is None:
        # Construct from description
        parts = [concept['description']]

        if concept.get('price'):
            parts.append(f"Price: {concept['price']}")

        if concept.get('features') and len(concept['features']) > 0:
            features_str = ', '.join(concept['features'])
            parts.append(f"Features: {features_str}")

        if concept.get('occasion'):
            parts.append(f"Occasion: {concept['occasion']}")

        concept['full_text'] = '. '.join(parts)

    return concept


def create_concept_template() -> Dict[str, Any]:
    """
    Create an empty concept template with all fields.

    Returns:
        Concept template dictionary
    """
    return {
        'id': '',
        'name': '',
        'description': '',
        'full_text': '',
        'price': None,
        'features': [],
        'occasion': None
    }


def format_concept_example() -> str:
    """
    Get a formatted example of a valid concept dictionary.

    Returns:
        String representation of example concept
    """
    example = {
        'id': 'Concept1',
        'name': 'Premium Lottery Experience',
        'description': 'A new lottery game that offers enhanced odds and exclusive prizes for premium players',
        'full_text': 'Introducing our Premium Lottery Experience: a revolutionary new game designed for players who want more. Enhanced odds of winning, exclusive prize tiers, and a VIP playing experience.',
        'price': '$5 per ticket',
        'features': [
            'Enhanced winning odds',
            'Exclusive prize tiers',
            'VIP member benefits',
            'Online and retail play'
        ],
        'occasion': 'Regular play and special occasions'
    }

    import json
    return json.dumps(example, indent=2)


def print_concept_requirements():
    """Print concept schema requirements to console."""
    print("\n=== Concept Schema Requirements ===\n")
    print("Required fields:")
    for field in REQUIRED_FIELDS:
        print(f"  - {field}: string (non-empty)")

    print("\nOptional fields:")
    for field, default in OPTIONAL_FIELDS.items():
        print(f"  - {field}: {type(default).__name__} (default: {default})")

    print("\nExample concept:")
    print(format_concept_example())
    print()
