import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from cv_agent.models.state import CVSection, AnalysisScore, Improvement, CVState


class TestCVSection:
    """Test the CVSection model."""

    def test_cv_section_creation(self):
        """Test creating a CVSection instance."""
        section = CVSection(
            name="experience",
            content="Software Engineer at Company",
            position=1,
            confidence=0.8
        )
        
        assert section.name == "experience"
        assert section.content == "Software Engineer at Company"
        assert section.position == 1
        assert section.confidence == 0.8

    def test_cv_section_validation(self):
        """Test CVSection validation."""
        # Test with valid data
        section = CVSection(
            name="skills",
            content="Python, JavaScript",
            position=0,
            confidence=0.9
        )
        assert section.confidence == 0.9

    def test_cv_section_default_confidence(self):
        """Test CVSection with default confidence."""
        section = CVSection(
            name="education",
            content="Computer Science Degree",
            position=2
        )
        assert section.confidence == 0.0  # Default value

    def test_cv_section_serialization(self):
        """Test CVSection serialization."""
        section = CVSection(
            name="summary",
            content="Experienced developer",
            position=0,
            confidence=0.85
        )
        
        # Test model_dump (Pydantic v2)
        data = section.model_dump()
        assert isinstance(data, dict)
        assert data["name"] == "summary"
        assert data["content"] == "Experienced developer"
        assert data["position"] == 0
        assert data["confidence"] == 0.85


class TestAnalysisScore:
    """Test the AnalysisScore model."""

    def test_analysis_score_creation(self):
        """Test creating an AnalysisScore instance."""
        section_scores = {"experience": 0.8, "skills": 0.7}
        
        score = AnalysisScore(
            overall_score=0.75,
            section_scores=section_scores,
            ats_compatibility=0.8,
            keyword_density=0.6,
            formatting_score=0.9,
            content_quality=0.75
        )
        
        assert score.overall_score == 0.75
        assert score.section_scores == section_scores
        assert score.ats_compatibility == 0.8
        assert score.keyword_density == 0.6
        assert score.formatting_score == 0.9
        assert score.content_quality == 0.75

    def test_analysis_score_types(self):
        """Test AnalysisScore type validation."""
        score = AnalysisScore(
            overall_score=0.75,
            section_scores={"test": 0.5},
            ats_compatibility=0.8,
            keyword_density=0.6,
            formatting_score=0.9,
            content_quality=0.75
        )
        
        assert isinstance(score.overall_score, float)
        assert isinstance(score.section_scores, dict)
        assert isinstance(score.ats_compatibility, float)
        assert isinstance(score.keyword_density, float)
        assert isinstance(score.formatting_score, float)
        assert isinstance(score.content_quality, float)

    def test_analysis_score_serialization(self):
        """Test AnalysisScore serialization."""
        score = AnalysisScore(
            overall_score=0.75,
            section_scores={"experience": 0.8},
            ats_compatibility=0.8,
            keyword_density=0.6,
            formatting_score=0.9,
            content_quality=0.75
        )
        
        data = score.model_dump()
        assert isinstance(data, dict)
        assert data["overall_score"] == 0.75
        assert data["section_scores"]["experience"] == 0.8


class TestImprovement:
    """Test the Improvement model."""

    def test_improvement_creation(self):
        """Test creating an Improvement instance."""
        improvement = Improvement(
            section="experience",
            type="content",
            original_text="Worked at company",
            improved_text="Led development team at innovative tech company",
            reasoning="Added specific role and company description",
            priority="high",
            confidence=0.9
        )
        
        assert improvement.section == "experience"
        assert improvement.type == "content"
        assert improvement.original_text == "Worked at company"
        assert improvement.improved_text == "Led development team at innovative tech company"
        assert improvement.reasoning == "Added specific role and company description"
        assert improvement.priority == "high"
        assert improvement.confidence == 0.9

    def test_improvement_types(self):
        """Test different improvement types."""
        content_improvement = Improvement(
            section="skills",
            type="content",
            original_text="Python",
            improved_text="Python, Django, Flask",
            reasoning="Added specific frameworks",
            priority="medium",
            confidence=0.8
        )
        
        format_improvement = Improvement(
            section="experience",
            type="format",
            original_text="Developer 2020-2022",
            improved_text="• Software Developer (2020-2022)",
            reasoning="Added bullet point formatting",
            priority="low",
            confidence=0.7
        )
        
        assert content_improvement.type == "content"
        assert format_improvement.type == "format"

    def test_improvement_priorities(self):
        """Test improvement priority levels."""
        high_priority = Improvement(
            section="summary",
            type="content",
            original_text="Developer",
            improved_text="Senior Software Developer",
            reasoning="Added seniority level",
            priority="high",
            confidence=0.9
        )
        
        medium_priority = Improvement(
            section="skills",
            type="keyword",
            original_text="Programming",
            improved_text="Python Programming",
            reasoning="Added specific language",
            priority="medium",
            confidence=0.7
        )
        
        low_priority = Improvement(
            section="education",
            type="structure",
            original_text="CS Degree",
            improved_text="Bachelor of Computer Science",
            reasoning="Full degree name",
            priority="low",
            confidence=0.6
        )
        
        assert high_priority.priority == "high"
        assert medium_priority.priority == "medium"
        assert low_priority.priority == "low"

    def test_improvement_serialization(self):
        """Test Improvement serialization."""
        improvement = Improvement(
            section="experience",
            type="content",
            original_text="Developer",
            improved_text="Senior Developer",
            reasoning="Added seniority",
            priority="high",
            confidence=0.9
        )
        
        data = improvement.model_dump()
        assert isinstance(data, dict)
        assert data["section"] == "experience"
        assert data["type"] == "content"
        assert data["priority"] == "high"


class TestCVState:
    """Test the CVState TypedDict."""

    def test_cv_state_creation(self):
        """Test creating a CVState instance."""
        state = CVState(
            original_cv="John Doe CV content",
            file_format="txt",
            target_role="Software Engineer",
            target_industry="technology",
            parsed_sections={},
            raw_text="John Doe CV content",
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
        
        assert state["original_cv"] == "John Doe CV content"
        assert state["file_format"] == "txt"
        assert state["target_role"] == "Software Engineer"
        assert state["target_industry"] == "technology"
        assert isinstance(state["parsed_sections"], dict)
        assert isinstance(state["identified_gaps"], list)
        assert isinstance(state["suggested_improvements"], list)
        assert isinstance(state["applied_improvements"], list)
        assert isinstance(state["processing_errors"], list)

    def test_cv_state_with_sections(self):
        """Test CVState with parsed sections."""
        section = CVSection(
            name="experience",
            content="Software Engineer",
            position=0,
            confidence=0.9
        )
        
        state = CVState(
            original_cv="CV content",
            file_format="txt",
            target_role=None,
            target_industry=None,
            parsed_sections={"experience": section},
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
        
        assert "experience" in state["parsed_sections"]
        assert state["parsed_sections"]["experience"] == section

    def test_cv_state_with_analysis_scores(self):
        """Test CVState with analysis scores."""
        analysis = AnalysisScore(
            overall_score=0.8,
            section_scores={"experience": 0.9},
            ats_compatibility=0.7,
            keyword_density=0.6,
            formatting_score=0.8,
            content_quality=0.85
        )
        
        state = CVState(
            original_cv="CV content",
            file_format="txt",
            target_role=None,
            target_industry=None,
            parsed_sections={},
            raw_text="CV content",
            analysis_scores=analysis,
            identified_gaps=[],
            suggested_improvements=[],
            applied_improvements=[],
            enhanced_cv=None,
            enhancement_summary=None,
            processing_errors=[],
            processing_time=None,
            model_used=None
        )
        
        assert state["analysis_scores"] == analysis
        assert state["analysis_scores"].overall_score == 0.8

    def test_cv_state_with_improvements(self):
        """Test CVState with improvements."""
        improvement = Improvement(
            section="skills",
            type="content",
            original_text="Python",
            improved_text="Python, Django, FastAPI",
            reasoning="Added frameworks",
            priority="medium",
            confidence=0.8
        )
        
        state = CVState(
            original_cv="CV content",
            file_format="txt",
            target_role=None,
            target_industry=None,
            parsed_sections={},
            raw_text="CV content",
            analysis_scores=None,
            identified_gaps=["Missing contact info"],
            suggested_improvements=[improvement],
            applied_improvements=[],
            enhanced_cv=None,
            enhancement_summary=None,
            processing_errors=[],
            processing_time=1.5,
            model_used="gpt-4o"
        )
        
        assert len(state["suggested_improvements"]) == 1
        assert state["suggested_improvements"][0] == improvement
        assert state["identified_gaps"] == ["Missing contact info"]
        assert state["processing_time"] == 1.5

    def test_cv_state_optional_fields(self):
        """Test CVState with optional fields."""
        state = CVState(
            original_cv="CV content",
            file_format="txt",
            target_role=None,  # Optional
            target_industry=None,  # Optional
            parsed_sections={},
            raw_text="CV content",
            analysis_scores=None,  # Optional
            identified_gaps=[],
            suggested_improvements=[],
            applied_improvements=[],
            enhanced_cv=None,  # Optional
            enhancement_summary=None,  # Optional
            processing_errors=[],
            processing_time=None,  # Optional
            model_used=None  # Optional
        )
        
        assert state["target_role"] is None
        assert state["target_industry"] is None
        assert state["analysis_scores"] is None
        assert state["enhanced_cv"] is None
        assert state["enhancement_summary"] is None
        assert state["processing_time"] is None
        assert state["model_used"] is None

    def test_cv_state_complete_workflow(self):
        """Test CVState representing a complete workflow."""
        # Initial state
        state = CVState(
            original_cv="John Doe CV",
            file_format="txt",
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
        
        # Simulate workflow progression
        state["raw_text"] = "John Doe CV"
        state["parsed_sections"] = {
            "summary": CVSection(name="summary", content="Developer", position=0, confidence=0.8)
        }
        state["analysis_scores"] = AnalysisScore(
            overall_score=0.7,
            section_scores={"summary": 0.8},
            ats_compatibility=0.6,
            keyword_density=0.7,
            formatting_score=0.8,
            content_quality=0.75
        )
        state["identified_gaps"] = ["Missing experience section"]
        state["suggested_improvements"] = [
            Improvement(
                section="summary",
                type="content",
                original_text="Developer",
                improved_text="Senior Software Developer",
                reasoning="Added seniority",
                priority="high",
                confidence=0.9
            )
        ]
        state["processing_time"] = 2.3
        
        # Verify complete state
        assert state["original_cv"] == "John Doe CV"
        assert state["raw_text"] == "John Doe CV"
        assert len(state["parsed_sections"]) == 1
        assert state["analysis_scores"].overall_score == 0.7
        assert len(state["identified_gaps"]) == 1
        assert len(state["suggested_improvements"]) == 1
        assert state["processing_time"] == 2.3


if __name__ == "__main__":
    pytest.main([__file__])