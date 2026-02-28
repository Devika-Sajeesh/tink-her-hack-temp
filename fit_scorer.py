from typing import Dict, Any, List

ALIASES = {
    "ai/ml": ["python", "ml", "deep-learning", "scikit-learn", "tensorflow", "torch", "nlp"],
    "llm / agentic ai": ["langchain", "llm-agents", "transformers", "nlp", "openai"],
    "rest apis": ["backend", "fastapi", "flask", "django"],
    "cloud platforms": ["aws", "azure", "gcp", "cloud"],
    "docker": ["docker", "container"],
    "kubernetes": ["kubernetes", "k8s"],
    "python": ["python", "Python"]
}

def matches(skill: str, competency_map: Dict[str, float]) -> bool:
    """Fuzzy match against explicit aliases or partial lowercase string match."""
    skill_lower = skill.lower()
    
    # Get all variations to look for (itself + any aliases)
    search_terms = ALIASES.get(skill_lower, [skill_lower])
    if skill_lower not in search_terms:
        search_terms.append(skill_lower)
        
    for term in search_terms:
        for comp_skill, score in competency_map.items():
            if term in comp_skill.lower() and score > 0.1:
                return True
                
    return False

def calculate_fit(competency_map: Dict[str, Any], jd_analysis: Dict[str, Any]) -> Dict[str, Any]:
    hard_skills: List[str] = jd_analysis.get('hard_skills', [])
    nice_to_have: List[str] = jd_analysis.get('nice_to_have', [])
    legitimacy_score: int = jd_analysis.get('legitimacy_score', 0)
    
    hard_matched = [s for s in hard_skills if matches(s, competency_map)]
    soft_matched = [s for s in nice_to_have if matches(s, competency_map)]
    hard_missing = [s for s in hard_skills if not matches(s, competency_map)]

    hard_score = (len(hard_matched) / max(len(hard_skills), 1)) * 60
    soft_score = (len(soft_matched) / max(len(nice_to_have), 1)) * 25
    legit_score = legitimacy_score * 0.15

    fit_score = round(hard_score + soft_score + legit_score)
    
    if fit_score >= 70:
        recommendation = "YES — Apply with confidence"
    elif fit_score >= 50:
        recommendation = "BORDERLINE — Address the gaps in cover letter"
    else:
        recommendation = "NO — Skill gap too large or suspicious posting"
        
    return {
        "fit_score": fit_score,
        "hard_matched": hard_matched,
        "hard_missing": hard_missing,
        "soft_matched": soft_matched,
        "recommendation": recommendation,
        "legitimacy_score": legitimacy_score
    }
