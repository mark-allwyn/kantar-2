"""
Test Individual Components (No API Calls)

Tests components that don't require external APIs.
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.persona.generator import PersonaGenerator
from src.logic.conditional_logic import create_standard_survey_logic, Operator
from src.scales.registry import create_default_scales
from src.ssr.similarity import cosine_similarity, softmax_with_temperature
from src.validation.metrics import ValidationMetrics


def test_persona_generation():
    """Test persona generation"""
    print("\n" + "="*80)
    print("Testing Persona Generation")
    print("="*80)

    try:
        gen = PersonaGenerator(random_seed=42)
        persona = gen.generate_persona()

        assert persona.id is not None
        assert 'age' in persona.demographics
        assert 'gender' in persona.demographics
        assert 18 <= persona.demographics['age'] <= 75

        print(f"✓ Generated persona: {persona.to_description()}")

        # Test batch generation
        batch = gen.generate_batch(10)
        assert len(batch) == 10
        print(f"✓ Generated batch of {len(batch)} personas")

        return True
    except Exception as e:
        print(f"✗ Persona generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conditional_logic():
    """Test survey logic"""
    print("\n" + "="*80)
    print("Testing Conditional Logic")
    print("="*80)

    try:
        logic = create_standard_survey_logic()

        # Test B21 conditional (barriers if low intent)
        responses_high = {'B2': 1}  # High intent
        responses_low = {'B2': 5}   # Low intent

        should_ask_high = logic.should_ask_question('B21', responses_high)
        should_ask_low = logic.should_ask_question('B21', responses_low)

        assert should_ask_high == False, "Should not ask barriers with high intent"
        assert should_ask_low == True, "Should ask barriers with low intent"

        print("✓ B21 conditional logic works correctly")

        # Test screening
        valid_persona = {'occupation': 'Technology', 'age': 30}
        invalid_persona = {'occupation': 'Marketing/Market Research', 'age': 30}

        passes_valid, _ = logic.apply_screening(valid_persona)
        passes_invalid, reason = logic.apply_screening(invalid_persona)

        assert passes_valid == True
        assert passes_invalid == False

        print(f"✓ Screening works (invalid reason: {reason})")

        return True
    except Exception as e:
        print(f"✗ Conditional logic failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scales():
    """Test scale registry"""
    print("\n" + "="*80)
    print("Testing Scales")
    print("="*80)

    try:
        registry = create_default_scales()

        assert len(registry.scales) > 0
        print(f"✓ Created {len(registry.scales)} scales")

        # Test specific scale
        scale = registry.get_scale('likert5_purchase_intent_v1')
        assert scale is not None
        assert scale.num_levels == 5
        assert len(scale.anchor_texts) == 5
        assert len(scale.level_values) == 5

        print(f"✓ Purchase intent scale validated:")
        print(f"   Levels: {scale.num_levels}")
        print(f"   First anchor: {scale.anchor_texts[0][:50]}...")

        return True
    except Exception as e:
        print(f"✗ Scales failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_similarity():
    """Test similarity functions"""
    print("\n" + "="*80)
    print("Testing Similarity Functions")
    print("="*80)

    try:
        # Test cosine similarity
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([1, 0, 0])
        vec3 = np.array([0, 1, 0])

        sim_same = cosine_similarity(vec1, vec2)
        sim_diff = cosine_similarity(vec1, vec3)

        assert np.isclose(sim_same, 1.0), f"Same vectors should have similarity 1.0, got {sim_same}"
        assert np.isclose(sim_diff, 0.0), f"Orthogonal vectors should have similarity 0.0, got {sim_diff}"

        print(f"✓ Cosine similarity: same={sim_same:.3f}, different={sim_diff:.3f}")

        # Test softmax
        similarities = np.array([0.5, 0.7, 0.6, 0.3, 0.4])
        probs = softmax_with_temperature(similarities, temperature=0.5)

        assert np.isclose(probs.sum(), 1.0), f"Probabilities should sum to 1, got {probs.sum()}"
        assert np.all(probs >= 0), "All probabilities should be non-negative"
        assert np.argmax(probs) == 1, "Highest similarity should have highest probability"

        print(f"✓ Softmax: probs sum to {probs.sum():.3f}, highest at index {np.argmax(probs)}")

        return True
    except Exception as e:
        print(f"✗ Similarity functions failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation_metrics():
    """Test validation metrics"""
    print("\n" + "="*80)
    print("Testing Validation Metrics")
    print("="*80)

    try:
        # Test KL divergence
        p = np.array([0.2, 0.3, 0.3, 0.2])  # Ground truth
        q_perfect = np.array([0.2, 0.3, 0.3, 0.2])  # Perfect match
        q_different = np.array([0.4, 0.1, 0.1, 0.4])  # Different

        kl_perfect = ValidationMetrics.kl_divergence(p, q_perfect)
        kl_different = ValidationMetrics.kl_divergence(p, q_different)

        assert kl_perfect < 0.01, f"Perfect match should have KL≈0, got {kl_perfect}"
        assert kl_different > kl_perfect, "Different distribution should have higher KL"

        print(f"✓ KL divergence: perfect={kl_perfect:.6f}, different={kl_different:.4f}")

        # Test correlation
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([1.1, 2.0, 3.1, 3.9, 5.1])

        corr = ValidationMetrics.correlation(x, y)
        assert corr > 0.95, f"Highly correlated data should have correlation >0.95, got {corr}"

        print(f"✓ Correlation: {corr:.4f}")

        return True
    except Exception as e:
        print(f"✗ Validation metrics failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all component tests"""
    print("\n" + "="*80)
    print("RUNNING COMPONENT TESTS (No API calls)")
    print("="*80)

    results = {
        'Persona Generation': test_persona_generation(),
        'Conditional Logic': test_conditional_logic(),
        'Scales': test_scales(),
        'Similarity Functions': test_similarity(),
        'Validation Metrics': test_validation_metrics(),
    }

    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 All component tests passed!")
    else:
        print(f"\n⚠️  {sum(not v for v in results.values())} tests failed")

    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
