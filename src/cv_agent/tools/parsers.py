import re
from typing import Dict, Optional
from pathlib import Path
import PyPDF2
from docx import Document

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


class ParserFactory:
    """Factory for creating appropriate parsers based on file extension."""
    
    @staticmethod
    def create_parser(file_path: str) -> DocumentParser:
        """Create parser based on file extension."""
        suffix = Path(file_path).suffix.lower()
        
        if suffix == '.pdf':
            return PDFParser()
        elif suffix in ['.docx', '.doc']:
            return DocxParser()
        elif suffix == '.txt':
            return TextParser()
        else:
            raise ValueError(f"Unsupported file format: {suffix}")