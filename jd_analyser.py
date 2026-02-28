import json
import time
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

def analyse_jd(jd_text: str) -> dict:
    jd_text = jd_text.strip()
    jd_text = jd_text.replace('\r\n', ' ')
    jd_text = jd_text.replace('\n', ' ')
    jd_text = jd_text.replace('\t', ' ')
    prompt_template = """You are a hiring manager. Analyse this job description and return ONLY valid JSON with these keys:
- hard_skills: list of must-have skills (strings)
- nice_to_have: list of preferred skills (strings)
- quick_learn_skills: list of skills from the above requirements that a candidate could realistically learn the basics of in under 2 weeks (e.g., a specific library, a straightforward API, or basic tool, rather than an entire paradigm or language).
- role_summary: one sentence description
- stipend: extracted stipend or 'not mentioned'

Job Description: {jd_text}
"""

    prompt = PromptTemplate.from_template(prompt_template)

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
                response = chain.invoke({"jd_text": jd_text})
                break
            except Exception as e:
                if '429' in str(e) and attempt < 2:
                    time.sleep(15)
                    continue
                raise e
                
        if response is None:
             raise Exception("LLM generation failed after retries.")

        content = response.content.strip()

        # Clean markdown blocks if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()
        llm_data = json.loads(content)

        llm_data.setdefault("hard_skills", [])
        llm_data.setdefault("nice_to_have", [])
        llm_data.setdefault("quick_learn_skills", [])
        llm_data.setdefault("role_summary", "")
        llm_data.setdefault("stipend", "not mentioned")

    except Exception as e:
        print(f"LLM or JSON parsing failed: {e}")
        llm_data = {
            "hard_skills": [],
            "nice_to_have": [],
            "quick_learn_skills": [],
            "role_summary": "Error parsing JD",
            "stipend": "not mentioned"
        }

    red_flag_keywords = [
        'registration fee', 'training fee', 'pay to apply',
        'performance based stipend', 'unpaid mandatory',
        'no stipend', 'portfolio fee'
    ]

    jd_lower = jd_text.lower()
    red_flags = [kw for kw in red_flag_keywords if kw in jd_lower]
    legitimacy_score = max(0, 100 - len(red_flags) * 15)

    result = {**llm_data}
    result["red_flags"] = red_flags
    result["legitimacy_score"] = legitimacy_score

    return result