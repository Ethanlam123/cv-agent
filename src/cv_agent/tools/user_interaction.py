from typing import Dict, List, Optional, Any
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from ..models.state import CVState


class UserInteractionManager:
    """Manages user interactions for gathering additional information and providing suggestions."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize with specified LLM model."""
        self.model_name = model_name
    
    def ask_for_more_information(self, state: CVState) -> Dict[str, str]:
        """
        Ask user for more specific information based on CV analysis.
        
        Args:
            state: Current CV processing state
            
        Returns:
            Dictionary with questions for the user
        """
        questions = {}
        
        # Analyze what information is missing or needs clarification
        parsed_sections = state.get("parsed_sections", {})
        target_role = state.get("target_role")
        target_industry = state.get("target_industry")
        
        # Generate questions based on missing or weak sections
        if not target_role:
            questions["target_role"] = "What specific job role are you targeting? (e.g., 'Senior Data Scientist', 'Full Stack Developer')"
        
        if not target_industry:
            questions["target_industry"] = "What industry are you focusing on? (e.g., 'technology', 'healthcare', 'finance')"
        
        # Check for missing or weak sections
        if "summary" not in parsed_sections or len(parsed_sections.get("summary", {}).get("content", "")) < 50:
            questions["professional_summary"] = "Could you provide a brief professional summary highlighting your key strengths and career goals?"
        
        if "skills" not in parsed_sections:
            questions["key_skills"] = "What are your top 5-10 technical skills most relevant to your target role?"
        
        if "experience" not in parsed_sections or len(parsed_sections.get("experience", {}).get("content", "")) < 100:
            questions["work_experience"] = "Could you elaborate on your most relevant work experience and key achievements?"
        
        # Generate questions about career goals and preferences
        questions["career_goals"] = "What are your short-term and long-term career goals?"
        questions["preferred_companies"] = "Are there specific types of companies or work environments you prefer?"
        
        # Ask about quantifiable achievements
        if self._lacks_quantifiable_metrics(parsed_sections):
            questions["achievements"] = "Can you provide specific metrics or numbers that demonstrate your impact? (e.g., 'increased sales by 25%', 'managed team of 8 people')"
        
        return questions
    
    def generate_specific_suggestions(self, state: CVState, user_responses: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """
        Generate specific, actionable suggestions based on CV analysis and user responses.
        
        Args:
            state: Current CV processing state
            user_responses: Optional responses from user interaction
            
        Returns:
            List of specific suggestions with priorities and actions
        """
        try:
            llm = init_chat_model(self.model_name, temperature=0.3)
            
            # Prepare context for LLM
            context = self._prepare_context(state, user_responses)
            
            system_prompt = """You are an expert career counselor and CV optimization specialist. 
            Based on the CV analysis and user responses, provide specific, actionable suggestions.
            
            Each suggestion should include:
            1. A clear, specific recommendation
            2. The reason why it's important
            3. How to implement it (specific steps)
            4. Priority level (high/medium/low)
            5. Expected impact
            
            Focus on suggestions that will have the highest impact on job search success."""
            
            human_prompt = f"""Based on this CV analysis and context, provide 5-8 specific suggestions:
            
            {context}
            
            Provide suggestions in this format:
            **Suggestion 1: [Title]**
            - **Why**: [Reason]
            - **Action**: [Specific steps]
            - **Priority**: [High/Medium/Low]
            - **Impact**: [Expected outcome]
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = llm.invoke(messages)
            suggestions = self._parse_suggestions_from_response(response.content)
            
            return suggestions
            
        except Exception as e:
            # Fallback to rule-based suggestions
            print(f"LLM suggestion generation failed: {str(e)}, using rule-based suggestions")
            return self._generate_rule_based_suggestions(state, user_responses)
    
    def interactive_improvement_session(self, state: CVState) -> Dict[str, Any]:
        """
        Conduct an interactive session to gather information and provide suggestions.
        
        Args:
            state: Current CV processing state
            
        Returns:
            Updated state with user responses and suggestions
        """
        print("\n=== CV Improvement Interactive Session ===")
        
        # Step 1: Ask for more information
        questions = self.ask_for_more_information(state)
        user_responses = {}
        
        print(f"\nI have {len(questions)} questions to help improve your CV:")
        for i, (key, question) in enumerate(questions.items(), 1):
            print(f"\n{i}. {question}")
            response = input("Your answer: ").strip()
            if response:
                user_responses[key] = response
        
        # Step 2: Generate specific suggestions
        print("\n=== Generating Personalized Suggestions ===")
        suggestions = self.generate_specific_suggestions(state, user_responses)
        
        # Step 3: Present suggestions
        print(f"\nBased on your responses, here are {len(suggestions)} specific suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. **{suggestion['title']}** (Priority: {suggestion['priority']})")
            print(f"   Why: {suggestion['reason']}")
            print(f"   Action: {suggestion['action']}")
            print(f"   Impact: {suggestion['impact']}")
        
        return {
            **state,
            "user_responses": user_responses,
            "personalized_suggestions": suggestions,
            "interaction_complete": True
        }
    
    def _lacks_quantifiable_metrics(self, parsed_sections: Dict) -> bool:
        """Check if CV lacks quantifiable achievements."""
        content = ""
        for section_data in parsed_sections.values():
            if isinstance(section_data, dict):
                content += section_data.get("content", "")
        
        # Look for numbers, percentages, dollar amounts
        import re
        metrics_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+\+',  # Numbers with plus
            r'increased.*\d+',  # Increased by number
            r'reduced.*\d+',   # Reduced by number
            r'managed.*\d+',   # Managed X people/projects
        ]
        
        for pattern in metrics_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        
        return True
    
    def _prepare_context(self, state: CVState, user_responses: Dict[str, str] = None) -> str:
        """Prepare context string for LLM analysis."""
        context_parts = []
        
        # Basic info
        context_parts.append(f"Target Role: {state.get('target_role', 'Not specified')}")
        context_parts.append(f"Target Industry: {state.get('target_industry', 'Not specified')}")
        
        # CV sections summary
        parsed_sections = state.get("parsed_sections", {})
        context_parts.append(f"CV has {len(parsed_sections)} sections: {list(parsed_sections.keys())}")
        
        # Analysis scores if available
        analysis_scores = state.get("analysis_scores")
        if analysis_scores:
            context_parts.append(f"Overall CV Score: {analysis_scores.get('overall_score', 'Unknown')}")
        
        # Identified gaps
        gaps = state.get("identified_gaps", [])
        if gaps:
            context_parts.append(f"Identified Gaps: {', '.join(gaps[:3])}")
        
        # User responses
        if user_responses:
            context_parts.append("\nUser Responses:")
            for key, value in user_responses.items():
                context_parts.append(f"- {key}: {value}")
        
        return "\n".join(context_parts)
    
    def _parse_suggestions_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured suggestions."""
        suggestions = []
        current_suggestion = {}
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            
            if line.startswith('**Suggestion') and ':' in line:
                if current_suggestion:
                    suggestions.append(current_suggestion)
                title = line.split(':', 1)[1].strip().replace('**', '')
                current_suggestion = {'title': title}
            
            elif line.startswith('- **Why**:'):
                current_suggestion['reason'] = line.replace('- **Why**:', '').strip()
            elif line.startswith('- **Action**:'):
                current_suggestion['action'] = line.replace('- **Action**:', '').strip()
            elif line.startswith('- **Priority**:'):
                priority = line.replace('- **Priority**:', '').strip().lower()
                current_suggestion['priority'] = priority
            elif line.startswith('- **Impact**:'):
                current_suggestion['impact'] = line.replace('- **Impact**:', '').strip()
        
        if current_suggestion:
            suggestions.append(current_suggestion)
        
        return suggestions
    
    def _generate_rule_based_suggestions(self, state: CVState, user_responses: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Generate suggestions using rule-based approach as fallback."""
        suggestions = []
        parsed_sections = state.get("parsed_sections", {})
        
        # Common rule-based suggestions
        if "summary" not in parsed_sections:
            suggestions.append({
                "title": "Add Professional Summary",
                "reason": "A compelling summary is the first thing recruiters see",
                "action": "Write a 2-3 sentence summary highlighting your key skills and experience",
                "priority": "high",
                "impact": "Increases recruiter engagement by 40%"
            })
        
        if self._lacks_quantifiable_metrics(parsed_sections):
            suggestions.append({
                "title": "Add Quantifiable Achievements",
                "reason": "Numbers make your impact concrete and memorable",
                "action": "Replace generic descriptions with specific metrics and percentages",
                "priority": "high",
                "impact": "Makes your achievements 3x more compelling"
            })
        
        if "skills" not in parsed_sections:
            suggestions.append({
                "title": "Add Skills Section",
                "reason": "ATS systems look for specific keywords and skills",
                "action": "Create a dedicated skills section with role-relevant technologies",
                "priority": "medium",
                "impact": "Improves ATS matching by 60%"
            })
        
        return suggestions