"""
Data integrity checker for Enhanced SciRAG.

This module provides comprehensive data integrity validation for enhanced chunks,
mathematical content, assets, and glossary terms.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from scirag.enhanced_processing.enhanced_chunk import EnhancedChunk, ContentType, MathematicalContent, AssetContent, GlossaryContent


class DataIntegrityChecker:
    """Comprehensive data integrity checker for enhanced SciRAG."""
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_enhanced_chunks(self, chunks: List[EnhancedChunk]) -> Tuple[bool, List[str]]:
        """
        Validate enhanced chunks for data integrity.
        
        Args:
            chunks: List of enhanced chunks to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        if not chunks:
            self.validation_warnings.append("No chunks provided for validation")
            return True, self.validation_warnings
        
        for i, chunk in enumerate(chunks):
            self._validate_chunk_basic(chunk, i)
            self._validate_chunk_content_type(chunk, i)
            self._validate_chunk_metadata(chunk, i)
        
        is_valid = len(self.validation_errors) == 0
        all_messages = self.validation_errors + self.validation_warnings
        
        return is_valid, all_messages
    
    def _validate_chunk_basic(self, chunk: EnhancedChunk, index: int):
        """Validate basic chunk properties."""
        if not chunk.id:
            self.validation_errors.append(f"Chunk {index}: Missing ID")
        
        if not chunk.text:
            self.validation_errors.append(f"Chunk {index}: Missing text content")
        
        if not chunk.source_id:
            self.validation_errors.append(f"Chunk {index}: Missing source ID")
        
        if chunk.chunk_index < 0:
            self.validation_errors.append(f"Chunk {index}: Invalid chunk index: {chunk.chunk_index}")
        
        if not isinstance(chunk.content_type, ContentType):
            self.validation_errors.append(f"Chunk {index}: Invalid content type: {chunk.content_type}")
        
        if not (0.0 <= chunk.confidence <= 1.0):
            self.validation_errors.append(f"Chunk {index}: Invalid confidence score: {chunk.confidence}")
    
    def _validate_chunk_content_type(self, chunk: EnhancedChunk, index: int):
        """Validate content type specific properties."""
        if chunk.content_type == ContentType.EQUATION:
            self._validate_mathematical_content(chunk, index)
        elif chunk.content_type in [ContentType.FIGURE, ContentType.TABLE]:
            self._validate_asset_content(chunk, index)
        elif chunk.content_type == ContentType.DEFINITION:
            self._validate_glossary_content(chunk, index)
    
    def _validate_mathematical_content(self, chunk: EnhancedChunk, index: int):
        """Validate mathematical content."""
        if not chunk.mathematical_content:
            self.validation_errors.append(f"Chunk {index}: Missing mathematical content for equation")
            return
        
        math_content = chunk.mathematical_content
        
        if not math_content.equation_tex:
            self.validation_errors.append(f"Chunk {index}: Missing equation LaTeX")
        
        if not math_content.math_norm:
            self.validation_warnings.append(f"Chunk {index}: Missing normalized equation")
        
        if not math_content.math_tokens:
            self.validation_warnings.append(f"Chunk {index}: Missing math tokens")
        
        if not math_content.math_kgrams:
            self.validation_warnings.append(f"Chunk {index}: Missing math k-grams")
        
        if math_content.complexity_score < 0:
            self.validation_errors.append(f"Chunk {index}: Invalid complexity score: {math_content.complexity_score}")
        
        # Validate equation consistency
        if math_content.equation_tex and math_content.math_norm:
            if not self._validate_equation_consistency(math_content.equation_tex, math_content.math_norm):
                self.validation_warnings.append(f"Chunk {index}: Equation normalization may be inconsistent")
    
    def _validate_asset_content(self, chunk: EnhancedChunk, index: int):
        """Validate asset content."""
        if not chunk.asset_content:
            self.validation_errors.append(f"Chunk {index}: Missing asset content for {chunk.content_type.value}")
            return
        
        asset_content = chunk.asset_content
        
        if not asset_content.asset_type:
            self.validation_errors.append(f"Chunk {index}: Missing asset type")
        
        if not asset_content.caption:
            self.validation_warnings.append(f"Chunk {index}: Missing asset caption")
        
        if asset_content.file_path and not Path(asset_content.file_path).exists():
            self.validation_warnings.append(f"Chunk {index}: Asset file not found: {asset_content.file_path}")
    
    def _validate_glossary_content(self, chunk: EnhancedChunk, index: int):
        """Validate glossary content."""
        if not chunk.glossary_content:
            self.validation_errors.append(f"Chunk {index}: Missing glossary content for definition")
            return
        
        glossary_content = chunk.glossary_content
        
        if not glossary_content.term:
            self.validation_errors.append(f"Chunk {index}: Missing glossary term")
        
        if not glossary_content.definition:
            self.validation_errors.append(f"Chunk {index}: Missing glossary definition")
        
        if not glossary_content.context:
            self.validation_warnings.append(f"Chunk {index}: Missing glossary context")
    
    def _validate_chunk_metadata(self, chunk: EnhancedChunk, index: int):
        """Validate chunk metadata."""
        if chunk.processing_time < 0:
            self.validation_errors.append(f"Chunk {index}: Invalid processing time: {chunk.processing_time}")
        
        if chunk.error_count < 0:
            self.validation_errors.append(f"Chunk {index}: Invalid error count: {chunk.error_count}")
        
        if not chunk.processing_version:
            self.validation_warnings.append(f"Chunk {index}: Missing processing version")
        
        # Validate metadata dictionary
        if not isinstance(chunk.metadata, dict):
            self.validation_errors.append(f"Chunk {index}: Invalid metadata type: {type(chunk.metadata)}")
    
    def _validate_equation_consistency(self, equation_tex: str, math_norm: str) -> bool:
        """Validate that equation normalization is consistent."""
        # Basic consistency checks
        if not equation_tex or not math_norm:
            return False
        
        # Check that normalized version doesn't contain LaTeX commands
        latex_commands = ['\\', '{', '}', '^', '_', '&', '%', '$']
        for cmd in latex_commands:
            if cmd in math_norm:
                return False
        
        return True
    
    def validate_processing_pipeline(self, input_data: Any, output_chunks: List[EnhancedChunk]) -> Tuple[bool, List[str]]:
        """
        Validate the entire processing pipeline.
        
        Args:
            input_data: Original input data
            output_chunks: Processed chunks
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        # Validate input data
        if not input_data:
            self.validation_errors.append("No input data provided")
            return False, self.validation_errors
        
        # Validate output chunks
        chunks_valid, chunk_errors = self.validate_enhanced_chunks(output_chunks)
        self.validation_errors.extend(chunk_errors)
        
        # Validate pipeline consistency
        self._validate_pipeline_consistency(input_data, output_chunks)
        
        is_valid = len(self.validation_errors) == 0
        all_messages = self.validation_errors + self.validation_warnings
        
        return is_valid, all_messages
    
    def _validate_pipeline_consistency(self, input_data: Any, output_chunks: List[EnhancedChunk]):
        """Validate consistency between input and output."""
        if not output_chunks:
            self.validation_errors.append("No chunks produced from input data")
            return
        
        # Check that all chunks have the same source_id if input is a single document
        if isinstance(input_data, (str, Path)):
            source_ids = set(chunk.source_id for chunk in output_chunks)
            if len(source_ids) > 1:
                self.validation_warnings.append("Multiple source IDs found in single document processing")
        
        # Check that chunk indices are sequential
        chunk_indices = [chunk.chunk_index for chunk in output_chunks]
        if chunk_indices != sorted(chunk_indices):
            self.validation_warnings.append("Chunk indices are not sequential")
        
        # Check for duplicate chunk IDs
        chunk_ids = [chunk.id for chunk in output_chunks]
        if len(chunk_ids) != len(set(chunk_ids)):
            self.validation_errors.append("Duplicate chunk IDs found")
    
    def validate_mathematical_processing(self, equation_tex: str, processed_result: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate mathematical processing results.
        
        Args:
            equation_tex: Original equation LaTeX
            processed_result: Processed mathematical content
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        if not equation_tex:
            self.validation_errors.append("No equation provided")
            return False, self.validation_errors
        
        if not processed_result:
            self.validation_errors.append("No processing result provided")
            return False, self.validation_errors
        
        # Validate required fields
        required_fields = ['equation_tex', 'math_norm', 'math_tokens', 'math_kgrams']
        for field in required_fields:
            if field not in processed_result:
                self.validation_errors.append(f"Missing required field: {field}")
        
        # Validate equation consistency
        if 'equation_tex' in processed_result and 'math_norm' in processed_result:
            if processed_result['equation_tex'] != equation_tex:
                self.validation_errors.append("Equation LaTeX mismatch")
            
            if not self._validate_equation_consistency(processed_result['equation_tex'], processed_result['math_norm']):
                self.validation_warnings.append("Equation normalization may be inconsistent")
        
        # Validate tokens and k-grams
        if 'math_tokens' in processed_result and 'math_kgrams' in processed_result:
            tokens = processed_result['math_tokens']
            kgrams = processed_result['math_kgrams']
            
            if not isinstance(tokens, list):
                self.validation_errors.append("Math tokens must be a list")
            
            if not isinstance(kgrams, list):
                self.validation_errors.append("Math k-grams must be a list")
            
            if tokens and kgrams:
                # Check that k-grams are derived from tokens
                if not self._validate_kgrams_consistency(tokens, kgrams):
                    self.validation_warnings.append("K-grams may not be consistent with tokens")
        
        is_valid = len(self.validation_errors) == 0
        all_messages = self.validation_errors + self.validation_warnings
        
        return is_valid, all_messages
    
    def _validate_kgrams_consistency(self, tokens: List[str], kgrams: List[str]) -> bool:
        """Validate that k-grams are consistent with tokens."""
        if not tokens or not kgrams:
            return True
        
        # Basic check: k-grams should be substrings of token sequences
        token_string = ' '.join(tokens)
        for kgram in kgrams:
            if kgram not in token_string:
                return False
        
        return True
    
    def generate_integrity_report(self, chunks: List[EnhancedChunk]) -> Dict[str, Any]:
        """
        Generate a comprehensive integrity report.
        
        Args:
            chunks: List of enhanced chunks
            
        Returns:
            Integrity report dictionary
        """
        is_valid, messages = self.validate_enhanced_chunks(chunks)
        
        # Count content types
        content_type_counts = {}
        for chunk in chunks:
            content_type = chunk.content_type.value
            content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        
        # Count chunks with enhanced content
        mathematical_chunks = sum(1 for chunk in chunks if chunk.is_mathematical())
        asset_chunks = sum(1 for chunk in chunks if chunk.is_asset())
        glossary_chunks = sum(1 for chunk in chunks if chunk.is_glossary())
        
        # Calculate processing statistics
        total_processing_time = sum(chunk.processing_time for chunk in chunks)
        total_errors = sum(chunk.error_count for chunk in chunks)
        avg_confidence = sum(chunk.confidence for chunk in chunks) / len(chunks) if chunks else 0
        
        report = {
            'is_valid': is_valid,
            'total_chunks': len(chunks),
            'content_type_distribution': content_type_counts,
            'enhanced_content_counts': {
                'mathematical': mathematical_chunks,
                'asset': asset_chunks,
                'glossary': glossary_chunks
            },
            'processing_statistics': {
                'total_processing_time': total_processing_time,
                'total_errors': total_errors,
                'average_confidence': avg_confidence
            },
            'validation_messages': messages,
            'error_count': len(self.validation_errors),
            'warning_count': len(self.validation_warnings)
        }
        
        return report
    
    def export_validation_report(self, chunks: List[EnhancedChunk], format: str = 'json') -> str:
        """
        Export validation report in specified format.
        
        Args:
            chunks: List of enhanced chunks
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported report string
        """
        report = self.generate_integrity_report(chunks)
        
        if format == 'json':
            return json.dumps(report, indent=2)
        elif format == 'csv':
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Metric', 'Value'])
            
            # Write basic metrics
            writer.writerow(['Total Chunks', report['total_chunks']])
            writer.writerow(['Is Valid', report['is_valid']])
            writer.writerow(['Error Count', report['error_count']])
            writer.writerow(['Warning Count', report['warning_count']])
            
            # Write content type distribution
            for content_type, count in report['content_type_distribution'].items():
                writer.writerow([f'Content Type: {content_type}', count])
            
            # Write enhanced content counts
            for content_type, count in report['enhanced_content_counts'].items():
                writer.writerow([f'Enhanced Content: {content_type}', count])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
