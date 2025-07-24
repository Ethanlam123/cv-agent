# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment Setup

```bash
# Install dependencies using uv
uv venv
source .venv/bin/activate 
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=your_key_here
# LANGSMITH_API_KEY=your_key_here (optional)
```

## Running the Application

```bash
# IMPORTANT: Always activate the virtual environment before running Python code
source .venv/bin/activate

# Run the interactive CLI
python main.py

# Run the Streamlit web interface
streamlit run streamlit_app.py

# For development/testing with sample CV
python main.py
# Choose 'y' for sample CV, then specify target role/industry
```

## Code Architecture

This is a LangGraph-based CV improvement agent that processes CVs through a multi-node workflow:

### Core Workflow (src/cv_agent/workflow.py)
- **Entry**: `parse_cv` � `analyze_quality` � `match_requirements` � `generate_improvements`
- **Conditional**: High-confidence improvements go to `apply_improvements`, others skip to `quality_check`
- **Exit**: `quality_check` (final scoring and completion)

### State Management (src/cv_agent/models/state.py)
- **CVState**: TypedDict managing workflow state across all nodes
- **Pydantic Models**: CVSection, AnalysisScore, Improvement for type safety
- State flows through nodes, accumulating analysis results and improvements

### Node Structure (src/cv_agent/nodes/)
- **parsing.py**: Document parsing (PDF/DOCX/text) → structured sections with LLM enhancement
- **analysis.py**: Quality scoring and requirement matching
- **improvement.py**: LLM-powered enhancement generation and application (GPT-4.1-mini)
- **user_interaction.py**: Conversational AI for personalized suggestions

### Tools (src/cv_agent/tools/)
- **analyzers.py**: CV scoring algorithms and ATS compatibility checks
- **parsers.py**: Multi-tiered parsing system (LLM → Docling → Traditional)
- **user_interaction.py**: Chat-based interaction and personalized suggestion generation
- **jd_analyzer.py**: Job description parsing, CV matching, and gap analysis

### Dependencies
- **LangGraph**: Workflow orchestration
- **LangSmith**: Optional monitoring and tracing  
- **LangChain**: LLM integrations (OpenAI/Anthropic/Google)
- **Streamlit**: Modern web interface for CV processing
- **Docling**: Advanced document parsing with OCR and structure detection
- **PyPDF2/python-docx**: Traditional document parsing fallbacks

### LLM-Enhanced Section Parsing
The system uses a three-tier parsing approach for maximum accuracy:

1. **LLM Parsing (Primary)**: Uses GPT-4.1-mini with structured output to intelligently identify CV sections
   - Handles non-standard section names (e.g., "Professional Journey" → "experience")  
   - Better understanding of context and content grouping
   - Higher confidence scores for accurately identified sections
   - Graceful fallback when API keys unavailable

2. **Docling Parsing (Secondary)**: Advanced document processing with markdown structure
   - OCR capabilities for scanned documents
   - Table and layout structure preservation
   - Enhanced markdown-based section detection

3. **Traditional Parsing (Fallback)**: Regex-based pattern matching
   - Reliable baseline with standard CV section patterns
   - No external dependencies required

### Streamlit Web Interface
The modern web interface provides comprehensive CV improvement functionality:

**Core Features:**
- **Multi-tab Organization**: Analysis, Chat Enhancement, Job Matching, Before/After, Final Results
- **Interactive Chat**: Personalized improvement suggestions through conversational AI
- **Job Description Matching**: Upload and analyze job descriptions against CV
- **Before/After Comparison**: Visual side-by-side CV comparison with change analysis
- **Real-time Processing**: Live feedback and progress updates

**Interface Components:**
- **Upload Interface**: Support for PDF, DOCX, text files, and sample CVs
- **Analysis Dashboard**: Comprehensive scoring breakdown and gap identification
- **Chat Interface**: Intelligent conversation flow for gathering user context
- **JD Analyzer**: Job description parsing and CV matching analysis
- **Comparison Views**: Multiple viewing modes for before/after analysis

**Key Functions in streamlit_app.py:**
- `display_cv_before_after_comparison()`: Multi-tab comparison interface
- `display_chat_interface()`: Interactive conversation management
- `display_jd_interface()`: Job description analysis workflow
- `generate_personalized_suggestions()`: Context-aware improvement generation

**Usage Examples:**
```python
# Enable both LLM and Docling (default)
parser = ParserFactory.create_parser("cv.pdf", use_docling=True, use_llm=True)

# Traditional parsing only  
parser = ParserFactory.create_parser("cv.pdf", use_docling=False, use_llm=False)

# LLM-only for text
llm_parser = ParserFactory.create_llm_parser()
sections = llm_parser.extract_sections(cv_text)
```

## Documentation and Research

### Getting Documentation
- **LangGraph**: Use WebFetch to get docs from https://langchain-ai.github.io/langgraph/
- **LangSmith**: Use WebFetch to get docs from https://docs.smith.langchain.com/
- **LangChain**: Use WebFetch to get docs from https://python.langchain.com/docs/
- **Context**: When users mention "context7" or similar, they may be referring to external documentation sources - ask for clarification or use WebFetch with provided URLs

## Development Workflow

### For New Features/Bug Fixes

1. **Create a branch first** before implementing any changes:

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Implement and test** your changes on the branch

3. **Wait for user approval** - Do NOT merge automatically after implementation

4. **Merge only when user explicitly requests it**:

   ```bash
   git checkout master
   git merge feature/your-feature-name
   ```

## Testing

```bash
# Install test dependencies
uv sync --extra test

# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=src/cv_agent --cov-report=html

# Run specific test file
pytest tests/unit/tools/test_parsers.py -v

# Use Makefile shortcuts
make test
make test-coverage
```

## Project Structure Notes

- **CLI Entry Point**: `main.py` (interactive CLI demo)
- **Web Entry Point**: `streamlit_app.py` (modern web interface)
- **Package Structure**: `src/cv_agent/` with clear module separation
- **Dependency Management**: uv for Python packages (see pyproject.toml)
- **Testing**: Comprehensive test suite with 88 tests and 67% coverage
- **Configuration**: Environment variables managed via python-dotenv
- **Model**: Default GPT-4.1-mini across all components
- **Interface Types**: Both CLI and web-based Streamlit interface available
