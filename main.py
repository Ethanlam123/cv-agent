#!/usr/bin/env python3
"""
AI CV Improvement Agent - Example Usage Script

This script demonstrates how to use the CV Improvement Agent built with LangGraph.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cv_agent.workflow import CVImprovementAgent
from cv_agent.utils.monitoring import setup_langsmith_env
from cv_agent.tools.user_interaction import UserInteractionManager

# Load environment variables
load_dotenv()

def create_sample_cv() -> str:
    """Create a sample CV for testing."""
    return """
John Doe
Email: john.doe@email.com
Phone: (555) 123-4567

SUMMARY
Experienced software developer with background in web applications.

EXPERIENCE
Software Developer at Tech Company
- Worked on various projects
- Used programming languages
- Collaborated with team members

EDUCATION
Bachelor's Degree in Computer Science
University of Technology, 2020

SKILLS
Python, JavaScript, HTML, CSS
"""

def main():
    """Main execution function."""
    
    print("🚀 AI CV Improvement Agent - Demo")
    print("=" * 50)
    
    # Setup LangSmith monitoring (optional)
    if setup_langsmith_env():
        print("✅ LangSmith monitoring enabled")
    else:
        print("⚠️  LangSmith monitoring disabled (missing API key)")
    
    # Initialize the CV improvement agent
    print("\n🤖 Initializing CV Improvement Agent...")
    agent = CVImprovementAgent()
    
    # Create or load CV content
    use_sample = input("\n📄 Use sample CV? (y/n): ").lower().strip() == 'y'
    
    if use_sample:
        cv_content = create_sample_cv()
        print("\n📄 Using sample CV content")
    else:
        cv_path = input("📁 Enter CV file path: ").strip()
        if not os.path.exists(cv_path):
            print("❌ File not found. Using sample CV instead.")
            cv_content = create_sample_cv()
        else:
            cv_content = cv_path
    
    # Get target role and industry (optional)
    target_role = input("\n🎯 Target role (optional): ").strip() or None
    target_industry = input("🏢 Target industry (optional): ").strip() or None
    
    # Ask for interaction mode
    interaction_mode = input("\n💬 Use interactive mode for personalized suggestions? (y/n): ").lower().strip() == 'y'
    
    # Process the CV
    print(f"\n⚙️  Processing CV...")
    if target_role:
        print(f"   Target Role: {target_role}")
    if target_industry:
        print(f"   Target Industry: {target_industry}")
    
    try:
        # Run the CV improvement workflow
        result = agent.process_cv(
            cv_input=cv_content,
            target_role=target_role,
            target_industry=target_industry
        )
        
        # Display results
        print("\n" + "=" * 50)
        print("📊 ANALYSIS RESULTS")
        print("=" * 50)
        
        # Show summary
        summary = agent.get_improvement_summary(result)
        print(summary)
        
        # Show detailed analysis if available
        if result.get("analysis_scores"):
            scores = result["analysis_scores"]
            print(f"\n📈 Detailed Scores:")
            print(f"   Overall Score: {scores['overall_score']:.1%}")
            print(f"   ATS Compatibility: {scores['ats_compatibility']:.1%}")
            print(f"   Content Quality: {scores['content_quality']:.1%}")
            print(f"   Keyword Density: {scores['keyword_density']:.1%}")
            print(f"   Formatting: {scores['formatting_score']:.1%}")
        
        # Show suggested improvements
        improvements = result.get("suggested_improvements", [])
        if improvements:
            print(f"\n💡 Suggested Improvements ({len(improvements)}):")
            for i, improvement in enumerate(improvements[:5], 1):  # Show top 5
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                emoji = priority_emoji.get(improvement.get("priority", "medium"), "🔵")
                print(f"   {emoji} {improvement.get('reasoning', 'No description')}")
        
        # Show processing info
        processing_time = result.get("processing_time", 0)
        if processing_time:
            print(f"\n⏱️  Processing Time: {processing_time:.2f} seconds")
        
        # Show any errors
        errors = result.get("processing_errors", [])
        if errors:
            print(f"\n⚠️  Processing Issues:")
            for error in errors:
                print(f"   • {error}")
        
        # Option to save enhanced CV
        if result.get("enhanced_cv"):
            save_enhanced = input(f"\n💾 Save enhanced CV? (y/n): ").lower().strip() == 'y'
            if save_enhanced:
                output_path = input("📁 Output file path (e.g., enhanced_cv.txt): ").strip()
                if output_path:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result["enhanced_cv"])
                    print(f"✅ Enhanced CV saved to: {output_path}")
        
        # Interactive user suggestions (if enabled)
        if interaction_mode:
            print("\n" + "=" * 50)
            print("💬 INTERACTIVE SUGGESTIONS")
            print("=" * 50)
            
            try:
                interaction_manager = UserInteractionManager()
                
                # Create a minimal state for interaction
                from cv_agent.models.state import CVState
                interaction_state = CVState(
                    original_cv=cv_content,
                    file_format=result.get("file_format", "unknown"),
                    target_role=target_role,
                    target_industry=target_industry,
                    parsed_sections=result.get("parsed_sections", {}),
                    raw_text=result.get("raw_text", ""),
                    analysis_scores=result.get("analysis_scores"),
                    identified_gaps=result.get("identified_gaps", []),
                    suggested_improvements=result.get("suggested_improvements", []),
                    applied_improvements=result.get("applied_improvements", []),
                    enhanced_cv=result.get("enhanced_cv"),
                    enhancement_summary=result.get("enhancement_summary"),
                    processing_errors=result.get("processing_errors", []),
                    processing_time=result.get("processing_time"),
                    model_used=result.get("model_used", "gpt-4.1-mini")
                )
                
                # Run interactive session
                interactive_result = interaction_manager.interactive_improvement_session(interaction_state)
                
                # Show personalized suggestions
                personalized_suggestions = interactive_result.get("personalized_suggestions", [])
                if personalized_suggestions:
                    print(f"\n✨ Based on your responses, here are {len(personalized_suggestions)} personalized suggestions:")
                    for i, suggestion in enumerate(personalized_suggestions, 1):
                        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        emoji = priority_emoji.get(suggestion.get("priority", "medium"), "🔵")
                        print(f"\n{i}. {emoji} **{suggestion.get('title', 'Suggestion')}**")
                        print(f"   Why: {suggestion.get('reason', 'Improves CV quality')}")
                        print(f"   Action: {suggestion.get('action', 'Make improvements')}")
                        print(f"   Impact: {suggestion.get('impact', 'Positive results expected')}")
                
                print(f"\n💬 Interactive session completed!")
                
            except KeyboardInterrupt:
                print(f"\n👋 Interactive session cancelled by user")
            except Exception as interactive_error:
                print(f"\n⚠️  Interactive session failed: {str(interactive_error)}")
                print("Continuing with standard analysis results...")
        
        print(f"\n🎉 CV analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error processing CV: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
