import re
from typing import Dict, Optional
from pathlib import Path
import PyPDF2
from docx import Document
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PipelineOptions

from ..models.state import CVSection


class DocumentParser:
    """Base class for document parsing."""
    
    def parse(self, file_path: str) -> str:
        """Parse document and return raw text."""
        raise NotImplementedError
    
    def extract_sections(self, text: str) -> Dict[str, CVSection]:
        """Extract structured sections from text."""
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


class DoclingParser(DocumentParser):
    """Advanced document parser using Docling library."""
    
    def __init__(self):
        """Initialize Docling converter with optimized settings for CV parsing."""
        # Initialize with default configuration - Docling has good defaults for CV parsing
        self.converter = DocumentConverter()
    
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
        Leverages markdown formatting for better section detection.
        """
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
    def create_parser(file_path: str, use_docling: bool = True) -> DocumentParser:
        """
        Create parser based on file extension.
        
        Args:
            file_path: Path to the document
            use_docling: Whether to use Docling parser for supported formats
        """
        suffix = Path(file_path).suffix.lower()
        
        # Use Docling for supported formats when available
        if use_docling and suffix in ['.pdf', '.docx', '.doc']:
            return DoclingParser()
        
        # Fallback to traditional parsers
        if suffix == '.pdf':
            return PDFParser()
        elif suffix in ['.docx', '.doc']:
            return DocxParser()
        elif suffix == '.txt':
            return TextParser()
        else:
            raise ValueError(f"Unsupported file format: {suffix}")