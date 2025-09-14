"""
Document processing module for Enhanced SciRAG.

This module provides comprehensive document processing capabilities that
integrate mathematical processing, asset processing, and glossary extraction.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from .enhanced_chunk import EnhancedChunk, ContentType
from .enhanced_chunker import EnhancedChunker
from .mathematical_processor import MathematicalProcessor
from .content_classifier import ContentClassifier
from .asset_processor import AssetProcessor
from .glossary_extractor import GlossaryExtractor
from .monitoring import EnhancedProcessingMonitor


class EnhancedDocumentProcessor:
    """Enhanced document processor with RAGBook integration."""
    
    def __init__(self, 
                 chunk_size: int = 320,
                 overlap_ratio: float = 0.12,
                 enable_mathematical_processing: bool = True,
                 enable_asset_processing: bool = True,
                 enable_glossary_extraction: bool = True):
        """
        Initialize enhanced document processor.
        
        Args:
            chunk_size: Target chunk size in characters
            overlap_ratio: Overlap ratio between chunks
            enable_mathematical_processing: Whether to enable mathematical processing
            enable_asset_processing: Whether to enable asset processing
            enable_glossary_extraction: Whether to enable glossary extraction
        """
        self.chunk_size = chunk_size
        self.overlap_ratio = overlap_ratio
        self.enable_mathematical_processing = enable_mathematical_processing
        self.enable_asset_processing = enable_asset_processing
        self.enable_glossary_extraction = enable_glossary_extraction
        
        # Initialize components
        self.chunker = EnhancedChunker(
            chunk_size=chunk_size,
            overlap_ratio=overlap_ratio,
            preserve_math=enable_mathematical_processing,
            preserve_figures=enable_asset_processing,
            preserve_tables=enable_asset_processing
        )
        
        self.math_processor = MathematicalProcessor() if enable_mathematical_processing else None
        self.classifier = ContentClassifier()
        self.asset_processor = AssetProcessor() if enable_asset_processing else None
        self.glossary_extractor = GlossaryExtractor() if enable_glossary_extraction else None
        
        # Initialize monitoring
        self.monitor = EnhancedProcessingMonitor()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def process_document(self, file_path: Path, source_id: str) -> List[EnhancedChunk]:
        """
        Process a document into enhanced chunks.
        
        Args:
            file_path: Path to the document file
            source_id: Source document identifier
            
        Returns:
            List of enhanced chunks
        """
        try:
            self.logger.info(f"Processing document: {file_path}")
            
            # Read document content
            content = self._read_document(file_path)
            if not content:
                self.logger.warning(f"Empty document: {file_path}")
                return []
            
            # Process document into chunks
            chunks = self.chunker.chunk_document(content, source_id)
            
            # Enhance chunks with additional processing
            enhanced_chunks = []
            for chunk in chunks:
                enhanced_chunk = self._enhance_chunk(chunk)
                if enhanced_chunk:
                    enhanced_chunks.append(enhanced_chunk)
            
            # Record processing metrics
            self.monitor.record_success("document_processing", 0.1)
            
            self.logger.info(f"Processed {len(enhanced_chunks)} chunks from {file_path}")
            return enhanced_chunks
            
        except Exception as e:
            self.logger.error(f"Error processing document {file_path}: {e}")
            self.monitor.record_error("document_processing", str(e))
            return []
    
    def _read_document(self, file_path: Path) -> str:
        """Read document content from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return ""
    
    def _enhance_chunk(self, chunk: EnhancedChunk) -> Optional[EnhancedChunk]:
        """Enhance chunk with additional processing."""
        try:
            # Add mathematical content if enabled
            if (self.enable_mathematical_processing and 
                chunk.content_type == ContentType.EQUATION and 
                self.math_processor):
                self._add_mathematical_content(chunk)
            
            # Add asset content if enabled
            if (self.enable_asset_processing and 
                chunk.content_type in [ContentType.FIGURE, ContentType.TABLE] and 
                self.asset_processor):
                self._add_asset_content(chunk)
            
            # Add glossary content if enabled
            if (self.enable_glossary_extraction and 
                chunk.content_type == ContentType.DEFINITION and 
                self.glossary_extractor):
                self._add_glossary_content(chunk)
            
            return chunk
            
        except Exception as e:
            self.logger.error(f"Error enhancing chunk {chunk.id}: {e}")
            return chunk
    
    def _add_mathematical_content(self, chunk: EnhancedChunk):
        """Add mathematical content to chunk."""
        if not self.math_processor:
            return
        
        try:
            # Extract equation from text
            equation = self._extract_equation(chunk.text)
            if equation:
                math_content = self.math_processor.create_mathematical_content(equation)
                chunk.mathematical_content = math_content
        except Exception as e:
            self.logger.warning(f"Error adding mathematical content: {e}")
    
    def _add_asset_content(self, chunk: EnhancedChunk):
        """Add asset content to chunk."""
        if not self.asset_processor:
            return
        
        try:
            asset_content = self.asset_processor.process_asset(chunk.text, chunk.source_id)
            if asset_content:
                chunk.asset_content = asset_content
        except Exception as e:
            self.logger.warning(f"Error adding asset content: {e}")
    
    def _add_glossary_content(self, chunk: EnhancedChunk):
        """Add glossary content to chunk."""
        if not self.glossary_extractor:
            return
        
        try:
            glossary_terms = self.glossary_extractor.extract_glossary_terms(chunk.text, chunk.source_id)
            if glossary_terms:
                # Use the first glossary term
                chunk.glossary_content = glossary_terms[0]
        except Exception as e:
            self.logger.warning(f"Error adding glossary content: {e}")
    
    def _extract_equation(self, text: str) -> Optional[str]:
        """Extract equation from text."""
        import re
        
        # Look for LaTeX equation environments
        equation_patterns = [
            r'\\begin\{equation\}(.*?)\\end\{equation\}',
            r'\\begin\{align\}(.*?)\\end\{align\}',
            r'\\begin\{eqnarray\}(.*?)\\end\{eqnarray\}',
            r'\$([^$]+)\$',
            r'\\\[([^\]]+)\\\]',
            r'\\\(([^)]+)\\\)'
        ]
        
        for pattern in equation_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return None
    
    def process_multiple_documents(self, file_paths: List[Path], source_ids: List[str]) -> List[EnhancedChunk]:
        """
        Process multiple documents.
        
        Args:
            file_paths: List of file paths
            source_ids: List of source IDs
            
        Returns:
            List of all enhanced chunks
        """
        all_chunks = []
        
        for file_path, source_id in zip(file_paths, source_ids):
            chunks = self.process_document(file_path, source_id)
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def get_processing_statistics(self, chunks: List[EnhancedChunk]) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Args:
            chunks: List of enhanced chunks
            
        Returns:
            Dictionary containing processing statistics
        """
        if not chunks:
            return {}
        
        # Get chunker statistics
        chunker_stats = self.chunker.get_chunk_statistics(chunks)
        
        # Get monitoring metrics
        monitor_metrics = self.monitor.get_metrics()
        
        # Combine statistics
        stats = {
            'total_chunks': len(chunks),
            'chunker_statistics': chunker_stats,
            'processing_metrics': monitor_metrics,
            'enhanced_processing_enabled': {
                'mathematical': self.enable_mathematical_processing,
                'asset': self.enable_asset_processing,
                'glossary': self.enable_glossary_extraction
            }
        }
        
        return stats
    
    def export_chunks(self, chunks: List[EnhancedChunk], format: str = 'json') -> str:
        """
        Export chunks in specified format.
        
        Args:
            chunks: List of enhanced chunks
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported chunks string
        """
        if format == 'json':
            import json
            chunk_data = [chunk.to_dict() for chunk in chunks]
            return json.dumps(chunk_data, indent=2)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['id', 'text', 'content_type', 'source_id', 'chunk_index'])
            
            # Write data
            for chunk in chunks:
                writer.writerow([
                    chunk.id,
                    chunk.text,
                    chunk.content_type.value,
                    chunk.source_id,
                    chunk.chunk_index
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get processor health status."""
        return self.monitor.check_health()