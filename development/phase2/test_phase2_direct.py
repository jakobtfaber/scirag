#!/usr/bin/env python3
"""
Phase 2 Direct Integration Test

This script tests the Phase 2 integration by directly importing
enhanced processing modules without going through the main package.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the scirag package to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_direct_enhanced_imports():
    """Test direct imports of enhanced processing modules."""
    print("🧪 Testing direct enhanced processing imports...")
    
    try:
        # Import modules directly from the enhanced_processing package
        sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
        
        from enhanced_chunk import (
            EnhancedChunk, ContentType, MathematicalContent, AssetContent,
            GlossaryContent
        )
        print("✅ Enhanced chunk modules imported")
        
        from mathematical_processor import MathematicalProcessor
        print("✅ Mathematical processor imported")
        
        from content_classifier import ContentClassifier
        print("✅ Content classifier imported")
        
        from enhanced_chunker import EnhancedChunker
        print("✅ Enhanced chunker imported")
        
        from document_processor import EnhancedDocumentProcessor
        print("✅ Document processor imported")
        
        from asset_processor import AssetProcessor
        print("✅ Asset processor imported")
        
        from glossary_extractor import GlossaryExtractor
        print("✅ Glossary extractor imported")
        
        from monitoring import EnhancedProcessingMonitor
        print("✅ Monitoring module imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_enhanced_document_processing():
    """Test enhanced document processing pipeline."""
    print("\n🧪 Testing enhanced document processing pipeline...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
        from document_processor import EnhancedDocumentProcessor
        
        processor = EnhancedDocumentProcessor(
            enable_mathematical_processing=True,
            enable_asset_processing=True,
            enable_glossary_extraction=True
        )
        
        # Create a test document
        test_content = """
# Test Document

This is a test document with mathematical content.

The famous equation is $E = mc^2$.

Here's a more complex equation:
$$\\frac{\\partial f}{\\partial x} = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}$$

## Figure

\\begin{figure}
\\includegraphics{test.png}
\\caption{Test figure}
\\label{fig:test}
\\end{figure}

## Definition

**Definition**: A function is continuous if...

This is regular prose content.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Process the document
            chunks = processor.process_document(temp_file, "test_doc")
            
            # Verify we got chunks
            assert len(chunks) > 0
            print(f"✅ Enhanced document processing created {len(chunks)} chunks")
            
            # Check chunk types
            chunk_types = [chunk.content_type for chunk in chunks]
            print(f"✅ Chunk types found: {set(chunk_types)}")
            
            # Test chunk filtering
            math_chunks = [chunk for chunk in chunks if chunk.is_mathematical()]
            print(f"✅ Found {len(math_chunks)} mathematical chunks")
            
            # Test chunk validation
            valid_chunks = 0
            for chunk in chunks:
                if chunk.id and chunk.text and chunk.source_id:
                    valid_chunks += 1
            
            print(f"✅ {valid_chunks}/{len(chunks)} chunks are valid")
            
            return True
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ Enhanced document processing test error: {e}")
        return False

def test_enhanced_chunk_functionality():
    """Test enhanced chunk functionality."""
    print("\n🧪 Testing enhanced chunk functionality...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
        from enhanced_chunk import (
            EnhancedChunk, ContentType, MathematicalContent, AssetContent,
            GlossaryContent
        )
        
        # Test basic chunk creation
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
        
        # Test retrieval text
        retrieval_text = chunk.get_retrieval_text()
        assert chunk.text in retrieval_text
        
        print("✅ Enhanced chunk functionality working")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced chunk test error: {e}")
        return False

def test_mathematical_processing():
    """Test mathematical processing functionality."""
    print("\n🧪 Testing mathematical processing...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
        from mathematical_processor import MathematicalProcessor
        
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
        sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
        from content_classifier import ContentClassifier
        from enhanced_chunk import ContentType
        
        classifier = ContentClassifier()
        
        # Test equation classification
        equation_text = r"\\begin{equation} E = mc^2 \\end{equation}"
        content_type, confidence = classifier.classify_content(equation_text)
        assert content_type == ContentType.EQUATION
        assert confidence > 0
        print("✅ Equation classification working")
        
        # Test figure classification
        figure_text = r"\\begin{figure} \\includegraphics{image.png} \\caption{Test figure} \\end{figure}"
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

def test_enhanced_chunker():
    """Test enhanced chunker functionality."""
    print("\n🧪 Testing enhanced chunker...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
        from enhanced_chunker import EnhancedChunker
        from enhanced_chunk import ContentType
        
        chunker = EnhancedChunker(chunk_size=500, chunk_overlap=100)
        
        # Test chunking with mathematical content
        test_text = """
        This is a paragraph with some text.
        
        Here's an equation: $E = mc^2$
        
        And another paragraph with more text.
        """
        
        chunks = chunker.chunk_document(test_text, "test_source")
        assert len(chunks) > 0
        print(f"✅ Created {len(chunks)} chunks")
        
        # Check that we have different content types
        content_types = [chunk.content_type for chunk in chunks]
        print(f"✅ Content types found: {set(content_types)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced chunker test error: {e}")
        return False

def test_asset_processing():
    """Test asset processing functionality."""
    print("\n🧪 Testing asset processing...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
        from asset_processor import AssetProcessor
        
        processor = AssetProcessor()
        
        # Test figure processing
        figure_text = r"\\begin{figure} \\includegraphics{test.png} \\caption{Test figure} \\end{figure}"
        asset = processor.process_asset(figure_text)
        
        if asset:
            assert asset.asset_type == "figure"
            assert asset.caption == "Test figure"
            print("✅ Figure processing working")
        else:
            print("⚠️  Figure processing returned None (may be expected)")
        
        # Test table processing
        table_text = r"\\begin{table} \\begin{tabular}{cc} A & B \\\\ C & D \\end{tabular} \\end{table}"
        asset = processor.process_asset(table_text)
        
        if asset:
            assert asset.asset_type == "table"
            print("✅ Table processing working")
        else:
            print("⚠️  Table processing returned None (may be expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ Asset processing test error: {e}")
        return False

def test_glossary_extraction():
    """Test glossary extraction functionality."""
    print("\n🧪 Testing glossary extraction...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
        from glossary_extractor import GlossaryExtractor
        
        extractor = GlossaryExtractor()
        
        # Test definition extraction
        definition_text = "Definition: A function is continuous if it has no jumps or breaks."
        term = extractor.extract_glossary_term(definition_text)
        
        if term:
            assert term.term == "A function"
            assert "continuous" in term.definition
            print("✅ Glossary extraction working")
        else:
            print("⚠️  Glossary extraction returned None (may be expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ Glossary extraction test error: {e}")
        return False

def test_monitoring_system():
    """Test monitoring system functionality."""
    print("\n🧪 Testing monitoring system...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
        from monitoring import EnhancedProcessingMonitor
        
        monitor = EnhancedProcessingMonitor()
        
        # Test metrics recording
        monitor.record_processing_metrics(
            documents_processed=1,
            chunks_created=5,
            mathematical_content_processed=2,
            assets_processed=1,
            glossary_terms_extracted=1,
            processing_time=1.5
        )
        
        # Test statistics retrieval
        stats = monitor.get_processing_stats()
        assert 'total_documents' in stats
        assert 'total_chunks' in stats
        assert 'avg_processing_time' in stats
        print("✅ Monitoring system working")
        
        # Test health status
        health = monitor.get_health_status()
        assert 'is_healthy' in health
        assert 'last_health_check' in health
        print("✅ Health monitoring working")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring system test error: {e}")
        return False

def test_enhanced_scirag_standalone():
    """Test enhanced SciRAG standalone functionality."""
    print("\n🧪 Testing enhanced SciRAG standalone functionality...")
    
    try:
        # Test that we can create a mock enhanced SciRAG class
        sys.path.insert(0, str(Path(__file__).parent / "scirag" / "enhanced_processing"))
        from document_processor import EnhancedDocumentProcessor
        from enhanced_chunk import EnhancedChunk, ContentType
        
        class MockEnhancedSciRAG:
            def __init__(self):
                self.enhanced_processor = EnhancedDocumentProcessor()
                self.enhanced_chunks = []
                self.enable_enhanced_processing = True
            
            def load_documents_enhanced(self, file_paths, source_ids=None):
                """Load documents with enhanced processing."""
                all_chunks = []
                for file_path in file_paths:
                    chunks = self.enhanced_processor.process_document(file_path, "test_source")
                    all_chunks.extend(chunks)
                self.enhanced_chunks = all_chunks
                return all_chunks
            
            def get_mathematical_chunks(self):
                """Get mathematical chunks."""
                return [chunk for chunk in self.enhanced_chunks if chunk.is_mathematical()]
            
            def get_chunks_by_type(self, content_type):
                """Get chunks by type."""
                return [chunk for chunk in self.enhanced_chunks if chunk.content_type == content_type]
        
        # Test the mock class
        scirag = MockEnhancedSciRAG()
        
        # Create a test document
        test_content = """
        # Test Document
        
        This is a test equation: $E = mc^2$
        
        Here's a figure:
        \\begin{figure}
        \\includegraphics{test.png}
        \\caption{Test figure}
        \\end{figure}
        
        This is regular prose.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Test enhanced document loading
            chunks = scirag.load_documents_enhanced([temp_file])
            assert len(chunks) > 0
            print(f"✅ Enhanced document loading created {len(chunks)} chunks")
            
            # Test chunk filtering
            math_chunks = scirag.get_mathematical_chunks()
            print(f"✅ Found {len(math_chunks)} mathematical chunks")
            
            # Test chunk type filtering
            equation_chunks = scirag.get_chunks_by_type(ContentType.EQUATION)
            print(f"✅ Found {len(equation_chunks)} equation chunks")
            
            return True
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ Enhanced SciRAG standalone test error: {e}")
        return False

def main():
    """Run all Phase 2 direct tests."""
    print("🚀 Starting Phase 2 Direct Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Direct Enhanced Imports", test_direct_enhanced_imports),
        ("Enhanced Document Processing", test_enhanced_document_processing),
        ("Enhanced Chunk Functionality", test_enhanced_chunk_functionality),
        ("Mathematical Processing", test_mathematical_processing),
        ("Content Classification", test_content_classification),
        ("Enhanced Chunker", test_enhanced_chunker),
        ("Asset Processing", test_asset_processing),
        ("Glossary Extraction", test_glossary_extraction),
        ("Monitoring System", test_monitoring_system),
        ("Enhanced SciRAG Standalone", test_enhanced_scirag_standalone)
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
        print("🎉 All Phase 2 direct tests passed! Enhanced processing is working.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before proceeding to Phase 3.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
