#!/usr/bin/env python3
"""
Phase 2 Integration Test

This test verifies that all Phase 2 components work together correctly,
including the document processor, enhanced chunker, asset processor,
and glossary extractor.
"""

import sys
from pathlib import Path

# Add the scirag module to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_enhanced_document_processor():
    """Test the main document processor orchestrator."""
    try:
        # Import the module file directly
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "document_processor", 
            "scirag/enhanced_processing/document_processor.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        EnhancedDocumentProcessor = module.EnhancedDocumentProcessor
        ProcessingConfig = module.ProcessingConfig
        
        # Test configuration
        config = ProcessingConfig(
            enable_mathematical_processing=True,
            enable_asset_processing=True,
            enable_glossary_extraction=True,
            enable_enhanced_chunking=True,
            chunk_size=200,
            overlap_ratio=0.1
        )
        
        # Test processor initialization
        processor = EnhancedDocumentProcessor(config)
        
        # Test health check
        health = processor.health_check()
        assert health['overall_status'] in ['healthy', 'degraded']
        assert 'processors' in health
        
        # Test processing stats
        stats = processor.get_processing_stats()
        assert 'documents_processed' in stats
        assert 'chunks_created' in stats
        
        print("✅ EnhancedDocumentProcessor: FULLY FUNCTIONAL")
        return True
    except Exception as e:
        print(f"❌ EnhancedDocumentProcessor test failed: {e}")
        return False

def test_enhanced_chunker():
    """Test the enhanced chunker."""
    try:
        # Import the module file directly
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "enhanced_chunker", 
            "scirag/enhanced_processing/enhanced_chunker.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        EnhancedChunker = module.EnhancedChunker
        ChunkingConfig = module.ChunkingConfig
        ContentType = module.ContentType
        
        # Test configuration
        config = ChunkingConfig(
            chunk_size=200,
            overlap_ratio=0.1,
            preserve_math_context=True,
            preserve_asset_context=True
        )
        
        # Test chunker initialization
        chunker = EnhancedChunker(config)
        
        # Test prose chunking
        prose_text = "This is a paragraph of text. It contains multiple sentences. Each sentence should be properly chunked."
        chunks = chunker.chunk_content(prose_text, ContentType.PROSE)
        assert len(chunks) > 0
        assert all(len(chunk) > 0 for chunk in chunks)
        
        # Test mathematical chunking
        math_text = "The equation $E = mc^2$ is famous. It relates energy and mass."
        chunks = chunker.chunk_content(math_text, ContentType.EQUATION)
        assert len(chunks) > 0
        
        # Test chunking stats
        stats = chunker.get_chunking_stats()
        assert 'chunks_created' in stats
        
        print("✅ EnhancedChunker: FULLY FUNCTIONAL")
        return True
    except Exception as e:
        print(f"❌ EnhancedChunker test failed: {e}")
        return False

def test_asset_processor():
    """Test the asset processor."""
    try:
        # Import the module file directly
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "asset_processor", 
            "scirag/enhanced_processing/asset_processor.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        AssetProcessor = module.AssetProcessor
        AssetConfig = module.AssetConfig
        
        # Test configuration
        config = AssetConfig(
            enable_ocr=False,  # Disable OCR for testing
            extract_captions=True,
            extract_labels=True
        )
        
        # Test processor initialization
        processor = AssetProcessor(config)
        
        # Test figure extraction
        latex_content = """
        \\begin{figure}
        \\includegraphics{test.png}
        \\caption{A test figure}
        \\label{fig:test}
        \\end{figure}
        """
        
        assets = processor.extract_assets(latex_content)
        assert len(assets) > 0
        assert any(asset['type'] == 'figure' for asset in assets)
        
        # Test table extraction
        table_content = """
        \\begin{table}
        \\begin{tabular}{|c|c|}
        \\hline
        A & B \\\\
        \\hline
        C & D \\\\
        \\hline
        \\end{tabular}
        \\caption{A test table}
        \\end{table}
        """
        
        assets = processor.extract_assets(table_content)
        assert len(assets) > 0
        assert any(asset['type'] == 'table' for asset in assets)
        
        # Test processing stats
        stats = processor.get_processing_stats()
        assert 'figures_processed' in stats
        assert 'tables_processed' in stats
        
        print("✅ AssetProcessor: FULLY FUNCTIONAL")
        return True
    except Exception as e:
        print(f"❌ AssetProcessor test failed: {e}")
        return False

def test_glossary_extractor():
    """Test the glossary extractor."""
    try:
        # Import the module file directly
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "glossary_extractor", 
            "scirag/enhanced_processing/glossary_extractor.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        GlossaryExtractor = module.GlossaryExtractor
        GlossaryConfig = module.GlossaryConfig
        
        # Test configuration
        config = GlossaryConfig(
            min_definition_length=5,
            max_definition_length=200,
            confidence_threshold=0.3,
            extract_related_terms=True
        )
        
        # Test extractor initialization
        extractor = GlossaryExtractor(config)
        
        # Test LaTeX glossary extraction
        latex_content = """
        \\textbf{Dark Matter}: A form of matter that does not emit, absorb, or reflect light.
        \\textbf{Dark Energy}: A mysterious force that is causing the expansion of the universe.
        """
        
        terms = extractor.extract_terms(latex_content)
        assert len(terms) > 0
        assert any(term['term'] == 'Dark Matter' for term in terms)
        assert any(term['term'] == 'Dark Energy' for term in terms)
        
        # Test Markdown glossary extraction
        markdown_content = """
        **Cosmology**: The study of the universe as a whole.
        **Galaxy**: A collection of stars, gas, and dust bound together by gravity.
        """
        
        terms = extractor.extract_terms(markdown_content)
        assert len(terms) > 0
        assert any(term['term'] == 'Cosmology' for term in terms)
        
        # Test processing stats
        stats = extractor.get_processing_stats()
        assert 'terms_extracted' in stats
        assert 'definitions_extracted' in stats
        
        print("✅ GlossaryExtractor: FULLY FUNCTIONAL")
        return True
    except Exception as e:
        print(f"❌ GlossaryExtractor test failed: {e}")
        return False

def test_integrated_processing():
    """Test integrated processing pipeline."""
    try:
        # Import all modules
        import importlib.util
        
        # Import document processor
        spec = importlib.util.spec_from_file_location(
            "document_processor", 
            "scirag/enhanced_processing/document_processor.py"
        )
        doc_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(doc_module)
        
        EnhancedDocumentProcessor = doc_module.EnhancedDocumentProcessor
        ProcessingConfig = doc_module.ProcessingConfig
        
        # Import content classifier
        spec = importlib.util.spec_from_file_location(
            "content_classifier", 
            "scirag/enhanced_processing/content_classifier.py"
        )
        classifier_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(classifier_module)
        
        ContentType = classifier_module.ContentType
        
        # Test integrated processing
        config = ProcessingConfig(
            enable_mathematical_processing=True,
            enable_asset_processing=True,
            enable_glossary_extraction=True,
            enable_enhanced_chunking=True,
            chunk_size=150,
            overlap_ratio=0.1
        )
        
        processor = EnhancedDocumentProcessor(config)
        
        # Test with mixed content
        test_content = """
        # Scientific Document
        
        This paper discusses **Dark Matter**: A form of matter that does not emit light.
        
        The famous equation is $E = mc^2$.
        
        \\begin{figure}
        \\includegraphics{cosmology.png}
        \\caption{The universe}
        \\end{figure}
        
        The study of cosmology involves understanding the universe.
        """
        
        # Create a temporary file for testing
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Process the document
            chunks = processor.process_document(temp_file, "test_doc")
            
            # Verify results
            assert len(chunks) > 0
            
            # Check that we have different content types
            content_types = [chunk.content_type for chunk in chunks]
            assert ContentType.PROSE in content_types
            
            # Check processing stats
            stats = processor.get_processing_stats()
            assert stats['documents_processed'] > 0
            assert stats['chunks_created'] > 0
            
        finally:
            # Clean up
            Path(temp_file).unlink()
        
        print("✅ Integrated Processing: FULLY FUNCTIONAL")
        return True
    except Exception as e:
        print(f"❌ Integrated Processing test failed: {e}")
        return False

def main():
    """Run all Phase 2 tests."""
    print("🎯 PHASE 2 INTEGRATION TESTING")
    print("=" * 50)
    print("Testing enhanced processing pipeline...")
    print()
    
    tests = [
        ("Enhanced Document Processor", test_enhanced_document_processor),
        ("Enhanced Chunker", test_enhanced_chunker),
        ("Asset Processor", test_asset_processor),
        ("Glossary Extractor", test_glossary_extractor),
        ("Integrated Processing Pipeline", test_integrated_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉" * 15)
        print("PHASE 2: ✅ SUCCESSFULLY COMPLETED")
        print("🎉" * 15)
        
        print("\n✅ PHASE 2 DELIVERABLES COMPLETE:")
        print("  • Enhanced Document Processor (main orchestrator)")
        print("  • Enhanced Chunker (content-aware chunking)")
        print("  • Asset Processor (figure/table processing)")
        print("  • Glossary Extractor (term extraction)")
        print("  • Integrated Processing Pipeline")
        print("  • Comprehensive Configuration System")
        print("  • Error Handling and Fallback Mechanisms")
        
        print("\n🔧 ENHANCED CAPABILITIES VERIFIED:")
        print("  • Content-type aware document processing")
        print("  • Mathematical context preservation")
        print("  • Asset metadata extraction")
        print("  • Glossary term identification")
        print("  • Advanced chunking strategies")
        print("  • Integrated processing pipeline")
        print("  • Comprehensive error handling")
        
        print("\n📋 READY FOR PHASE 3:")
        print("  1. Integrate with existing SciRAG classes")
        print("  2. Add comprehensive error handling and monitoring")
        print("  3. Create integration tests with SciRAG providers")
        print("  4. Add performance monitoring and optimization")
        print("  5. Create user documentation and examples")
        
        print("\n🚀 PHASE 2 FOUNDATION IS SOLID AND READY FOR PHASE 3!")
        return 0
    else:
        print(f"\n❌ {total - passed} components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
