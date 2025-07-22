import re
from typing import Dict, List, Optional, Any
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from ..models.state import CVState


class JobRequirement(BaseModel):
    """Represents a specific job requirement extracted from JD."""
    category: str  # 'technical_skills', 'soft_skills', 'experience', 'education', 'certifications'
    requirement: str
    importance: str  # 'required', 'preferred', 'nice_to_have'
    keywords: List[str]


class JDAnalysis(BaseModel):
    """Analysis results from job description."""
    job_title: str
    company: Optional[str]
    industry: Optional[str]
    requirements: List[JobRequirement]
    key_responsibilities: List[str]
    required_experience_years: Optional[int]
    salary_range: Optional[str]
    location: Optional[str]
    remote_option: Optional[bool]


class JobDescriptionAnalyzer:
    """Analyzes job descriptions and matches them against CVs."""
    
    def __init__(self, model_name: str = "gpt-4.1-mini"):
        """Initialize with specified LLM model."""
        self.model_name = model_name
    
    def analyze_job_description(self, jd_text: str) -> JDAnalysis:
        """
        Analyze job description and extract key requirements.
        
        Args:
            jd_text: Raw job description text
            
        Returns:
            Structured analysis of the job description
        """
        try:
            llm = init_chat_model(self.model_name, temperature=0.2)
            
            system_prompt = """You are an expert recruiter and job analysis specialist. 
            Analyze the provided job description and extract key information in a structured format.
            
            Focus on:
            1. Technical skills and technologies mentioned
            2. Soft skills and competencies required
            3. Experience requirements (years, specific domains)
            4. Educational requirements
            5. Certifications mentioned
            6. Key responsibilities and duties
            7. Job details (title, company, location, etc.)
            
            Categorize requirements by importance: 'required', 'preferred', or 'nice_to_have'."""
            
            human_prompt = f"""Analyze this job description and provide a structured breakdown:

{jd_text}

Please extract:
1. Job title and company (if mentioned)
2. Industry and location
3. Required vs preferred qualifications
4. Technical skills with importance levels
5. Soft skills mentioned
6. Experience requirements (years, specific areas)
7. Key responsibilities
8. Education and certification requirements

Format your response as structured data that can be easily parsed."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = llm.invoke(messages)
            
            # Parse the LLM response into structured format
            return self._parse_jd_analysis(response.content, jd_text)
            
        except Exception as e:
            print(f"LLM JD analysis failed: {str(e)}, using rule-based analysis")
            return self._rule_based_jd_analysis(jd_text)
    
    def match_cv_to_jd(self, cv_state: CVState, jd_analysis: JDAnalysis) -> Dict[str, Any]:
        """
        Match CV against job description and identify gaps.
        
        Args:
            cv_state: Current CV processing state
            jd_analysis: Analyzed job description
            
        Returns:
            Matching analysis with gaps and suggestions
        """
        parsed_sections = cv_state.get("parsed_sections", {})
        
        # Extract CV content for analysis
        cv_content = self._extract_cv_content(parsed_sections)
        
        # Calculate match scores
        match_results = {
            "overall_match_score": 0.0,
            "technical_skills_match": self._match_technical_skills(cv_content, jd_analysis),
            "experience_match": self._match_experience(cv_content, jd_analysis),
            "education_match": self._match_education(cv_content, jd_analysis),
            "missing_keywords": self._find_missing_keywords(cv_content, jd_analysis),
            "matching_keywords": self._find_matching_keywords(cv_content, jd_analysis),
            "gap_analysis": self._analyze_gaps(cv_content, jd_analysis),
            "improvement_priority": self._prioritize_improvements(cv_content, jd_analysis)
        }
        
        # Calculate overall match score
        match_results["overall_match_score"] = self._calculate_overall_match(match_results)
        
        return match_results
    
    def generate_jd_specific_suggestions(self, cv_state: CVState, jd_analysis: JDAnalysis, 
                                       match_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate specific suggestions based on JD analysis and CV matching.
        
        Args:
            cv_state: Current CV state
            jd_analysis: Job description analysis
            match_results: CV-JD matching results
            
        Returns:
            List of specific improvement suggestions
        """
        try:
            llm = init_chat_model(self.model_name, temperature=0.3)
            
            context = self._prepare_jd_context(cv_state, jd_analysis, match_results)
            
            system_prompt = """You are an expert career coach specializing in CV optimization for specific job applications.
            Based on the job description analysis and CV matching results, provide specific, actionable suggestions
            to improve the CV's alignment with the job requirements.
            
            Each suggestion should include:
            1. Specific recommendation
            2. Why it's important for this role
            3. How to implement it
            4. Priority level (high/medium/low)
            5. Expected impact on application success
            
            Focus on the biggest gaps and highest-impact improvements."""
            
            human_prompt = f"""Based on this job analysis and CV matching data, provide 5-8 specific suggestions:

{context}

Provide actionable suggestions in this format:
**Suggestion 1: [Title]**
- **Why**: [Importance for this specific role]
- **Action**: [Specific implementation steps]
- **Priority**: [High/Medium/Low]
- **Impact**: [Expected outcome for this application]
"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = llm.invoke(messages)
            suggestions = self._parse_suggestions_from_response(response.content)
            
            return suggestions
            
        except Exception as e:
            print(f"LLM suggestion generation failed: {str(e)}, using rule-based suggestions")
            return self._generate_rule_based_jd_suggestions(cv_state, jd_analysis, match_results)
    
    def _parse_jd_analysis(self, llm_response: str, original_jd: str) -> JDAnalysis:
        """Parse LLM response into structured JD analysis."""
        # This is a simplified parser - in production, you'd want more robust parsing
        # For now, we'll extract what we can and use rule-based fallback
        
        # Extract job title
        job_title_match = re.search(r'(?i)job\s*title[:\-\s]*(.+)', llm_response)
        job_title = job_title_match.group(1).strip() if job_title_match else "Unknown Position"
        
        # Extract basic info using rule-based approach as fallback
        return self._rule_based_jd_analysis(original_jd, job_title)
    
    def _rule_based_jd_analysis(self, jd_text: str, job_title: str = None) -> JDAnalysis:
        """Rule-based fallback for JD analysis."""
        
        # Extract job title if not provided
        if not job_title:
            title_patterns = [
                r'(?i)job\s*title[:\-\s]*(.+)',
                r'(?i)position[:\-\s]*(.+)',
                r'(?i)role[:\-\s]*(.+)',
            ]
            job_title = "Unknown Position"
            for pattern in title_patterns:
                match = re.search(pattern, jd_text)
                if match:
                    job_title = match.group(1).strip()
                    break
        
        # Extract requirements using keywords
        technical_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'api', 'database', 'machine learning', 'ai', 'cloud'
        ]
        
        soft_skills_keywords = [
            'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
            'collaboration', 'management', 'mentoring', 'presentation', 'strategic'
        ]
        
        requirements = []
        
        # Find technical skills
        jd_lower = jd_text.lower()
        for skill in technical_keywords:
            if skill in jd_lower:
                importance = 'required' if any(req_word in jd_lower for req_word in ['required', 'must have', 'essential']) else 'preferred'
                requirements.append(JobRequirement(
                    category='technical_skills',
                    requirement=skill,
                    importance=importance,
                    keywords=[skill]
                ))
        
        # Find soft skills
        for skill in soft_skills_keywords:
            if skill in jd_lower:
                requirements.append(JobRequirement(
                    category='soft_skills',
                    requirement=skill,
                    importance='preferred',
                    keywords=[skill]
                ))
        
        # Extract experience years
        exp_match = re.search(r'(\d+)[\+\-\s]*(?:years?|yrs?)', jd_text, re.IGNORECASE)
        experience_years = int(exp_match.group(1)) if exp_match else None
        
        return JDAnalysis(
            job_title=job_title,
            company=None,
            industry=None,
            requirements=requirements,
            key_responsibilities=[],
            required_experience_years=experience_years,
            salary_range=None,
            location=None,
            remote_option=None
        )
    
    def _extract_cv_content(self, parsed_sections: Dict) -> str:
        """Extract all CV content as a single string."""
        content_parts = []
        for section_data in parsed_sections.values():
            if isinstance(section_data, dict):
                content_parts.append(section_data.get("content", ""))
        return " ".join(content_parts).lower()
    
    def _match_technical_skills(self, cv_content: str, jd_analysis: JDAnalysis) -> Dict[str, Any]:
        """Match technical skills between CV and JD."""
        tech_requirements = [req for req in jd_analysis.requirements if req.category == 'technical_skills']
        
        matched = []
        missing = []
        
        for req in tech_requirements:
            found = any(keyword.lower() in cv_content for keyword in req.keywords)
            if found:
                matched.append(req.requirement)
            else:
                missing.append(req.requirement)
        
        match_percentage = len(matched) / len(tech_requirements) if tech_requirements else 1.0
        
        return {
            "match_percentage": match_percentage,
            "matched_skills": matched,
            "missing_skills": missing,
            "total_required": len(tech_requirements)
        }
    
    def _match_experience(self, cv_content: str, jd_analysis: JDAnalysis) -> Dict[str, Any]:
        """Match experience requirements."""
        # Simple experience matching - could be enhanced
        exp_patterns = [r'(\d+)[\+\-\s]*(?:years?|yrs?)']
        cv_experience_years = []
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, cv_content)
            cv_experience_years.extend([int(match) for match in matches])
        
        max_cv_experience = max(cv_experience_years) if cv_experience_years else 0
        required_experience = jd_analysis.required_experience_years or 0
        
        meets_requirement = max_cv_experience >= required_experience
        
        return {
            "meets_requirement": meets_requirement,
            "cv_max_experience": max_cv_experience,
            "required_experience": required_experience,
            "gap_years": max(0, required_experience - max_cv_experience)
        }
    
    def _match_education(self, cv_content: str, jd_analysis: JDAnalysis) -> Dict[str, Any]:
        """Match education requirements."""
        education_keywords = ['degree', 'bachelor', 'master', 'phd', 'diploma', 'certification']
        has_education = any(keyword in cv_content for keyword in education_keywords)
        
        return {
            "has_relevant_education": has_education,
            "education_found": has_education
        }
    
    def _find_missing_keywords(self, cv_content: str, jd_analysis: JDAnalysis) -> List[str]:
        """Find JD keywords missing from CV."""
        missing = []
        for req in jd_analysis.requirements:
            if not any(keyword.lower() in cv_content for keyword in req.keywords):
                missing.extend(req.keywords)
        return missing
    
    def _find_matching_keywords(self, cv_content: str, jd_analysis: JDAnalysis) -> List[str]:
        """Find JD keywords present in CV."""
        matching = []
        for req in jd_analysis.requirements:
            for keyword in req.keywords:
                if keyword.lower() in cv_content:
                    matching.append(keyword)
        return matching
    
    def _analyze_gaps(self, cv_content: str, jd_analysis: JDAnalysis) -> List[str]:
        """Identify key gaps between CV and JD."""
        gaps = []
        
        # Technical skills gaps
        tech_match = self._match_technical_skills(cv_content, jd_analysis)
        if tech_match["missing_skills"]:
            gaps.append(f"Missing technical skills: {', '.join(tech_match['missing_skills'][:3])}")
        
        # Experience gaps
        exp_match = self._match_experience(cv_content, jd_analysis)
        if exp_match["gap_years"] > 0:
            gaps.append(f"Experience gap: {exp_match['gap_years']} years short")
        
        return gaps
    
    def _prioritize_improvements(self, cv_content: str, jd_analysis: JDAnalysis) -> List[Dict[str, str]]:
        """Prioritize improvement areas."""
        priorities = []
        
        tech_match = self._match_technical_skills(cv_content, jd_analysis)
        if tech_match["match_percentage"] < 0.7:
            priorities.append({
                "area": "Technical Skills",
                "priority": "high",
                "reason": f"Only {tech_match['match_percentage']:.0%} technical skills match"
            })
        
        return priorities
    
    def _calculate_overall_match(self, match_results: Dict[str, Any]) -> float:
        """Calculate overall match score."""
        tech_score = match_results["technical_skills_match"]["match_percentage"]
        exp_score = 1.0 if match_results["experience_match"]["meets_requirement"] else 0.5
        edu_score = 1.0 if match_results["education_match"]["has_relevant_education"] else 0.7
        
        # Weighted average
        overall_score = (tech_score * 0.5 + exp_score * 0.3 + edu_score * 0.2)
        return overall_score
    
    def _prepare_jd_context(self, cv_state: CVState, jd_analysis: JDAnalysis, 
                           match_results: Dict[str, Any]) -> str:
        """Prepare context string for LLM analysis."""
        context_parts = [
            f"Job Title: {jd_analysis.job_title}",
            f"Overall Match Score: {match_results['overall_match_score']:.1%}",
            f"Technical Skills Match: {match_results['technical_skills_match']['match_percentage']:.1%}",
            f"Missing Skills: {', '.join(match_results['missing_keywords'][:5])}",
            f"Experience Gap: {match_results.get('experience_match', {}).get('gap_years', 0)} years",
            f"Key Gaps: {'; '.join(match_results['gap_analysis'])}",
        ]
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
    
    def _generate_rule_based_jd_suggestions(self, cv_state: CVState, jd_analysis: JDAnalysis, 
                                          match_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate rule-based suggestions as fallback."""
        suggestions = []
        
        # Missing technical skills
        missing_skills = match_results["technical_skills_match"]["missing_skills"]
        if missing_skills:
            suggestions.append({
                "title": f"Add Missing Technical Skills",
                "reason": f"Job requires {', '.join(missing_skills[:3])} which are not highlighted in your CV",
                "action": f"Add a skills section or update existing one to include: {', '.join(missing_skills[:3])}",
                "priority": "high",
                "impact": "Significantly improves ATS matching and recruiter attention"
            })
        
        # Experience gap
        exp_gap = match_results["experience_match"]["gap_years"]
        if exp_gap > 0:
            suggestions.append({
                "title": "Highlight Relevant Experience",
                "reason": f"Position requires {match_results['experience_match']['required_experience']} years experience",
                "action": "Emphasize transferable skills and relevant project experience to bridge the gap",
                "priority": "medium",
                "impact": "Helps compensate for experience requirements"
            })
        
        # Overall match improvement
        if match_results["overall_match_score"] < 0.7:
            suggestions.append({
                "title": "Optimize Keywords for ATS",
                "reason": f"Current match score is {match_results['overall_match_score']:.0%}",
                "action": "Incorporate more keywords from job description throughout your CV",
                "priority": "high",
                "impact": "Improves ATS screening and keyword matching"
            })
        
        return suggestions