import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from cv_agent.tools.parsers import (
    DocumentParser,
    TextParser,
    PDFParser,
    DocxParser,
    DoclingParser,
    ParserFactory
)
from cv_agent.models.state import CVSection


class TestDocumentParser:
    """Test the base DocumentParser class."""

    def test_parse_not_implemented(self):
        """Test that parse method raises NotImplementedError."""
        parser = DocumentParser()
        with pytest.raises(NotImplementedError):
            parser.parse("dummy.txt")

    def test_extract_sections_basic(self):
        """Test basic section extraction functionality."""
        parser = DocumentParser()
        sample_text = """
John Doe
Email: john@example.com

SUMMARY
Experienced developer

EXPERIENCE
Software Engineer at Company
- Worked on projects

SKILLS
Python, JavaScript
"""
        sections = parser.extract_sections(sample_text)
        
        assert isinstance(sections, dict)
        assert len(sections) > 0
        
        # Check that sections contain CVSection objects
        for section_name, section in sections.items():
            assert isinstance(section, CVSection)
            assert section.name == section_name
            assert isinstance(section.content, str)
            assert isinstance(section.position, int)
            assert isinstance(section.confidence, float)


class TestTextParser:
    """Test the TextParser class."""

    def test_parse_text_file(self):
        """Test parsing a text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content\nSecond line")
            temp_path = f.name

        try:
            parser = TextParser()
            result = parser.parse(temp_path)
            assert result == "Test content\nSecond line"
        finally:
            os.unlink(temp_path)

    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file raises ValueError."""
        parser = TextParser()
        with pytest.raises(ValueError, match="Error parsing text file"):
            parser.parse("nonexistent.txt")

    def test_extract_sections_with_cv_content(self):
        """Test section extraction with CV-like content."""
        parser = TextParser()
        
        # Load sample CV content
        fixture_path = Path(__file__).parent.parent.parent / "fixtures" / "sample_cv.txt"
        with open(fixture_path, 'r') as f:
            cv_content = f.read()
        
        sections = parser.extract_sections(cv_content)
        
        # Check that common CV sections are detected
        expected_sections = ['summary', 'experience', 'education', 'skills']
        for section_name in expected_sections:
            assert section_name in sections
            assert len(sections[section_name].content) > 0
            assert sections[section_name].confidence > 0


class TestPDFParser:
    """Test the PDFParser class."""

    @patch('cv_agent.tools.parsers.PyPDF2.PdfReader')
    def test_parse_pdf_success(self, mock_pdf_reader):
        """Test successful PDF parsing."""
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF content"
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name

        try:
            parser = PDFParser()
            result = parser.parse(temp_path)
            assert result == "PDF content"
        finally:
            os.unlink(temp_path)

    def test_parse_pdf_error(self):
        """Test PDF parsing with error."""
        parser = PDFParser()
        with pytest.raises(ValueError, match="Error parsing PDF"):
            parser.parse("nonexistent.pdf")


class TestDocxParser:
    """Test the DocxParser class."""

    @patch('cv_agent.tools.parsers.Document')
    def test_parse_docx_success(self, mock_document):
        """Test successful DOCX parsing."""
        # Mock Document
        mock_paragraph = MagicMock()
        mock_paragraph.text = "DOCX content"
        mock_doc_instance = MagicMock()
        mock_doc_instance.paragraphs = [mock_paragraph]
        mock_document.return_value = mock_doc_instance

        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            temp_path = f.name

        try:
            parser = DocxParser()
            result = parser.parse(temp_path)
            assert result == "DOCX content"
        finally:
            os.unlink(temp_path)

    def test_parse_docx_error(self):
        """Test DOCX parsing with error."""
        parser = DocxParser()
        with pytest.raises(ValueError, match="Error parsing DOCX"):
            parser.parse("nonexistent.docx")


class TestDoclingParser:
    """Test the DoclingParser class."""

    @patch('cv_agent.tools.parsers.DocumentConverter')
    def test_init_docling_parser(self, mock_converter):
        """Test DoclingParser initialization."""
        parser = DoclingParser()
        assert hasattr(parser, 'converter')
        mock_converter.assert_called_once()

    @patch('cv_agent.tools.parsers.DocumentConverter')
    def test_parse_docling_success(self, mock_converter):
        """Test successful Docling parsing."""
        # Mock converter and result
        mock_document = MagicMock()
        mock_document.export_to_markdown.return_value = "# Markdown content"
        mock_result = MagicMock()
        mock_result.document = mock_document
        mock_converter_instance = MagicMock()
        mock_converter_instance.convert.return_value = mock_result
        mock_converter.return_value = mock_converter_instance

        parser = DoclingParser()
        result = parser.parse("test.pdf")
        assert result == "# Markdown content"

    @patch('cv_agent.tools.parsers.DocumentConverter')
    def test_parse_docling_error(self, mock_converter):
        """Test Docling parsing with error."""
        mock_converter_instance = MagicMock()
        mock_converter_instance.convert.side_effect = Exception("Docling error")
        mock_converter.return_value = mock_converter_instance

        parser = DoclingParser()
        with pytest.raises(ValueError, match="Error parsing document with Docling"):
            parser.parse("test.pdf")

    def test_extract_sections_markdown(self):
        """Test section extraction with markdown content."""
        parser = DoclingParser()
        
        # Load sample markdown CV content
        fixture_path = Path(__file__).parent.parent.parent / "fixtures" / "sample_cv_markdown.md"
        with open(fixture_path, 'r') as f:
            markdown_content = f.read()
        
        sections = parser.extract_sections(markdown_content)
        
        # Check that markdown sections are detected
        expected_sections = ['contact', 'summary', 'experience', 'education', 'skills']
        for section_name in expected_sections:
            assert section_name in sections
            assert len(sections[section_name].content) > 0
            # Docling parser should have higher confidence
            assert sections[section_name].confidence >= 0.9


class TestParserFactory:
    """Test the ParserFactory class."""

    def test_create_text_parser(self):
        """Test creating a text parser."""
        parser = ParserFactory.create_parser("test.txt", use_docling=False)
        assert isinstance(parser, TextParser)

    def test_create_pdf_parser_traditional(self):
        """Test creating a traditional PDF parser."""
        parser = ParserFactory.create_parser("test.pdf", use_docling=False)
        assert isinstance(parser, PDFParser)

    def test_create_docx_parser_traditional(self):
        """Test creating a traditional DOCX parser."""
        parser = ParserFactory.create_parser("test.docx", use_docling=False)
        assert isinstance(parser, DocxParser)

    @patch('cv_agent.tools.parsers.DoclingParser')
    def test_create_docling_parser_pdf(self, mock_docling):
        """Test creating a Docling parser for PDF."""
        mock_docling.return_value = MagicMock()
        parser = ParserFactory.create_parser("test.pdf", use_docling=True)
        mock_docling.assert_called_once()

    @patch('cv_agent.tools.parsers.DoclingParser')
    def test_create_docling_parser_docx(self, mock_docling):
        """Test creating a Docling parser for DOCX."""
        mock_docling.return_value = MagicMock()
        parser = ParserFactory.create_parser("test.docx", use_docling=True)
        mock_docling.assert_called_once()

    def test_create_parser_unsupported_format(self):
        """Test creating parser for unsupported format."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            ParserFactory.create_parser("test.xyz")

    def test_create_parser_default_docling(self):
        """Test that Docling is used by default for supported formats."""
        with patch('cv_agent.tools.parsers.DoclingParser') as mock_docling:
            mock_docling.return_value = MagicMock()
            parser = ParserFactory.create_parser("test.pdf")  # use_docling defaults to True
            mock_docling.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])