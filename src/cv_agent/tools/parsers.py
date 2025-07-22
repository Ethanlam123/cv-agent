import re
from typing import Dict, Optional, List
from pathlib import Path
import PyPDF2
from docx import Document
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PipelineOptions
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from ..models.state import CVSection


class ParsedSection(BaseModel):
    """Pydantic model for LLM-parsed CV sections."""
    name: str = Field(..., description="Section name (e.g., 'summary', 'experience', 'skills')")
    content: str = Field(..., description="Full content of the section")
    confidence: float = Field(..., description="Confidence score between 0 and 1")
    section_type: str = Field(..., description="Type classification (header, content, list, etc.)")


class CVSectionStructure(BaseModel):
    """Pydantic model for complete CV section structure."""
    sections: List[ParsedSection] = Field(..., description="List of identified CV sections")
    document_type: str = Field(..., description="Type of document (resume, cv, portfolio, etc.)")
    overall_confidence: float = Field(..., description="Overall parsing confidence")


class DocumentParser:
    """Base class for document parsing."""
    
    def parse(self, file_path: str) -> str:
        """Parse document and return raw text."""
        raise NotImplementedError
    
    def extract_sections(self, text: str) -> Dict[str, CVSection]:
        """Extract structured sections from text using traditional regex patterns."""
        sections = {}
        
        # Common CV section patterns
        section_patterns = {
            'contact': r'(?i)(contact|personal\s+info|personal\s+details)',
            'summary': r'(?i)(summary|profile|objective|about)',
            'experience': r'(?i)(experience|employment|work\s+history|professional\s+experience)',
            'education': r'(?i)(education|academic|qualifications)',
            'skills': r'(?i)(skills|technical\s+skills|competencies)',
            'projects': r'(?i)(projects|portfolio)',
            'certifications': r'(?i)(certifications|certificates|licenses)',
            'achievements': r'(?i)(achievements|accomplishments|awards)',
            'languages': r'(?i)(languages|linguistic)',
            'references': r'(?i)(references|referees)'
        }
        
        lines = text.split('\n')
        current_section = 'other'
        current_content = []
        position = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches any section header
            section_found = None
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line):
                    section_found = section_name
                    break
            
            if section_found:
                # Save previous section
                if current_content:
                    sections[current_section] = CVSection(
                        name=current_section,
                        content='\n'.join(current_content),
                        position=position,
                        confidence=0.8
                    )
                    position += 1
                
                # Start new section
                current_section = section_found
                current_content = [line]
            else:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = CVSection(
                name=current_section,
                content='\n'.join(current_content),
                position=position,
                confidence=0.8
            )
        
        return sections
    
    def extract_sections_with_llm(self, text: str, use_llm: bool = True) -> Dict[str, CVSection]:
        """
        Extract structured sections from text using LLM for intelligent parsing.
        Falls back to traditional regex parsing if LLM is unavailable.
        """
        if not use_llm:
            return self.extract_sections(text)
        
        try:
            # Initialize LLM
            llm = init_chat_model("gpt-4o-mini", temperature=0.1)
            
            # Set up output parser
            parser = PydanticOutputParser(pydantic_object=CVSectionStructure)
            
            # Create prompt for section identification
            system_prompt = """You are an expert CV/Resume parser. Your task is to analyze the given CV text and identify distinct sections with high accuracy.

Common CV sections include:
- contact: Contact information (name, email, phone, address)
- summary: Professional summary, objective, or about section
- experience: Work experience, employment history, professional experience
- education: Educational background, academic qualifications
- skills: Technical skills, core competencies, skill sets
- projects: Key projects, portfolio items
- certifications: Certifications, licenses, professional credentials
- achievements: Awards, accomplishments, honors
- languages: Language skills, linguistic abilities
- references: References, referees

For each section you identify:
1. Classify it with the most appropriate section name
2. Extract the complete content including headers
3. Assign a confidence score (0-1) based on how certain you are
4. Specify the section type (header, content, list, etc.)

Be precise and thorough. If content doesn't clearly fit a standard section, use descriptive names."""

            human_prompt = f"""Please parse the following CV text and identify all sections:

{text}

{parser.get_format_instructions()}"""

            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            # Get LLM response
            response = llm.invoke(messages)
            parsed_structure = parser.parse(response.content)
            
            # Convert to CVSection format
            sections = {}
            for i, section in enumerate(parsed_structure.sections):
                sections[section.name.lower()] = CVSection(
                    name=section.name.lower(),
                    content=section.content,
                    position=i,
                    confidence=section.confidence
                )
            
            return sections
            
        except Exception as e:
            print(f"LLM section parsing failed: {str(e)}, falling back to traditional parsing")
            # Call traditional parsing method directly to avoid recursion
            return DocumentParser.extract_sections(self, text)


class PDFParser(DocumentParser):
    """PDF document parser using PyPDF2."""
    
    def parse(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")


class DocxParser(DocumentParser):
    """DOCX document parser using python-docx."""
    
    def parse(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")


class TextParser(DocumentParser):
    """Plain text parser."""
    
    def parse(self, file_path: str) -> str:
        """Read plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise ValueError(f"Error parsing text file: {str(e)}")


class LLMDocumentParser(DocumentParser):
    """Document parser that uses LLM for intelligent section extraction."""
    
    def __init__(self, use_llm: bool = True):
        """Initialize LLM parser."""
        self.use_llm = use_llm
    
    def parse(self, file_path: str) -> str:
        """This parser works with pre-extracted text."""
        raise NotImplementedError("LLMDocumentParser requires pre-extracted text")
    
    def extract_sections(self, text: str) -> Dict[str, CVSection]:
        """Extract sections using LLM for intelligent parsing."""
        if self.use_llm:
            return self.extract_sections_with_llm(text, use_llm=True)
        else:
            # Use traditional parsing when LLM is disabled
            return DocumentParser.extract_sections(self, text)


class DoclingParser(DocumentParser):
    """Advanced document parser using Docling library with optional LLM section parsing."""
    
    def __init__(self, use_llm: bool = True):
        """Initialize Docling converter with optional LLM section parsing."""
        # Initialize with default configuration - Docling has good defaults for CV parsing
        self.converter = DocumentConverter()
        self.use_llm = use_llm
    
    def parse(self, file_path: str) -> str:
        """Extract text from document using Docling."""
        try:
            # Convert document
            result = self.converter.convert(file_path)
            
            # Export to markdown for better structure preservation
            markdown_content = result.document.export_to_markdown()
            
            return markdown_content
        except Exception as e:
            raise ValueError(f"Error parsing document with Docling: {str(e)}")
    
    def extract_sections(self, text: str) -> Dict[str, CVSection]:
        """
        Enhanced section extraction using Docling's structured output.
        Uses LLM if enabled, otherwise falls back to markdown pattern matching.
        """
        if self.use_llm:
            try:
                return self.extract_sections_with_llm(text, use_llm=True)
            except Exception as e:
                print(f"LLM parsing failed in DoclingParser: {str(e)}, using traditional markdown parsing")
                # Continue to traditional markdown parsing below
        
        # Traditional markdown-based parsing as fallback
        sections = {}
        
        # Enhanced CV section patterns that work with markdown
        section_patterns = {
            'contact': r'(?i)^#+\s*(contact|personal\s+info|personal\s+details)',
            'summary': r'(?i)^#+\s*(summary|profile|objective|about|professional\s+summary)',
            'experience': r'(?i)^#+\s*(experience|employment|work\s+history|professional\s+experience)',
            'education': r'(?i)^#+\s*(education|academic|qualifications|academic\s+background)',
            'skills': r'(?i)^#+\s*(skills|technical\s+skills|competencies|core\s+competencies)',
            'projects': r'(?i)^#+\s*(projects|portfolio|key\s+projects)',
            'certifications': r'(?i)^#+\s*(certifications|certificates|licenses)',
            'achievements': r'(?i)^#+\s*(achievements|accomplishments|awards)',
            'languages': r'(?i)^#+\s*(languages|linguistic|language\s+skills)',
            'references': r'(?i)^#+\s*(references|referees)'
        }
        
        lines = text.split('\n')
        current_section = 'other'
        current_content = []
        position = 0
        confidence_base = 0.9  # Higher confidence due to structured markdown
        
        for line_idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a markdown header that matches section pattern
            section_found = None
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line):
                    section_found = section_name
                    break
            
            if section_found:
                # Save previous section with content
                if current_content:
                    content_text = '\n'.join(current_content)
                    # Calculate confidence based on content quality
                    confidence = min(confidence_base + (len(content_text) / 1000), 1.0)
                    
                    sections[current_section] = CVSection(
                        name=current_section,
                        content=content_text,
                        position=position,
                        confidence=confidence
                    )
                    position += 1
                
                # Start new section
                current_section = section_found
                current_content = []
            else:
                # Add content to current section (skip empty lines and minor headers)
                if line and not line.startswith('###'):
                    current_content.append(line)
        
        # Save final section
        if current_content:
            content_text = '\n'.join(current_content)
            confidence = min(confidence_base + (len(content_text) / 1000), 1.0)
            
            sections[current_section] = CVSection(
                name=current_section,
                content=content_text,
                position=position,
                confidence=confidence
            )
        
        return sections


class ParserFactory:
    """Factory for creating appropriate parsers based on file extension."""
    
    @staticmethod
    def create_parser(file_path: str, use_docling: bool = True, use_llm: bool = True) -> DocumentParser:
        """
        Create parser based on file extension.
        
        Args:
            file_path: Path to the document
            use_docling: Whether to use Docling parser for supported formats
            use_llm: Whether to use LLM for section extraction
        """
        suffix = Path(file_path).suffix.lower()
        
        # Use Docling for supported formats when available
        if use_docling and suffix in ['.pdf', '.docx', '.doc']:
            return DoclingParser(use_llm=use_llm)
        
        # Fallback to traditional parsers
        if suffix == '.pdf':
            return PDFParser()
        elif suffix in ['.docx', '.doc']:
            return DocxParser()
        elif suffix == '.txt':
            # For text files, we can use LLM parsing if requested
            if use_llm:
                # Create a composite parser that uses TextParser for file reading
                # and LLMDocumentParser for section extraction
                class LLMTextParser(TextParser):
                    def __init__(self):
                        super().__init__()
                        self.llm_parser = LLMDocumentParser(use_llm=True)
                    
                    def extract_sections(self, text: str) -> Dict[str, CVSection]:
                        return self.llm_parser.extract_sections(text)
                
                return LLMTextParser()
            else:
                return TextParser()
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    @staticmethod
    def create_llm_parser() -> LLMDocumentParser:
        """Create a pure LLM parser for text that's already extracted."""
        return LLMDocumentParser(use_llm=True)