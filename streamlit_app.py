import streamlit as st
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
load_dotenv()

from src.cv_agent.workflow import CVImprovementAgent
from src.cv_agent.tools.user_interaction import UserInteractionManager
from src.cv_agent.tools.jd_analyzer import JobDescriptionAnalyzer

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

def create_sample_jd() -> str:
    """Create a sample job description for testing."""
    return """
Senior Software Engineer - Full Stack Development

About the Role:
We are seeking a highly skilled Senior Software Engineer to join our dynamic development team. The ideal candidate will have 5+ years of experience in full-stack web development and a passion for building scalable applications.

Key Responsibilities:
- Design and develop robust web applications using React and Node.js
- Build and maintain RESTful APIs and microservices
- Work with cloud platforms (AWS, Azure) for deployment and scaling
- Collaborate with cross-functional teams including product managers and designers
- Mentor junior developers and conduct code reviews
- Implement best practices for testing, security, and performance optimization

Required Qualifications:
- Bachelor's degree in Computer Science or related field
- 5+ years of experience in software development
- Strong proficiency in JavaScript, TypeScript, and Python
- Experience with React, Node.js, and modern front-end frameworks
- Knowledge of database systems (SQL and NoSQL)
- Experience with cloud services (AWS preferred)
- Understanding of DevOps practices and CI/CD pipelines
- Strong problem-solving and communication skills

Preferred Qualifications:
- Experience with Docker and Kubernetes
- Knowledge of machine learning frameworks
- Previous experience in agile development environments
- Contributing to open-source projects

Benefits:
- Competitive salary: $120,000 - $160,000
- Remote work options available
- Health, dental, and vision insurance
- 401(k) matching
- Professional development budget
"""

def init_session_state():
    """Initialize session state variables."""
    if "agent" not in st.session_state:
        st.session_state.agent = CVImprovementAgent()
    if "processed_result" not in st.session_state:
        st.session_state.processed_result = None
    if "user_interaction_manager" not in st.session_state:
        st.session_state.user_interaction_manager = UserInteractionManager()
    if "jd_analyzer" not in st.session_state:
        st.session_state.jd_analyzer = JobDescriptionAnalyzer()
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "questions_generated" not in st.session_state:
        st.session_state.questions_generated = False
    if "current_questions" not in st.session_state:
        st.session_state.current_questions = {}
    if "user_responses" not in st.session_state:
        st.session_state.user_responses = {}
    if "jd_analysis" not in st.session_state:
        st.session_state.jd_analysis = None
    if "jd_match_results" not in st.session_state:
        st.session_state.jd_match_results = None
    if "jd_suggestions" not in st.session_state:
        st.session_state.jd_suggestions = None

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

def display_cv_before_after_comparison():
    """Display before and after CV comparison side by side."""
    if not st.session_state.processed_result:
        return
    
    original_cv = st.session_state.processed_result.get("original_cv_text", "")
    enhanced_cv = st.session_state.processed_result.get("enhanced_cv", "")
    
    if not original_cv and not enhanced_cv:
        st.info("No CV comparison available. Process a CV to see before/after comparison.")
        return
    
    st.subheader("📊 Before vs After Comparison")
    
    # Create tabs for different view modes
    tab1, tab2, tab3, tab4 = st.tabs(["Side by Side", "Before Only", "After Only", "Key Changes"])
    
    with tab1:
        if original_cv or enhanced_cv:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 **Original CV**")
                if original_cv:
                    st.text_area("Original CV", original_cv, height=500, key="original_cv_display")
                else:
                    st.info("Original CV content not available")
            
            with col2:
                st.markdown("### ✨ **Enhanced CV**")
                if enhanced_cv:
                    st.text_area("Enhanced CV", enhanced_cv, height=500, key="enhanced_cv_display")
                else:
                    st.info("Enhanced CV not yet generated")
    
    with tab2:
        st.markdown("### 📝 **Original CV**")
        if original_cv:
            st.text_area("Original CV Content", original_cv, height=600, key="original_only")
        else:
            st.info("Original CV content not available")
    
    with tab3:
        st.markdown("### ✨ **Enhanced CV**")
        if enhanced_cv:
            st.text_area("Enhanced CV Content", enhanced_cv, height=600, key="enhanced_only")
        else:
            st.info("Enhanced CV not yet generated")
    
    with tab4:
        st.markdown("### 🔍 **Key Changes Analysis**")
        if original_cv and enhanced_cv:
            # Simple change detection - could be enhanced with proper diff algorithms
            original_sections = original_cv.split('\n\n')
            enhanced_sections = enhanced_cv.split('\n\n')
            
            st.markdown("**Notable Changes:**")
            
            # Basic change analysis
            if len(enhanced_sections) > len(original_sections):
                st.success(f"✅ **Added {len(enhanced_sections) - len(original_sections)} new sections**")
            elif len(enhanced_sections) < len(original_sections):
                st.info(f"📝 **Consolidated {len(original_sections) - len(enhanced_sections)} sections**")
            
            # Word count changes
            original_words = original_cv.split()
            enhanced_words = enhanced_cv.split()
            word_diff = len(enhanced_words) - len(original_words)
            
            if word_diff > 0:
                st.success(f"✅ **Added {word_diff} words** for more detailed descriptions")
            elif word_diff < 0:
                st.info(f"📝 **Reduced by {abs(word_diff)} words** for better conciseness")
            else:
                st.info("📊 **Maintained similar length** while improving content quality")
            
            # Check for specific improvements
            improvement_indicators = {
                "quantified": ["increased", "decreased", "improved", "%", "$", "managed"],
                "action_words": ["developed", "implemented", "led", "created", "designed", "optimized"],
                "technical": ["API", "database", "framework", "technology", "system"],
                "skills": ["Python", "JavaScript", "SQL", "AWS", "React", "Node.js"]
            }
            
            for category, keywords in improvement_indicators.items():
                original_count = sum(1 for word in keywords if word.lower() in original_cv.lower())
                enhanced_count = sum(1 for word in keywords if word.lower() in enhanced_cv.lower())
                
                if enhanced_count > original_count:
                    improvement = enhanced_count - original_count
                    category_name = category.replace("_", " ").title()
                    st.success(f"✅ **{category_name}**: Added {improvement} relevant terms")
        else:
            st.info("Process a CV to see detailed change analysis.")
    
    # Add improvement summary if available
    if original_cv and enhanced_cv:
        st.subheader("📈 Improvement Summary")
        
        # Calculate basic metrics
        original_length = len(original_cv.split())
        enhanced_length = len(enhanced_cv.split())
        length_change = enhanced_length - original_length
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Original Word Count", original_length)
        with col2:
            st.metric("Enhanced Word Count", enhanced_length)
        with col3:
            st.metric("Word Count Change", length_change, delta=length_change)
        
        # Show key improvements if available
        if st.session_state.processed_result.get("suggested_improvements"):
            st.markdown("**Key Improvements Applied:**")
            improvements = st.session_state.processed_result["suggested_improvements"]
            for i, improvement in enumerate(improvements[:5], 1):  # Show top 5
                if hasattr(improvement, 'reasoning'):
                    st.write(f"{i}. {improvement.reasoning}")
                elif isinstance(improvement, dict):
                    st.write(f"{i}. {improvement.get('reasoning', 'Improvement applied')}")

def display_chat_interface():
    """Display interactive chat interface for gathering user information."""
    st.subheader("💬 CV Enhancement Chat")
    
    # Display existing chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Generate questions if CV has been processed and questions haven't been generated yet
    if (st.session_state.processed_result and 
        not st.session_state.questions_generated and 
        st.session_state.processed_result.get("parsed_sections")):
        
        # Create a mock state object for the UserInteractionManager
        mock_state = {
            "parsed_sections": st.session_state.processed_result.get("parsed_sections", {}),
            "target_role": st.session_state.processed_result.get("target_role"),
            "target_industry": st.session_state.processed_result.get("target_industry"),
            "analysis_scores": st.session_state.processed_result.get("analysis_scores"),
            "identified_gaps": st.session_state.processed_result.get("identified_gaps", [])
        }
        
        # Generate questions
        questions = st.session_state.user_interaction_manager.ask_for_more_information(mock_state)
        st.session_state.current_questions = questions
        st.session_state.questions_generated = True
        
        # Add initial bot message
        if questions:
            num_questions = len(questions)
            bot_message = f"Great! I've analyzed your CV and have {num_questions} targeted questions to help create personalized improvement suggestions. This should only take a couple of minutes."
            st.session_state.chat_messages.append({"role": "assistant", "content": bot_message})
            
            # Add first question
            first_question = list(questions.values())[0]
            st.session_state.chat_messages.append({"role": "assistant", "content": first_question})
            st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Your response..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Process user response
        handle_user_response(prompt)
        
        st.rerun()

def handle_user_response(response: str):
    """Handle user response and generate appropriate follow-up with intelligent conversation flow."""
    current_questions = st.session_state.current_questions
    responses = st.session_state.user_responses
    
    if current_questions:
        # Map response to current question
        unanswered_questions = [key for key in current_questions.keys() if key not in responses]
        
        if unanswered_questions:
            current_key = unanswered_questions[0]
            responses[current_key] = response
            
            # Generate contextual acknowledgment
            acknowledgment = generate_contextual_acknowledgment(current_key, response)
            st.session_state.chat_messages.append({"role": "assistant", "content": acknowledgment})
            
            # Check if there are more questions
            remaining_questions = [key for key in current_questions.keys() if key not in responses]
            
            if remaining_questions:
                # Ask next question with smooth transition
                next_key = remaining_questions[0]
                next_question = current_questions[next_key]
                
                # Add transition if needed
                transition = generate_question_transition(current_key, next_key, response)
                if transition:
                    st.session_state.chat_messages.append({"role": "assistant", "content": transition})
                
                st.session_state.chat_messages.append({"role": "assistant", "content": next_question})
            else:
                # All questions answered, generate personalized suggestions
                completion_message = "Perfect! I now have all the information I need. Let me generate personalized suggestions based on your responses..."
                st.session_state.chat_messages.append({"role": "assistant", "content": completion_message})
                generate_personalized_suggestions()
        else:
            # All questions answered, handle follow-up conversation
            handle_followup_conversation(response)

def generate_contextual_acknowledgment(question_key: str, response: str) -> str:
    """Generate contextual acknowledgment based on the question type and response."""
    acknowledgments = {
        "target_role": f"Great! Focusing on {response} roles will help me provide targeted advice.",
        "target_industry": f"Excellent! The {response} industry has specific requirements I can address.",
        "professional_summary": "That's helpful context for strengthening your professional summary.",
        "key_skills": "Those skills will be important to highlight effectively.",
        "work_experience": "Thanks for sharing that experience - it gives me insight into your background.",
        "experience_details": "Those details will help make your experience section much more compelling.",
        "achievements": "Fantastic! Quantifiable achievements like these make a huge difference.",
        "career_stage": "Understanding your career stage helps me tailor my recommendations.",
        "application_context": "This context will help me provide more targeted suggestions."
    }
    
    return acknowledgments.get(question_key, "Thank you for that information!")

def generate_question_transition(current_key: str, next_key: str, response: str) -> Optional[str]:
    """Generate smooth transitions between questions."""
    # Special case for industry transition that uses response
    if current_key == "target_industry" and next_key == "key_skills":
        return f"For the {response} industry, technical skills are crucial."
    
    transitions = {
        ("target_role", "target_industry"): None,  # Already contextual
        ("target_role", "professional_summary"): "Now let's work on making your CV stand out for these roles.",
        ("professional_summary", "key_skills"): "Next, let's ensure your key skills are properly showcased.",
        ("key_skills", "achievements"): "Now I'd like to help you quantify your impact.",
        ("work_experience", "achievements"): "Let's add some concrete numbers to make your experience more impressive.",
    }
    
    return transitions.get((current_key, next_key))

def handle_followup_conversation(response: str):
    """Handle ongoing conversation after initial questions."""
    # Simple follow-up responses for additional conversation
    followup_responses = [
        "I've noted that additional information. Is there anything specific about your CV you'd like me to focus on?",
        "Thanks for the extra context! This will help refine my suggestions.",
        "That's useful information. Feel free to share any other details you think would be helpful.",
        "Got it! Any other aspects of your job search you'd like assistance with?"
    ]
    
    import random
    response_text = random.choice(followup_responses)
    st.session_state.chat_messages.append({"role": "assistant", "content": response_text})

def generate_personalized_suggestions():
    """Generate personalized suggestions based on user responses."""
    try:
        # Create state object with user responses
        mock_state = {
            "parsed_sections": st.session_state.processed_result.get("parsed_sections", {}),
            "target_role": st.session_state.processed_result.get("target_role"),
            "target_industry": st.session_state.processed_result.get("target_industry"),
            "analysis_scores": st.session_state.processed_result.get("analysis_scores"),
            "identified_gaps": st.session_state.processed_result.get("identified_gaps", [])
        }
        
        # Generate suggestions with user responses
        suggestions = st.session_state.user_interaction_manager.generate_specific_suggestions(
            mock_state, 
            st.session_state.user_responses
        )
        
        # Store suggestions in session state
        st.session_state.personalized_suggestions = suggestions
        
        # Add completion message
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": f"Perfect! Based on your responses, I've generated {len(suggestions)} personalized suggestions for improving your CV. You can view them in the 'Personalized Suggestions' section below."
        })
        
    except Exception as e:
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": f"I encountered an issue generating personalized suggestions: {str(e)}. However, you can still see the general improvements above."
        })

def display_personalized_suggestions():
    """Display personalized suggestions generated from chat responses."""
    if not hasattr(st.session_state, 'personalized_suggestions') or not st.session_state.personalized_suggestions:
        return
    
    st.subheader("🎯 Personalized Suggestions")
    st.write("Based on our conversation, here are tailored recommendations:")
    
    for i, suggestion in enumerate(st.session_state.personalized_suggestions, 1):
        with st.expander(f"Suggestion {i}: {suggestion.get('title', 'Recommendation')}"):
            st.write(f"**Priority:** {suggestion.get('priority', 'medium').title()}")
            st.write(f"**Why:** {suggestion.get('reason', 'No reason provided')}")
            st.write(f"**Action:** {suggestion.get('action', 'No action specified')}")
            st.write(f"**Expected Impact:** {suggestion.get('impact', 'Impact not specified')}")

def display_jd_interface():
    """Display job description input and analysis interface."""
    st.subheader("💼 Job Description Analysis")
    
    # Sample JD option
    use_sample_jd = st.checkbox("Use sample job description for testing")
    
    # Job description input
    if use_sample_jd:
        jd_text = st.text_area(
            "Job Description (Sample):",
            value=create_sample_jd(),
            height=200,
            help="Sample job description for testing the matching functionality"
        )
    else:
        jd_text = st.text_area(
            "Paste the Job Description here:",
            height=200,
            placeholder="Copy and paste the complete job description here...",
            help="Include the full job posting with requirements, responsibilities, and qualifications"
        )
    
    # Analyze button
    col1, col2 = st.columns([1, 3])
    with col1:
        analyze_jd = st.button("🔍 Analyze JD", type="primary")
    
    if analyze_jd and jd_text and st.session_state.processed_result:
        with st.spinner("Analyzing job description and matching against your CV..."):
            try:
                # Analyze job description
                jd_analysis = st.session_state.jd_analyzer.analyze_job_description(jd_text)
                st.session_state.jd_analysis = jd_analysis
                
                # Match CV against JD
                match_results = st.session_state.jd_analyzer.match_cv_to_jd(
                    st.session_state.processed_result, 
                    jd_analysis
                )
                st.session_state.jd_match_results = match_results
                
                # Generate JD-specific suggestions
                jd_suggestions = st.session_state.jd_analyzer.generate_jd_specific_suggestions(
                    st.session_state.processed_result,
                    jd_analysis,
                    match_results
                )
                st.session_state.jd_suggestions = jd_suggestions
                
                st.success("Job description analyzed successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error analyzing job description: {str(e)}")
    
    elif analyze_jd and not st.session_state.processed_result:
        st.warning("Please process your CV first before analyzing job descriptions.")
    elif analyze_jd and not jd_text:
        st.warning("Please paste a job description to analyze.")

def display_jd_analysis_results():
    """Display job description analysis results."""
    if not st.session_state.jd_analysis:
        st.info("Analyze a job description to see matching results here.")
        return
    
    jd_analysis = st.session_state.jd_analysis
    match_results = st.session_state.jd_match_results
    
    # Job information
    st.subheader("📋 Job Information")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Position", jd_analysis.job_title)
        if jd_analysis.required_experience_years:
            st.metric("Required Experience", f"{jd_analysis.required_experience_years} years")
    
    with col2:
        if match_results:
            st.metric("Overall Match Score", f"{match_results['overall_match_score']:.1%}")
    
    if match_results:
        # Match breakdown
        st.subheader("🎯 Matching Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            # Technical skills match
            tech_match = match_results["technical_skills_match"]
            st.metric(
                "Technical Skills Match", 
                f"{tech_match['match_percentage']:.1%}",
                f"{tech_match['total_required']} total skills"
            )
            
            if tech_match["matched_skills"]:
                st.success(f"✅ **Matched Skills:** {', '.join(tech_match['matched_skills'][:5])}")
            
            if tech_match["missing_skills"]:
                st.error(f"❌ **Missing Skills:** {', '.join(tech_match['missing_skills'][:5])}")
        
        with col2:
            # Experience match
            exp_match = match_results["experience_match"]
            exp_status = "✅ Meets Requirement" if exp_match["meets_requirement"] else "❌ Below Requirement"
            st.metric("Experience Match", exp_status)
            
            if exp_match["gap_years"] > 0:
                st.warning(f"⚠️ Gap: {exp_match['gap_years']} years short of requirement")
        
        # Gap analysis
        if match_results["gap_analysis"]:
            st.subheader("🔍 Gap Analysis")
            for gap in match_results["gap_analysis"]:
                st.warning(f"• {gap}")

def display_jd_specific_suggestions():
    """Display JD-specific improvement suggestions."""
    if not st.session_state.jd_suggestions:
        return
    
    st.subheader("💡 Job-Specific Recommendations")
    st.write("Based on this job description, here are targeted improvements:")
    
    # Group suggestions by priority
    high_priority = [s for s in st.session_state.jd_suggestions if s.get('priority', '').lower() == 'high']
    medium_priority = [s for s in st.session_state.jd_suggestions if s.get('priority', '').lower() == 'medium']
    low_priority = [s for s in st.session_state.jd_suggestions if s.get('priority', '').lower() == 'low']
    
    # Display high priority first
    if high_priority:
        st.markdown("### 🔥 High Priority")
        for i, suggestion in enumerate(high_priority, 1):
            with st.expander(f"🚨 {suggestion.get('title', 'High Priority Suggestion')}", expanded=True):
                st.write(f"**Why Important:** {suggestion.get('reason', 'No reason provided')}")
                st.write(f"**Action Steps:** {suggestion.get('action', 'No action specified')}")
                st.write(f"**Expected Impact:** {suggestion.get('impact', 'Impact not specified')}")
    
    # Display medium priority
    if medium_priority:
        st.markdown("### 📈 Medium Priority")
        for suggestion in medium_priority:
            with st.expander(f"⚡ {suggestion.get('title', 'Medium Priority Suggestion')}"):
                st.write(f"**Why Important:** {suggestion.get('reason', 'No reason provided')}")
                st.write(f"**Action Steps:** {suggestion.get('action', 'No action specified')}")
                st.write(f"**Expected Impact:** {suggestion.get('impact', 'Impact not specified')}")
    
    # Display low priority
    if low_priority:
        st.markdown("### 📝 Additional Improvements")
        for suggestion in low_priority:
            with st.expander(f"💡 {suggestion.get('title', 'Additional Suggestion')}"):
                st.write(f"**Why Helpful:** {suggestion.get('reason', 'No reason provided')}")
                st.write(f"**Action Steps:** {suggestion.get('action', 'No action specified')}")
                st.write(f"**Expected Impact:** {suggestion.get('impact', 'Impact not specified')}")

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
                    # Store original CV text for before/after comparison
                    result["original_cv_text"] = result.get("raw_text", cv_input if isinstance(cv_input, str) and not cv_input.startswith("/") else "")
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
            
            # Create tabs for better organization
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analysis", "💬 Chat Enhancement", "💼 Job Matching", "📊 Before/After", "✨ Final Results"])
            
            with tab1:
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
            
            with tab2:
                # Interactive chat interface
                display_chat_interface()
                
                # Display personalized suggestions if available
                display_personalized_suggestions()
            
            with tab3:
                # Job Description Analysis
                display_jd_interface()
                
                # Display JD analysis results
                display_jd_analysis_results()
                
                # Display JD-specific suggestions
                display_jd_specific_suggestions()
            
            with tab4:
                # Display before/after comparison
                display_cv_before_after_comparison()
            
            with tab5:
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