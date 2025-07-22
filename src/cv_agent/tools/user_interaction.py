from typing import Dict, List, Any
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from ..models.state import CVState


class UserInteractionManager:
    """Manages user interactions for gathering additional information and providing suggestions."""
    
    def __init__(self, model_name: str = "gpt-4.1-mini"):
        """Initialize with specified LLM model."""
        self.model_name = model_name
    
    def ask_for_more_information(self, state: CVState) -> Dict[str, str]:
        """
        Ask user for more specific information based on CV analysis with intelligent prioritization.
        
        Args:
            state: Current CV processing state
            
        Returns:
            Dictionary with prioritized questions for the user
        """
        questions = {}
        
        # Analyze what information is missing or needs clarification
        parsed_sections = state.get("parsed_sections", {})
        target_role = state.get("target_role")
        target_industry = state.get("target_industry")
        
        # Priority 1: Essential targeting information (always ask first)
        if not target_role:
            questions["target_role"] = "I'd like to tailor my suggestions to your goals. What specific job role are you targeting? (e.g., 'Senior Software Engineer', 'Marketing Manager', 'Data Analyst')"
        
        if not target_industry and target_role:
            # Make industry question contextual to the role
            questions["target_industry"] = f"Great! For a {target_role} position, which industry interests you most? (e.g., 'technology', 'healthcare', 'finance', 'consulting')"
        elif not target_industry:
            questions["target_industry"] = "Which industry or sector are you focusing your job search on?"
        
        # Priority 2: Critical missing sections that impact ATS and first impressions
        if "summary" not in parsed_sections or len(parsed_sections.get("summary", {}).get("content", "")) < 50:
            if target_role:
                questions["professional_summary"] = f"I notice your CV could benefit from a stronger professional summary. Can you describe your key strengths and what makes you an ideal {target_role} candidate in 2-3 sentences?"
            else:
                questions["professional_summary"] = "Your CV would benefit from a compelling professional summary. What are your key strengths and career highlights that set you apart?"
        
        # Priority 3: Skills gap analysis
        if "skills" not in parsed_sections or len(parsed_sections.get("skills", {}).get("content", "")) < 30:
            if target_role:
                questions["key_skills"] = f"To optimize your CV for {target_role} positions, what are your strongest technical skills and tools? Please list 5-8 most relevant ones."
            else:
                questions["key_skills"] = "What are your core technical skills, software proficiencies, or specialized competencies? List your top 5-8."
        
        # Priority 4: Experience enhancement (context-aware)
        if "experience" not in parsed_sections or len(parsed_sections.get("experience", {}).get("content", "")) < 100:
            questions["work_experience"] = "I'd like to help strengthen your experience section. Can you tell me about your most relevant role and 2-3 key accomplishments or projects?"
        elif self._has_weak_experience_descriptions(parsed_sections):
            questions["experience_details"] = "Your experience section could be more impactful. Can you share specific results or achievements from your current/recent role? (e.g., projects led, problems solved, improvements made)"
        
        # Priority 5: Quantifiable achievements (highly targeted)
        if self._lacks_quantifiable_metrics(parsed_sections):
            if "experience" in parsed_sections:
                questions["achievements"] = "Numbers make a huge difference! Can you quantify any of your achievements? (e.g., 'increased efficiency by 30%', 'managed $2M budget', 'led team of 12')"
            else:
                questions["achievements"] = "Do you have any measurable accomplishments or results you can share? Even approximate numbers help (e.g., team size, budget, percentages, timeframes)"
        
        # Priority 6: Career context (only if basics are covered)
        if len(questions) <= 2:  # Only ask if not overwhelming with basic questions
            if target_role and target_industry:
                questions["career_stage"] = f"To provide the most relevant advice, are you looking to advance within {target_industry}, transition from another field, or return after a break?"
            else:
                questions["career_goals"] = "What's your main career objective right now? (advancing in current field, changing industries, seeking leadership roles, etc.)"
        
        # Priority 7: Application-specific context (advanced)
        if len(questions) <= 1:  # Only if most basics are covered
            questions["application_context"] = "Are you applying to specific companies or types of roles? This helps me tailor keyword and formatting suggestions."
        
        # Limit to 3-4 questions max to avoid overwhelming the user
        prioritized_questions = {}
        question_keys = list(questions.keys())
        for key in question_keys[:4]:  # Take first 4 prioritized questions
            prioritized_questions[key] = questions[key]
        
        return prioritized_questions
    
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
            r'\d+\s*(years?|months?)',  # Time periods
            r'\d+\s*(people|team|members)',  # Team sizes
        ]
        
        for pattern in metrics_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        
        return True
    
    def _has_weak_experience_descriptions(self, parsed_sections: Dict) -> bool:
        """Check if experience descriptions are weak or generic."""
        experience_section = parsed_sections.get("experience", {})
        if not experience_section:
            return True
            
        experience_content = experience_section.get("content", "").lower()
        
        # Check for weak indicators
        weak_phrases = [
            "worked on", "responsible for", "involved in", "participated in",
            "helped with", "assisted with", "various projects", "daily tasks",
            "collaborated with team", "used programming languages"
        ]
        
        # Check for strength indicators
        strong_phrases = [
            "led", "developed", "implemented", "designed", "created", "built",
            "optimized", "improved", "achieved", "delivered", "launched"
        ]
        
        weak_count = sum(1 for phrase in weak_phrases if phrase in experience_content)
        strong_count = sum(1 for phrase in strong_phrases if phrase in experience_content)
        
        # If more weak phrases than strong ones, or very short content
        return weak_count > strong_count or len(experience_content) < 200
    
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
        # user_responses parameter kept for API consistency but not used in rule-based approach
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