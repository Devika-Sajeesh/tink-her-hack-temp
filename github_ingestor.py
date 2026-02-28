import os
import re
from typing import Dict, Any
from github import Github, GithubException

PACKAGE_SKILL_MAP = {
    'fastapi': 'backend', 'flask': 'backend', 'django': 'backend',
    'requests': 'backend', 'aiohttp': 'backend',
    'transformers': 'nlp', 'spacy': 'nlp', 'nltk': 'nlp',
    'opencv-python': 'computer-vision', 
    'torch': 'deep-learning', 'tensorflow': 'deep-learning', 
    'react': 'frontend',
    'langchain': 'llm-agents', 'openai': 'llm-agents',
    'scikit-learn': 'ml', 'numpy': 'ml', 'pandas': 'ml'
}

def extract_username(url: str) -> str:
    url = url.rstrip('/')
    return url.split('/')[-1]

def get_competency_map(github_url: str) -> Dict[str, float]:
    username = extract_username(github_url)
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        print("Warning: GITHUB_TOKEN not found in environment.")
        g = Github() # Unauthenticated, low rate limit
    else:
        g = Github(token)
    
    language_bytes = {}
    language_repos = {}
    package_skills = set()
    total_repos = 0
    
    try:
        user = g.get_user(username)
        repos = user.get_repos()
        
        for repo in repos:
            try:
                total_repos += 1
                # 1. Get Languages
                langs = repo.get_languages()
                for lang, b in langs.items():
                    language_bytes[lang] = language_bytes.get(lang, 0) + b
                    language_repos[lang] = language_repos.get(lang, 0) + 1
                    
                # 2. Get requirements.txt for packages
                req_file = repo.get_contents("requirements.txt")
                if not isinstance(req_file, list):
                    content = req_file.decoded_content.decode('utf-8')
                    for line in content.splitlines():
                        pkg_match = re.split(r'==|>=|<=|>|<|~=|\s|;', line.strip())
                        if pkg_match:
                            pkg_name = pkg_match[0].lower()
                            if pkg_name in PACKAGE_SKILL_MAP:
                                package_skills.add(PACKAGE_SKILL_MAP[pkg_name])
                                
            except GithubException as e:
                if e.status in [403, 404]:
                    continue
                raise e

        total_bytes = sum(language_bytes.values()) if language_bytes else 0
        final_scores = {}
        
        if total_repos > 0 and total_bytes > 0:
            for lang in language_bytes.keys():
                repo_fraction = language_repos[lang] / total_repos
                bytes_fraction = language_bytes[lang] / total_bytes
                score = (repo_fraction * 0.7) + (bytes_fraction * 0.3)
                
                # Filter out noise
                if score >= 0.05:
                    final_scores[lang] = round(score, 2)
                
        # Merge package skills to final dict, we'll assign confidence 1.0
        for skill in package_skills:
            final_scores[skill] = 1.0
            
        # Return sorted dict descending
        return dict(sorted(final_scores.items(), key=lambda item: item[1], reverse=True))
        
    except GithubException as e:
        print(f"GitHub API Error: {e}")
        return {"error": f"Failed to fetch data for {username}"}
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {"error": str(e)}
