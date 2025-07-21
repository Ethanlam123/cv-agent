from typing import Dict, Any

from ..models.state import CVState, CVSection
from ..tools.analyzers import CVAnalyzer


def analyze_quality_node(state: CVState) -> Dict[str, Any]:
    """
    LangGraph node for analyzing CV quality and identifying improvement areas.
    
    Args:
        state: Current CVState containing parsed sections and raw text
        
    Returns:
        Updated state with analysis scores and identified gaps
    """
    
    try:
        # Initialize analyzer
        analyzer = CVAnalyzer()
        
        # Convert parsed sections back to CVSection objects
        sections = {}
        for name, section_data in state.get("parsed_sections", {}).items():
            sections[name] = CVSection(**section_data)
        
        raw_text = state.get("raw_text", "")
        target_industry = state.get("target_industry")
        
        # Perform comprehensive analysis
        analysis_scores = analyzer.generate_analysis_score(
            sections=sections,
            raw_text=raw_text,
            target_industry=target_industry
        )
        
        # Identify gaps and weaknesses
        identified_gaps = analyzer.identify_gaps(sections)
        
        # Update state with analysis results
        return {
            **state,
            "analysis_scores": analysis_scores.model_dump(),
            "identified_gaps": identified_gaps
        }
        
    except Exception as e:
        error_message = f"Error in analyze_quality_node: {str(e)}"
        
        # Add error to processing errors
        errors = state.get("processing_errors", [])
        errors.append(error_message)
        
        return {
            **state,
            "analysis_scores": None,
            "identified_gaps": [],
            "processing_errors": errors
        }


def match_requirements_node(state: CVState) -> Dict[str, Any]:
    """
    LangGraph node for matching CV content against job/industry requirements.
    
    Args:
        state: Current CVState with analysis results
        
    Returns:
        Updated state with requirement matching results
    """
    
    try:
        target_role = state.get("target_role")
        target_industry = state.get("target_industry")
        raw_text = state.get("raw_text", "").lower()
        
        # Role-specific keyword matching
        role_keywords = {
            'software engineer': [
                'programming', 'coding', 'development', 'software', 'algorithms',
                'data structures', 'debugging', 'testing', 'version control'
            ],
            'data scientist': [
                'machine learning', 'statistics', 'python', 'r', 'sql', 'data analysis',
                'visualization', 'modeling', 'pandas', 'numpy', 'scikit-learn'
            ],
            'product manager': [
                'product strategy', 'roadmap', 'stakeholder management', 'agile',
                'user experience', 'market research', 'analytics', 'prioritization'
            ],
            'marketing manager': [
                'campaign management', 'digital marketing', 'seo', 'sem', 'analytics',
                'brand management', 'content strategy', 'lead generation'
            ]
        }
        
        gaps = state.get("identified_gaps", [])
        
        # Add role-specific gap analysis
        if target_role and target_role.lower() in role_keywords:
            role_words = role_keywords[target_role.lower()]
            missing_keywords = [keyword for keyword in role_words 
                              if keyword not in raw_text]
            
            if missing_keywords:
                gaps.append(f"Consider adding keywords relevant to {target_role}: {', '.join(missing_keywords[:5])}")
        
        return {
            **state,
            "identified_gaps": gaps
        }
        
    except Exception as e:
        error_message = f"Error in match_requirements_node: {str(e)}"
        
        errors = state.get("processing_errors", [])
        errors.append(error_message)
        
        return {
            **state,
            "processing_errors": errors
        }