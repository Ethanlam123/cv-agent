import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from cv_agent.workflow import CVImprovementAgent, create_cv_improvement_workflow, should_apply_improvements, quality_check_node
from cv_agent.models.state import CVState, CVSection, AnalysisScore, Improvement


class TestWorkflowFunctions:
    """Test individual workflow functions."""

    def test_should_apply_improvements_with_high_priority(self):
        """Test should_apply_improvements with high priority improvements."""
        state = CVState(
            original_cv="CV content",
            file_format="txt",
            target_role=None,
            target_industry=None,
            parsed_sections={},
            raw_text="CV content",
            analysis_scores=None,
            identified_gaps=[],
            suggested_improvements=[
                Improvement(
                    section="experience",
                    type="content",
                    original_text="Developer",
                    improved_text="Senior Developer",
                    reasoning="Added seniority",
                    priority="high",
                    confidence=0.8
                )
            ],
            applied_improvements=[],
            enhanced_cv=None,
            enhancement_summary=None,
            processing_errors=[],
            processing_time=None,
            model_used=None
        )
        
        result = should_apply_improvements(state)
        assert result == "apply_improvements"

    def test_should_apply_improvements_no_high_priority(self):
        """Test should_apply_improvements without high priority improvements."""
        state = CVState(
            original_cv="CV content",
            file_format="txt",
            target_role=None,
            target_industry=None,
            parsed_sections={},
            raw_text="CV content",
            analysis_scores=None,
            identified_gaps=[],
            suggested_improvements=[
                Improvement(
                    section="skills",
                    type="content",
                    original_text="Python",
                    improved_text="Python, Django",
                    reasoning="Added framework",
                    priority="medium",
                    confidence=0.7
                )
            ],
            applied_improvements=[],
            enhanced_cv=None,
            enhancement_summary=None,
            processing_errors=[],
            processing_time=None,
            model_used=None
        )
        
        result = should_apply_improvements(state)
        assert result == "quality_check"

    def test_should_apply_improvements_low_confidence(self):
        """Test should_apply_improvements with high priority but low confidence."""
        state = CVState(
            original_cv="CV content",
            file_format="txt",
            target_role=None,
            target_industry=None,
            parsed_sections={},
            raw_text="CV content",
            analysis_scores=None,
            identified_gaps=[],
            suggested_improvements=[
                Improvement(
                    section="experience",
                    type="content",
                    original_text="Developer",
                    improved_text="Senior Developer",
                    reasoning="Added seniority",
                    priority="high",
                    confidence=0.5  # Low confidence
                )
            ],
            applied_improvements=[],
            enhanced_cv=None,
            enhancement_summary=None,
            processing_errors=[],
            processing_time=None,
            model_used=None
        )
        
        result = should_apply_improvements(state)
        assert result == "quality_check"

    def test_should_apply_improvements_empty_list(self):
        """Test should_apply_improvements with empty improvements list."""
        state = CVState(
            original_cv="CV content",
            file_format="txt",
            target_role=None,
            target_industry=None,
            parsed_sections={},
            raw_text="CV content",
            analysis_scores=None,
            identified_gaps=[],
            suggested_improvements=[],  # Empty list
            applied_improvements=[],
            enhanced_cv=None,
            enhancement_summary=None,
            processing_errors=[],
            processing_time=None,
            model_used=None
        )
        
        result = should_apply_improvements(state)
        assert result == "quality_check"

    def test_quality_check_node_with_enhancements(self):
        """Test quality_check_node with enhanced CV and applied improvements."""
        state = CVState(
            original_cv="CV content",
            file_format="txt",
            target_role=None,
            target_industry=None,
            parsed_sections={},
            raw_text="CV content",
            analysis_scores=None,
            identified_gaps=[],
            suggested_improvements=[],
            applied_improvements=[
                Improvement(
                    section="skills",
                    type="content",
                    original_text="Python",
                    improved_text="Python, Django",
                    reasoning="Added framework",
                    priority="medium",
                    confidence=0.8
                )
            ],
            enhanced_cv="Enhanced CV content",
            enhancement_summary=None,
            processing_errors=[],
            processing_time=None,
            model_used=None
        )
        
        result = quality_check_node(state)
        
        assert result["final_quality_score"] == 0.85
        assert result["processing_complete"] is True
        assert "enhanced_cv" in result
        assert "applied_improvements" in result

    def test_quality_check_node_without_enhancements(self):
        """Test quality_check_node without enhancements."""
        state = CVState(
            original_cv="CV content",
            file_format="txt",
            target_role=None,
            target_industry=None,
            parsed_sections={},
            raw_text="CV content",
            analysis_scores=None,
            identified_gaps=[],
            suggested_improvements=[],
            applied_improvements=[],
            enhanced_cv=None,
            enhancement_summary=None,
            processing_errors=[],
            processing_time=None,
            model_used=None
        )
        
        result = quality_check_node(state)
        
        assert result["final_quality_score"] == 0.70
        assert result["processing_complete"] is True


class TestWorkflowCreation:
    """Test workflow creation and structure."""

    def test_create_cv_improvement_workflow(self):
        """Test creating the CV improvement workflow."""
        workflow = create_cv_improvement_workflow()
        
        # Check that workflow is created
        assert workflow is not None
        
        # Check that nodes are added (this is implementation-dependent)
        # We can't easily test the internal structure without accessing private methods

    @patch('cv_agent.workflow.create_cv_improvement_workflow')
    def test_workflow_compilation(self, mock_create_workflow):
        """Test that workflow can be compiled."""
        mock_workflow = MagicMock()
        mock_workflow.compile.return_value = MagicMock()
        mock_create_workflow.return_value = mock_workflow
        
        agent = CVImprovementAgent()
        
        # Check that workflow was created and compiled
        mock_create_workflow.assert_called_once()
        mock_workflow.compile.assert_called_once()


class TestCVImprovementAgent:
    """Test the CVImprovementAgent class."""

    @patch('cv_agent.workflow.create_cv_improvement_workflow')
    def test_agent_initialization(self, mock_create_workflow):
        """Test CVImprovementAgent initialization."""
        mock_workflow = MagicMock()
        mock_app = MagicMock()
        mock_workflow.compile.return_value = mock_app
        mock_create_workflow.return_value = mock_workflow
        
        agent = CVImprovementAgent()
        
        assert hasattr(agent, 'workflow')
        assert hasattr(agent, 'app')
        assert agent.app == mock_app

    @patch('cv_agent.workflow.create_cv_improvement_workflow')
    def test_process_cv_with_text_input(self, mock_create_workflow):
        """Test processing CV with text input."""
        # Mock workflow and app
        mock_workflow = MagicMock()
        mock_app = MagicMock()
        mock_workflow.compile.return_value = mock_app
        mock_create_workflow.return_value = mock_workflow
        
        # Mock app.invoke result
        expected_result = {
            "original_cv": "John Doe CV",
            "file_format": "txt",
            "raw_text": "John Doe CV",
            "parsed_sections": {},
            "analysis_scores": None,
            "processing_complete": True
        }
        mock_app.invoke.return_value = expected_result
        
        agent = CVImprovementAgent()
        result = agent.process_cv(
            cv_input="John Doe CV",
            target_role="Software Engineer",
            target_industry="technology"
        )
        
        # Check that app.invoke was called with correct initial state
        mock_app.invoke.assert_called_once()
        call_args = mock_app.invoke.call_args[0][0]
        
        assert call_args["original_cv"] == "John Doe CV"
        assert call_args["target_role"] == "Software Engineer"
        assert call_args["target_industry"] == "technology"
        assert call_args["file_format"] == "unknown"
        assert call_args["model_used"] == "gpt-4o"
        
        assert result == expected_result

    @patch('cv_agent.workflow.create_cv_improvement_workflow')
    def test_process_cv_with_optional_parameters(self, mock_create_workflow):
        """Test processing CV with optional parameters."""
        mock_workflow = MagicMock()
        mock_app = MagicMock()
        mock_workflow.compile.return_value = mock_app
        mock_create_workflow.return_value = mock_workflow
        
        mock_app.invoke.return_value = {"result": "success"}
        
        agent = CVImprovementAgent()
        result = agent.process_cv(cv_input="CV content")  # No target_role or target_industry
        
        call_args = mock_app.invoke.call_args[0][0]
        assert call_args["target_role"] is None
        assert call_args["target_industry"] is None

    def test_get_improvement_summary_with_complete_results(self):
        """Test getting improvement summary with complete results."""
        agent = CVImprovementAgent()
        
        result = {
            "analysis_scores": {
                "overall_score": 0.75
            },
            "identified_gaps": [
                "Missing contact information",
                "Skills section needs expansion",
                "Experience lacks quantified achievements"
            ],
            "applied_improvements": [
                {"section": "experience", "type": "content"},
                {"section": "skills", "type": "keyword"}
            ],
            "enhancement_summary": "CV has been improved with better formatting and content",
            "processing_errors": []
        }
        
        summary = agent.get_improvement_summary(result)
        
        assert "Overall CV Score: 75.0%" in summary
        assert "Identified 3 improvement areas:" in summary
        assert "Missing contact information" in summary
        assert "Applied 2 high-priority improvements" in summary
        assert "CV has been improved with better formatting and content" in summary

    def test_get_improvement_summary_with_partial_results(self):
        """Test getting improvement summary with partial results."""
        agent = CVImprovementAgent()
        
        result = {
            "analysis_scores": {
                "overall_score": 0.60
            },
            "identified_gaps": ["Missing summary section"],
            "processing_errors": ["Parser warning: Low confidence in section detection"]
        }
        
        summary = agent.get_improvement_summary(result)
        
        assert "Overall CV Score: 60.0%" in summary
        assert "Identified 1 improvement areas:" in summary
        assert "Missing summary section" in summary
        assert "Processing Issues: 1" in summary

    def test_get_improvement_summary_with_empty_results(self):
        """Test getting improvement summary with empty results."""
        agent = CVImprovementAgent()
        
        result = {}
        
        summary = agent.get_improvement_summary(result)
        
        assert summary == "CV analysis completed successfully."

    def test_get_improvement_summary_shows_top_gaps_only(self):
        """Test that improvement summary shows only top 3 gaps."""
        agent = CVImprovementAgent()
        
        result = {
            "identified_gaps": [
                "Gap 1",
                "Gap 2", 
                "Gap 3",
                "Gap 4",
                "Gap 5"
            ]
        }
        
        summary = agent.get_improvement_summary(result)
        
        assert "Gap 1" in summary
        assert "Gap 2" in summary
        assert "Gap 3" in summary
        assert "Gap 4" not in summary
        assert "Gap 5" not in summary


class TestWorkflowIntegration:
    """Test full workflow integration scenarios."""

    @patch('cv_agent.workflow.parse_cv_node')
    @patch('cv_agent.workflow.analyze_quality_node')
    @patch('cv_agent.workflow.match_requirements_node')
    @patch('cv_agent.workflow.generate_improvements_node')
    @patch('cv_agent.workflow.apply_improvements_node')
    def test_workflow_execution_mock(self, mock_apply, mock_generate, mock_match, mock_analyze, mock_parse):
        """Test workflow execution with mocked nodes."""
        # This is a simplified test since we can't easily test LangGraph execution
        # In a real scenario, you'd want integration tests with a test LangGraph setup
        
        # Mock each node to return expected state updates
        mock_parse.return_value = {"raw_text": "parsed", "parsed_sections": {}}
        mock_analyze.return_value = {"analysis_scores": {"overall_score": 0.7}}
        mock_match.return_value = {"identified_gaps": ["gap1"]}
        mock_generate.return_value = {"suggested_improvements": []}
        mock_apply.return_value = {"applied_improvements": []}
        
        # Test that we can create the workflow (actual execution would require more setup)
        workflow = create_cv_improvement_workflow()
        assert workflow is not None

    def test_state_flow_simulation(self):
        """Test simulated state flow through workflow steps."""
        # Simulate the state as it would flow through the workflow
        
        # Initial state
        initial_state = CVState(
            original_cv="John Doe CV content",
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
        
        # After parsing
        post_parse_state = initial_state.copy()
        post_parse_state.update({
            "raw_text": "John Doe CV content",
            "file_format": "txt",
            "parsed_sections": {
                "summary": CVSection(name="summary", content="Developer", position=0, confidence=0.8)
            }
        })
        
        # After analysis
        post_analysis_state = post_parse_state.copy()
        post_analysis_state.update({
            "analysis_scores": AnalysisScore(
                overall_score=0.7,
                section_scores={"summary": 0.8},
                ats_compatibility=0.6,
                keyword_density=0.7,
                formatting_score=0.8,
                content_quality=0.75
            )
        })
        
        # After improvements
        post_improvements_state = post_analysis_state.copy()
        post_improvements_state.update({
            "suggested_improvements": [
                Improvement(
                    section="summary",
                    type="content",
                    original_text="Developer",
                    improved_text="Senior Software Developer",
                    reasoning="Added seniority level",
                    priority="high",
                    confidence=0.9
                )
            ]
        })
        
        # Verify state progression
        assert initial_state["raw_text"] == ""
        assert post_parse_state["raw_text"] == "John Doe CV content"
        assert post_analysis_state["analysis_scores"] is not None
        assert len(post_improvements_state["suggested_improvements"]) == 1


if __name__ == "__main__":
    pytest.main([__file__])