from typing import Dict, Any
from ..models.state import CVState
from ..tools.user_interaction import UserInteractionManager


def user_interaction_node(state: CVState) -> Dict[str, Any]:
    """
    LangGraph node for interactive user engagement.
    Gathers additional information and provides personalized suggestions.
    
    Args:
        state: Current CVState with analysis results
        
    Returns:
        Updated state with user responses and personalized suggestions
    """
    interaction_manager = UserInteractionManager()
    
    # Conduct interactive session
    updated_state = interaction_manager.interactive_improvement_session(state)
    
    return updated_state


def generate_suggestions_node(state: CVState) -> Dict[str, Any]:
    """
    LangGraph node for generating suggestions without user interaction.
    Useful for automated processing.
    
    Args:
        state: Current CVState with analysis results
        
    Returns:
        Updated state with AI-generated suggestions
    """
    interaction_manager = UserInteractionManager()
    
    # Generate suggestions based on current state
    suggestions = interaction_manager.generate_specific_suggestions(state)
    
    return {
        **state,
        "personalized_suggestions": suggestions,
        "suggestions_generated": True
    }