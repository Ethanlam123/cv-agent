from typing import Dict, Any
import time
from pathlib import Path

from ..models.state import CVState
from ..tools.parsers import ParserFactory


def parse_cv_node(state: CVState) -> Dict[str, Any]:
    """
    LangGraph node for parsing CV documents and extracting structured content.
    
    Args:
        state: Current CVState containing the original CV path or content
        
    Returns:
        Updated state with parsed sections and raw text
    """
    start_time = time.time()
    
    try:
        # Determine if we have a file path or raw content
        if state.get("original_cv", "").startswith("/") or state.get("original_cv", "").startswith("./"):
            # It's a file path
            file_path = state["original_cv"]
            
            # Determine file format
            suffix = Path(file_path).suffix.lower()
            file_format = suffix[1:] if suffix else "unknown"
            
            # Create appropriate parser
            parser = ParserFactory.create_parser(file_path)
            
            # Parse the document
            raw_text = parser.parse(file_path)
            parsed_sections = parser.extract_sections(raw_text)
            
        else:
            # It's raw text content
            raw_text = state["original_cv"]
            file_format = "txt"
            
            # Use text parser for section extraction
            parser = ParserFactory.create_parser("dummy.txt")
            parsed_sections = parser.extract_sections(raw_text)
        
        processing_time = time.time() - start_time
        
        return {
            **state,
            "raw_text": raw_text,
            "file_format": file_format,
            "parsed_sections": {name: section.model_dump() for name, section in parsed_sections.items()},
            "processing_time": processing_time,
            "processing_errors": []
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_message = f"Error in parse_cv_node: {str(e)}"
        
        return {
            **state,
            "raw_text": "",
            "file_format": "unknown",
            "parsed_sections": {},
            "processing_time": processing_time,
            "processing_errors": [error_message]
        }