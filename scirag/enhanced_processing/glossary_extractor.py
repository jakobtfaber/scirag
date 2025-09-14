"""
Glossary extraction module for Enhanced SciRAG.

This module provides capabilities for extracting and processing glossary terms,
definitions, and related concepts from scientific documents.
"""

import re
from typing import List, Dict, Any, Optional
from .enhanced_chunk import GlossaryContent


class GlossaryExtractor:
    """Glossary term and definition extractor."""
    
    def __init__(self):
        """Initialize glossary extractor."""
        self.definition_patterns = [
            r'\\textbf\{[^}]*definition[^}]*\}',
            r'\\textit\{[^}]*definition[^}]*\}',
            r'definition:',
            r'def\.',
            r'\\def\s+',
            r'is defined as',
            r'is the',
            r'means',
            r'refers to'
        ]
        
        self.term_patterns = [
            r'\\textbf\{([^}]+)\}',
            r'\\textit\{([^}]+)\}',
            r'\\emph\{([^}]+)\}',
            r'\\term\{([^}]+)\}'
        ]
        
        self.related_terms_patterns = [
            r'see also',
            r'related to',
            r'similar to',
            r'cf\.',
            r'compare with'
        ]
    
    def extract_glossary_terms(self, text: str, source_id: str) -> List[GlossaryContent]:
        """
        Extract glossary terms from text.
        
        Args:
            text: Text to extract glossary terms from
            source_id: Source document ID
            
        Returns:
            List of GlossaryContent objects
        """
        if not text:
            return []
        
        glossary_terms = []
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            if self._is_definition_sentence(sentence):
                term = self._extract_term(sentence)
                definition = self._extract_definition(sentence)
                context = self._extract_context(sentence)
                related_terms = self._extract_related_terms(sentence)
                
                if term and definition:
                    glossary_content = GlossaryContent(
                        term=term,
                        definition=definition,
                        context=context,
                        related_terms=related_terms
                    )
                    glossary_terms.append(glossary_content)
        
        return glossary_terms
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _is_definition_sentence(self, sentence: str) -> bool:
        """Check if sentence contains a definition."""
        sentence_lower = sentence.lower()
        
        for pattern in self.definition_patterns:
            if re.search(pattern, sentence_lower):
                return True
        
        return False
    
    def _extract_term(self, sentence: str) -> Optional[str]:
        """Extract term from definition sentence."""
        # Look for bold/italic terms
        for pattern in self.term_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Look for terms before definition indicators
        for pattern in self.definition_patterns:
            match = re.search(r'([^.!?]+?)\s+' + pattern, sentence, re.IGNORECASE)
            if match:
                term = match.group(1).strip()
                # Clean up the term
                term = re.sub(r'[^\w\s-]', '', term)
                if term:
                    return term
        
        return None
    
    def _extract_definition(self, sentence: str) -> Optional[str]:
        """Extract definition from sentence."""
        # Look for definition after indicators
        for pattern in self.definition_patterns:
            match = re.search(pattern + r'\s*([^.!?]+)', sentence, re.IGNORECASE)
            if match:
                definition = match.group(1).strip()
                # Clean up the definition
                definition = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', definition)
                definition = re.sub(r'[{}]', '', definition)
                if definition:
                    return definition
        
        return None
    
    def _extract_context(self, sentence: str) -> Optional[str]:
        """Extract context from sentence."""
        # Look for context indicators
        context_indicators = [
            r'in the context of',
            r'in the field of',
            r'in mathematics',
            r'in physics',
            r'in chemistry',
            r'in biology',
            r'in computer science'
        ]
        
        for indicator in context_indicators:
            match = re.search(indicator + r'\s*([^.!?]+)', sentence, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_related_terms(self, sentence: str) -> List[str]:
        """Extract related terms from sentence."""
        related_terms = []
        
        for pattern in self.related_terms_patterns:
            match = re.search(pattern + r'\s*([^.!?]+)', sentence, re.IGNORECASE)
            if match:
                terms_text = match.group(1).strip()
                # Split by common separators
                terms = re.split(r'[,;]', terms_text)
                for term in terms:
                    term = term.strip()
                    if term:
                        related_terms.append(term)
        
        return related_terms
    
    def extract_glossary_from_document(self, document_text: str, source_id: str) -> List[GlossaryContent]:
        """
        Extract glossary terms from entire document.
        
        Args:
            document_text: Full document text
            source_id: Source document ID
            
        Returns:
            List of GlossaryContent objects
        """
        if not document_text:
            return []
        
        # Split document into paragraphs
        paragraphs = document_text.split('\n\n')
        
        all_glossary_terms = []
        for paragraph in paragraphs:
            if paragraph.strip():
                terms = self.extract_glossary_terms(paragraph, source_id)
                all_glossary_terms.extend(terms)
        
        return all_glossary_terms
    
    def get_glossary_statistics(self, glossary_terms: List[GlossaryContent]) -> Dict[str, Any]:
        """
        Get statistics about glossary terms.
        
        Args:
            glossary_terms: List of GlossaryContent objects
            
        Returns:
            Dictionary containing glossary statistics
        """
        if not glossary_terms:
            return {}
        
        # Count terms with context
        terms_with_context = sum(1 for term in glossary_terms if term.context)
        
        # Count terms with related terms
        terms_with_related = sum(1 for term in glossary_terms if term.related_terms)
        
        # Calculate average definition length
        definition_lengths = [len(term.definition) for term in glossary_terms if term.definition]
        avg_definition_length = sum(definition_lengths) / len(definition_lengths) if definition_lengths else 0
        
        # Count related terms
        total_related_terms = sum(len(term.related_terms) for term in glossary_terms)
        
        return {
            'total_terms': len(glossary_terms),
            'terms_with_context': terms_with_context,
            'terms_with_related': terms_with_related,
            'context_rate': terms_with_context / len(glossary_terms) if glossary_terms else 0,
            'related_rate': terms_with_related / len(glossary_terms) if glossary_terms else 0,
            'average_definition_length': avg_definition_length,
            'total_related_terms': total_related_terms
        }
    
    def search_glossary_terms(self, glossary_terms: List[GlossaryContent], query: str) -> List[GlossaryContent]:
        """
        Search glossary terms by query.
        
        Args:
            glossary_terms: List of GlossaryContent objects
            query: Search query
            
        Returns:
            List of matching GlossaryContent objects
        """
        if not query or not glossary_terms:
            return []
        
        query_lower = query.lower()
        matching_terms = []
        
        for term in glossary_terms:
            # Search in term name
            if query_lower in term.term.lower():
                matching_terms.append(term)
                continue
            
            # Search in definition
            if term.definition and query_lower in term.definition.lower():
                matching_terms.append(term)
                continue
            
            # Search in context
            if term.context and query_lower in term.context.lower():
                matching_terms.append(term)
                continue
            
            # Search in related terms
            for related_term in term.related_terms:
                if query_lower in related_term.lower():
                    matching_terms.append(term)
                    break
        
        return matching_terms