import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from github_ingestor import get_competency_map
from jd_analyser import analyse_jd
from fit_scorer import calculate_fit
from cover_letter_generator import generate_cover_letter
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Fitr API")

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Request Bodies ---

class IngestRequest(BaseModel):
    github_url: str

class AnalyseRequest(BaseModel):
    jd_text: str

class FitRequest(BaseModel):
    competency_map: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    github_url: str
    role_summary: str

class FullAnalysisRequest(BaseModel):
    github_url: str
    jd_text: str

# --- Placeholder Functions ---

# mock_fit replaced by calculate_fit from fit_calculator

# --- Routes ---

@app.post("/ingest")
async def ingest_route(request: IngestRequest):
    """
    Accepts {github_url: str}, returns {competency_map: dict}
    """
    try:
        return {"competency_map": get_competency_map(request.github_url)}
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyse")
async def analyse_route(request: AnalyseRequest):
    """
    Accepts {jd_text: str}, returns {hard_skills, nice_to_have, red_flags, legitimacy_score}
    """
    try:
        return analyse_jd(request.jd_text)
    except Exception as e:
        return {"error": str(e)}

@app.post("/fit")
async def fit_route(request: FitRequest):
    """
    Accepts {competency_map: dict, jd_analysis: dict, github_url: str, role_summary: str}, returns {fit_score, matched, missing, recommendation, cover_letter}
    """
    try:
        # Calculate initial fit result
        fit_result = calculate_fit(request.competency_map, request.jd_analysis)
        
        # Generate tailored cover letter
        cover_letter = generate_cover_letter(
            fit_result=fit_result,
            competency_map=request.competency_map,
            role_summary=request.role_summary,
            github_url=request.github_url
        )
        
        # Attach to the final result
        fit_result["cover_letter"] = cover_letter
        return fit_result
    except Exception as e:
        return {"error": str(e)}

@app.post("/full-analysis")
async def full_analysis_route(request: FullAnalysisRequest):
    """
    Accepts {github_url: str, jd_text: str} and runs the full pipeline.
    """
    try:
        # 1. Ingest GitHub profile
        competency_map = get_competency_map(request.github_url)
        if "error" in competency_map:
            return {"error": f"GitHub extraction failed: {competency_map['error']}"}
        
        # 2. Analyse Job Description
        jd_analysis = analyse_jd(request.jd_text)
        if "error" in jd_analysis:
            return {"error": f"JD analysis failed: {jd_analysis['error']}"}
            
        # 3. Calculate Fit and Generate Cover Letter
        fit_result = calculate_fit(competency_map, jd_analysis)
        
        cover_letter = generate_cover_letter(
            fit_result=fit_result,
            competency_map=competency_map,
            role_summary=jd_analysis.get('role_summary', 'open role'),
            github_url=request.github_url
        )
        
        fit_result["cover_letter"] = cover_letter
        
        return {
            "github_competency": competency_map,
            "jd_analysis": jd_analysis,
            "fit_analysis": fit_result
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/demo")
async def demo_route():
    """
    Returns a mocked full analysis response for demonstration purposes.
    """
    return {
        "github_competency": {
            "python": 0.95,
            "javascript": 0.05,
            "backend": 1.0,
            "fastapi": 1.0
        },
        "jd_analysis": {
            "hard_skills": ["python", "fastapi", "docker", "sql"],
            "nice_to_have": ["aws", "kubernetes"],
            "role_summary": "Backend Engineering Intern (Python)",
            "stipend": "$3000/month",
            "red_flags": [],
            "legitimacy_score": 100
        },
        "fit_analysis": {
            "fit_score": 88,
            "hard_matched": ["python", "fastapi"],
            "hard_missing": ["docker", "sql"],
            "soft_matched": [],
            "recommendation": "YES — Apply with confidence",
            "cover_letter": "Dear Hiring Manager,\n\nI am writing to express my strong interest in the Backend Engineering Intern position. Based on my GitHub projects, I have demonstrated solid capability in Python and FastAPI.\n\nWhile I am actively learning Docker and SQL, my strong foundation in backend engineering will allow me to ramp up quickly and contribute to your team.\n\nI would welcome the opportunity to discuss how my skills align with your needs.\n\nBest regards,\nDemo Candidate"
        }
    }

if __name__ == "__main__":
    import uvicorn
    # Make sure to run the app using `python main.py` or `uvicorn main:app --reload`
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
