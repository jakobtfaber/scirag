"""
Enhanced Processing Module for SciRAG

This module integrates RAGBook's sophisticated document processing capabilities
into SciRAG, providing advanced mathematical content processing, content type
classification, and enhanced chunking strategies.
"""
from .enhanced_chunk import (
    EnhancedChunk, ContentType, MathematicalContent, AssetContent,
    GlossaryContent
)
from .mathematical_processor import MathematicalProcessor
from .content_classifier import ContentClassifier
from .enhanced_chunker import EnhancedChunker
from .document_processor import EnhancedDocumentProcessor
from .asset_processor import AssetProcessor
from .glossary_extractor import GlossaryExtractor
from .monitoring import EnhancedProcessingMonitor

__all__ = [
    'EnhancedChunk',
    'ContentType',
    'MathematicalContent',
    'AssetContent',
    'GlossaryContent',
    'MathematicalProcessor',
    'ContentClassifier',
    'EnhancedChunker',
    'EnhancedDocumentProcessor',
    'AssetProcessor',
    'GlossaryExtractor',
    'EnhancedProcessingMonitor'
]

__version__ = "0.1.0"