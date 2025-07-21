from typing import Dict, Any, List
from langchain.chat_models import init_chat_model

from ..models.state import CVState, Improvement


class ImprovementGenerator:
    """Generates targeted CV improvements using LLM."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.model = init_chat_model(
            model=model_name,
            temperature=0.3,
            max_tokens=2000
        )
    
    def generate_content_improvements(self, section_name: str, content: str, 
                                    gaps: List[str], target_role: str = None) -> List[Improvement]:
        """Generate content improvements for a specific section."""
        
        role_context = f" for a {target_role} position" if target_role else ""
        
        prompt = f"""
        Analyze this CV {section_name} section and provide specific improvements{role_context}:
        
        Original content:
        {content}
        
        Identified issues:
        {', '.join(gaps) if gaps else 'General improvement needed'}
        
        Provide 2-3 specific improvements in this JSON format:
        [
            {{
                "type": "content|format|keyword|structure",
                "original_text": "exact text to replace",
                "improved_text": "improved version",
                "reasoning": "why this improvement helps",
                "priority": "high|medium|low",
                "confidence": 0.85
            }}
        ]
        
        Focus on:
        1. Adding quantified achievements where possible
        2. Using stronger action verbs
        3. Improving clarity and impact
        4. Adding relevant keywords
        """
        
        try:
            response = self.model.invoke(prompt)
            # Parse the JSON response (simplified - in production would use proper JSON parsing)
            improvements = []
            
            # For demo purposes, create sample improvements
            if section_name == "experience":
                improvements.append(Improvement(
                    section=section_name,
                    type="content",
                    original_text=content[:100] + "..." if len(content) > 100 else content,
                    improved_text="Enhanced with quantified achievements and stronger action verbs",
                    reasoning="Added specific metrics and impact measurements to demonstrate value",
                    priority="high",
                    confidence=0.85
                ))
            
            if section_name == "skills":
                improvements.append(Improvement(
                    section=section_name,
                    type="keyword",
                    original_text=content,
                    improved_text="Added industry-relevant technical skills and certifications",
                    reasoning="Includes keywords commonly searched by ATS systems",
                    priority="medium",
                    confidence=0.80
                ))
            
            return improvements
            
        except Exception as e:
            # Return a default improvement if LLM call fails
            return [Improvement(
                section=section_name,
                type="content",
                original_text=content,
                improved_text="Content needs enhancement for better impact",
                reasoning=f"Error generating specific improvements: {str(e)}",
                priority="medium",
                confidence=0.50
            )]
    
    def generate_formatting_improvements(self, raw_text: str) -> List[Improvement]:
        """Generate formatting and structure improvements."""
        improvements = []
        
        # Check for bullet points
        if not any(char in raw_text for char in ['•', '▪', '*', '-']):
            improvements.append(Improvement(
                section="format",
                type="format",
                original_text="Plain text format",
                improved_text="Use bullet points for better readability",
                reasoning="Bullet points improve ATS compatibility and readability",
                priority="medium",
                confidence=0.90
            ))
        
        # Check for section headers
        common_headers = ['experience', 'education', 'skills', 'summary']
        missing_headers = [h for h in common_headers if h.lower() not in raw_text.lower()]
        
        if missing_headers:
            improvements.append(Improvement(
                section="structure",
                type="structure",
                original_text="Current section organization",
                improved_text=f"Add clear section headers: {', '.join(missing_headers)}",
                reasoning="Clear section headers improve document structure and ATS parsing",
                priority="high",
                confidence=0.95
            ))
        
        return improvements


def generate_improvements_node(state: CVState) -> Dict[str, Any]:
    """
    LangGraph node for generating targeted CV improvements.
    
    Args:
        state: Current CVState with analysis results and identified gaps
        
    Returns:
        Updated state with suggested improvements
    """
    
    try:
        # Initialize improvement generator
        generator = ImprovementGenerator()
        
        # Get analysis data
        parsed_sections = state.get("parsed_sections", {})
        identified_gaps = state.get("identified_gaps", [])
        raw_text = state.get("raw_text", "")
        target_role = state.get("target_role")
        
        all_improvements = []
        
        # Generate content improvements for each section
        for section_name, section_data in parsed_sections.items():
            if section_data.get("content"):
                section_gaps = [gap for gap in identified_gaps 
                              if section_name.lower() in gap.lower()]
                
                content_improvements = generator.generate_content_improvements(
                    section_name=section_name,
                    content=section_data["content"],
                    gaps=section_gaps,
                    target_role=target_role
                )
                all_improvements.extend(content_improvements)
        
        # Generate formatting improvements
        format_improvements = generator.generate_formatting_improvements(raw_text)
        all_improvements.extend(format_improvements)
        
        # Convert improvements to dict format for state
        improvements_data = [imp.model_dump() for imp in all_improvements]
        
        return {
            **state,
            "suggested_improvements": improvements_data
        }
        
    except Exception as e:
        error_message = f"Error in generate_improvements_node: {str(e)}"
        
        errors = state.get("processing_errors", [])
        errors.append(error_message)
        
        return {
            **state,
            "suggested_improvements": [],
            "processing_errors": errors
        }


def apply_improvements_node(state: CVState) -> Dict[str, Any]:
    """
    LangGraph node for applying selected improvements to the CV.
    
    Args:
        state: Current CVState with suggested improvements
        
    Returns:
        Updated state with enhanced CV content
    """
    
    try:
        suggested_improvements = state.get("suggested_improvements", [])
        raw_text = state.get("raw_text", "")
        parsed_sections = state.get("parsed_sections", {})
        
        # For demo purposes, apply high-priority improvements
        applied_improvements = []
        enhanced_sections = parsed_sections.copy()
        
        for improvement_data in suggested_improvements:
            improvement = Improvement(**improvement_data)
            
            if improvement.priority == "high" and improvement.confidence > 0.7:
                # Apply the improvement to the relevant section
                if improvement.section in enhanced_sections:
                    section_data = enhanced_sections[improvement.section].copy()
                    
                    # Simple text replacement (in production, would be more sophisticated)
                    if improvement.original_text in section_data["content"]:
                        section_data["content"] = section_data["content"].replace(
                            improvement.original_text,
                            improvement.improved_text
                        )
                        enhanced_sections[improvement.section] = section_data
                
                applied_improvements.append(improvement_data)
        
        # Generate enhanced CV text
        enhanced_cv_parts = []
        for section_name, section_data in enhanced_sections.items():
            enhanced_cv_parts.append(f"{section_name.upper()}\n{section_data['content']}\n")
        
        enhanced_cv = "\n".join(enhanced_cv_parts)
        
        # Generate summary of changes
        summary_parts = []
        for imp in applied_improvements:
            summary_parts.append(f"- {imp['reasoning']}")
        
        enhancement_summary = "Applied improvements:\n" + "\n".join(summary_parts) if summary_parts else "No high-priority improvements applied"
        
        return {
            **state,
            "applied_improvements": applied_improvements,
            "enhanced_cv": enhanced_cv,
            "enhancement_summary": enhancement_summary
        }
        
    except Exception as e:
        error_message = f"Error in apply_improvements_node: {str(e)}"
        
        errors = state.get("processing_errors", [])
        errors.append(error_message)
        
        return {
            **state,
            "applied_improvements": [],
            "enhanced_cv": state.get("raw_text", ""),
            "enhancement_summary": f"Error applying improvements: {str(e)}",
            "processing_errors": errors
        }