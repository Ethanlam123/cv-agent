from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .models.state import CVState
from .nodes.parsing import parse_cv_node
from .nodes.analysis import analyze_quality_node, match_requirements_node  
from .nodes.improvement import generate_improvements_node, apply_improvements_node


def should_apply_improvements(state: CVState) -> str:
    """Conditional edge to determine if improvements should be applied."""
    improvements = state.get("suggested_improvements", [])
    high_priority_improvements = []
    
    for imp in improvements:
        # Handle both Pydantic objects and dictionary formats
        if hasattr(imp, 'priority'):  # Pydantic object
            priority = imp.priority
            confidence = imp.confidence
        else:  # Dictionary
            priority = imp.get("priority")
            confidence = imp.get("confidence", 0)
        
        if priority == "high" and confidence > 0.7:
            high_priority_improvements.append(imp)
    
    if high_priority_improvements:
        return "apply_improvements"
    else:
        return "quality_check"


def quality_check_node(state: CVState) -> Dict[str, Any]:
    """Final quality check node."""
    
    # Simple quality check - in production would be more comprehensive
    enhanced_cv = state.get("enhanced_cv", "")
    applied_improvements = state.get("applied_improvements", [])
    
    if enhanced_cv and applied_improvements:
        quality_score = 0.85  # Assume improvements increased quality
    else:
        quality_score = 0.70  # Base score without improvements
    
    return {
        **state,
        "final_quality_score": quality_score,
        "processing_complete": True
    }


def create_cv_improvement_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for CV improvement.
    
    Returns:
        Configured StateGraph workflow
    """
    
    # Initialize the graph
    workflow = StateGraph(CVState)
    
    # Add nodes
    workflow.add_node("parse_cv", parse_cv_node)
    workflow.add_node("analyze_quality", analyze_quality_node)
    workflow.add_node("match_requirements", match_requirements_node)
    workflow.add_node("generate_improvements", generate_improvements_node)
    workflow.add_node("apply_improvements", apply_improvements_node)
    workflow.add_node("quality_check", quality_check_node)
    
    # Add edges
    workflow.set_entry_point("parse_cv")
    workflow.add_edge("parse_cv", "analyze_quality")
    workflow.add_edge("analyze_quality", "match_requirements")
    workflow.add_edge("match_requirements", "generate_improvements")
    
    # Conditional edge based on improvement quality
    workflow.add_conditional_edges(
        "generate_improvements",
        should_apply_improvements,
        {
            "apply_improvements": "apply_improvements",
            "quality_check": "quality_check"
        }
    )
    
    workflow.add_edge("apply_improvements", "quality_check")
    workflow.add_edge("quality_check", END)
    
    return workflow


class CVImprovementAgent:
    """Main CV Improvement Agent class."""
    
    def __init__(self):
        self.workflow = create_cv_improvement_workflow()
        self.app = self.workflow.compile()
    
    def process_cv(self, cv_input: str, target_role: str = None, 
                  target_industry: str = None) -> Dict[str, Any]:
        """
        Process a CV and return improvement recommendations.
        
        Args:
            cv_input: File path to CV or raw text content
            target_role: Target job role for optimization
            target_industry: Target industry for keyword optimization
            
        Returns:
            Final state with analysis results and improvements
        """
        
        initial_state = CVState(
            original_cv=cv_input,
            file_format="unknown",
            target_role=target_role,
            target_industry=target_industry,
            parsed_sections={},
            raw_text="",
            analysis_scores=None,
            identified_gaps=[],
            suggested_improvements=[],
            applied_improvements=[],
            enhanced_cv=None,
            enhancement_summary=None,
            processing_errors=[],
            processing_time=None,
            model_used="gpt-4.1-mini"
        )
        
        # Run the workflow
        result = self.app.invoke(initial_state)
        
        return result
    
    def get_improvement_summary(self, result: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of the CV analysis and improvements.
        
        Args:
            result: Result from process_cv method
            
        Returns:
            Formatted summary string
        """
        
        summary_parts = []
        
        # Overall score
        if result.get("analysis_scores"):
            overall_score = result["analysis_scores"].get("overall_score", 0)
            summary_parts.append(f"Overall CV Score: {overall_score:.1%}")
        
        # Key findings
        if result.get("identified_gaps"):
            summary_parts.append(f"\nIdentified {len(result['identified_gaps'])} improvement areas:")
            for gap in result["identified_gaps"][:3]:  # Show top 3
                summary_parts.append(f"  • {gap}")
        
        # Applied improvements
        if result.get("applied_improvements"):
            summary_parts.append(f"\nApplied {len(result['applied_improvements'])} high-priority improvements")
        
        # Enhancement summary
        if result.get("enhancement_summary"):
            summary_parts.append(f"\n{result['enhancement_summary']}")
        
        # Processing errors
        if result.get("processing_errors"):
            summary_parts.append(f"\nProcessing Issues: {len(result['processing_errors'])}")
        
        return "\n".join(summary_parts) if summary_parts else "CV analysis completed successfully."