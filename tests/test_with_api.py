"""
Test With Real API and Documents

This tests the actual pipeline with OpenAI API.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import os

def test_api_key():
    """Test that API key is set"""
    print("\n" + "="*80)
    print("Testing API Key")
    print("="*80)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set in .env")
        return False

    if not api_key.startswith("sk-"):
        print("❌ API key doesn't look valid (should start with 'sk-')")
        return False

    print(f"✓ API key found: {api_key[:10]}...{api_key[-4:]}")
    return True


def test_document_parsing():
    """Test parsing actual documents"""
    print("\n" + "="*80)
    print("Testing Document Parsing")
    print("="*80)

    from src.parsers.questionnaire_parser import QuestionnaireParser
    from src.parsers.concept_parser import ConceptParser
    from src.parsers.data_analyzer import DataAnalyzer

    # Test questionnaire
    try:
        print("\n1. Parsing questionnaire...")
        q_path = "source docs/Board games_questionnaire EN MASTER.docx"
        parser = QuestionnaireParser(q_path)
        questionnaire = parser.parse()

        print(f"   ✓ Parsed {len(questionnaire.questions)} questions")
        print(f"   ✓ Found {len(questionnaire.dimensions)} dimensions")

        # Show sample
        if 'B2' in questionnaire.questions:
            q = questionnaire.questions['B2']
            print(f"   ✓ Sample: {q.id} - {q.text[:50]}...")
    except Exception as e:
        print(f"   ❌ Questionnaire parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test concepts
    try:
        print("\n2. Parsing concepts...")
        c_path = "source docs/Tech_Enabled_CZ_Concepts_EN.pptx"
        c_parser = ConceptParser(c_path)
        concepts = c_parser.parse()

        print(f"   ✓ Parsed {len(concepts)} concepts")
        if concepts:
            print(f"   ✓ Sample: {concepts[0].name}")
    except Exception as e:
        print(f"   ❌ Concept parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test data analysis
    try:
        print("\n3. Analyzing ground truth data...")
        d_path = "source docs/KAP400232611_Respondent_Data_Tech Enabled CZ.xlsx"
        analyzer = DataAnalyzer(d_path)
        structure = analyzer.analyze()

        print(f"   ✓ Analyzed {structure.num_rows} rows, {structure.num_columns} columns")
        print(f"   ✓ Found {len(structure.demographic_columns)} demographic columns")
    except Exception as e:
        print(f"   ❌ Data analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_llm_integration():
    """Test LLM with a simple prompt"""
    print("\n" + "="*80)
    print("Testing LLM Integration")
    print("="*80)

    try:
        from src.llm.client import LLMClient

        print("\nInitializing LLM client...")
        client = LLMClient(model="gpt-4o", temperature=0.5)
        print("✓ Client initialized")

        print("\nGenerating test response...")
        system = "You are a helpful assistant."
        user = "Say 'Hello from the synthetic survey system!' in exactly those words."

        response = client.generate_response(system, user)
        print(f"✓ Response received: {response}")

        if "Hello from the synthetic survey system!" in response:
            print("✓ Response format correct")
        else:
            print(f"⚠️  Response unexpected: {response}")

        return True
    except Exception as e:
        print(f"❌ LLM integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embedding_service():
    """Test embedding generation"""
    print("\n" + "="*80)
    print("Testing Embedding Service")
    print("="*80)

    try:
        from src.ssr.embeddings import EmbeddingService

        print("\nInitializing embedding service...")
        service = EmbeddingService(model_id="text-embedding-3-small")
        print("✓ Service initialized")

        print("\nGenerating embeddings...")
        texts = ["I would definitely buy this product.", "I would not buy this product."]
        embeddings = service.embed_texts(texts)

        print(f"✓ Generated embeddings: shape {embeddings.shape}")
        assert embeddings.shape[0] == 2
        assert embeddings.shape[1] == 1536  # text-embedding-3-small dimension

        return True
    except Exception as e:
        print(f"❌ Embedding service failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ssr_pipeline():
    """Test complete SSR pipeline"""
    print("\n" + "="*80)
    print("Testing SSR Pipeline")
    print("="*80)

    try:
        from src.ssr.embeddings import EmbeddingService
        from src.ssr.rating_engine import RatingEngine
        from src.scales.registry import create_default_scales

        print("\nInitializing components...")
        embedding_service = EmbeddingService()
        scale_registry = create_default_scales()
        rating_engine = RatingEngine(scale_registry, embedding_service)
        print("✓ Components initialized")

        print("\nTesting purchase intent rating...")
        test_response = "I really like this product and would definitely consider buying it at that price."

        result = rating_engine.rate_answer(
            test_response,
            scale_id="likert5_purchase_intent_v1",
            temperature=0.5
        )

        print(f"✓ Rating generated: {result.to_formatted_response()}")
        print(f"   Level: {result.chosen_level_value}")
        print(f"   Confidence: {result.probabilities[result.chosen_level_index]:.3f}")
        print(f"   Probabilities: {[f'{p:.3f}' for p in result.probabilities]}")

        return True
    except Exception as e:
        print(f"❌ SSR pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_single():
    """Test complete flow for a single response"""
    print("\n" + "="*80)
    print("Testing End-to-End Single Response")
    print("="*80)

    try:
        from src.persona.generator import PersonaGenerator
        from src.llm.client import LLMClient
        from src.llm.prompts import PromptBuilder
        from src.ssr.embeddings import EmbeddingService
        from src.ssr.rating_engine import RatingEngine
        from src.scales.registry import create_default_scales
        from src.survey.question_handler import QuestionHandler

        print("\n1. Generating persona...")
        persona_gen = PersonaGenerator(random_seed=42)
        persona = persona_gen.generate_persona()
        print(f"   ✓ Persona: {persona.to_description()}")

        print("\n2. Initializing components...")
        llm_client = LLMClient(temperature=0.5)
        embedding_service = EmbeddingService()
        scale_registry = create_default_scales()
        rating_engine = RatingEngine(scale_registry, embedding_service)
        question_handler = QuestionHandler(llm_client, rating_engine)
        print("   ✓ Components ready")

        print("\n3. Testing question...")
        concept = {
            'description': '''Christmas AR Message Scratchcard
Price: 250 CZK
- Record personal Christmas video with festive AR filters
- Recipient scans QR code to see AR message above card
- Available in stores and online'''
        }

        response = question_handler.handle_question(
            question_id='B2',
            question_type='single_coded',
            persona=persona,
            concept_description=concept['description'],
            scale_id='likert5_purchase_intent_v1'
        )

        print(f"   ✓ LLM Response: {response.raw_response[:100]}...")
        print(f"   ✓ Rating: {response.formatted_response}")
        print(f"   ✓ Confidence: {response.metadata.get('confidence', 0):.3f}")

        return True
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*80)
    print("RUNNING TESTS WITH REAL API AND DOCUMENTS")
    print("="*80)

    results = {}

    # Test 1: API Key
    results['API Key'] = test_api_key()
    if not results['API Key']:
        print("\n❌ Cannot proceed without API key")
        return False

    # Test 2: Document Parsing
    results['Document Parsing'] = test_document_parsing()

    # Test 3: LLM Integration
    results['LLM Integration'] = test_llm_integration()

    # Test 4: Embedding Service
    results['Embedding Service'] = test_embedding_service()

    # Test 5: SSR Pipeline
    results['SSR Pipeline'] = test_ssr_pipeline()

    # Test 6: End-to-End
    results['End-to-End'] = test_end_to_end_single()

    # Summary
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 All tests passed! System is working!")
        print("\nYou can now:")
        print("  1. Run notebooks/02_ssr_demo.ipynb for interactive demo")
        print("  2. Run notebooks/06_full_generation.ipynb to generate dataset")
        print("  3. Run: python run_full_pipeline.py -n 10")
    else:
        failed = [name for name, passed in results.items() if not passed]
        print(f"\n⚠️  {len(failed)} test(s) failed: {', '.join(failed)}")
        print("Check error messages above for details")

    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
