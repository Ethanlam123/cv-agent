"""
Test configuration and fixtures for CV Agent tests.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cv_agent.models.state import CVSection, AnalysisScore, Improvement, CVState


@pytest.fixture
def sample_cv_text():
    """Sample CV text content for testing."""
    return """John Doe
Email: john.doe@example.com
Phone: (555) 123-4567

SUMMARY
Experienced software developer with 5+ years of experience in web applications and backend systems.

EXPERIENCE
Senior Software Developer at Tech Company
2021 - Present
- Developed scalable web applications using Python and React
- Led a team of 3 developers on microservices architecture
- Improved system performance by 40% through optimization

Software Developer at StartupCorp
2019 - 2021
- Built REST APIs using Django and PostgreSQL
- Implemented CI/CD pipelines using Jenkins
- Collaborated with cross-functional teams

EDUCATION
Bachelor's Degree in Computer Science
University of Technology, 2019
GPA: 3.8/4.0

SKILLS
Programming Languages: Python, JavaScript, Java, Go
Frameworks: Django, React, Node.js, FastAPI
Databases: PostgreSQL, MongoDB, Redis
Cloud: AWS, Docker, Kubernetes

PROJECTS
E-commerce Platform
- Built full-stack web application with payment integration
- Used microservices architecture with Docker containers

CERTIFICATIONS
AWS Certified Developer Associate
Certified Kubernetes Administrator (CKA)

LANGUAGES
English: Native
Spanish: Conversational"""


@pytest.fixture
def sample_cv_markdown():
    """Sample CV markdown content for testing."""
    return """# John Doe

## Contact Information
Email: john.doe@example.com
Phone: (555) 123-4567

## Summary
Experienced software developer with 5+ years of experience in web applications and backend systems.

## Experience

### Senior Software Developer at Tech Company
**2021 - Present**
- Developed scalable web applications using Python and React
- Led a team of 3 developers on microservices architecture
- Improved system performance by 40% through optimization

### Software Developer at StartupCorp
**2019 - 2021**
- Built REST APIs using Django and PostgreSQL
- Implemented CI/CD pipelines using Jenkins
- Collaborated with cross-functional teams

## Education
**Bachelor's Degree in Computer Science**
University of Technology, 2019
GPA: 3.8/4.0

## Skills
**Programming Languages:** Python, JavaScript, Java, Go
**Frameworks:** Django, React, Node.js, FastAPI
**Databases:** PostgreSQL, MongoDB, Redis
**Cloud:** AWS, Docker, Kubernetes

## Projects

### E-commerce Platform
- Built full-stack web application with payment integration
- Used microservices architecture with Docker containers

## Certifications
- AWS Certified Developer Associate
- Certified Kubernetes Administrator (CKA)

## Languages
- **English:** Native
- **Spanish:** Conversational"""


@pytest.fixture
def sample_cv_sections():
    """Sample CV sections for testing."""
    return {
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


@pytest.fixture
def sample_analysis_score():
    """Sample analysis score for testing."""
    return AnalysisScore(
        overall_score=0.75,
        section_scores={
            'summary': 0.8,
            'experience': 0.9,
            'skills': 0.7,
            'education': 0.6
        },
        ats_compatibility=0.8,
        keyword_density=0.7,
        formatting_score=0.75,
        content_quality=0.8
    )


@pytest.fixture
def sample_improvements():
    """Sample improvements for testing."""
    return [
        Improvement(
            section='experience',
            type='content',
            original_text='Worked on projects',
            improved_text='Led development of scalable web applications',
            reasoning='Added specific leadership role and technical details',
            priority='high',
            confidence=0.9
        ),
        Improvement(
            section='skills',
            type='keyword',
            original_text='Programming',
            improved_text='Python Programming',
            reasoning='Added specific programming language',
            priority='medium',
            confidence=0.8
        ),
        Improvement(
            section='summary',
            type='format',
            original_text='Developer with experience',
            improved_text='• Experienced software developer',
            reasoning='Added bullet point formatting',
            priority='low',
            confidence=0.7
        )
    ]


@pytest.fixture
def sample_cv_state(sample_cv_text, sample_cv_sections, sample_analysis_score):
    """Sample CV state for testing."""
    return CVState(
        original_cv=sample_cv_text,
        file_format="txt",
        target_role="Software Engineer",
        target_industry="technology",
        parsed_sections=sample_cv_sections,
        raw_text=sample_cv_text,
        analysis_scores=sample_analysis_score,
        identified_gaps=["Missing contact section"],
        suggested_improvements=[],
        applied_improvements=[],
        enhanced_cv=None,
        enhancement_summary=None,
        processing_errors=[],
        processing_time=1.5,
        model_used="gpt-4o"
    )


@pytest.fixture
def temp_text_file(sample_cv_text):
    """Create a temporary text file with CV content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_cv_text)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def temp_pdf_file():
    """Create a temporary PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def temp_docx_file():
    """Create a temporary DOCX file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def mock_docling_parser():
    """Mock Docling parser for testing."""
    mock = MagicMock()
    mock.parse.return_value = "# Parsed markdown content"
    mock.extract_sections.return_value = {
        'summary': CVSection(
            name='summary',
            content='Experienced developer',
            position=0,
            confidence=0.95
        )
    }
    return mock


@pytest.fixture
def mock_traditional_parser():
    """Mock traditional parser for testing."""
    mock = MagicMock()
    mock.parse.return_value = "Parsed text content"
    mock.extract_sections.return_value = {
        'experience': CVSection(
            name='experience',
            content='Software Engineer',
            position=0,
            confidence=0.8
        )
    }
    return mock


@pytest.fixture
def mock_cv_analyzer():
    """Mock CV analyzer for testing."""
    mock = MagicMock()
    mock.analyze_content_quality.return_value = {'summary': 0.8, 'experience': 0.9}
    mock.check_ats_compatibility.return_value = 0.85
    mock.calculate_keyword_density.return_value = 0.7
    mock.analyze_formatting.return_value = 0.8
    mock.identify_gaps.return_value = ["Missing contact section"]
    mock.generate_analysis_score.return_value = AnalysisScore(
        overall_score=0.8,
        section_scores={'summary': 0.8},
        ats_compatibility=0.85,
        keyword_density=0.7,
        formatting_score=0.8,
        content_quality=0.8
    )
    return mock


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment."""
    # Ensure test fixtures directory exists
    fixtures_dir = Path(__file__).parent / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    
    # Set environment variables for testing
    os.environ["PYTEST_RUNNING"] = "1"
    
    yield
    
    # Cleanup
    if "PYTEST_RUNNING" in os.environ:
        del os.environ["PYTEST_RUNNING"]


# Markers for different test types
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")


# Skip tests that require optional dependencies
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle optional dependencies."""
    skip_docling = pytest.mark.skip(reason="Docling not available")
    
    for item in items:
        # Skip Docling tests if import fails
        if "docling" in item.name.lower():
            try:
                import docling
            except ImportError:
                item.add_marker(skip_docling)