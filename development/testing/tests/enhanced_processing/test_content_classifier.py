"""
Tests for ContentClassifier class.
"""

import pytest
import sys
from pathlib import Path

# Add the scirag module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scirag.enhanced_processing.content_classifier import ContentClassifier, ContentType


class TestContentClassifier:
    """Test cases for ContentClassifier."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = ContentClassifier()
    
    def test_classify_equation(self):
        """Test equation classification."""
        equation_text = "The equation $E = mc^2$ is famous."
        content_type, confidence = self.classifier.classify_content(equation_text)
        
        assert content_type == ContentType.EQUATION
        assert confidence > 0.3
    
    def test_classify_display_equation(self):
        """Test display equation classification."""
        equation_text = "$$\\frac{a}{b} = c$$"
        content_type, confidence = self.classifier.classify_content(equation_text)
        
        assert content_type == ContentType.EQUATION
        assert confidence > 0.5
    
    def test_classify_figure(self):
        """Test figure classification."""
        figure_text = "\\begin{figure}\\includegraphics{image.png}\\caption{A test figure}\\end{figure}"
        content_type, confidence = self.classifier.classify_content(figure_text)
        
        assert content_type == ContentType.FIGURE
        assert confidence > 0.5
    
    def test_classify_markdown_figure(self):
        """Test markdown figure classification."""
        figure_text = "![Test Image](image.png)"
        content_type, confidence = self.classifier.classify_content(figure_text)
        
        assert content_type == ContentType.FIGURE
        assert confidence > 0.3
    
    def test_classify_table(self):
        """Test table classification."""
        table_text = "\\begin{table}\\begin{tabular}{cc} A & B \\\\ C & D \\end{tabular}\\end{table}"
        content_type, confidence = self.classifier.classify_content(table_text)
        
        assert content_type == ContentType.TABLE
        assert confidence > 0.5
    
    def test_classify_markdown_table(self):
        """Test markdown table classification."""
        table_text = "| A | B |\n|---|---|\n| C | D |"
        content_type, confidence = self.classifier.classify_content(table_text)
        
        assert content_type == ContentType.TABLE
        assert confidence > 0.3
    
    def test_classify_glossary(self):
        """Test glossary classification."""
        glossary_text = "**Term**: This is a definition of the term."
        content_type, confidence = self.classifier.classify_content(glossary_text)
        
        assert content_type == ContentType.GLOSSARY
        assert confidence > 0.3
    
    def test_classify_latex_glossary(self):
        """Test LaTeX glossary classification."""
        glossary_text = "\\textbf{Term}: This is a definition of the term."
        content_type, confidence = self.classifier.classify_content(glossary_text)
        
        assert content_type == ContentType.GLOSSARY
        assert confidence > 0.5
    
    def test_classify_code(self):
        """Test code classification."""
        code_text = "```python\ndef hello():\n    print('Hello, World!')\n```"
        content_type, confidence = self.classifier.classify_content(code_text)
        
        assert content_type == ContentType.CODE
        assert confidence > 0.5
    
    def test_classify_inline_code(self):
        """Test inline code classification."""
        code_text = "Use the `print()` function to output text."
        content_type, confidence = self.classifier.classify_content(code_text)
        
        assert content_type == ContentType.CODE
        assert confidence > 0.3
    
    def test_classify_reference(self):
        """Test reference classification."""
        ref_text = "See \\cite{author2024} for more details."
        content_type, confidence = self.classifier.classify_content(ref_text)
        
        assert content_type == ContentType.REFERENCE
        assert confidence > 0.5
    
    def test_classify_markdown_reference(self):
        """Test markdown reference classification."""
        ref_text = "See [this paper](https://example.com) for more details."
        content_type, confidence = self.classifier.classify_content(ref_text)
        
        assert content_type == ContentType.REFERENCE
        assert confidence > 0.3
    
    def test_classify_prose(self):
        """Test prose classification."""
        prose_text = "This is a paragraph of regular text that describes something in detail."
        content_type, confidence = self.classifier.classify_content(prose_text)
        
        assert content_type == ContentType.PROSE
        assert confidence > 0.3
    
    def test_classify_with_metadata(self):
        """Test classification with metadata hints."""
        text = "Some text"
        metadata = {"content_type": "equation"}
        
        content_type, confidence = self.classifier.classify_content(text, metadata)
        
        # Should be influenced by metadata
        assert confidence > 0.3
    
    def test_classify_multiple(self):
        """Test classification of multiple texts."""
        texts = [
            "The equation $E = mc^2$ is famous.",
            "This is regular prose text.",
            "\\begin{figure}\\includegraphics{test.png}\\end{figure}"
        ]
        
        results = self.classifier.classify_multiple(texts)
        
        assert len(results) == 3
        assert results[0][0] == ContentType.EQUATION
        assert results[1][0] == ContentType.PROSE
        assert results[2][0] == ContentType.FIGURE
    
    def test_classification_summary(self):
        """Test classification summary generation."""
        classifications = [
            (ContentType.EQUATION, 0.8),
            (ContentType.PROSE, 0.6),
            (ContentType.EQUATION, 0.9),
            (ContentType.FIGURE, 0.7)
        ]
        
        summary = self.classifier.get_classification_summary(classifications)
        
        assert summary['total_chunks'] == 4
        assert summary['content_type_counts']['equation'] == 2
        assert summary['content_type_counts']['prose'] == 1
        assert summary['content_type_counts']['figure'] == 1
        assert summary['average_confidence'] > 0.5
    
    def test_equation_classification_detailed(self):
        """Test detailed equation classification."""
        # Test inline math
        inline_text = "$x + y = z$"
        content_type, confidence = self.classifier._classify_equation(inline_text, {})
        assert confidence > 0.3
        
        # Test display math
        display_text = "$$\\frac{a}{b} = c$$"
        content_type, confidence = self.classifier._classify_equation(display_text, {})
        assert confidence > 0.5
        
        # Test LaTeX equation
        latex_text = "\\begin{equation}E = mc^2\\end{equation}"
        content_type, confidence = self.classifier._classify_equation(latex_text, {})
        assert confidence > 0.7
    
    def test_figure_classification_detailed(self):
        """Test detailed figure classification."""
        # Test LaTeX figure
        latex_figure = "\\begin{figure}\\includegraphics{test.png}\\end{figure}"
        content_type, confidence = self.classifier._classify_figure(latex_figure, {})
        assert confidence > 0.7
        
        # Test markdown image
        markdown_image = "![Test](test.png)"
        content_type, confidence = self.classifier._classify_figure(markdown_image, {})
        assert confidence > 0.5
    
    def test_table_classification_detailed(self):
        """Test detailed table classification."""
        # Test LaTeX table
        latex_table = "\\begin{table}\\begin{tabular}{cc}A&B\\\\C&D\\end{tabular}\\end{table}"
        content_type, confidence = self.classifier._classify_table(latex_table, {})
        assert confidence > 0.7
        
        # Test markdown table
        markdown_table = "| A | B |\n|---|---|\n| C | D |"
        content_type, confidence = self.classifier._classify_table(markdown_table, {})
        assert confidence > 0.5
    
    def test_glossary_classification_detailed(self):
        """Test detailed glossary classification."""
        # Test bold term format
        bold_term = "**Term**: Definition"
        content_type, confidence = self.classifier._classify_glossary(bold_term, {})
        assert confidence > 0.5
        
        # Test colon format
        colon_format = "Term: Definition"
        content_type, confidence = self.classifier._classify_glossary(colon_format, {})
        assert confidence > 0.3
    
    def test_code_classification_detailed(self):
        """Test detailed code classification."""
        # Test code block
        code_block = "```python\ndef test():\n    pass\n```"
        content_type, confidence = self.classifier._classify_code(code_block, {})
        assert confidence > 0.7
        
        # Test inline code
        inline_code = "Use `print()` function"
        content_type, confidence = self.classifier._classify_code(inline_code, {})
        assert confidence > 0.3
    
    def test_reference_classification_detailed(self):
        """Test detailed reference classification."""
        # Test LaTeX citation
        latex_cite = "\\cite{author2024}"
        content_type, confidence = self.classifier._classify_reference(latex_cite, {})
        assert confidence > 0.7
        
        # Test markdown link
        markdown_link = "[Paper](https://example.com)"
        content_type, confidence = self.classifier._classify_reference(markdown_link, {})
        assert confidence > 0.3
    
    def test_prose_classification_detailed(self):
        """Test detailed prose classification."""
        # Test paragraph
        paragraph = "This is a complete sentence with proper structure and punctuation."
        content_type, confidence = self.classifier._classify_prose(paragraph, {})
        assert confidence > 0.3
        
        # Test section header
        section = "# This is a section header"
        content_type, confidence = self.classifier._classify_prose(section, {})
        assert confidence > 0.2


if __name__ == "__main__":
    pytest.main([__file__])
