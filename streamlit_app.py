import streamlit as st
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
load_dotenv()

from src.cv_agent.workflow import CVImprovementAgent

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

def init_session_state():
    """Initialize session state variables."""
    if "agent" not in st.session_state:
        st.session_state.agent = CVImprovementAgent()
    if "processed_result" not in st.session_state:
        st.session_state.processed_result = None

def display_analysis_scores(scores):
    """Display analysis scores in a formatted way."""
    st.subheader("📊 CV Analysis Scores")
    
    # Handle both Pydantic objects and dictionary formats
    if hasattr(scores, 'overall_score'):  # Pydantic object
        overall_score = scores.overall_score
        ats_score = scores.ats_compatibility
        content_score = scores.content_quality
        keyword_score = scores.keyword_density
        formatting_score = scores.formatting_score
    else:  # Dictionary
        overall_score = scores.get('overall_score', 0)
        ats_score = scores.get('ats_compatibility', 0)
        content_score = scores.get('content_quality', 0)
        keyword_score = scores.get('keyword_density', 0)
        formatting_score = scores.get('formatting_score', 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Overall Score", f"{overall_score:.1%}")
        st.metric("ATS Compatibility", f"{ats_score:.1%}")
        st.metric("Formatting", f"{formatting_score:.1%}")
    
    with col2:
        st.metric("Content Quality", f"{content_score:.1%}")
        st.metric("Keyword Density", f"{keyword_score:.1%}")

def display_improvements(improvements: list):
    """Display suggested improvements."""
    if not improvements:
        return
    
    st.subheader("💡 Suggested Improvements")
    
    for i, improvement in enumerate(improvements):
        # Handle both Pydantic objects and dictionary formats
        if hasattr(improvement, 'section'):  # Pydantic object
            section = improvement.section
            improvement_type = improvement.type
            priority = improvement.priority
            confidence = improvement.confidence
            reasoning = improvement.reasoning
            original_text = improvement.original_text
            improved_text = improvement.improved_text
        else:  # Dictionary
            section = improvement.get('section', 'General')
            improvement_type = improvement.get('type', 'improvement')
            priority = improvement.get('priority', 'medium')
            confidence = improvement.get('confidence', 0)
            reasoning = improvement.get('reasoning', 'No description available')
            original_text = improvement.get('original_text', '')
            improved_text = improvement.get('improved_text', '')
        
        # Create expander with meaningful title
        title = f"{section.title()} - {improvement_type.title()}"
        with st.expander(f"Improvement {i+1}: {title}"):
            st.write(f"**Section:** {section}")
            st.write(f"**Type:** {improvement_type}")
            st.write(f"**Priority:** {priority}")
            st.write(f"**Confidence:** {confidence:.1%}")
            st.write(f"**Reasoning:** {reasoning}")
            
            if original_text:
                st.write("**Original Text:**")
                st.code(original_text, language="text")
            
            if improved_text:
                st.write("**Suggested Improvement:**")
                st.code(improved_text, language="text")

def display_enhanced_cv(enhanced_cv: str):
    """Display the enhanced CV."""
    if not enhanced_cv:
        return
    
    st.subheader("✨ Enhanced CV")
    st.text_area("Enhanced CV Content", enhanced_cv, height=400)

def main():
    st.set_page_config(
        page_title="CV Improvement Agent",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 CV Improvement Agent")
    st.write("Upload your CV and get AI-powered improvement suggestions!")
    
    init_session_state()
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    target_role = st.sidebar.text_input("Target Role", placeholder="e.g., Software Engineer")
    target_industry = st.sidebar.text_input("Target Industry", placeholder="e.g., Technology")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Upload CV")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a CV file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your CV in PDF, DOCX, or TXT format"
        )
        
        # Text input option
        st.write("Or paste your CV content:")
        cv_text = st.text_area("CV Text", height=200)
        
        # Sample CV option
        use_sample = st.checkbox("Use sample CV for testing")
        
        # Process button
        if st.button("Process CV", type="primary"):
            if uploaded_file is not None:
                # Save uploaded file to temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    cv_input = tmp_file.name
            elif cv_text:
                cv_input = cv_text
            elif use_sample:
                cv_input = create_sample_cv()
            else:
                st.error("Please upload a file, paste CV text, or use sample CV")
                return
            
            # Process CV with loading indicator
            with st.spinner("Processing CV... This may take a few moments."):
                try:
                    result = st.session_state.agent.process_cv(
                        cv_input=cv_input,
                        target_role=target_role if target_role else None,
                        target_industry=target_industry if target_industry else None
                    )
                    st.session_state.processed_result = result
                    st.success("CV processed successfully!")
                except Exception as e:
                    st.error(f"Error processing CV: {str(e)}")
                finally:
                    # Clean up temporary file if it exists
                    if uploaded_file is not None and 'cv_input' in locals():
                        try:
                            os.unlink(cv_input)
                        except:
                            pass
    
    with col2:
        st.header("Results")
        
        if st.session_state.processed_result:
            result = st.session_state.processed_result
            
            # Display analysis scores
            if result.get("analysis_scores"):
                display_analysis_scores(result["analysis_scores"])
            
            # Display processing summary
            if result.get("enhancement_summary"):
                st.subheader("📋 Summary")
                st.write(result["enhancement_summary"])
            
            # Display identified gaps
            if result.get("identified_gaps"):
                st.subheader("🎯 Identified Gaps")
                for gap in result["identified_gaps"]:
                    st.write(f"• {gap}")
            
            # Display improvements
            if result.get("suggested_improvements"):
                display_improvements(result["suggested_improvements"])
            
            # Display enhanced CV
            if result.get("enhanced_cv"):
                display_enhanced_cv(result["enhanced_cv"])
            
            # Display processing errors if any
            if result.get("processing_errors"):
                st.subheader("⚠️ Processing Issues")
                for error in result["processing_errors"]:
                    st.warning(error)
            
            # Final quality score
            if result.get("final_quality_score"):
                st.subheader("🏆 Final Quality Score")
                st.metric("Updated Score", f"{result['final_quality_score']:.1%}")
        
        else:
            st.info("Upload and process a CV to see results here.")

if __name__ == "__main__":
    main()