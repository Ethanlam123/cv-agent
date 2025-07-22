import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from cv_agent.tools.analyzers import CVAnalyzer
from cv_agent.models.state import CVSection, AnalysisScore


class TestCVAnalyzer:
    """Test the CVAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CVAnalyzer()
        
        # Sample CV sections for testing
        self.sample_sections = {
            'summary': CVSection(
                name='summary',
                content='Experienced software developer with 5+ years of experience in web applications.',
                position=0,
                confidence=0.9
            ),
            'experience': CVSection(
                name='experience',
                content='''Senior Software Developer at Tech Company (2021-Present)
                - Developed scalable web applications using Python and React
                - Led a team of 3 developers on microservices architecture
                - Improved system performance by 40% through optimization''',
                position=1,
                confidence=0.95
            ),
            'skills': CVSection(
                name='skills',
                content='Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, PostgreSQL',
                position=2,
                confidence=0.85
            ),
            'education': CVSection(
                name='education',
                content='Bachelor of Computer Science, University of Technology (2019)',
                position=3,
                confidence=0.8
            )
        }

    def test_analyzer_initialization(self):
        """Test CVAnalyzer initialization."""
        analyzer = CVAnalyzer()
        assert hasattr(analyzer, 'industry_keywords')
        assert hasattr(analyzer, 'ats_patterns')
        assert 'technology' in analyzer.industry_keywords
        assert 'marketing' in analyzer.industry_keywords
        assert 'finance' in analyzer.industry_keywords

    def test_analyze_content_quality(self):
        """Test content quality analysis."""
        scores = self.analyzer.analyze_content_quality(self.sample_sections)
        
        assert isinstance(scores, dict)
        assert len(scores) == len(self.sample_sections)
        
        for section_name, score in scores.items():
            assert 0 <= score <= 1
            assert isinstance(score, float)
        
        # Experience section should have reasonable score due to action verbs and quantified achievements
        assert scores['experience'] > 0.3

    def test_analyze_content_quality_summary_section(self):
        """Test content quality analysis for summary section specifically."""
        summary_section = {
            'summary': CVSection(
                name='summary',
                content='Achieved 95% customer satisfaction. Developed innovative solutions. Managed team of 10+.',
                position=0,
                confidence=0.9
            )
        }
        
        scores = self.analyzer.analyze_content_quality(summary_section)
        assert scores['summary'] > 0.3  # Should score reasonably due to action verbs and numbers

    def test_analyze_content_quality_empty_content(self):
        """Test content quality analysis with empty content."""
        empty_section = {
            'empty': CVSection(
                name='empty',
                content='',
                position=0,
                confidence=0.5
            )
        }
        
        scores = self.analyzer.analyze_content_quality(empty_section)
        assert scores['empty'] == 0.0

    def test_check_ats_compatibility(self):
        """Test ATS compatibility checking."""
        sample_cv = '''
John Doe
Email: john.doe@example.com
Phone: (555) 123-4567

SUMMARY
Experienced developer from 2019-2023

EXPERIENCE
• Software Engineer at Company (Jan 2021 - Present)
- Developed applications
• Junior Developer at StartupCorp (2019-2021)
- Built web applications

EDUCATION
Bachelor's Degree (2019)

SKILLS
Python, JavaScript, React
'''
        
        score = self.analyzer.check_ats_compatibility(sample_cv)
        
        assert 0 <= score <= 1
        assert isinstance(score, float)
        # Should score well due to email, phone, dates, and bullet points
        assert score > 0.5

    def test_check_ats_compatibility_missing_elements(self):
        """Test ATS compatibility with missing elements."""
        poor_cv = "Just some text without proper formatting"
        
        score = self.analyzer.check_ats_compatibility(poor_cv)
        assert score < 0.3  # Should score poorly

    def test_calculate_keyword_density_technology(self):
        """Test keyword density calculation for technology industry."""
        tech_content = "Python developer with experience in AWS, Docker, and Kubernetes. Built APIs and microservices."
        
        density = self.analyzer.calculate_keyword_density(tech_content, "technology")
        
        assert 0 <= density <= 1
        assert density > 0.1  # Should find some tech keywords

    def test_calculate_keyword_density_no_industry(self):
        """Test keyword density calculation with no industry specified."""
        content = "Generic content"
        
        density = self.analyzer.calculate_keyword_density(content, None)
        assert density == 0.5  # Default score

    def test_calculate_keyword_density_unknown_industry(self):
        """Test keyword density calculation with unknown industry."""
        content = "Some content"
        
        density = self.analyzer.calculate_keyword_density(content, "unknown_industry")
        assert density == 0.5  # Default score

    def test_analyze_formatting(self):
        """Test formatting analysis."""
        well_formatted_cv = '''John Doe
Engineer

SUMMARY
Experienced developer

EXPERIENCE
Software Engineer
- Built applications
- Led projects

EDUCATION
Computer Science Degree

SKILLS
Python, JavaScript
'''
        
        score = self.analyzer.analyze_formatting(well_formatted_cv)
        
        assert 0 <= score <= 1
        assert score > 0.4  # Should score reasonably well

    def test_analyze_formatting_poor_format(self):
        """Test formatting analysis with poor formatting."""
        poor_cv = "john doe engineer python javascript"  # Very minimal
        
        score = self.analyzer.analyze_formatting(poor_cv)
        assert score < 0.5  # Should score poorly

    def test_identify_gaps(self):
        """Test gap identification."""
        gaps = self.analyzer.identify_gaps(self.sample_sections)
        
        assert isinstance(gaps, list)
        # Should suggest adding contact section
        contact_gap = any("contact" in gap.lower() for gap in gaps)
        assert contact_gap

    def test_identify_gaps_missing_essential_sections(self):
        """Test gap identification with missing essential sections."""
        incomplete_sections = {
            'summary': self.sample_sections['summary']
            # Missing experience, skills, education
        }
        
        gaps = self.analyzer.identify_gaps(incomplete_sections)
        
        assert len(gaps) > 0
        essential_gaps = [gap for gap in gaps if "Missing essential section" in gap]
        assert len(essential_gaps) >= 2  # Should identify missing experience, skills, education

    def test_identify_gaps_insufficient_content(self):
        """Test gap identification with insufficient content."""
        weak_sections = {
            'experience': CVSection(
                name='experience',
                content='Developer',  # Very short content
                position=0,
                confidence=0.5
            ),
            'skills': CVSection(
                name='skills',
                content='Python',  # Limited skills
                position=1,
                confidence=0.5
            ),
            'education': CVSection(
                name='education',
                content='Computer Science',
                position=2,
                confidence=0.5
            )
        }
        
        gaps = self.analyzer.identify_gaps(weak_sections)
        
        insufficient_gaps = [gap for gap in gaps if "Insufficient content" in gap]
        skills_gaps = [gap for gap in gaps if "Skills section appears limited" in gap]
        
        assert len(insufficient_gaps) > 0 or len(skills_gaps) > 0

    def test_generate_analysis_score(self):
        """Test comprehensive analysis score generation."""
        sample_cv_text = '''John Doe
john.doe@example.com
(555) 123-4567

SUMMARY
Experienced software developer with 5+ years

EXPERIENCE
• Senior Developer (2021-Present)
- Developed applications
- Improved performance by 40%

SKILLS
Python, JavaScript, AWS, Docker

EDUCATION
Computer Science (2019)
'''
        
        analysis = self.analyzer.generate_analysis_score(
            self.sample_sections, 
            sample_cv_text, 
            "technology"
        )
        
        assert isinstance(analysis, AnalysisScore)
        assert 0 <= analysis.overall_score <= 1
        assert 0 <= analysis.ats_compatibility <= 1
        assert 0 <= analysis.keyword_density <= 1
        assert 0 <= analysis.formatting_score <= 1
        assert 0 <= analysis.content_quality <= 1
        assert isinstance(analysis.section_scores, dict)
        
        # Check that scores are properly rounded
        assert len(str(analysis.overall_score).split('.')[-1]) <= 3

    def test_generate_analysis_score_empty_sections(self):
        """Test analysis score generation with empty sections."""
        empty_sections = {}
        empty_cv = ""
        
        analysis = self.analyzer.generate_analysis_score(empty_sections, empty_cv)
        
        assert isinstance(analysis, AnalysisScore)
        assert analysis.overall_score >= 0
        assert analysis.content_quality == 0  # No sections

    def test_industry_keywords_coverage(self):
        """Test that industry keywords are comprehensive."""
        # Technology keywords
        tech_keywords = self.analyzer.industry_keywords['technology']
        assert 'python' in tech_keywords
        assert 'javascript' in tech_keywords
        assert 'aws' in tech_keywords
        assert 'docker' in tech_keywords
        
        # Marketing keywords
        marketing_keywords = self.analyzer.industry_keywords['marketing']
        assert 'seo' in marketing_keywords
        assert 'social media' in marketing_keywords
        
        # Finance keywords
        finance_keywords = self.analyzer.industry_keywords['finance']
        assert 'financial analysis' in finance_keywords
        assert 'budgeting' in finance_keywords

    def test_ats_patterns_validity(self):
        """Test that ATS patterns are valid regex patterns."""
        import re
        
        for pattern_name, pattern in self.analyzer.ats_patterns.items():
            try:
                re.compile(pattern)
            except re.error:
                pytest.fail(f"Invalid regex pattern for {pattern_name}: {pattern}")

    def test_action_verbs_detection(self):
        """Test that action verbs are properly detected in content quality analysis."""
        action_heavy_section = {
            'experience': CVSection(
                name='experience',
                content='Achieved goals. Developed software. Managed teams. Led projects. Created solutions. Implemented features.',
                position=0,
                confidence=0.9
            )
        }
        
        scores = self.analyzer.analyze_content_quality(action_heavy_section)
        assert scores['experience'] > 0.3  # Should score reasonably due to many action verbs

    def test_quantified_achievements_detection(self):
        """Test that quantified achievements are properly detected."""
        quantified_section = {
            'experience': CVSection(
                name='experience',
                content='Increased revenue by 25%. Managed $2M budget. Led team of 15+ developers. Improved performance by 3x.',
                position=0,
                confidence=0.9
            )
        }
        
        scores = self.analyzer.analyze_content_quality(quantified_section)
        assert scores['experience'] > 0.5  # Should score well due to quantified achievements


if __name__ == "__main__":
    pytest.main([__file__])