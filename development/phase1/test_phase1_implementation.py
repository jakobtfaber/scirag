#!/usr/bin/env python3
"""
Phase 1 Implementation Test

This script tests the Phase 1 implementation of RAGBook-SciRAG integration,
verifying that all core modules can be imported and basic functionality works.
"""

import sys
import os
from pathlib import Path

# Add the scirag package to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all enhanced processing modules can be imported."""
    print("🧪 Testing Phase 1 imports...")
    
    try:
        # Test main enhanced processing module
        from scirag.enhanced_processing import (
            EnhancedChunk, ContentType, MathematicalContent, 
            AssetContent, GlossaryContent, MathematicalProcessor,
            ContentClassifier, EnhancedChunker, EnhancedDocumentProcessor,
            AssetProcessor, GlossaryExtractor, EnhancedProcessingMonitor
        )
        print("✅ Enhanced processing modules imported successfully")
        
        # Test configuration
        from scirag.config import enhanced_config, EnhancedProcessingConfig
        print("✅ Enhanced configuration imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of core components."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from scirag.enhanced_processing import (
            ContentType, MathematicalProcessor, ContentClassifier,
            EnhancedChunker, EnhancedDocumentProcessor
        )
        
        # Test ContentType enum
        assert ContentType.EQUATION.value == "equation"
        assert ContentType.FIGURE.value == "figure"
        print("✅ ContentType enum working")
        
        # Test MathematicalProcessor
        math_processor = MathematicalProcessor()
        test_equation = r"E = mc^2"
        result = math_processor.process_equation(test_equation)
        assert result.equation_tex == test_equation
        assert result.math_norm is not None
        print("✅ MathematicalProcessor working")
        
        # Test ContentClassifier
        classifier = ContentClassifier()
        content_type, confidence = classifier.classify_content("This is a test equation: $E = mc^2$")
        assert content_type in [ContentType.EQUATION, ContentType.OTHER]
        print("✅ ContentClassifier working")
        
        # Test EnhancedChunker
        chunker = EnhancedChunker()
        assert chunker.chunk_size > 0
        assert chunker.chunk_overlap >= 0
        print("✅ EnhancedChunker working")
        
        # Test EnhancedDocumentProcessor
        processor = EnhancedDocumentProcessor()
        assert processor.enable_mathematical_processing is not None
        print("✅ EnhancedDocumentProcessor working")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def test_configuration():
    """Test configuration system."""
    print("\n🧪 Testing configuration...")
    
    try:
        from scirag.config import enhanced_config, EnhancedProcessingConfig
        
        # Test config access
        config_dict = enhanced_config.get_config_dict()
        assert 'enhanced_processing' in config_dict
        assert 'mathematical_processing' in config_dict
        print("✅ Configuration access working")
        
        # Test config validation
        errors = enhanced_config.validate_config()
        assert isinstance(errors, list)
        print("✅ Configuration validation working")
        
        # Test config values
        assert isinstance(enhanced_config.ENABLE_ENHANCED_PROCESSING, bool)
        assert isinstance(enhanced_config.MAX_PROCESSING_TIME, float)
        print("✅ Configuration values working")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def test_enhanced_chunk():
    """Test EnhancedChunk data structure."""
    print("\n🧪 Testing EnhancedChunk...")
    
    try:
        from scirag.enhanced_processing import EnhancedChunk, ContentType, MathematicalContent
        
        # Create a test chunk
        chunk = EnhancedChunk(
            id="test_chunk_1",
            text="This is a test equation: $E = mc^2$",
            source_id="test_source",
            chunk_index=0,
            content_type=ContentType.EQUATION
        )
        
        # Test basic properties
        assert chunk.id == "test_chunk_1"
        assert chunk.content_type == ContentType.EQUATION
        assert chunk.is_mathematical() == False  # No mathematical content yet
        
        # Test serialization
        chunk_dict = chunk.to_dict()
        assert 'id' in chunk_dict
        assert 'content_type' in chunk_dict
        
        # Test JSON export
        json_str = chunk.to_json()
        assert '"id": "test_chunk_1"' in json_str
        
        # Test summary
        summary = chunk.get_summary()
        assert 'id' in summary
        assert 'content_type' in summary
        
        print("✅ EnhancedChunk working")
        return True
        
    except Exception as e:
        print(f"❌ EnhancedChunk test error: {e}")
        return False

def test_mathematical_processing():
    """Test mathematical processing functionality."""
    print("\n🧪 Testing mathematical processing...")
    
    try:
        from scirag.enhanced_processing import MathematicalProcessor
        
        processor = MathematicalProcessor()
        
        # Test equation detection
        test_text = "The famous equation is $E = mc^2$ and also $$\\frac{a}{b} = c$$"
        equations = processor.detect_equations(test_text)
        assert len(equations) >= 2  # Should find both equations
        print("✅ Equation detection working")
        
        # Test equation processing
        equation = r"E = mc^2"
        result = processor.process_equation(equation)
        assert result.equation_tex == equation
        assert result.math_norm is not None
        assert len(result.math_tokens) > 0
        print("✅ Equation processing working")
        
        # Test variable extraction
        variables = processor.extract_variables(equation)
        assert 'E' in variables or 'm' in variables or 'c' in variables
        print("✅ Variable extraction working")
        
        # Test complexity scoring
        complexity = processor.calculate_complexity_score(equation, result.math_tokens)
        assert 0 <= complexity <= 1
        print("✅ Complexity scoring working")
        
        return True
        
    except Exception as e:
        print(f"❌ Mathematical processing test error: {e}")
        return False

def test_content_classification():
    """Test content classification functionality."""
    print("\n🧪 Testing content classification...")
    
    try:
        from scirag.enhanced_processing import ContentClassifier, ContentType
        
        classifier = ContentClassifier()
        
        # Test equation classification
        equation_text = r"\begin{equation} E = mc^2 \end{equation}"
        content_type, confidence = classifier.classify_content(equation_text)
        assert content_type == ContentType.EQUATION
        assert confidence > 0
        print("✅ Equation classification working")
        
        # Test figure classification
        figure_text = r"\begin{figure} \includegraphics{image.png} \caption{Test figure} \end{figure}"
        content_type, confidence = classifier.classify_content(figure_text)
        assert content_type == ContentType.FIGURE
        assert confidence > 0
        print("✅ Figure classification working")
        
        # Test prose classification
        prose_text = "This is a regular paragraph with some text content."
        content_type, confidence = classifier.classify_content(prose_text)
        assert content_type == ContentType.PROSE
        assert confidence > 0
        print("✅ Prose classification working")
        
        return True
        
    except Exception as e:
        print(f"❌ Content classification test error: {e}")
        return False

def main():
    """Run all Phase 1 tests."""
    print("🚀 Starting Phase 1 Implementation Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Configuration", test_configuration),
        ("EnhancedChunk", test_enhanced_chunk),
        ("Mathematical Processing", test_mathematical_processing),
        ("Content Classification", test_content_classification)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 1 tests passed! Ready for Phase 2.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before proceeding to Phase 2.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
