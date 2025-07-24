# AI CV Improvement Agent

An intelligent CV/resume improvement agent built with LangGraph and LangSmith that analyzes, scores, and enhances CVs with targeted recommendations and automated improvements.

## Features

- **Multi-format Support**: Parse PDFs, DOCX, and text files with advanced parsing options
- **Comprehensive Analysis**: Content quality scoring and ATS compatibility checking  
- **Smart Improvements**: AI-powered enhancement suggestions with confidence scores
- **Industry Targeting**: Role and industry-specific optimization
- **Interactive Chat Interface**: Personalized CV improvement through conversational AI
- **Job Description Matching**: Analyze CV compatibility against specific job postings
- **Before/After Comparison**: Visual comparison of original vs enhanced CVs
- **Streamlit Web Interface**: Modern web-based interface alongside CLI
- **LangSmith Integration**: Advanced monitoring and optimization capabilities
- **LLM-Enhanced Parsing**: Three-tier parsing system with GPT-4.1-mini, Docling, and traditional methods

## Architecture

### LangGraph Workflow

```text
Input CV -> Parse Document -> Analyze Content -> Match Requirements -> Generate Improvements -> Apply Changes -> Quality Check -> Output Enhanced CV
```

### Core Components

- **Document Processing**: Advanced three-tier parsing (LLM + Docling + Traditional)
- **Analysis Engine**: Multi-dimensional scoring (ATS, content quality, formatting)
- **Improvement Generator**: LLM-powered targeted enhancements with GPT-4.1-mini
- **Interactive Chat**: Personalized suggestion generation through conversation
- **Job Description Analyzer**: CV-to-JD matching and gap analysis
- **State Management**: Comprehensive workflow state tracking
- **Web Interface**: Streamlit-based modern UI with tabbed organization
- **Monitoring**: LangSmith integration for performance tracking

### Parsing System

The system employs a sophisticated three-tier parsing approach:

1. **LLM Parsing (Primary)**: GPT-4.1-mini with structured output for intelligent section identification
2. **Docling Parsing (Secondary)**: Advanced document processing with OCR and layout detection
3. **Traditional Parsing (Fallback)**: Regex-based pattern matching for reliability

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key (or alternative LLM provider)
- Optional: LangSmith API key for monitoring

### Installation

1. Clone and setup:

```bash
cd cv-agent
cp .env.example .env
# Edit .env with your API keys
```

2. Install dependencies:

```bash
uv venv
source .venv/bin/activate 
uv sync
```

3. Run the agent:

**CLI Interface:**
```bash
python main.py
```

**Web Interface (Streamlit):**
```bash
streamlit run streamlit_app.py
```

### Environment Variables

Required:

```bash
OPENAI_API_KEY=your_key_here
```

Optional:

```bash
LANGSMITH_API_KEY=your_key_here  # For monitoring
ANTHROPIC_API_KEY=your_key_here  # Alternative LLM
```

## Usage

### Web Interface (Streamlit)

The modern web interface provides:

1. **CV Upload**: File upload, text input, or sample CV
2. **Analysis Dashboard**: Comprehensive scoring and gap identification
3. **Interactive Chat**: Personalized improvement suggestions through conversation
4. **Job Matching**: Upload job descriptions for targeted optimization
5. **Before/After Comparison**: Visual comparison with detailed change analysis
6. **Enhanced Results**: Download improved CV content

### Command Line Interface

The interactive CLI guides you through:

1. **CV Input**: File upload or sample CV
2. **Targeting**: Specify role and industry (optional)  
3. **Analysis**: Comprehensive CV scoring
4. **Improvements**: View and apply suggestions
5. **Export**: Save enhanced CV

### Example Session

```text
AI CV Improvement Agent - Demo
==================================================

Initializing CV Improvement Agent...

Use sample CV? (y/n): y
Target role (optional): Software Engineer
Target industry (optional): technology

Processing CV...
   Target Role: Software Engineer
   Target Industry: technology

==================================================
ANALYSIS RESULTS
==================================================

Overall CV Score: 72.5%

Identified 4 improvement areas:
  - Experience section lacks duration information
  - Skills section appears limited - consider adding more relevant skills
  - Consider adding keywords relevant to Software Engineer: algorithms, debugging, testing

Detailed Scores:
   Overall Score: 72.5%
   ATS Compatibility: 80.0%
   Content Quality: 65.0%
   Keyword Density: 70.0%
   Formatting: 82.5%

Suggested Improvements (3):
   [HIGH] Added specific metrics and impact measurements to demonstrate value
   [MED]  Includes keywords commonly searched by ATS systems
   [MED]  Clear section headers improve document structure and ATS parsing

CV analysis completed successfully!
```

## API Usage

```python
from src.cv_agent.workflow import CVImprovementAgent

# Initialize agent
agent = CVImprovementAgent()

# Process CV
result = agent.process_cv(
    cv_input="path/to/cv.pdf",  # or raw text
    target_role="Software Engineer",
    target_industry="technology"
)

# Get summary
summary = agent.get_improvement_summary(result)
print(summary)

# Access detailed results
scores = result["analysis_scores"]
improvements = result["suggested_improvements"]
enhanced_cv = result["enhanced_cv"]
```

## Monitoring with LangSmith

When LangSmith is configured, the agent automatically tracks:

- Processing performance and success rates
- Improvement suggestion quality
- User feedback and satisfaction
- A/B testing of different strategies

## Configuration

### Model Settings

The system now uses GPT-4.1-mini by default. Customize in `.env`:

```bash
MODEL_NAME=gpt-4.1-mini    # LLM model (default)
MODEL_TEMPERATURE=0.3      # Creativity level
MAX_TOKENS=2000           # Response length
```

### Analysis Weights

Modify scoring weights in `src/cv_agent/tools/analyzers.py`:

```python
content_weight = 0.4      # Content quality importance
ats_weight = 0.25         # ATS compatibility importance  
keyword_weight = 0.2      # Keyword relevance importance
format_weight = 0.15      # Formatting importance
```

## Enterprise Features

- **Batch Processing**: Process multiple CVs simultaneously
- **Custom Industry Keywords**: Add domain-specific vocabularies
- **Integration APIs**: Connect with ATS and HRIS systems
- **Advanced Analytics**: Performance dashboards and reporting
- **Multi-language Support**: International CV formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues tracker
- **Community**: Discussions tab

---

Built with LangGraph, LangSmith, and modern AI technologies.