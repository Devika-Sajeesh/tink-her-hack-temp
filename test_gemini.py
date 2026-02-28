import os
import json
import traceback
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

jd_text = """Company Description:

Sroniyan Technology is a global Indian company, known for its expertise in artificial intelligence, internet-related services, and software products. Since its inception in 2014 and official founding in 2018, the company has been at the forefront of innovative solutions in areas such as machine learning, deep learning, natural language processing, and cloud computing implementation.

Role Description:

We are looking for a motivated and enthusiastic Junior AI Engineer to support our team in building AI/ML solutions and LLM/Agentic AI applications.

Mandatory Skills: 
Minimum 1 year hands-on experience in AI/ML (mandatory).
Minimum 1 year hands-on experience in LLM / Agentic AI (mandatory).
2–3 years hands-on Python experience with strong coding basics.

Stipend: $3000/month"""

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

prompt_template = """You are a hiring manager. Analyse this job description and return ONLY valid JSON with these keys:
- hard_skills: list of must-have skills (strings)
- nice_to_have: list of preferred skills (strings)
- role_summary: one sentence description
- stipend: extracted stipend or 'not mentioned'

Job Description: {jd_text}"""

prompt = PromptTemplate.from_template(prompt_template)
chain = prompt | llm

try:
    print("Invoking chain...")
    response = chain.invoke({"jd_text": jd_text})
    print("\nRAW LLM RESPONSE:")
    print(repr(response.content))
    
    content = response.content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    print("\nCLEANED CONTENT:")
    print(repr(content))
    
    parsed = json.loads(content)
    print("\nPARSED JSON:")
    print(json.dumps(parsed, indent=2))
except Exception as e:
    print("\nERROR TRACEBACK:")
    traceback.print_exc()
