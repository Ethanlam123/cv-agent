from typing import Dict, Any
import time
from pathlib import Path

from ..models.state import CVState
from ..tools.parsers import ParserFactory


def parse_cv_node(state: CVState) -> Dict[str, Any]:
    """
    LangGraph node for parsing CV documents and extracting structured content.
    Enhanced with Docling parser and LLM-based section extraction for superior document understanding.
    
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
            
            # Create appropriate parser with Docling and LLM enabled by default
            use_docling = True
            use_llm = True
            try:
                parser = ParserFactory.create_parser(file_path, use_docling=use_docling, use_llm=use_llm)
            except ImportError:
                # Fallback to traditional parsers if Docling is not available
                print("Warning: Docling not available, falling back to traditional parsers")
                parser = ParserFactory.create_parser(file_path, use_docling=False, use_llm=use_llm)
            
            # Parse the document
            raw_text = parser.parse(file_path)
            parsed_sections = parser.extract_sections(raw_text)
            
        else:
            # It's raw text content
            raw_text = state["original_cv"]
            file_format = "txt"
            
            # Use text parser with LLM for section extraction
            use_llm = True
            parser = ParserFactory.create_parser("dummy.txt", use_docling=False, use_llm=use_llm)
            parsed_sections = parser.extract_sections(raw_text)
        
        processing_time = time.time() - start_time
        
        # Log parsing success
        parser_type = "Docling+LLM" if hasattr(parser, 'converter') and hasattr(parser, 'use_llm') and parser.use_llm else \
                     "Docling" if hasattr(parser, 'converter') else \
                     "LLM-Enhanced" if hasattr(parser, 'llm_parser') else "Traditional"
        print(f"CV parsed successfully using {parser_type} parser in {processing_time:.2f}s")
        print(f"Extracted {len(parsed_sections)} sections: {list(parsed_sections.keys())}")
        
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
        
        # Try fallback parsing if Docling fails
        if "docling" in str(e).lower() and state.get("original_cv", "").startswith("/"):
            try:
                print("Docling parsing failed, attempting fallback to traditional parsers...")
                file_path = state["original_cv"]
                parser = ParserFactory.create_parser(file_path, use_docling=False, use_llm=True)  # Still use LLM if available
                raw_text = parser.parse(file_path)
                parsed_sections = parser.extract_sections(raw_text)
                
                processing_time = time.time() - start_time
                
                return {
                    **state,
                    "raw_text": raw_text,
                    "file_format": Path(file_path).suffix.lower()[1:],
                    "parsed_sections": {name: section.model_dump() for name, section in parsed_sections.items()},
                    "processing_time": processing_time,
                    "processing_errors": [f"Docling failed, used fallback parser: {str(e)}"]
                }
            except Exception as fallback_error:
                error_message = f"Both Docling and fallback parsing failed: {str(e)}, {str(fallback_error)}"
        
        return {
            **state,
            "raw_text": "",
            "file_format": "unknown",
            "parsed_sections": {},
            "processing_time": processing_time,
            "processing_errors": [error_message]
        }