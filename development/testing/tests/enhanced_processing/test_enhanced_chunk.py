"""
Tests for EnhancedChunk data structure.
"""

import pytest
import sys
import json
from pathlib import Path

# Add the scirag module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scirag.enhanced_processing.enhanced_chunk import (
    EnhancedChunk, 
    ContentType, 
    MathematicalContent, 
    AssetContent, 
    GlossaryContent
)


class TestEnhancedChunk:
    """Test cases for EnhancedChunk."""
    
    def test_basic_chunk_creation(self):
        """Test basic chunk creation."""
        chunk = EnhancedChunk(
            id="test_1",
            text="This is a test chunk",
            source_id="test_source",
            chunk_index=0
        )
        
        assert chunk.id == "test_1"
        assert chunk.text == "This is a test chunk"
        assert chunk.source_id == "test_source"
        assert chunk.chunk_index == 0
        assert chunk.content_type == ContentType.PROSE
        assert chunk.confidence == 1.0
    
    def test_chunk_with_math_content(self):
        """Test chunk with mathematical content."""
        math_content = MathematicalContent(
            equation_tex="E = mc^2",
            math_norm="E=mc^2",
            math_tokens=["E", "=", "m", "c", "^", "2"],
            math_kgrams=["E = m", "= m c", "m c ^", "c ^ 2"],
            equation_type="inline",
            variables=["E", "m", "c"],
            operators=["=", "^"]
        )
        
        chunk = EnhancedChunk(
            id="math_1",
            text="The famous equation $E = mc^2$",
            source_id="physics_paper",
            chunk_index=1,
            content_type=ContentType.EQUATION,
            math_content=math_content
        )
        
        assert chunk.content_type == ContentType.EQUATION
        assert chunk.math_content is not None
        assert chunk.math_content.equation_tex == "E = mc^2"
        assert chunk.math_content.variables == ["E", "m", "c"]
    
    def test_chunk_with_asset_content(self):
        """Test chunk with asset content."""
        asset_content = AssetContent(
            asset_type="figure",
            asset_id="fig1",
            caption="A test figure",
            label="Figure 1",
            file_path="figures/test.png",
            dimensions={"width": 800, "height": 600}
        )
        
        chunk = EnhancedChunk(
            id="asset_1",
            text="\\begin{figure}\\includegraphics{test.png}\\caption{A test figure}\\end{figure}",
            source_id="paper",
            chunk_index=2,
            content_type=ContentType.FIGURE,
            asset_content=asset_content
        )
        
        assert chunk.content_type == ContentType.FIGURE
        assert chunk.asset_content is not None
        assert chunk.asset_content.asset_type == "figure"
        assert chunk.asset_content.caption == "A test figure"
    
    def test_chunk_with_glossary_content(self):
        """Test chunk with glossary content."""
        glossary_content = GlossaryContent(
            term="Dark Matter",
            definition="A form of matter that does not emit, absorb, or reflect light",
            context="In cosmology, dark matter is believed to make up about 27% of the universe",
            related_terms=["Dark Energy", "Baryonic Matter"],
            confidence=0.95
        )
        
        chunk = EnhancedChunk(
            id="glossary_1",
            text="**Dark Matter**: A form of matter that does not emit, absorb, or reflect light",
            source_id="cosmology_textbook",
            chunk_index=3,
            content_type=ContentType.GLOSSARY,
            glossary_content=glossary_content
        )
        
        assert chunk.content_type == ContentType.GLOSSARY
        assert chunk.glossary_content is not None
        assert chunk.glossary_content.term == "Dark Matter"
        assert chunk.glossary_content.confidence == 0.95
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        math_content = MathematicalContent(
            equation_tex="x + y = z",
            math_norm="x+y=z",
            math_tokens=["x", "+", "y", "=", "z"]
        )
        
        chunk = EnhancedChunk(
            id="test_1",
            text="Test equation: $x + y = z$",
            source_id="test",
            chunk_index=0,
            content_type=ContentType.EQUATION,
            math_content=math_content,
            confidence=0.8
        )
        
        chunk_dict = chunk.to_dict()
        
        assert chunk_dict['id'] == "test_1"
        assert chunk_dict['text'] == "Test equation: $x + y = z$"
        assert chunk_dict['content_type'] == "equation"
        assert chunk_dict['confidence'] == 0.8
        assert chunk_dict['math_content'] is not None
        assert chunk_dict['math_content']['equation_tex'] == "x + y = z"
    
    def test_from_dict_conversion(self):
        """Test creation from dictionary."""
        chunk_dict = {
            'id': 'test_1',
            'text': 'Test equation: $x + y = z$',
            'source_id': 'test',
            'chunk_index': 0,
            'content_type': 'equation',
            'confidence': 0.8,
            'math_content': {
                'equation_tex': 'x + y = z',
                'math_norm': 'x+y=z',
                'math_tokens': ['x', '+', 'y', '=', 'z'],
                'math_kgrams': [],
                'math_canonical': None,
                'equation_type': None,
                'variables': [],
                'operators': []
            },
            'asset_content': None,
            'glossary_content': None,
            'processing_version': '1.0',
            'processing_metadata': {},
            'embedding': None,
            'retrieval_score': None,
            'retrieval_rank': None
        }
        
        chunk = EnhancedChunk.from_dict(chunk_dict)
        
        assert chunk.id == "test_1"
        assert chunk.text == "Test equation: $x + y = z$"
        assert chunk.content_type == ContentType.EQUATION
        assert chunk.confidence == 0.8
        assert chunk.math_content is not None
        assert chunk.math_content.equation_tex == "x + y = z"
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        math_content = MathematicalContent(
            equation_tex="E = mc^2",
            math_norm="E=mc^2",
            math_tokens=["E", "=", "m", "c", "^", "2"]
        )
        
        chunk = EnhancedChunk(
            id="json_test",
            text="Einstein's equation: $E = mc^2$",
            source_id="physics",
            chunk_index=0,
            content_type=ContentType.EQUATION,
            math_content=math_content
        )
        
        # Test to JSON
        json_str = chunk.to_json()
        assert isinstance(json_str, str)
        
        # Test from JSON
        chunk_from_json = EnhancedChunk.from_json(json_str)
        assert chunk_from_json.id == chunk.id
        assert chunk_from_json.text == chunk.text
        assert chunk_from_json.content_type == chunk.content_type
        assert chunk_from_json.math_content.equation_tex == chunk.math_content.equation_tex
    
    def test_get_retrieval_text(self):
        """Test retrieval text generation."""
        # Test equation chunk
        math_content = MathematicalContent(
            equation_tex="E = mc^2",
            math_norm="E=mc^2"
        )
        
        equation_chunk = EnhancedChunk(
            id="eq_1",
            text="The equation $E = mc^2$",
            source_id="physics",
            chunk_index=0,
            content_type=ContentType.EQUATION,
            math_content=math_content
        )
        
        retrieval_text = equation_chunk.get_retrieval_text()
        assert retrieval_text == "E=mc^2"  # Should use normalized form
        
        # Test glossary chunk
        glossary_content = GlossaryContent(
            term="Dark Matter",
            definition="A form of matter that does not emit light"
        )
        
        glossary_chunk = EnhancedChunk(
            id="gloss_1",
            text="**Dark Matter**: A form of matter that does not emit light",
            source_id="cosmology",
            chunk_index=0,
            content_type=ContentType.GLOSSARY,
            glossary_content=glossary_content
        )
        
        retrieval_text = glossary_chunk.get_retrieval_text()
        assert "Dark Matter" in retrieval_text
        assert "A form of matter" in retrieval_text
        
        # Test prose chunk
        prose_chunk = EnhancedChunk(
            id="prose_1",
            text="This is regular prose text",
            source_id="general",
            chunk_index=0,
            content_type=ContentType.PROSE
        )
        
        retrieval_text = prose_chunk.get_retrieval_text()
        assert retrieval_text == "This is regular prose text"  # Should use original text
    
    def test_get_metadata_summary(self):
        """Test metadata summary generation."""
        math_content = MathematicalContent(
            equation_tex="x + y = z",
            math_tokens=["x", "+", "y", "=", "z"],
            equation_type="inline"
        )
        
        asset_content = AssetContent(
            asset_type="figure",
            caption="Test figure"
        )
        
        glossary_content = GlossaryContent(
            term="Test Term",
            confidence=0.9
        )
        
        chunk = EnhancedChunk(
            id="summary_test",
            text="Test chunk with all content types",
            source_id="test",
            chunk_index=0,
            content_type=ContentType.MIXED,
            math_content=math_content,
            asset_content=asset_content,
            glossary_content=glossary_content,
            confidence=0.8
        )
        
        summary = chunk.get_metadata_summary()
        
        assert summary['content_type'] == 'mixed'
        assert summary['confidence'] == 0.8
        assert summary['has_math'] == True
        assert summary['has_asset'] == True
        assert summary['has_glossary'] == True
        assert summary['text_length'] == len("Test chunk with all content types")
        assert summary['math_tokens_count'] == 5
        assert summary['equation_type'] == 'inline'
        assert summary['asset_type'] == 'figure'
        assert summary['has_caption'] == True
        assert summary['glossary_term'] == 'Test Term'
        assert summary['glossary_confidence'] == 0.9
    
    def test_mathematical_content_creation(self):
        """Test MathematicalContent creation."""
        math_content = MathematicalContent(
            equation_tex="\\frac{a}{b} = c",
            math_norm="a/b=c",
            math_tokens=["a", "/", "b", "=", "c"],
            math_kgrams=["a / b", "/ b =", "b = c"],
            math_canonical="a/b = c",
            equation_type="display",
            variables=["a", "b", "c"],
            operators=["/", "="]
        )
        
        assert math_content.equation_tex == "\\frac{a}{b} = c"
        assert math_content.math_norm == "a/b=c"
        assert math_content.variables == ["a", "b", "c"]
        assert math_content.operators == ["/", "="]
    
    def test_asset_content_creation(self):
        """Test AssetContent creation."""
        asset_content = AssetContent(
            asset_type="table",
            asset_id="tab1",
            caption="Test table",
            label="Table 1",
            file_path="tables/test.csv",
            dimensions={"rows": 10, "cols": 5},
            ocr_text="Extracted text from image"
        )
        
        assert asset_content.asset_type == "table"
        assert asset_content.asset_id == "tab1"
        assert asset_content.caption == "Test table"
        assert asset_content.dimensions["rows"] == 10
    
    def test_glossary_content_creation(self):
        """Test GlossaryContent creation."""
        glossary_content = GlossaryContent(
            term="Cosmology",
            definition="The study of the universe",
            context="In physics, cosmology is a branch of astronomy",
            related_terms=["Astronomy", "Physics", "Universe"],
            confidence=0.95
        )
        
        assert glossary_content.term == "Cosmology"
        assert glossary_content.definition == "The study of the universe"
        assert glossary_content.related_terms == ["Astronomy", "Physics", "Universe"]
        assert glossary_content.confidence == 0.95


if __name__ == "__main__":
    pytest.main([__file__])
