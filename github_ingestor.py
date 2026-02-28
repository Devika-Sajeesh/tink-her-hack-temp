import os
import re
from typing import Dict, Any, List, Tuple, Set, Iterable
from github import Github, GithubException

PACKAGE_SKILL_MAP = {
    # Backend
    'fastapi': 'backend', 'flask': 'backend', 'django': 'backend',
    'djangorestframework': 'backend', 'starlette': 'backend',
    'requests': 'backend', 'aiohttp': 'backend', 'httpx': 'backend',
    'uvicorn': 'backend', 'gunicorn': 'backend', 'tornado': 'backend',
    'bottle': 'backend', 'sanic': 'backend', 'falcon': 'backend',
    'pydantic': 'backend', 'sqlalchemy': 'backend', 'alembic': 'backend',
    'celery': 'backend', 'redis': 'backend', 'pymongo': 'backend',
    'psycopg2': 'backend', 'asyncpg': 'backend', 'motor': 'backend',

    # Frontend
    'react': 'frontend', 'vue': 'frontend', 'angular': 'frontend',
    'svelte': 'frontend', 'nextjs': 'frontend', 'nuxtjs': 'frontend',
    'tailwindcss': 'frontend', 'bootstrap': 'frontend',
    'webpack': 'frontend', 'vite': 'frontend', 'parcel': 'frontend',
    'axios': 'frontend', 'jquery': 'frontend',

    # NLP
    'transformers': 'nlp', 'spacy': 'nlp', 'nltk': 'nlp',
    'gensim': 'nlp', 'textblob': 'nlp', 'sentence-transformers': 'nlp',
    'tokenizers': 'nlp', 'datasets': 'nlp', 'evaluate': 'nlp',
    'huggingface-hub': 'nlp', 'bert': 'nlp', 'flair': 'nlp',
    'stanza': 'nlp', 'allennlp': 'nlp', 'fasttext': 'nlp',

    # Computer Vision
    'opencv-python': 'computer-vision', 'cv2': 'computer-vision',
    'pillow': 'computer-vision', 'scikit-image': 'computer-vision',
    'imageio': 'computer-vision', 'albumentations': 'computer-vision',
    'torchvision': 'computer-vision', 'detectron2': 'computer-vision',
    'mediapipe': 'computer-vision', 'pytesseract': 'computer-vision',
    'easyocr': 'computer-vision', 'ultralytics': 'computer-vision',
    'imgaug': 'computer-vision', 'mahotas': 'computer-vision',

    # Deep Learning
    'torch': 'deep-learning', 'tensorflow': 'deep-learning',
    'keras': 'deep-learning', 'jax': 'deep-learning',
    'flax': 'deep-learning', 'paddle': 'deep-learning',
    'mxnet': 'deep-learning', 'caffe': 'deep-learning',
    'lightning': 'deep-learning', 'pytorch-lightning': 'deep-learning',
    'timm': 'deep-learning', 'einops': 'deep-learning',
    'onnx': 'deep-learning', 'onnxruntime': 'deep-learning',
    'tensorboard': 'deep-learning', 'wandb': 'deep-learning',

    # ML
    'scikit-learn': 'ml', 'numpy': 'ml', 'pandas': 'ml',
    'scipy': 'ml', 'statsmodels': 'ml', 'xgboost': 'ml',
    'lightgbm': 'ml', 'catboost': 'ml', 'optuna': 'ml',
    'mlflow': 'ml', 'joblib': 'ml', 'imbalanced-learn': 'ml',
    'shap': 'ml', 'lime': 'ml', 'yellowbrick': 'ml',
    'feature-engine': 'ml', 'boruta': 'ml', 'eli5': 'ml',

    # LLM / Agents
    'langchain': 'llm-agents', 'openai': 'llm-agents',
    'langchain-core': 'llm-agents', 'langchain-community': 'llm-agents',
    'langchain-groq': 'llm-agents', 'langchain-google-genai': 'llm-agents',
    'langchain-openai': 'llm-agents', 'langgraph': 'llm-agents',
    'llama-index': 'llm-agents', 'llama-cpp-python': 'llm-agents',
    'anthropic': 'llm-agents', 'groq': 'llm-agents',
    'google-generativeai': 'llm-agents', 'cohere': 'llm-agents',
    'guidance': 'llm-agents', 'outlines': 'llm-agents',
    'instructor': 'llm-agents', 'dspy': 'llm-agents',
    'autogen': 'llm-agents', 'crewai': 'llm-agents',
    'semantic-kernel': 'llm-agents', 'haystack': 'llm-agents',

    # Cloud / DevOps
    'boto3': 'cloud', 'azure-sdk': 'cloud', 'google-cloud': 'cloud',
    'google-cloud-storage': 'cloud', 'google-cloud-bigquery': 'cloud',
    'azure-storage-blob': 'cloud', 'paramiko': 'cloud',
    'docker': 'devops', 'kubernetes': 'devops', 'ansible': 'devops',
    'terraform': 'devops', 'pulumi': 'devops',
    'github-actions': 'devops', 'fabric': 'devops',

    # Data Engineering
    'apache-airflow': 'data-engineering', 'airflow': 'data-engineering',
    'pyspark': 'data-engineering', 'dask': 'data-engineering',
    'prefect': 'data-engineering', 'dagster': 'data-engineering',
    'great-expectations': 'data-engineering', 'dbt': 'data-engineering',
    'kafka-python': 'data-engineering', 'confluent-kafka': 'data-engineering',
    'pyarrow': 'data-engineering', 'polars': 'data-engineering',

    # Data Visualisation
    'matplotlib': 'data-viz', 'seaborn': 'data-viz',
    'plotly': 'data-viz', 'bokeh': 'data-viz',
    'altair': 'data-viz', 'dash': 'data-viz',
    'streamlit': 'data-viz', 'gradio': 'data-viz',

    # Mobile
    'kivy': 'mobile', 'kivymd': 'mobile',
    'flutter': 'mobile', 'react-native': 'mobile',

    # Desktop / GUI
    'pyqt5': 'desktop', 'pyqt6': 'desktop', 'pyside6': 'desktop',
    'tkinter': 'desktop', 'wxpython': 'desktop', 'pygame': 'desktop',
    'pyglet': 'desktop', 'customtkinter': 'desktop',

    # Security / Scraping
    'scrapy': 'scraping', 'beautifulsoup4': 'scraping',
    'selenium': 'scraping', 'playwright': 'scraping',
    'mechanize': 'scraping', 'httplib2': 'scraping',
    'cryptography': 'security', 'pyjwt': 'security',
    'passlib': 'security', 'python-jose': 'security',

    # Testing
    'pytest': 'testing', 'unittest': 'testing',
    'hypothesis': 'testing', 'faker': 'testing',
    'coverage': 'testing', 'tox': 'testing',
}

def extract_username(url: str) -> str:
    url = url.rstrip('/')
    return url.split('/')[-1]

def authenticate_github(github_url: str) -> Github:
    username = extract_username(github_url)
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Warning: GITHUB_TOKEN not found in environment.")
        return Github()
    else:
        return Github(token)

def get_repos(g: Github, username: str) -> Any:
    user = g.get_user(username)
    return user.get_repos()

def extract_language_info(repos: Any) -> Tuple[Dict[str, int], Dict[str, int], Set[str], int]:
    language_bytes = {}
    language_repos = {}
    package_skills = set()
    total_repos = 0
    for repo in repos:
        try:
            total_repos += 1
            langs = repo.get_languages()
            for lang, b in langs.items():
                language_bytes[lang] = language_bytes.get(lang, 0) + b
                language_repos[lang] = language_repos.get(lang, 0) + 1

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
                total_repos -= 1 # adjust if we failed to fetch
                continue
            raise e
    return language_bytes, language_repos, package_skills, total_repos

def calculate_language_scores(language_bytes: Dict[str, int], language_repos: Dict[str, int], total_repos: int, total_bytes: int, package_skills: Set[str]) -> Dict[str, float]:
    final_scores = {}
    if total_repos > 0 and total_bytes > 0:
        for lang in language_bytes.keys():
            repo_fraction = language_repos[lang] / total_repos
            bytes_fraction = language_bytes[lang] / total_bytes
            score = (repo_fraction * 0.7) + (bytes_fraction * 0.3)
            if score >= 0.05:
                final_scores[lang] = round(score, 2)
    for skill in package_skills:
        final_scores[skill] = 1.0
    return dict(sorted(final_scores.items(), key=lambda item: item[1], reverse=True))

def get_competency_map(github_url: str) -> Dict[str, float]:
    g = authenticate_github(github_url)
    username = extract_username(github_url)
    try:
        repos = get_repos(g, username)
        language_bytes, language_repos, package_skills, total_repos = extract_language_info(repos)
        total_bytes = sum(language_bytes.values()) if language_bytes else 0
        return calculate_language_scores(language_bytes, language_repos, total_repos, total_bytes, package_skills)
    except GithubException as e:
        print(f"GitHub API Error: {e}")
        return {"error": f"Failed to fetch data for {username}"}
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {"error": str(e)}
