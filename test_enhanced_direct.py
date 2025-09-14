#!/usr/bin/env python3
"""
Direct test of Enhanced SciRAG components without complex imports.
This bypasses the main scirag module to test individual components.
"""

import sys
import os

# Add the parent directory of 'scirag' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("🚀 Enhanced SciRAG Direct Component Test")
print("==================================================")

def test_mathematical_processing():
    """Test mathematical processing component."""
    print("\n1. Testing Mathematical Processing...")
    try:
        from scirag.enhanced_processing.mathematical_processor import MathematicalProcessor
        processor = MathematicalProcessor()
        result = processor.process_equation('E = mc^2')
        print(f"   ✅ Equation processed: {result['equation_type']}")
        print(f"   ✅ Complexity score: {result['complexity_score']}")
        print(f"   ✅ Normalized: {result['math_norm']}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_content_classification():
    """Test content classification component."""
    print("\n2. Testing Content Classification...")
    try:
        from scirag.enhanced_processing.content_classifier import ContentClassifier
        classifier = ContentClassifier()
        content_type = classifier.classify_content('The equation E = mc^2 represents mass-energy equivalence.')
        print(f"   ✅ Content classified as: {content_type}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_enhanced_chunking():
    """Test enhanced chunking component."""
    print("\n3. Testing Enhanced Chunking...")
    try:
        from scirag.enhanced_processing.enhanced_chunker import EnhancedChunker
        chunker = EnhancedChunker()
        chunks = chunker.chunk_document('E = mc^2 is a famous equation.', 'test_doc')
        print(f"   ✅ Generated {len(chunks)} enhanced chunks")
        if chunks:
            print(f"   ✅ First chunk type: {chunks[0].content_type}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_asset_processing():
    """Test asset processing component."""
    print("\n4. Testing Asset Processing...")
    try:
        from scirag.enhanced_processing.asset_processor import AssetProcessor
        processor = AssetProcessor()
        result = processor.process_asset('Figure 1: A diagram showing the relationship between energy and mass.', 'figure')
        print(f"   ✅ Asset processed: {result['asset_type']}")
        print(f"   ✅ Confidence: {result['confidence']}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_glossary_extraction():
    """Test glossary extraction component."""
    print("\n5. Testing Glossary Extraction...")
    try:
        from scirag.enhanced_processing.glossary_extractor import GlossaryExtractor
        extractor = GlossaryExtractor()
        terms = extractor.extract_glossary_terms('The mass-energy equivalence principle states that E = mc^2.')
        print(f"   ✅ Extracted {len(terms)} glossary terms")
        if terms:
            print(f"   ✅ First term: {terms[0].term}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_document_processing():
    """Test document processing pipeline."""
    print("\n6. Testing Document Processing Pipeline...")
    try:
        from scirag.enhanced_processing.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        # Test with a simple document
        test_doc = """
        The mass-energy equivalence principle is expressed by the equation E = mc^2.
        
        Figure 1: A diagram showing the relationship between energy and mass.
        
        This principle was first proposed by Albert Einstein in 1905.
        """
        
        result = processor.process_document(test_doc, 'test_doc')
        print(f"   ✅ Document processed successfully")
        print(f"   ✅ Generated {len(result.chunks)} chunks")
        print(f"   ✅ Processing time: {result.processing_time:.2f}s")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    tests = [
        test_mathematical_processing,
        test_content_classification,
        test_enhanced_chunking,
        test_asset_processing,
        test_glossary_extraction,
        test_document_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Enhanced SciRAG components are working correctly!")
        print("\n📚 Usage Examples:")
        print("==================")
        print("\n1. Mathematical Processing:")
        print("   from scirag.enhanced_processing.mathematical_processor import MathematicalProcessor")
        print("   processor = MathematicalProcessor()")
        print("   result = processor.process_equation('E = mc^2')")
        
        print("\n2. Enhanced Document Processing:")
        print("   from scirag.enhanced_processing.document_processor import DocumentProcessor")
        print("   processor = DocumentProcessor()")
        print("   result = processor.process_document('Your document...', 'doc_id')")
        
        print("\n3. Content Classification:")
        print("   from scirag.enhanced_processing.content_classifier import ContentClassifier")
        print("   classifier = ContentClassifier()")
        print("   content_type = classifier.classify_content('Your content...')")
        
    else:
        print(f"⚠️  {total - passed} tests failed. Check the errors above.")
        print("\n🔧 To resolve issues:")
        print("1. Ensure all dependencies are installed")
        print("2. Check that the enhanced_processing modules are properly configured")
        print("3. Verify that the required data files are present")

if __name__ == "__main__":
    main()
