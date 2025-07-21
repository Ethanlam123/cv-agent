import re
from typing import Dict, List, Set
from ..models.state import CVSection, AnalysisScore


class CVAnalyzer:
    """Analyzer for CV content quality and ATS compatibility."""
    
    def __init__(self):
        # Common industry keywords for different domains
        self.industry_keywords = {
            'technology': [
                'python', 'java', 'javascript', 'react', 'node.js', 'aws', 'docker', 
                'kubernetes', 'sql', 'mongodb', 'api', 'microservices', 'agile', 
                'scrum', 'git', 'ci/cd', 'devops', 'machine learning', 'ai'
            ],
            'marketing': [
                'seo', 'sem', 'google analytics', 'social media', 'content marketing',
                'campaign management', 'lead generation', 'conversion optimization',
                'brand management', 'market research', 'digital marketing'
            ],
            'finance': [
                'financial analysis', 'budgeting', 'forecasting', 'excel', 'financial modeling',
                'risk management', 'compliance', 'audit', 'tax', 'investment analysis'
            ]
        }
        
        # ATS-friendly formatting patterns
        self.ats_patterns = {
            'bullet_points': r'[•·▪▫◦‣⁃]|\*\s|\-\s|^\d+\.\s',
            'dates': r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{1,2}\/\d{1,2}\/\d{2,4}|\d{4})\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        }
    
    def analyze_content_quality(self, sections: Dict[str, CVSection]) -> Dict[str, float]:
        """Analyze content quality for each section."""
        scores = {}
        
        for section_name, section in sections.items():
            content = section.content.lower()
            score = 0.0
            
            # Length check (not too short, not too long)
            word_count = len(content.split())
            if section_name == 'summary':
                score += min(word_count / 50, 1.0) * 0.3  # Ideal: 30-50 words
            elif section_name == 'experience':
                score += min(word_count / 200, 1.0) * 0.3  # More detailed for experience
            else:
                score += min(word_count / 30, 1.0) * 0.3
            
            # Action verbs check
            action_verbs = [
                'achieved', 'developed', 'managed', 'led', 'created', 'implemented',
                'improved', 'increased', 'reduced', 'optimized', 'delivered',
                'collaborated', 'designed', 'built', 'analyzed', 'executed'
            ]
            action_verb_count = sum(1 for verb in action_verbs if verb in content)
            score += min(action_verb_count / 5, 1.0) * 0.3
            
            # Quantified achievements check
            numbers_pattern = r'\b\d+%|\b\d+\s*(million|thousand|k|m)\b|\$\d+|\b\d+\+\b'
            quantified_count = len(re.findall(numbers_pattern, content, re.IGNORECASE))
            score += min(quantified_count / 3, 1.0) * 0.4
            
            scores[section_name] = min(score, 1.0)
        
        return scores
    
    def check_ats_compatibility(self, raw_text: str) -> float:
        """Check ATS compatibility of the CV format."""
        score = 0.0
        
        # Check for standard contact information
        if re.search(self.ats_patterns['email'], raw_text, re.IGNORECASE):
            score += 0.2
        if re.search(self.ats_patterns['phone'], raw_text):
            score += 0.2
        
        # Check for proper date formatting
        date_matches = len(re.findall(self.ats_patterns['dates'], raw_text, re.IGNORECASE))
        score += min(date_matches / 5, 1.0) * 0.2
        
        # Check for bullet points usage
        bullet_matches = len(re.findall(self.ats_patterns['bullet_points'], raw_text, re.MULTILINE))
        score += min(bullet_matches / 10, 1.0) * 0.2
        
        # Check for proper section headers
        section_headers = [
            'experience', 'education', 'skills', 'summary', 'contact',
            'projects', 'certifications', 'achievements'
        ]
        header_count = sum(1 for header in section_headers 
                          if re.search(rf'\b{header}\b', raw_text, re.IGNORECASE))
        score += min(header_count / 5, 1.0) * 0.2
        
        return min(score, 1.0)
    
    def calculate_keyword_density(self, content: str, target_industry: str = None) -> float:
        """Calculate keyword density for industry relevance."""
        if not target_industry or target_industry.lower() not in self.industry_keywords:
            # Use general scoring if no industry specified
            return 0.5
        
        content_lower = content.lower()
        industry_words = self.industry_keywords[target_industry.lower()]
        
        found_keywords = sum(1 for keyword in industry_words if keyword in content_lower)
        density = found_keywords / len(industry_words)
        
        return min(density, 1.0)
    
    def analyze_formatting(self, raw_text: str) -> float:
        """Analyze overall formatting quality."""
        score = 0.0
        
        lines = raw_text.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        # Consistent formatting check
        if len(non_empty_lines) > 10:
            score += 0.3
        
        # Appropriate use of whitespace
        if len(lines) > len(non_empty_lines) * 1.2:  # Some empty lines for spacing
            score += 0.2
        
        # Length appropriateness (1-2 pages typically)
        word_count = len(raw_text.split())
        if 300 <= word_count <= 800:
            score += 0.3
        elif word_count < 300:
            score += 0.1
        
        # Professional tone indicators
        professional_indicators = ['experience', 'skills', 'education', 'professional', 'career']
        professional_count = sum(1 for indicator in professional_indicators 
                                if indicator in raw_text.lower())
        score += min(professional_count / 3, 1.0) * 0.2
        
        return min(score, 1.0)
    
    def identify_gaps(self, sections: Dict[str, CVSection]) -> List[str]:
        """Identify missing or weak sections in the CV."""
        gaps = []
        
        essential_sections = ['experience', 'skills', 'education']
        recommended_sections = ['summary', 'contact']
        
        # Check for missing essential sections
        for section in essential_sections:
            if section not in sections:
                gaps.append(f"Missing essential section: {section}")
            elif len(sections[section].content.split()) < 10:
                gaps.append(f"Insufficient content in {section} section")
        
        # Check for missing recommended sections
        for section in recommended_sections:
            if section not in sections:
                gaps.append(f"Consider adding {section} section")
        
        # Check for weak content indicators
        if 'experience' in sections:
            exp_content = sections['experience'].content.lower()
            if not re.search(r'\d+\s*(year|month)', exp_content):
                gaps.append("Experience section lacks duration information")
            if not re.search(r'[•·▪▫◦‣⁃]|\*\s|\-\s', sections['experience'].content):
                gaps.append("Experience section would benefit from bullet points")
        
        if 'skills' in sections:
            skills_content = sections['skills'].content
            if len(skills_content.split(',')) < 5:
                gaps.append("Skills section appears limited - consider adding more relevant skills")
        
        return gaps
    
    def generate_analysis_score(self, sections: Dict[str, CVSection], 
                              raw_text: str, target_industry: str = None) -> AnalysisScore:
        """Generate comprehensive analysis score for the CV."""
        
        # Calculate individual scores
        section_scores = self.analyze_content_quality(sections)
        ats_score = self.check_ats_compatibility(raw_text)
        keyword_score = self.calculate_keyword_density(raw_text, target_industry)
        formatting_score = self.analyze_formatting(raw_text)
        
        # Calculate overall score (weighted average)
        content_weight = 0.4
        ats_weight = 0.25
        keyword_weight = 0.2
        format_weight = 0.15
        
        avg_section_score = sum(section_scores.values()) / len(section_scores) if section_scores else 0
        overall_score = (
            avg_section_score * content_weight +
            ats_score * ats_weight +
            keyword_score * keyword_weight +
            formatting_score * format_weight
        )
        
        return AnalysisScore(
            overall_score=round(overall_score, 3),
            section_scores=section_scores,
            ats_compatibility=round(ats_score, 3),
            keyword_density=round(keyword_score, 3),
            formatting_score=round(formatting_score, 3),
            content_quality=round(avg_section_score, 3)
        )