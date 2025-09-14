#!/usr/bin/env python3
"""
Standalone test for enhanced processing functionality.
"""

import sys
from pathlib import Path

# Add the scirag module to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_mathematical_processor():
    """Test MathematicalProcessor basic functionality."""
    try:
        # Import directly from the module
        from scirag.enhanced_processing.mathematical_processor import MathematicalProcessor
        
        processor = MathematicalProcessor(enable_sympy=False, enable_ragbook=False)
        
        # Test equation detection
        text = "The equation $E = mc^2$ is famous."
        equations = processor.detect_equations(text)
        assert len(equations) == 1
        assert equations[0][0] == "E = mc^2"
        
        # Test equation processing
        result = processor.process_equation("x + y = z", "inline")
        assert 'math_norm' in result
        assert 'math_tokens' in result
        
        print("✓ MathematicalProcessor tests passed")
        return True
    except Exception as e:
        print(f"✗ MathematicalProcessor test failed: {e}")
        return False

def test_content_classifier():
    """Test ContentClassifier basic functionality."""
    try:
        from scirag.enhanced_processing.content_classifier import ContentClassifier
        from scirag.enhanced_processing.enhanced_chunk import ContentType
        
        classifier = ContentClassifier()
        
        # Test equation classification
        text = "The equation $E = mc^2$ is famous."
        content_type, confidence = classifier.classify_content(text)
        assert content_type == ContentType.EQUATION
        assert confidence > 0.3
        
        # Test prose classification
        text = "This is regular prose text."
        content_type, confidence = classifier.classify_content(text)
        assert content_type == ContentType.PROSE
        
        print("✓ ContentClassifier tests passed")
        return True
    except Exception as e:
        print(f"✗ ContentClassifier test failed: {e}")
        return False

def test_enhanced_chunk():
    """Test EnhancedChunk basic functionality."""
    try:
        from scirag.enhanced_processing.enhanced_chunk import EnhancedChunk, ContentType, MathematicalContent
        
        # Test basic chunk creation
        chunk = EnhancedChunk(
            id="test_1",
            text="Test chunk",
            source_id="test_source",
            chunk_index=0
        )
        assert chunk.id == "test_1"
        assert chunk.content_type == ContentType.PROSE
        
        # Test chunk with math content
        math_content = MathematicalContent(
            equation_tex="E = mc^2",
            math_norm="E=mc^2",
            math_tokens=["E", "=", "m", "c", "^", "2"]
        )
        
        chunk = EnhancedChunk(
            id="math_1",
            text="The equation $E = mc^2$",
            source_id="physics",
            chunk_index=1,
            content_type=ContentType.EQUATION,
            math_content=math_content
        )
        
        # Test serialization
        chunk_dict = chunk.to_dict()
        assert chunk_dict['id'] == "math_1"
        assert chunk_dict['content_type'] == "equation"
        
        # Test deserialization
        chunk_from_dict = EnhancedChunk.from_dict(chunk_dict)
        assert chunk_from_dict.id == "math_1"
        assert chunk_from_dict.content_type == ContentType.EQUATION
        
        print("✓ EnhancedChunk tests passed")
        return True
    except Exception as e:
        print(f"✗ EnhancedChunk test failed: {e}")
        return False

def test_enhanced_processing_module():
    """Test the enhanced_processing module directly."""
    try:
        from scirag.enhanced_processing import MathematicalProcessor, ContentClassifier, ContentType, EnhancedChunk
        
        # Test that we can create instances
        processor = MathematicalProcessor(enable_sympy=False, enable_ragbook=False)
        classifier = ContentClassifier()
        chunk = EnhancedChunk(
            id="test",
            text="test",
            source_id="test",
            chunk_index=0
        )
        
        print("✓ Enhanced processing module tests passed")
        return True
    except Exception as e:
        print(f"✗ Enhanced processing module test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Enhanced Processing Integration (Standalone)...")
    print("=" * 60)
    
    tests = [
        test_mathematical_processor,
        test_content_classifier,
        test_enhanced_chunk,
        test_enhanced_processing_module
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All core tests passed! Phase 1 integration is working.")
        print("\nNext steps:")
        print("1. Install RAGBook dependencies")
        print("2. Create remaining modules (document_processor, enhanced_chunker, etc.)")
        print("3. Integrate with existing SciRAG classes")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
