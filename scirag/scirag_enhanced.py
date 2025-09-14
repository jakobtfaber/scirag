"""
Enhanced SciRAG Base Class

This module provides an enhanced version of SciRAG that integrates
RAGBook's advanced document processing capabilities while maintaining
backward compatibility with existing SciRAG functionality.
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass

# Import enhanced processing modules
try:
    from .enhanced_processing import (
        EnhancedDocumentProcessor, EnhancedChunk, ContentType,
        MathematicalContent, AssetContent, GlossaryContent
    )
    ENHANCED_PROCESSING_AVAILABLE = True
except ImportError:
    ENHANCED_PROCESSING_AVAILABLE = False
    # Fallback imports for when enhanced processing is not available
    EnhancedDocumentProcessor = None
    EnhancedChunk = None
    ContentType = None

# Import original SciRAG components
from .scirag import SciRag
from .config import enhanced_config


@dataclass
class EnhancedProcessingStats:
    """Statistics for enhanced processing operations."""
    documents_processed: int = 0
    chunks_created: int = 0
    mathematical_content_processed: int = 0
    assets_processed: int = 0
    glossary_terms_extracted: int = 0
    processing_time: float = 0.0
    errors: int = 0


class SciRagEnhanced(SciRag):
    """
    Enhanced SciRAG class with RAGBook integration.
    
    This class extends the original SciRAG functionality with advanced
    document processing capabilities while maintaining full backward
    compatibility.
    """
    
    def __init__(self,
                 client=None,
                 credentials=None,
                 markdown_files_path=None,
                 corpus_name="enhanced_corpus",
                 gen_model="gpt-4",
                 # Enhanced processing parameters
                 enable_enhanced_processing: bool = True,
                 enable_mathematical_processing: bool = True,
                 enable_asset_processing: bool = True,
                 enable_glossary_extraction: bool = True,
                 enable_enhanced_chunking: bool = True,
                 # Chunking parameters
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 # Fallback parameters
                 fallback_on_error: bool = True,
                 **kwargs):
        """
        Initialize enhanced SciRAG with optional enhanced processing.
        
        Args:
            client: LLM client (OpenAI, Vertex AI, etc.)
            credentials: Authentication credentials
            markdown_files_path: Path to markdown files
            corpus_name: Name of the corpus
            gen_model: Generation model to use
            enable_enhanced_processing: Enable enhanced processing features
            enable_mathematical_processing: Enable mathematical content processing
            enable_asset_processing: Enable figure/table processing
            enable_glossary_extraction: Enable glossary term extraction
            enable_enhanced_chunking: Enable content-aware chunking
            chunk_size: Target chunk size for enhanced chunking
            chunk_overlap: Overlap between chunks
            fallback_on_error: Fallback to original processing on errors
            **kwargs: Additional arguments passed to parent class
        """
        # Initialize parent class
        super().__init__(
            client=client,
            credentials=credentials,
            markdown_files_path=markdown_files_path,
            corpus_name=corpus_name,
            gen_model=gen_model,
            **kwargs
        )
        
        # Enhanced processing configuration
        self.enable_enhanced_processing = (
            enable_enhanced_processing and 
            ENHANCED_PROCESSING_AVAILABLE and
            enhanced_config.ENABLE_ENHANCED_PROCESSING
        )
        
        # Individual feature flags
        self.enable_mathematical_processing = (
            enable_mathematical_processing and 
            enhanced_config.ENABLE_MATHEMATICAL_PROCESSING
        )
        self.enable_asset_processing = (
            enable_asset_processing and 
            enhanced_config.ENABLE_ASSET_PROCESSING
        )
        self.enable_glossary_extraction = (
            enable_glossary_extraction and 
            enhanced_config.ENABLE_GLOSSARY_EXTRACTION
        )
        self.enable_enhanced_chunking = (
            enable_enhanced_chunking and 
            enhanced_config.ENABLE_ENHANCED_CHUNKING
        )
        
        # Processing parameters
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.fallback_on_error = fallback_on_error
        
        # Enhanced processing components
        self.enhanced_processor = None
        self.enhanced_chunks = []
        self.processing_stats = EnhancedProcessingStats()
        
        # Initialize enhanced processing if enabled
        if self.enable_enhanced_processing:
            self._initialize_enhanced_processing()
        
        # Logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Enhanced SciRAG initialized with enhanced_processing={self.enable_enhanced_processing}")
    
    def _initialize_enhanced_processing(self):
        """Initialize enhanced processing components."""
        try:
            if ENHANCED_PROCESSING_AVAILABLE:
                self.enhanced_processor = EnhancedDocumentProcessor(
                    enable_mathematical_processing=self.enable_mathematical_processing,
                    enable_asset_processing=self.enable_asset_processing,
                    enable_glossary_extraction=self.enable_glossary_extraction,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
                self.logger.info("Enhanced processing initialized successfully")
            else:
                self.logger.warning("Enhanced processing not available, falling back to basic processing")
                self.enable_enhanced_processing = False
        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced processing: {e}")
            if self.fallback_on_error:
                self.enable_enhanced_processing = False
                self.logger.info("Falling back to basic processing")
            else:
                raise
    
    def load_documents_enhanced(self, 
                               file_paths: List[Union[str, Path]], 
                               source_ids: Optional[List[str]] = None) -> List[EnhancedChunk]:
        """
        Load documents with enhanced processing capabilities.
        
        Args:
            file_paths: List of file paths to process
            source_ids: Optional list of source IDs (defaults to file names)
            
        Returns:
            List of EnhancedChunk objects
        """
        if not self.enable_enhanced_processing or not self.enhanced_processor:
            self.logger.warning("Enhanced processing not available, using basic processing")
            return self._load_documents_basic(file_paths, source_ids)
        
        try:
            start_time = time.time()
            
            # Convert to Path objects
            file_paths = [Path(fp) for fp in file_paths]
            
            # Generate source IDs if not provided
            if source_ids is None:
                source_ids = [fp.stem for fp in file_paths]
            
            # Process documents
            all_chunks = []
            for file_path, source_id in zip(file_paths, source_ids):
                try:
                    chunks = self.enhanced_processor.process_document(
                        file_path, source_id
                    )
                    all_chunks.extend(chunks)
                    self.processing_stats.documents_processed += 1
                except Exception as e:
                    self.logger.error(f"Error processing document {file_path}: {e}")
                    self.processing_stats.errors += 1
                    
                    if self.fallback_on_error:
                        # Fallback to basic processing for this document
                        basic_chunks = self._load_document_basic(file_path, source_id)
                        all_chunks.extend(basic_chunks)
            
            # Update statistics
            self.enhanced_chunks = all_chunks
            self.processing_stats.chunks_created = len(all_chunks)
            self.processing_stats.processing_time = time.time() - start_time
            
            # Count specialized content
            self._update_content_stats(all_chunks)
            
            self.logger.info(f"Enhanced processing completed: {len(all_chunks)} chunks created")
            return all_chunks
            
        except Exception as e:
            self.logger.error(f"Enhanced processing failed: {e}")
            if self.fallback_on_error:
                self.logger.info("Falling back to basic processing")
                return self._load_documents_basic(file_paths, source_ids)
            else:
                raise
    
    def _load_documents_basic(self, 
                             file_paths: List[Union[str, Path]], 
                             source_ids: Optional[List[str]] = None) -> List[EnhancedChunk]:
        """Fallback to basic document loading."""
        # This would use the original SciRAG document loading
        # For now, return empty list as placeholder
        self.logger.info("Using basic document loading (fallback)")
        return []
    
    def _load_document_basic(self, file_path: Path, source_id: str) -> List[EnhancedChunk]:
        """Load a single document using basic processing."""
        # This would use the original SciRAG document loading
        # For now, return empty list as placeholder
        return []
    
    def _update_content_stats(self, chunks: List[EnhancedChunk]):
        """Update content-specific statistics."""
        for chunk in chunks:
            if chunk.is_mathematical():
                self.processing_stats.mathematical_content_processed += 1
            if chunk.is_asset():
                self.processing_stats.assets_processed += 1
            if chunk.is_glossary():
                self.processing_stats.glossary_terms_extracted += 1
    
    def get_enhanced_response(self, 
                             query: str, 
                             content_types: Optional[List[ContentType]] = None,
                             max_chunks: int = 10) -> str:
        """
        Get enhanced response with content type filtering.
        
        Args:
            query: Query string
            content_types: Optional list of content types to filter by
            max_chunks: Maximum number of chunks to use
            
        Returns:
            Enhanced response string
        """
        if not self.enable_enhanced_processing or not self.enhanced_chunks:
            self.logger.warning("Enhanced processing not available, using basic response")
            return self.get_response(query)
        
        try:
            # Filter chunks by content type if specified
            filtered_chunks = self._filter_chunks_by_type(content_types)
            
            # Limit number of chunks
            if len(filtered_chunks) > max_chunks:
                filtered_chunks = filtered_chunks[:max_chunks]
            
            # Get context from filtered chunks
            context = self._build_context_from_chunks(filtered_chunks)
            
            # Generate response using the context
            response = self._generate_enhanced_response(query, context)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Enhanced response generation failed: {e}")
            if self.fallback_on_error:
                self.logger.info("Falling back to basic response")
                return self.get_response(query)
            else:
                raise
    
    def _filter_chunks_by_type(self, content_types: Optional[List[ContentType]]) -> List[EnhancedChunk]:
        """Filter chunks by content type."""
        if not content_types:
            return self.enhanced_chunks
        
        return [chunk for chunk in self.enhanced_chunks 
                if chunk.content_type in content_types]
    
    def _build_context_from_chunks(self, chunks: List[EnhancedChunk]) -> str:
        """Build context string from enhanced chunks."""
        context_parts = []
        
        for chunk in chunks:
            # Use enhanced retrieval text that includes metadata
            context_parts.append(chunk.get_retrieval_text())
        
        return "\n\n".join(context_parts)
    
    def _generate_enhanced_response(self, query: str, context: str) -> str:
        """Generate response using enhanced context."""
        # This would use the parent class's generation method
        # with enhanced context
        prompt = f"Context:\n{context}\n\nQuery: {query}\n\nResponse:"
        
        # Use the parent class's generation method
        return self._generate_response_with_prompt(prompt)
    
    def _generate_response_with_prompt(self, prompt: str) -> str:
        """Generate response using a custom prompt."""
        # This would be implemented by the specific provider classes
        # For now, return a placeholder
        return f"Enhanced response for: {prompt[:100]}..."
    
    def get_mathematical_chunks(self) -> List[EnhancedChunk]:
        """Get chunks containing mathematical content."""
        if not self.enhanced_chunks:
            return []
        
        return [chunk for chunk in self.enhanced_chunks if chunk.is_mathematical()]
    
    def get_asset_chunks(self) -> List[EnhancedChunk]:
        """Get chunks containing asset content."""
        if not self.enhanced_chunks:
            return []
        
        return [chunk for chunk in self.enhanced_chunks if chunk.is_asset()]
    
    def get_glossary_chunks(self) -> List[EnhancedChunk]:
        """Get chunks containing glossary content."""
        if not self.enhanced_chunks:
            return []
        
        return [chunk for chunk in self.enhanced_chunks if chunk.is_glossary()]
    
    def get_chunks_by_type(self, content_type: ContentType) -> List[EnhancedChunk]:
        """Get chunks of a specific content type."""
        if not self.enhanced_chunks:
            return []
        
        return [chunk for chunk in self.enhanced_chunks 
                if chunk.content_type == content_type]
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get enhanced processing statistics."""
        return {
            'enhanced_processing_enabled': self.enable_enhanced_processing,
            'mathematical_processing_enabled': self.enable_mathematical_processing,
            'asset_processing_enabled': self.enable_asset_processing,
            'glossary_extraction_enabled': self.enable_glossary_extraction,
            'enhanced_chunking_enabled': self.enable_enhanced_chunking,
            'documents_processed': self.processing_stats.documents_processed,
            'chunks_created': self.processing_stats.chunks_created,
            'mathematical_content_processed': self.processing_stats.mathematical_content_processed,
            'assets_processed': self.processing_stats.assets_processed,
            'glossary_terms_extracted': self.processing_stats.glossary_terms_extracted,
            'processing_time': self.processing_stats.processing_time,
            'errors': self.processing_stats.errors
        }
    
    def export_enhanced_chunks(self, format: str = 'json') -> str:
        """Export enhanced chunks in specified format."""
        if not self.enhanced_chunks:
            return "No enhanced chunks available"
        
        if format.lower() == 'json':
            import json
            return json.dumps([chunk.to_dict() for chunk in self.enhanced_chunks], indent=2)
        elif format.lower() == 'csv':
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['id', 'text', 'content_type', 'confidence', 'source_id'])
            
            # Write data
            for chunk in self.enhanced_chunks:
                writer.writerow([
                    chunk.id,
                    chunk.text[:100] + '...' if len(chunk.text) > 100 else chunk.text,
                    chunk.content_type.value,
                    chunk.confidence,
                    chunk.source_id
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def validate_enhanced_chunks(self) -> Dict[str, Any]:
        """Validate enhanced chunks for quality and consistency."""
        if not self.enhanced_chunks:
            return {'total_chunks': 0, 'valid_chunks': 0, 'invalid_chunks': 0}
        
        valid_chunks = 0
        invalid_chunks = 0
        content_type_distribution = {}
        
        for chunk in self.enhanced_chunks:
            try:
                # Basic validation
                if not chunk.id or not chunk.text or not chunk.source_id:
                    invalid_chunks += 1
                    continue
                
                # Content type distribution
                content_type = chunk.content_type.value
                content_type_distribution[content_type] = content_type_distribution.get(content_type, 0) + 1
                
                valid_chunks += 1
                
            except Exception:
                invalid_chunks += 1
        
        return {
            'total_chunks': len(self.enhanced_chunks),
            'valid_chunks': valid_chunks,
            'invalid_chunks': invalid_chunks,
            'content_type_distribution': content_type_distribution
        }
