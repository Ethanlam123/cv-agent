"""
Integration tests for the main application.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cv_agent.workflow import CVImprovementAgent


class TestMainIntegration:
    """Integration tests for main application functionality."""

    @patch('cv_agent.workflow.create_cv_improvement_workflow')
    def test_full_cv_processing_flow(self, mock_create_workflow, sample_cv_text):
        """Test the complete CV processing flow."""
        # Mock the workflow
        mock_workflow = MagicMock()
        mock_app = MagicMock()
        mock_workflow.compile.return_value = mock_app
        mock_create_workflow.return_value = mock_workflow
        
        # Mock a complete processing result
        mock_result = {
            "original_cv": sample_cv_text,
            "file_format": "txt",
            "raw_text": sample_cv_text,
            "parsed_sections": {
                "summary": {
                    "name": "summary",
                    "content": "Experienced software developer",
                    "position": 0,
                    "confidence": 0.9
                },
                "experience": {
                    "name": "experience", 
                    "content": "Senior Software Developer at Tech Company",
                    "position": 1,
                    "confidence": 0.95
                }
            },
            "analysis_scores": {
                "overall_score": 0.78,
                "section_scores": {"summary": 0.8, "experience": 0.9},
                "ats_compatibility": 0.75,
                "keyword_density": 0.8,
                "formatting_score": 0.7,
                "content_quality": 0.85
            },
            "identified_gaps": [
                "Missing contact information",
                "Skills section could be expanded"
            ],
            "suggested_improvements": [
                {
                    "section": "summary",
                    "type": "content",
                    "original_text": "Developer",
                    "improved_text": "Senior Software Developer", 
                    "reasoning": "Added seniority level",
                    "priority": "high",
                    "confidence": 0.9
                }
            ],
            "applied_improvements": [],
            "enhanced_cv": None,
            "enhancement_summary": None,
            "processing_errors": [],
            "processing_time": 2.1,
            "model_used": "gpt-4o",
            "final_quality_score": 0.82,
            "processing_complete": True
        }
        
        mock_app.invoke.return_value = mock_result
        
        # Test the agent
        agent = CVImprovementAgent()
        result = agent.process_cv(
            cv_input=sample_cv_text,
            target_role="Software Engineer",
            target_industry="technology"
        )
        
        # Verify the workflow was called correctly
        mock_app.invoke.assert_called_once()
        call_args = mock_app.invoke.call_args[0][0]
        
        assert call_args["original_cv"] == sample_cv_text
        assert call_args["target_role"] == "Software Engineer"
        assert call_args["target_industry"] == "technology"
        assert call_args["model_used"] == "gpt-4o"
        
        # Verify the result
        assert result == mock_result
        assert result["processing_complete"] is True
        assert result["final_quality_score"] == 0.82

    @patch('cv_agent.workflow.create_cv_improvement_workflow')
    def test_improvement_summary_generation(self, mock_create_workflow):
        """Test improvement summary generation."""
        mock_workflow = MagicMock()
        mock_app = MagicMock()
        mock_workflow.compile.return_value = mock_app
        mock_create_workflow.return_value = mock_workflow
        
        agent = CVImprovementAgent()
        
        # Test with comprehensive results
        result = {
            "analysis_scores": {
                "overall_score": 0.725
            },
            "identified_gaps": [
                "Experience section lacks duration information",
                "Skills section appears limited - consider adding more relevant skills",
                "Consider adding keywords relevant to Software Engineer: algorithms, debugging, testing"
            ],
            "applied_improvements": [
                {"section": "experience", "type": "content"},
                {"section": "skills", "type": "keyword"}
            ],
            "enhancement_summary": "CV has been enhanced with specific technical skills and quantified achievements",
            "processing_errors": []
        }
        
        summary = agent.get_improvement_summary(result)
        
        expected_parts = [
            "Overall CV Score: 72.5%",
            "Identified 3 improvement areas:",
            "Experience section lacks duration information",
            "Applied 2 high-priority improvements",
            "CV has been enhanced with specific technical skills and quantified achievements"
        ]
        
        for part in expected_parts:
            assert part in summary

    @patch('cv_agent.workflow.create_cv_improvement_workflow')
    def test_error_handling_in_processing(self, mock_create_workflow):
        """Test error handling during CV processing."""
        mock_workflow = MagicMock()
        mock_app = MagicMock()
        mock_workflow.compile.return_value = mock_app
        mock_create_workflow.return_value = mock_workflow
        
        # Mock an error result
        error_result = {
            "original_cv": "Invalid CV",
            "file_format": "unknown",
            "raw_text": "",
            "parsed_sections": {},
            "analysis_scores": None,
            "identified_gaps": [],
            "suggested_improvements": [],
            "applied_improvements": [],
            "enhanced_cv": None,
            "enhancement_summary": None,
            "processing_errors": ["Error parsing document: Invalid format"],
            "processing_time": 0.5,
            "model_used": "gpt-4o",
            "processing_complete": False
        }
        
        mock_app.invoke.return_value = error_result
        
        agent = CVImprovementAgent()
        result = agent.process_cv(cv_input="Invalid CV")
        
        assert result["processing_complete"] is False
        assert len(result["processing_errors"]) == 1
        assert "Invalid format" in result["processing_errors"][0]
        
        # Test summary with errors
        summary = agent.get_improvement_summary(result)
        assert "Processing Issues: 1" in summary

    @patch('cv_agent.workflow.create_cv_improvement_workflow')
    def test_cv_processing_with_different_formats(self, mock_create_workflow, temp_text_file):
        """Test CV processing with different file formats."""
        mock_workflow = MagicMock()
        mock_app = MagicMock()
        mock_workflow.compile.return_value = mock_app
        mock_create_workflow.return_value = mock_workflow
        
        # Mock result for file processing
        mock_result = {
            "original_cv": temp_text_file,
            "file_format": "txt",
            "raw_text": "File content",
            "parsed_sections": {},
            "processing_errors": [],
            "processing_complete": True
        }
        
        mock_app.invoke.return_value = mock_result
        
        agent = CVImprovementAgent()
        result = agent.process_cv(cv_input=temp_text_file)
        
        # Verify file path was passed correctly
        call_args = mock_app.invoke.call_args[0][0]
        assert call_args["original_cv"] == temp_text_file
        
        assert result["file_format"] == "txt"
        assert result["processing_complete"] is True

    @pytest.mark.slow
    @patch('cv_agent.workflow.create_cv_improvement_workflow')
    def test_performance_with_large_cv(self, mock_create_workflow):
        """Test performance with large CV content."""
        mock_workflow = MagicMock()
        mock_app = MagicMock()
        mock_workflow.compile.return_value = mock_app
        mock_create_workflow.return_value = mock_workflow
        
        # Create large CV content
        large_cv = "Large CV content. " * 1000  # Simulate large document
        
        mock_result = {
            "original_cv": large_cv,
            "processing_time": 5.2,  # Simulated longer processing time
            "processing_complete": True,
            "processing_errors": []
        }
        
        mock_app.invoke.return_value = mock_result
        
        agent = CVImprovementAgent()
        result = agent.process_cv(cv_input=large_cv)
        
        assert result["processing_complete"] is True
        assert result["processing_time"] > 0
        assert len(result["processing_errors"]) == 0

    def test_agent_initialization_robustness(self):
        """Test that agent initialization is robust."""
        # Test multiple initializations
        agents = []
        for i in range(3):
            with patch('cv_agent.workflow.create_cv_improvement_workflow') as mock_create:
                mock_workflow = MagicMock()
                mock_workflow.compile.return_value = MagicMock()
                mock_create.return_value = mock_workflow
                
                agent = CVImprovementAgent()
                agents.append(agent)
                
                assert hasattr(agent, 'workflow')
                assert hasattr(agent, 'app')
        
        # Verify all agents are independent
        assert len(agents) == 3
        assert all(agent.workflow is not None for agent in agents)


if __name__ == "__main__":
    pytest.main([__file__])