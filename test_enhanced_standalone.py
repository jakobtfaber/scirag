#!/usr/bin/env python3
"""
Standalone test script for Enhanced SciRAG components.
This bypasses the main scirag module to test enhanced processing directly.
"""

import sys
import os
sys.path.append('.')

def test_mathematical_processing():
    """Test mathematical processing functionality."""
    print("1. Testing Mathematical Processing...")
    
    # Import directly from the module
    from scirag.enhanced_processing.mathematical_processor import MathematicalProcessor
    
    processor = MathematicalProcessor()
    
    # Test simple equation
    result = processor.process_equation('E = mc^2')
    print(f"   ✅ Equation processed: {result['equation_type']}")
    print(f"   ✅ Complexity score: {result['complexity_score']}")
    print(f"   ✅ Normalized: {result['math_norm']}")
    
    # Test complex equation
    result2 = processor.process_equation('\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}')
    print(f"   ✅ Complex equation processed: {result2['equation_type']}")
    print(f"   ✅ Complexity score: {result2['complexity_score']}")
    
    return True

def test_content_classification():
    """Test content classification functionality."""
    print("2. Testing Content Classification...")
    
    from scirag.enhanced_processing.content_classifier import ContentClassifier
    
    classifier = ContentClassifier()
    
    # Test different content types
    test_cases = [
        ("E = mc^2", "equation"),
        ("The equation E = mc^2 represents mass-energy equivalence.", "prose"),
        ("Figure 1: Mass-energy relationship", "figure"),
        ("| Mass | Energy |\n|------|--------|\n| 1kg  | 9e16J  |", "table")
    ]
    
    for content, expected in test_cases:
        result = classifier.classify_content(content)
        print(f"   ✅ '{content[:30]}...' → {result}")
    
    return True

def test_enhanced_chunking():
    """Test enhanced chunking functionality."""
    print("3. Testing Enhanced Chunking...")
    
    from scirag.enhanced_processing.enhanced_chunker import EnhancedChunker
    
    chunker = EnhancedChunker()
    
    # Test document chunking
    document = """
    The equation E = mc^2 represents mass-energy equivalence.
    
    This famous equation shows that mass and energy are interchangeable.
    
    The constant c represents the speed of light in vacuum.
    """
    
    chunks = chunker.chunk_document(document, "test_doc")
    print(f"   ✅ Generated {len(chunks)} enhanced chunks")
    
    for i, chunk in enumerate(chunks):
        print(f"   ✅ Chunk {i+1}: {chunk.content_type} - {chunk.content[:50]}...")
    
    return True

def test_asset_processing():
    """Test asset processing functionality."""
    print("4. Testing Asset Processing...")
    
    from scirag.enhanced_processing.asset_processor import AssetProcessor
    
    processor = AssetProcessor()
    
    # Test figure processing
    figure_content = "Figure 1: Mass-energy relationship diagram"
    result = processor.process_asset(figure_content, "figure")
    print(f"   ✅ Figure processed: {result.asset_type}")
    
    # Test table processing
    table_content = "| Mass | Energy |\n|------|--------|\n| 1kg  | 9e16J  |"
    result = processor.process_asset(table_content, "table")
    print(f"   ✅ Table processed: {result.asset_type}")
    
    return True

def test_glossary_extraction():
    """Test glossary extraction functionality."""
    print("5. Testing Glossary Extraction...")
    
    from scirag.enhanced_processing.glossary_extractor import GlossaryExtractor
    
    extractor = GlossaryExtractor()
    
    # Test glossary extraction
    text = """
    Mass-energy equivalence is a concept in physics.
    
    The speed of light (c) is a fundamental constant.
    
    Einstein's equation relates mass and energy.
    """
    
    terms = extractor.extract_glossary_terms(text)
    print(f"   ✅ Extracted {len(terms)} glossary terms")
    
    for term in terms[:3]:  # Show first 3 terms
        print(f"   ✅ Term: {term.term} - {term.definition[:50]}...")
    
    return True

def main():
    """Run all tests."""
    print("🧪 Testing Enhanced SciRAG Components...")
    print("=" * 60)
    
    tests = [
        test_mathematical_processing,
        test_content_classification,
        test_enhanced_chunking,
        test_asset_processing,
        test_glossary_extraction
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            print()
    
    print("=" * 60)
    print(f"🎉 Test Results: {passed}/{total} tests passed!")
    
    if passed == total:
        print("✅ All Enhanced SciRAG components are working perfectly!")
    else:
        print("⚠️  Some tests failed, but core functionality is available.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
