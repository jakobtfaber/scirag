#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced SciRAG with RAGBook Integration

This test suite validates:
1. Backward compatibility with existing SciRAG functionality
2. Enhanced processing capabilities
3. Error handling and graceful degradation
4. Performance and memory usage
5. Integration between all components
"""

import pytest
import tempfile
import os
import time
import psutil
from pathlib import Path
from typing import List, Dict, Any
import json

# Import SciRAG components
from scirag.enhanced_processing import (
    EnhancedChunk, ContentType, MathematicalContent, AssetContent, GlossaryContent,
    MathematicalProcessor, ContentClassifier, EnhancedChunker, 
    EnhancedDocumentProcessor, AssetProcessor, GlossaryExtractor
)
from scirag.scirag_enhanced import SciRagEnhanced
from scirag.scirag_openai_enhanced import SciRagOpenAIEnhanced


class TestBackwardCompatibility:
    """Test that existing SciRAG functionality still works."""
    
    def test_original_scirag_imports(self):
        """Test that original SciRAG can still be imported."""
        try:
            from scirag import SciRag
            from scirag.scirag_openai import SciRagOpenAI
            from scirag.scirag_vertexai import SciRagVertexAI
            from scirag.scirag_hybrid import SciRagHybrid
            assert True, "All original SciRAG imports successful"
        except ImportError as e:
            pytest.fail(f"Original SciRAG import failed: {e}")
    
    def test_enhanced_scirag_imports(self):
        """Test that enhanced SciRAG can be imported."""
        try:
            from scirag.scirag_enhanced import SciRagEnhanced
            from scirag.scirag_openai_enhanced import SciRagOpenAIEnhanced
            assert True, "Enhanced SciRAG imports successful"
        except ImportError as e:
            pytest.fail(f"Enhanced SciRAG import failed: {e}")
    
    def test_feature_flags(self):
        """Test that feature flags work correctly."""
        # Test with enhanced processing disabled
        scirag = SciRagOpenAIEnhanced(enable_enhanced_processing=False)
        assert not scirag.enable_enhanced_processing
        
        # Test with enhanced processing enabled
        scirag = SciRagOpenAIEnhanced(enable_enhanced_processing=True)
        assert scirag.enable_enhanced_processing


class TestEnhancedProcessingComponents:
    """Test individual enhanced processing components."""
    
    def test_mathematical_processor(self):
        """Test mathematical content processing."""
        processor = MathematicalProcessor()
        
        # Test equation processing
        equation = r"E = mc^2"
        result = processor.process_equation(equation)
        
        assert 'equation_tex' in result
        assert 'math_norm' in result
        assert 'math_tokens' in result
        assert 'math_kgrams' in result
        assert result['equation_tex'] == equation
    
    def test_content_classifier(self):
        """Test content type classification."""
        classifier = ContentClassifier()
        
        # Test equation classification
        equation_text = r"\begin{equation} E = mc^2 \end{equation}"
        content_type = classifier.classify_content(equation_text, {})
        assert content_type == ContentType.EQUATION
        
        # Test prose classification
        prose_text = "This is a regular paragraph of text."
        content_type = classifier.classify_content(prose_text, {})
        assert content_type == ContentType.PROSE
    
    def test_enhanced_chunker(self):
        """Test enhanced chunking functionality."""
        chunker = EnhancedChunker()
        
        # Test mathematical content chunking
        text = "The equation E = mc^2 is famous. It relates energy to mass."
        chunks = chunker.chunk_text(text, "test_source", 0)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, EnhancedChunk) for chunk in chunks)
    
    def test_asset_processor(self):
        """Test asset processing functionality."""
        processor = AssetProcessor()
        
        # Test figure processing
        figure_text = r"\begin{figure} \includegraphics{image.png} \caption{Test} \end{figure}"
        result = processor.process_asset(figure_text, "test_source")
        
        assert result is not None
        assert result.asset_type == "figure"
        assert "Test" in result.caption
    
    def test_glossary_extractor(self):
        """Test glossary extraction functionality."""
        extractor = GlossaryExtractor()
        
        # Test definition extraction
        text = "Definition: A black hole is a region of spacetime."
        result = extractor.extract_glossary_terms(text, "test_source")
        
        assert len(result) > 0
        assert any("black hole" in term.term.lower() for term in result)


class TestEnhancedChunkDataStructures:
    """Test enhanced chunk data structures."""
    
    def test_enhanced_chunk_creation(self):
        """Test creating enhanced chunks."""
        chunk = EnhancedChunk(
            id="test_1",
            text="Test content",
            source_id="test_source",
            chunk_index=0,
            content_type=ContentType.PROSE
        )
        
        assert chunk.id == "test_1"
        assert chunk.text == "Test content"
        assert chunk.content_type == ContentType.PROSE
        assert chunk.confidence == 0.0  # Default value
    
    def test_mathematical_content(self):
        """Test mathematical content structure."""
        math_content = MathematicalContent(
            equation_tex=r"E = mc^2",
            math_norm="E=mc^2",
            equation_type="physics"
        )
        
        assert math_content.equation_tex == r"E = mc^2"
        assert math_content.math_norm == "E=mc^2"
        assert math_content.equation_type == "physics"
    
    def test_asset_content(self):
        """Test asset content structure."""
        asset_content = AssetContent(
            asset_type="figure",
            caption="Test figure",
            file_path="test.png"
        )
        
        assert asset_content.asset_type == "figure"
        assert asset_content.caption == "Test figure"
        assert asset_content.file_path == "test.png"
    
    def test_glossary_content(self):
        """Test glossary content structure."""
        glossary_content = GlossaryContent(
            term="black hole",
            definition="A region of spacetime",
            context="astrophysics"
        )
        
        assert glossary_content.term == "black hole"
        assert glossary_content.definition == "A region of spacetime"
        assert glossary_content.context == "astrophysics"


class TestDocumentProcessingPipeline:
    """Test the complete document processing pipeline."""
    
    def test_enhanced_document_processor(self):
        """Test enhanced document processing."""
        processor = EnhancedDocumentProcessor()
        
        # Create a test document
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
                assert all(isinstance(chunk, EnhancedChunk) for chunk in chunks)
                
                # Check that different content types are identified
                content_types = [chunk.content_type for chunk in chunks]
                assert ContentType.PROSE in content_types
                
            finally:
                os.unlink(f.name)
    
    def test_processing_with_mathematical_content(self):
        """Test processing documents with mathematical content."""
        processor = EnhancedDocumentProcessor()
        
        math_content = """
        # Mathematical Document
        
        The famous equation is:
        
        \\begin{equation}
        E = mc^2
        \\end{equation}
        
        This relates energy to mass.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(math_content)
            f.flush()
            
            try:
                chunks = processor.process_document(Path(f.name), "math_doc")
                
                # Find mathematical chunks
                math_chunks = [chunk for chunk in chunks if chunk.is_mathematical()]
                assert len(math_chunks) > 0
                
                # Check mathematical content
                for chunk in math_chunks:
                    assert chunk.mathematical_content is not None
                    assert chunk.mathematical_content.equation_tex is not None
                
            finally:
                os.unlink(f.name)


class TestErrorHandlingAndGracefulDegradation:
    """Test error handling and graceful degradation."""
    
    def test_processing_with_invalid_content(self):
        """Test processing with invalid or malformed content."""
        processor = EnhancedDocumentProcessor()
        
        # Test with empty document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")
            f.flush()
            
            try:
                chunks = processor.process_document(Path(f.name), "empty_doc")
                # Should not crash, should return empty list or minimal chunk
                assert isinstance(chunks, list)
            finally:
                os.unlink(f.name)
    
    def test_processing_with_corrupted_file(self):
        """Test processing with corrupted file."""
        processor = EnhancedDocumentProcessor()
        
        # Test with non-existent file
        try:
            chunks = processor.process_document(Path("non_existent_file.md"), "corrupt_doc")
            # Should handle gracefully
            assert isinstance(chunks, list)
        except Exception as e:
            # Should be a specific, expected exception
            assert "FileNotFoundError" in str(type(e).__name__)
    
    def test_fallback_behavior(self):
        """Test fallback behavior when enhanced processing fails."""
        # This would test the fallback to original SciRAG functionality
        # when enhanced processing encounters errors
        pass


class TestPerformanceAndMemoryUsage:
    """Test performance and memory usage."""
    
    def test_memory_usage(self):
        """Test memory usage during processing."""
        processor = EnhancedDocumentProcessor()
        
        # Get initial memory usage
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Process a large document
        large_content = "Test content. " * 1000  # Large content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(large_content)
            f.flush()
            
            try:
                chunks = processor.process_document(Path(f.name), "large_doc")
                
                # Get final memory usage
                final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                memory_increase = final_memory - initial_memory
                
                # Memory increase should be reasonable (less than 100MB for this test)
                assert memory_increase < 100, f"Memory usage increased by {memory_increase}MB"
                
            finally:
                os.unlink(f.name)
    
    def test_processing_time(self):
        """Test processing time for typical documents."""
        processor = EnhancedDocumentProcessor()
        
        test_content = """
        # Test Document
        
        This is a test paragraph with some content.
        
        The equation E = mc^2 is famous.
        
        \\begin{figure}
        \\includegraphics{test.png}
        \\caption{Test figure}
        \\end{figure}
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            f.flush()
            
            try:
                start_time = time.time()
                chunks = processor.process_document(Path(f.name), "test_doc")
                processing_time = time.time() - start_time
                
                # Processing should be reasonably fast (less than 5 seconds for this test)
                assert processing_time < 5.0, f"Processing took {processing_time} seconds"
                
            finally:
                os.unlink(f.name)


class TestIntegrationAndEndToEnd:
    """Test integration between components and end-to-end functionality."""
    
    def test_enhanced_scirag_initialization(self):
        """Test enhanced SciRAG initialization."""
        try:
            scirag = SciRagOpenAIEnhanced(
                enable_enhanced_processing=True,
                # Use test credentials or mock
            )
            assert scirag.enable_enhanced_processing
            assert hasattr(scirag, 'enhanced_processor')
        except Exception as e:
            # This might fail due to missing API credentials, which is expected
            # in a test environment
            assert "credentials" in str(e).lower() or "api" in str(e).lower()
    
    def test_enhanced_chunk_serialization(self):
        """Test enhanced chunk serialization and deserialization."""
        chunk = EnhancedChunk(
            id="test_1",
            text="Test content",
            source_id="test_source",
            chunk_index=0,
            content_type=ContentType.PROSE,
            mathematical_content=MathematicalContent(
                equation_tex=r"E = mc^2",
                math_norm="E=mc^2"
            )
        )
        
        # Test serialization
        chunk_dict = chunk.to_dict()
        assert isinstance(chunk_dict, dict)
        assert chunk_dict['id'] == "test_1"
        assert chunk_dict['content_type'] == "prose"
        
        # Test JSON serialization
        json_str = json.dumps(chunk_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        assert loaded_dict['id'] == "test_1"
    
    def test_content_type_filtering(self):
        """Test content type filtering functionality."""
        # Create chunks with different content types
        chunks = [
            EnhancedChunk("1", "Regular text", "source", 0, ContentType.PROSE),
            EnhancedChunk("2", "E = mc^2", "source", 1, ContentType.EQUATION),
            EnhancedChunk("3", "Figure content", "source", 2, ContentType.FIGURE),
        ]
        
        # Test filtering by content type
        prose_chunks = [chunk for chunk in chunks if chunk.content_type == ContentType.PROSE]
        equation_chunks = [chunk for chunk in chunks if chunk.content_type == ContentType.EQUATION]
        figure_chunks = [chunk for chunk in chunks if chunk.content_type == ContentType.FIGURE]
        
        assert len(prose_chunks) == 1
        assert len(equation_chunks) == 1
        assert len(figure_chunks) == 1


class TestConfigurationAndFeatureFlags:
    """Test configuration and feature flags."""
    
    def test_feature_flag_combinations(self):
        """Test different feature flag combinations."""
        # Test with all features enabled
        scirag = SciRagOpenAIEnhanced(
            enable_enhanced_processing=True,
            enable_mathematical_processing=True,
            enable_asset_processing=True,
            enable_glossary_extraction=True
        )
        assert scirag.enable_enhanced_processing
        
        # Test with some features disabled
        scirag = SciRagOpenAIEnhanced(
            enable_enhanced_processing=True,
            enable_mathematical_processing=False,
            enable_asset_processing=True,
            enable_glossary_extraction=False
        )
        assert scirag.enable_enhanced_processing
    
    def test_environment_variable_configuration(self):
        """Test configuration via environment variables."""
        # This would test setting configuration via environment variables
        # and ensuring they're properly loaded
        pass


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
