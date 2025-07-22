#!/usr/bin/env python3
"""
Interactive CV improvement demo showcasing user interaction capabilities.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cv_agent.tools.user_interaction import UserInteractionManager
from cv_agent.models.state import CVState


def main():
    """Run interactive CV improvement demo."""
    
    print("🎯 Interactive CV Improvement Demo")
    print("=" * 50)
    
    # Sample CV state (normally this would come from workflow)
    sample_state = CVState(
        original_cv="sample_cv.pdf",
        file_format="pdf",
        target_role=None,  # Will be asked
        target_industry=None,  # Will be asked
        parsed_sections={
            "experience": {
                "name": "experience",
                "content": "Software Engineer at TechCorp\n- Developed web applications",
                "position": 0,
                "confidence": 0.9
            },
            "education": {
                "name": "education",
                "content": "BS Computer Science, University",
                "position": 1,
                "confidence": 0.8
            }
        },
        raw_text="Sample CV content...",
        analysis_scores={
            "overall_score": 0.65,
            "ats_compatibility": 0.7,
            "keyword_density": 0.6
        },
        identified_gaps=["Missing quantifiable achievements", "No professional summary"],
        suggested_improvements=[],
        applied_improvements=[],
        enhanced_cv=None,
        enhancement_summary=None,
        processing_errors=[],
        processing_time=1.2,
        model_used="gpt-4o"
    )
    
    # Initialize interaction manager
    interaction_manager = UserInteractionManager()
    
    # Option 1: Just ask questions
    print("\n📝 Option 1: Information Gathering")
    questions = interaction_manager.ask_for_more_information(sample_state)
    
    print(f"\nFound {len(questions)} areas that need more information:")
    for i, (key, question) in enumerate(questions.items(), 1):
        print(f"{i}. {question}")
    
    # Option 2: Generate suggestions based on current state
    print("\n🤖 Option 2: AI-Generated Suggestions")
    suggestions = interaction_manager.generate_specific_suggestions(sample_state)
    
    print(f"\nGenerated {len(suggestions)} suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. **{suggestion.get('title', 'Suggestion')}**")
        print(f"   Priority: {suggestion.get('priority', 'medium').upper()}")
        print(f"   Why: {suggestion.get('reason', 'Improves CV quality')}")
        print(f"   Action: {suggestion.get('action', 'Make improvements')}")
        print(f"   Impact: {suggestion.get('impact', 'Positive results expected')}")
    
    # Option 3: Full interactive session
    print("\n💬 Option 3: Full Interactive Session")
    response = input("\nWould you like to try the full interactive session? (y/n): ").strip().lower()
    
    if response == 'y':
        try:
            final_state = interaction_manager.interactive_improvement_session(sample_state)
            
            print("\n✅ Interactive session completed!")
            print(f"Gathered {len(final_state.get('user_responses', {}))} user responses")
            print(f"Generated {len(final_state.get('personalized_suggestions', []))} personalized suggestions")
            
        except KeyboardInterrupt:
            print("\n👋 Session cancelled by user")
        except Exception as e:
            print(f"\n❌ Error during interactive session: {str(e)}")
    
    print("\n🎉 Demo completed!")


if __name__ == "__main__":
    main()