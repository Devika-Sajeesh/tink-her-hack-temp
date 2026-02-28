import io
from typing import Set

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def extract_resume_skills(pdf_bytes: bytes) -> Set[str]:
    """
    Reads a PDF from bytes, extracts text, and returns a set of matched skill categories.
    Returns an empty set if PyPDF2 is unavailable or if parsing fails.
    """
    if PyPDF2 is None:
        print("Warning: PyPDF2 is not installed. Cannot parse resume.")
        return set()

    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        
        text_lower = text.lower()
        matched_categories = set()
        
        skill_keywords = {
            "python": "Python",
            "javascript": "JavaScript", 
            "react": "frontend",
            "fastapi": "backend",
            "flask": "backend",
            "django": "backend",
            "machine learning": "ml",
            "deep learning": "deep-learning",
            "nlp": "nlp",
            "natural language": "nlp",
            "computer vision": "computer-vision",
            "opencv": "computer-vision",
            "tensorflow": "deep-learning",
            "pytorch": "deep-learning",
            "langchain": "llm-agents",
            "large language": "llm-agents",
            "llm": "llm-agents",
            "docker": "devops",
            "kubernetes": "devops",
            "aws": "cloud",
            "azure": "cloud",
            "sql": "backend",
            "postgresql": "backend",
            "mongodb": "backend",
            "git": "devops",
            "rest api": "backend",
            "node": "backend",
            "java": "Java",
            "c++": "C++",
            "data analysis": "ml",
            "pandas": "ml",
            "numpy": "ml",
        }
        
        for keyword, category in skill_keywords.items():
            if keyword in text_lower:
                matched_categories.add(category)
                
        return matched_categories

    except Exception as e:
        print(f"Failed to parse PDF resume: {e}")
        return set()
