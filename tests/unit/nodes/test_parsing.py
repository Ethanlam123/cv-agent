import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from cv_agent.nodes.parsing import parse_cv_node
from cv_agent.models.state import CVState


class TestParsingNode:
    """Test the parse_cv_node function."""

    def test_parse_cv_node_with_text_content(self):
        """Test parsing CV node with raw text content."""
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
        
        initial_state = CVState(
            original_cv=sample_text,
            file_format="unknown",
            target_role="Software Engineer",
            target_industry="technology",
            parsed_sections={},
            raw_text="",
            analysis_scores=None,
            identified_gaps=[],
            suggested_improvements=[],
            applied_improvements=[],
            enhanced_cv=None,
            enhancement_summary=None,
            processing_errors=[],
            processing_time=None,
            model_used="gpt-4o"
        )
        
        result = parse_cv_node(initial_state)
        
        # Check basic results
        assert result["raw_text"] == sample_text
        assert result["file_format"] == "txt"
        assert isinstance(result["parsed_sections"], dict)
        assert len(result["parsed_sections"]) > 0
        assert result["processing_errors"] == []
        assert isinstance(result["processing_time"], float)
        assert result["processing_time"] >= 0

    def test_parse_cv_node_with_file_path(self):
        """Test parsing CV node with file path."""
        sample_content = "John Doe\nSoftware Engineer"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_content)
            temp_path = f.name

        try:
            initial_state = CVState(
                original_cv=temp_path,
                file_format="unknown",
                target_role=None,
                target_industry=None,
                parsed_sections={},
                raw_text="",
                analysis_scores=None,
                identified_gaps=[],
                suggested_improvements=[],
                applied_improvements=[],
                enhanced_cv=None,
                enhancement_summary=None,
                processing_errors=[],
                processing_time=None,
                model_used="gpt-4o"
            )
            
            result = parse_cv_node(initial_state)
            
            assert result["raw_text"] == sample_content
            assert result["file_format"] == "txt"
            assert isinstance(result["parsed_sections"], dict)
            assert result["processing_errors"] == []
        finally:
            os.unlink(temp_path)

    @patch('cv_agent.nodes.parsing.ParserFactory.create_parser')
    def test_parse_cv_node_with_docling_fallback(self, mock_create_parser):
        """Test parsing with Docling enabled and fallback behavior."""
        sample_content = "CV content"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            temp_path = f.name

        try:
            # Mock parser that works
            mock_parser = MagicMock()
            mock_parser.parse.return_value = sample_content
            mock_parser.extract_sections.return_value = {}
            mock_create_parser.return_value = mock_parser

            initial_state = CVState(
                original_cv=temp_path,
                file_format="unknown",
                target_role=None,
                target_industry=None,
                parsed_sections={},
                raw_text="",
                analysis_scores=None,
                identified_gaps=[],
                suggested_improvements=[],
                applied_improvements=[],
                enhanced_cv=None,
                enhancement_summary=None,
                processing_errors=[],
                processing_time=None,
                model_used="gpt-4o"
            )
            
            result = parse_cv_node(initial_state)
            
            # Should be called with use_docling=True and use_llm=True by default
            mock_create_parser.assert_called_with(temp_path, use_docling=True, use_llm=True)
            assert result["raw_text"] == sample_content
            assert result["file_format"] == "pdf"
            assert result["processing_errors"] == []
        finally:
            os.unlink(temp_path)

    @patch('cv_agent.nodes.parsing.ParserFactory.create_parser')
    def test_parse_cv_node_docling_import_error(self, mock_create_parser):
        """Test parsing when Docling import fails."""
        sample_content = "CV content"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            temp_path = f.name

        try:
            # First call raises ImportError, second call succeeds
            mock_parser = MagicMock()
            mock_parser.parse.return_value = sample_content
            mock_parser.extract_sections.return_value = {}
            
            mock_create_parser.side_effect = [ImportError("Docling not available"), mock_parser]

            initial_state = CVState(
                original_cv=temp_path,
                file_format="unknown",
                target_role=None,
                target_industry=None,
                parsed_sections={},
                raw_text="",
                analysis_scores=None,
                identified_gaps=[],
                suggested_improvements=[],
                applied_improvements=[],
                enhanced_cv=None,
                enhancement_summary=None,
                processing_errors=[],
                processing_time=None,
                model_used="gpt-4o"
            )
            
            result = parse_cv_node(initial_state)
            
            # Should be called twice: first with use_docling=True, then with use_docling=False
            assert mock_create_parser.call_count == 2
            assert result["raw_text"] == sample_content
            assert result["processing_errors"] == []
        finally:
            os.unlink(temp_path)

    @patch('cv_agent.nodes.parsing.ParserFactory.create_parser')
    def test_parse_cv_node_with_error(self, mock_create_parser):
        """Test parsing when an error occurs."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            # Mock parser that raises an error
            mock_create_parser.side_effect = Exception("Parsing failed")

            initial_state = CVState(
                original_cv=temp_path,
                file_format="unknown",
                target_role=None,
                target_industry=None,
                parsed_sections={},
                raw_text="",
                analysis_scores=None,
                identified_gaps=[],
                suggested_improvements=[],
                applied_improvements=[],
                enhanced_cv=None,
                enhancement_summary=None,
                processing_errors=[],
                processing_time=None,
                model_used="gpt-4o"
            )
            
            result = parse_cv_node(initial_state)
            
            assert result["raw_text"] == ""
            assert result["file_format"] == "unknown"
            assert result["parsed_sections"] == {}
            assert len(result["processing_errors"]) == 1
            assert "Parsing failed" in result["processing_errors"][0]
        finally:
            os.unlink(temp_path)

    @patch('cv_agent.nodes.parsing.ParserFactory.create_parser')
    def test_parse_cv_node_docling_error_with_fallback(self, mock_create_parser):
        """Test parsing when Docling fails and fallback succeeds."""
        sample_content = "CV content"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            temp_path = f.name

        try:
            # First parser raises docling error, second succeeds
            mock_parser_fallback = MagicMock()
            mock_parser_fallback.parse.return_value = sample_content
            mock_parser_fallback.extract_sections.return_value = {}
            
            mock_create_parser.side_effect = [
                Exception("docling conversion failed"),  # First call fails
                mock_parser_fallback  # Second call succeeds
            ]

            initial_state = CVState(
                original_cv=temp_path,
                file_format="unknown",
                target_role=None,
                target_industry=None,
                parsed_sections={},
                raw_text="",
                analysis_scores=None,
                identified_gaps=[],
                suggested_improvements=[],
                applied_improvements=[],
                enhanced_cv=None,
                enhancement_summary=None,
                processing_errors=[],
                processing_time=None,
                model_used="gpt-4o"
            )
            
            result = parse_cv_node(initial_state)
            
            # Should try fallback parsing
            assert mock_create_parser.call_count == 2
            assert result["raw_text"] == sample_content
            assert result["file_format"] == "pdf"
            assert len(result["processing_errors"]) == 1
            assert "Docling failed, used fallback parser" in result["processing_errors"][0]
        finally:
            os.unlink(temp_path)

    @patch('cv_agent.nodes.parsing.ParserFactory.create_parser')
    def test_parse_cv_node_both_docling_and_fallback_fail(self, mock_create_parser):
        """Test parsing when both Docling and fallback fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            temp_path = f.name

        try:
            # Both calls fail
            mock_create_parser.side_effect = [
                Exception("docling conversion failed"),  # First call fails
                Exception("fallback parsing failed")  # Second call also fails
            ]

            initial_state = CVState(
                original_cv=temp_path,
                file_format="unknown",
                target_role=None,
                target_industry=None,
                parsed_sections={},
                raw_text="",
                analysis_scores=None,
                identified_gaps=[],
                suggested_improvements=[],
                applied_improvements=[],
                enhanced_cv=None,
                enhancement_summary=None,
                processing_errors=[],
                processing_time=None,
                model_used="gpt-4o"
            )
            
            result = parse_cv_node(initial_state)
            
            assert result["raw_text"] == ""
            assert result["file_format"] == "unknown"
            assert result["parsed_sections"] == {}
            assert len(result["processing_errors"]) == 1
            assert "Both Docling and fallback parsing failed" in result["processing_errors"][0]
        finally:
            os.unlink(temp_path)

    def test_parse_cv_node_preserves_state(self):
        """Test that parsing node preserves original state fields."""
        sample_text = "John Doe\nSoftware Engineer"
        
        initial_state = CVState(
            original_cv=sample_text,
            file_format="unknown",
            target_role="Software Engineer",
            target_industry="technology",
            parsed_sections={},
            raw_text="",
            analysis_scores=None,
            identified_gaps=["existing gap"],
            suggested_improvements=[],
            applied_improvements=[],
            enhanced_cv=None,
            enhancement_summary=None,
            processing_errors=[],
            processing_time=None,
            model_used="gpt-4o"
        )
        
        result = parse_cv_node(initial_state)
        
        # Check that original state fields are preserved
        assert result["original_cv"] == sample_text
        assert result["target_role"] == "Software Engineer"
        assert result["target_industry"] == "technology"
        assert result["identified_gaps"] == ["existing gap"]
        assert result["model_used"] == "gpt-4o"


if __name__ == "__main__":
    pytest.main([__file__])