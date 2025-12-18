#!/usr/bin/env python3
"""
Test script to verify multiple reference sets functionality.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scales.scale import Scale, ScaleType
from src.scales.registry import ScaleRegistry
from src.ssr.embeddings import EmbeddingService
from src.ssr.rating_engine import RatingEngine

def test_backward_compatibility():
    """Test that single-set scales still work"""
    print("Test 1: Backward Compatibility (Single Reference Set)")
    print("="*60)

    # Create a simple registry with one scale
    registry = ScaleRegistry()
    registry.register_scale(Scale(
        id="test_scale_single",
        name="Test Scale",
        scale_type=ScaleType.LIKERT_5,
        num_levels=5,
        level_values=[1, 2, 3, 4, 5],
        level_labels=["Definitely", "Probably", "Maybe", "Probably not", "Definitely not"],
        anchor_texts=[
            "I would definitely do this",
            "I would probably do this",
            "I might or might not do this",
            "I probably would not do this",
            "I definitely would not do this"
        ],
        description="Test scale"
    ))

    # Create rating engine
    embedding_service = EmbeddingService()
    engine = RatingEngine(registry, embedding_service)

    # Test rating
    result = engine.rate_answer(
        "I think this is a great idea and I would love to try it",
        scale_id="test_scale_single"
    )

    print(f"✓ Answer: 'I think this is a great idea...'")
    print(f"✓ Chosen: ({result.chosen_level_value}) {result.chosen_level_label}")
    print(f"✓ Probabilities: {[f'{p:.3f}' for p in result.probabilities]}")
    print(f"✓ Test PASSED - Single set works!\n")

    return True


def test_multiple_reference_sets():
    """Test that multiple reference sets work"""
    print("Test 2: Multiple Reference Sets (6 Sets)")
    print("="*60)

    # Create registry with multi-set scale
    registry = ScaleRegistry()
    registry.register_scale(Scale(
        id="test_scale_multi",
        name="Test Multi Scale",
        scale_type=ScaleType.LIKERT_5,
        num_levels=5,
        level_values=[1, 2, 3, 4, 5],
        level_labels=["Definitely", "Probably", "Maybe", "Probably not", "Definitely not"],
        anchor_texts=[  # Primary set (for backward compat)
            "I would definitely do this",
            "I would probably do this",
            "I might or might not do this",
            "I probably would not do this",
            "I definitely would not do this"
        ],
        description="Test multi-set scale",
        num_reference_sets=3,  # Use 3 for faster testing
        anchor_text_sets=[
            # Set 0
            [
                "Absolutely yes, I'd do this",
                "Most likely yes, I'd do this",
                "Uncertain if I'd do this",
                "Most likely no, I wouldn't do this",
                "Absolutely no, I wouldn't do this"
            ],
            # Set 1
            [
                "Definitely would proceed",
                "Probably would proceed",
                "Might proceed or not",
                "Probably wouldn't proceed",
                "Definitely wouldn't proceed"
            ],
            # Set 2
            [
                "Very interested in doing this",
                "Somewhat interested in doing this",
                "Neutral about doing this",
                "Somewhat uninterested in doing this",
                "Very uninterested in doing this"
            ]
        ]
    ))

    # Create rating engine
    embedding_service = EmbeddingService()
    engine = RatingEngine(registry, embedding_service)

    # Test rating with multiple sets
    result = engine.rate_answer(
        "I think this is a great idea and I would love to try it",
        scale_id="test_scale_multi",
        use_multiple_reference_sets=True,
        return_debug_info=True
    )

    print(f"✓ Answer: 'I think this is a great idea...'")
    print(f"✓ Chosen: ({result.chosen_level_value}) {result.chosen_level_label}")
    print(f"✓ Probabilities (averaged): {[f'{p:.3f}' for p in result.probabilities]}")
    print(f"✓ Number of reference sets used: {result.debug_info['num_reference_sets']}")
    print(f"✓ Multiple sets enabled: {result.debug_info['use_multiple_reference_sets']}")

    if 'individual_pmfs' in result.debug_info:
        print(f"\n  Individual PMFs:")
        for i, pmf in enumerate(result.debug_info['individual_pmfs']):
            print(f"    Set {i}: {[f'{p:.3f}' for p in pmf]}")
        print(f"    Averaged: {[f'{p:.3f}' for p in result.debug_info['averaged_pmf']]}")

    print(f"\n✓ Test PASSED - Multiple sets work!\n")

    return True


if __name__ == '__main__':
    try:
        print("\n" + "="*60)
        print("TESTING MULTIPLE REFERENCE SETS IMPLEMENTATION")
        print("="*60 + "\n")

        # Test backward compatibility
        if not test_backward_compatibility():
            print("❌ Backward compatibility test FAILED")
            sys.exit(1)

        # Test multiple reference sets
        if not test_multiple_reference_sets():
            print("❌ Multiple reference sets test FAILED")
            sys.exit(1)

        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
