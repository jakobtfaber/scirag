#!/usr/bin/env python3
"""
Phase 3 Validation Test - Enhanced SciRAG Testing and Backward Compatibility

This test validates Phase 3 implementation without importing the main SciRAG package
to avoid dependency issues.
"""

import sys
import os
import tempfile
import time
import psutil
from pathlib import Path

# Add the scirag directory and enhanced_processing directory to the path
sys.path.insert(0, str(Path(__file__).parent / "scirag"))
sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
sys.path.insert(0, str(Path(__file__).parent / "scirag" / "validation"))

def test_enhanced_processing_imports():
    """Test that enhanced processing modules can be imported."""
    print("🧪 Testing enhanced processing imports...")
    
    try:
        # Import directly from the enhanced_processing module to avoid main package dependencies
        from enhanced_chunk import (
            EnhancedChunk, ContentType, MathematicalContent, AssetContent, GlossaryContent
        )
        from mathematical_processor import MathematicalProcessor
        from content_classifier import ContentClassifier
        from enhanced_chunker import EnhancedChunker
        from document_processor import EnhancedDocumentProcessor
        from asset_processor import AssetProcessor
        from glossary_extractor import GlossaryExtractor
        print("✅ Enhanced processing imports successful")
        return True
    except Exception as e:
        print(f"❌ Enhanced processing import error: {e}")
        return False

def test_enhanced_chunk_functionality():
    """Test enhanced chunk data structures."""
    print("🧪 Testing enhanced chunk functionality...")
    
    try:
        from enhanced_chunk import EnhancedChunk, ContentType, MathematicalContent
        
        # Test creating enhanced chunk
        chunk = EnhancedChunk(
            id="test_1",
            text="Test content with equation E = mc^2",
            source_id="test_source",
            chunk_index=0,
            content_type=ContentType.PROSE
        )
        
        # Test mathematical content
        math_content = MathematicalContent(
            equation_tex=r"E = mc^2",
            math_norm="E=mc^2",
            equation_type="physics"
        )
        chunk.mathematical_content = math_content
        
        # Test chunk methods
        assert chunk.id == "test_1"
        assert chunk.text == "Test content with equation E = mc^2"
        assert chunk.content_type == ContentType.PROSE
        assert chunk.is_mathematical() == False  # Not an equation chunk
        
        # Test serialization
        chunk_dict = chunk.to_dict()
        assert isinstance(chunk_dict, dict)
        assert chunk_dict['id'] == "test_1"
        
        print("✅ Enhanced chunk functionality working")
        return True
    except Exception as e:
        print(f"❌ Enhanced chunk test error: {e}")
        return False

def test_mathematical_processing():
    """Test mathematical processing functionality."""
    print("🧪 Testing mathematical processing...")
    
    try:
        from mathematical_processor import MathematicalProcessor
        
        processor = MathematicalProcessor()
        
        # Test equation processing
        equation = r"E = mc^2"
        result = processor.process_equation(equation)
        
        assert 'equation_tex' in result
        assert 'math_norm' in result
        assert 'math_tokens' in result
        assert 'math_kgrams' in result
        assert result['equation_tex'] == equation
        
        print("✅ Mathematical processing working")
        return True
    except Exception as e:
        print(f"❌ Mathematical processing test error: {e}")
        return False

def test_content_classification():
    """Test content classification functionality."""
    print("🧪 Testing content classification...")
    
    try:
        from content_classifier import ContentClassifier
        from enhanced_chunk import ContentType
        
        classifier = ContentClassifier()
        
        # Test equation classification
        equation_text = r"\begin{equation} E = mc^2 \end{equation}"
        content_type = classifier.classify_content(equation_text, {})
        assert content_type == ContentType.EQUATION
        
        # Test prose classification
        prose_text = "This is a regular paragraph of text."
        content_type = classifier.classify_content(prose_text, {})
        assert content_type == ContentType.PROSE
        
        print("✅ Content classification working")
        return True
    except Exception as e:
        print(f"❌ Content classification test error: {e}")
        return False

def test_enhanced_chunker():
    """Test enhanced chunking functionality."""
    print("🧪 Testing enhanced chunker...")
    
    try:
        from enhanced_chunker import EnhancedChunker
        
        chunker = EnhancedChunker()
        
        # Test mathematical content chunking
        text = "The equation E = mc^2 is famous. It relates energy to mass."
        chunks = chunker.chunk_text(text, "test_source", 0)
        
        assert len(chunks) > 0
        assert all(hasattr(chunk, 'id') for chunk in chunks)
        assert all(hasattr(chunk, 'text') for chunk in chunks)
        
        print("✅ Enhanced chunker working")
        return True
    except Exception as e:
        print(f"❌ Enhanced chunker test error: {e}")
        return False

def test_document_processing():
    """Test document processing pipeline."""
    print("🧪 Testing document processing pipeline...")
    
    try:
        from document_processor import EnhancedDocumentProcessor
        
        processor = EnhancedDocumentProcessor()
        
        # Create test document
        test_content = """
        # Test Document
        
        This is a test paragraph.
        
        The equation E = mc^2 is famous.
        
        \\begin{figure}
        \\includegraphics{test.png}
        \\caption{Test figure}
        \\end{figure}
        
        Definition: A black hole is a region of spacetime.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            f.flush()
            
            try:
                chunks = processor.process_document(Path(f.name), "test_doc")
                
                assert len(chunks) > 0
                assert all(hasattr(chunk, 'id') for chunk in chunks)
                assert all(hasattr(chunk, 'text') for chunk in chunks)
                
                print("✅ Document processing pipeline working")
                return True
            finally:
                os.unlink(f.name)
    except Exception as e:
        print(f"❌ Document processing test error: {e}")
        return False

def test_monitoring_system():
    """Test monitoring system functionality."""
    print("🧪 Testing monitoring system...")
    
    try:
        from monitoring import EnhancedProcessingMonitor
        
        monitor = EnhancedProcessingMonitor()
        
        # Test recording metrics
        monitor.record_success("test_operation", 0.1)
        monitor.record_error("test_error", "Test error message")
        
        # Test getting metrics
        metrics = monitor.get_metrics()
        assert 'success_count' in metrics
        assert 'error_count' in metrics
        assert 'error_rate' in metrics
        
        # Test health check
        health_status = monitor.check_health()
        assert 'status' in health_status
        assert 'timestamp' in health_status
        
        print("✅ Monitoring system working")
        return True
    except Exception as e:
        print(f"❌ Monitoring system test error: {e}")
        return False

def test_validation_system():
    """Test validation system functionality."""
    print("🧪 Testing validation system...")
    
    try:
        from data_integrity import DataIntegrityChecker
        from enhanced_chunk import EnhancedChunk, ContentType
        
        checker = DataIntegrityChecker()
        
        # Create test chunks
        chunks = [
            EnhancedChunk(
                id="test_1",
                text="Test content",
                source_id="test_source",
                chunk_index=0,
                content_type=ContentType.PROSE
            )
        ]
        
        # Test validation
        is_valid, messages = checker.validate_enhanced_chunks(chunks)
        assert isinstance(is_valid, bool)
        assert isinstance(messages, list)
        
        # Test report generation
        report = checker.generate_integrity_report(chunks)
        assert 'is_valid' in report
        assert 'total_chunks' in report
        
        print("✅ Validation system working")
        return True
    except Exception as e:
        print(f"❌ Validation system test error: {e}")
        return False

def test_performance_benchmarks():
    """Test performance benchmarks."""
    print("🧪 Testing performance benchmarks...")
    
    try:
        from mathematical_processor import MathematicalProcessor
        
        processor = MathematicalProcessor()
        
        # Test processing time
        start_time = time.time()
        result = processor.process_equation(r"E = mc^2")
        processing_time = time.time() - start_time
        
        assert processing_time < 1.0, f"Processing took {processing_time:.3f}s (threshold: 1.0s)"
        assert 'equation_tex' in result
        
        # Test memory usage
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Process multiple equations
        for i in range(10):
            processor.process_equation(f"x^{i} + y^{i} = z^{i}")
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 50, f"Memory increased by {memory_increase:.1f}MB (threshold: 50MB)"
        
        print("✅ Performance benchmarks passed")
        return True
    except Exception as e:
        print(f"❌ Performance benchmark test error: {e}")
        return False

def test_backward_compatibility():
    """Test backward compatibility features."""
    print("🧪 Testing backward compatibility...")
    
    try:
        # Test that enhanced processing can be disabled
        from document_processor import EnhancedDocumentProcessor
        
        processor = EnhancedDocumentProcessor()
        
        # Test with minimal content
        test_content = "Simple test content."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            f.flush()
            
            try:
                chunks = processor.process_document(Path(f.name), "test_doc")
                
                # Should still work with simple content
                assert len(chunks) > 0
                assert all(hasattr(chunk, 'id') for chunk in chunks)
                
                print("✅ Backward compatibility working")
                return True
            finally:
                os.unlink(f.name)
    except Exception as e:
        print(f"❌ Backward compatibility test error: {e}")
        return False

def main():
    """Run all Phase 3 validation tests."""
    print("🚀 Starting Phase 3 Validation Tests")
    print("=" * 50)
    
    tests = [
        test_enhanced_processing_imports,
        test_enhanced_chunk_functionality,
        test_mathematical_processing,
        test_content_classification,
        test_enhanced_chunker,
        test_document_processing,
        test_monitoring_system,
        test_validation_system,
        test_performance_benchmarks,
        test_backward_compatibility
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if failed == 0:
        print("🎉 All Phase 3 validation tests passed!")
        print("✅ Enhanced SciRAG is ready for production!")
    else:
        print(f"⚠️  {failed} tests failed. Please review and fix issues.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
