import time
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from typing import Dict, Any

def generate_cover_letter(fit_result: Dict[str, Any], competency_map: Dict[str, float], role_summary: str, github_url: str) -> str:
    # Extract top 3 skills by score
    sorted_skills = sorted(competency_map.items(), key=lambda item: item[1], reverse=True)
    top_3_skills = ", ".join([skill[0] for skill in sorted_skills[:3]])
    
    # Extract GitHub username
    username = github_url.rstrip('/').split('/')[-1]
    
    # Extract gap skill if it exists
    hard_missing = fit_result.get('hard_missing', [])
    gap_skill = hard_missing[0] if hard_missing else None
    
    gap_instruction = f"Address this skill gap constructively: {gap_skill}" if gap_skill else ""
    
    prompt_template = """Write a confident, specific cover letter for a {role_summary} internship.

Format the cover letter structurally with excellent spacing:
- Use a professional greeting (e.g., Dear Hiring Manager,)
- Separate paragraphs with double newlines.
- If highlighting specific capabilities, use a bulleted list (with dashes "-").
- End with a professional sign-off (e.g., Sincerely,\nCandidate)

Details to include:
- Mention these proven skills from the candidate's GitHub: {top_3_skills}
- Reference their GitHub profile explicitly: {github_url}
- {gap_instruction}

Rules: 
- Be direct and professional. No fluff. 
- Lead with capability and evidence from GitHub. 
- Keep it concise, around 150-200 words.
- Do not use markdown formatting like bolding (**), just return beautifully spaced plain text."""

    prompt = PromptTemplate(
        template=prompt_template, 
        input_variables=["role_summary", "top_3_skills", "github_url", "username", "gap_instruction"]
    )
    
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3
        )
        chain = prompt | llm
        
        response = None
        for attempt in range(3):
            try:
                response = chain.invoke({
                    "role_summary": role_summary,
                    "top_3_skills": top_3_skills,
                    "github_url": github_url,
                    "username": username,
                    "gap_instruction": gap_instruction
                })
                break
            except Exception as e:
                if '429' in str(e) and attempt < 2:
                    time.sleep(15)
                    continue
                raise e
                
        if response is None:
            raise Exception("LLM generation failed after retries.")
            
        return response.content.strip()
        
    except Exception as e:
        print(f"Failed to generate cover letter: {e}")
        return "Dear Hiring Manager,\n\nI am writing to express my strong interest in this position. Please find my qualifications attached.\n\nSincerely,\nCandidate"
