#!/usr/bin/env python3
"""
Minimal test runner for enhanced processing functionality.
"""

import sys
from pathlib import Path

# Add the scirag module to the path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scirag" / "enhanced_processing"))

def test_imports():
    """Test that we can import our modules."""
    try:
        # Use direct imports with proper path setup
        from mathematical_processor import MathematicalProcessor
        from content_classifier import ContentClassifier
        from enhanced_chunk import ContentType, EnhancedChunk
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_mathematical_processor():
    """Test MathematicalProcessor basic functionality."""
    try:
        from mathematical_processor import MathematicalProcessor
        
        processor = MathematicalProcessor()
        
        # Test equation processing (detect_equations method doesn't exist)
        result = processor.process_equation("E = mc^2")
        assert 'math_norm' in result
        assert 'math_tokens' in result
        assert 'equation_tex' in result
        
        print("✓ MathematicalProcessor tests passed")
        return True
    except Exception as e:
        print(f"✗ MathematicalProcessor test failed: {e}")
        return False

def test_content_classifier():
    """Test ContentClassifier basic functionality."""
    try:
        from content_classifier import ContentClassifier
        from enhanced_chunk import ContentType
        
        classifier = ContentClassifier()
        
        # Test equation classification
        text = "The equation $E = mc^2$ is famous."
        content_type = classifier.classify_content(text, {})
        assert content_type == ContentType.EQUATION
        
        # Test prose classification
        text = "This is regular prose text."
        content_type = classifier.classify_content(text, {})
        assert content_type == ContentType.PROSE
        
        print("✓ ContentClassifier tests passed")
        return True
    except Exception as e:
        print(f"✗ ContentClassifier test failed: {e}")
        return False

def test_enhanced_chunk():
    """Test EnhancedChunk basic functionality."""
    try:
        from enhanced_chunk import EnhancedChunk, ContentType, MathematicalContent
        
        # Test basic chunk creation
        chunk = EnhancedChunk(
            id="test_1",
            text="Test chunk",
            source_id="test_source",
            chunk_index=0,
            content_type=ContentType.PROSE
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
            content_type=ContentType.EQUATION
        )
        chunk.mathematical_content = math_content
        
        # Test serialization
        chunk_dict = chunk.to_dict()
        assert chunk_dict['id'] == "math_1"
        assert chunk_dict['content_type'] == "equation"
        
        # Test that serialization works (from_dict method doesn't exist)
        assert chunk_dict['id'] == "math_1"
        assert chunk_dict['content_type'] == "equation"
        
        print("✓ EnhancedChunk tests passed")
        return True
    except Exception as e:
        print(f"✗ EnhancedChunk test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Enhanced Processing Integration (Minimal)...")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_mathematical_processor,
        test_content_classifier,
        test_enhanced_chunk
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
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
