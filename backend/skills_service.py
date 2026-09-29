"""
skills_service.py
-----------------
Comprehensive skill catalog, extraction, categorization, and gap analysis
for SkillPath AI.
"""

import re
from typing import Dict, List, Tuple
from data import ROLE_SKILLS, TOPICS
from roles_config import filter_gaps_with_prerequisites, get_role_config

# Categorized Skill Taxonomy
SKILL_CATEGORIES: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "C++", "Java", "Go", "Rust", "Scala", "C#", "R", "SQL", "Bash"
    ],
    "Frontend Development": [
        "React", "Vue", "Angular", "HTML", "CSS", "Next.js", "Redux", "Tailwind CSS", "Bootstrap", "Webpack", "Vite"
    ],
    "Backend Development": [
        "FastAPI", "Node.js", "Express", "Django", "Flask", "Spring Boot", "REST API", "GraphQL", "Microservices"
    ],
    "Databases & Storage": [
        "PostgreSQL", "MongoDB", "MySQL", "Redis", "SQLite", "Cassandra", "Elasticsearch", "Neo4j", "DynamoDB"
    ],
    "AI & Machine Learning": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow", "PyTorch",
        "Scikit-learn", "Keras", "HuggingFace", "LLMs", "Generative AI", "Reinforcement Learning"
    ],
    "Data Engineering": [
        "Pandas", "NumPy", "Spark", "Kafka", "Hadoop", "Airflow", "ETL", "Data Pipelines", "Snowflake", "BigQuery"
    ],
    "Cloud & DevOps": [
        "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Git", "GitHub", "CI/CD", "Linux", "Terraform",
        "Ansible", "Prometheus", "Grafana", "Jenkins", "GitHub Actions", "DevSecOps", "Networking", "MLOps"
    ],
    "QA & Testing": [
        "Selenium", "Cypress", "Pytest", "Jest", "Postman", "API Testing", "Unit Testing", "Jira", "Manual Testing"
    ],
    "Architecture & Foundations": [
        "System Design", "Distributed Systems", "Design Patterns", "SOLID", "Statistics", "Linear Algebra", "Data Structures"
    ]
}

# Flattened set for quick lookup
ALL_TAXONOMY_SKILLS = [skill for cat, skills in SKILL_CATEGORIES.items() for skill in skills]

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extracts recognizable tech skills from raw text using boundary-aware regex.
    """
    if not text:
        return ["Python", "Machine Learning"]

    found_skills = set()
    for skill in ALL_TAXONOMY_SKILLS:
        # Match whole word / skill name (handling symbols like C++, .js, etc.)
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.add(skill)

    result = sorted(list(found_skills))
    return result if result else ["Python", "Machine Learning"]

def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """
    Groups a flat list of extracted skills into logical categories.
    """
    categorized: Dict[str, List[str]] = {}
    skills_set = set(s.lower() for s in (skills or []))

    for category, cat_skills in SKILL_CATEGORIES.items():
        matched = [s for s in cat_skills if s.lower() in skills_set]
        if matched:
            categorized[category] = matched

    return categorized

def compute_skill_gap(existing_skills: List[str], target_role: str) -> Dict:
    """
    Compares existing resume skills against target role required skills.
    Returns already_have, missing (gaps), match percentage, and prerequisite-ordered roadmap items.
    """
    role_conf = get_role_config(target_role)
    role_requirements = role_conf.get("skills", [
        "Python", "Machine Learning", "Deep Learning", "Docker", "Git", "Statistics"
    ])

    existing_lower = {s.lower().strip() for s in (existing_skills or [])}

    already_have = []
    missing = []

    for req in role_requirements:
        req_clean = req.lower().strip()
        # Flexible matching (e.g. AWS matches AWS Cloud, Git matches GitHub)
        matched = (req_clean in existing_lower) or any(req_clean in s or s in req_clean for s in existing_lower)
        if matched:
            already_have.append(req)
        else:
            missing.append(req)

    total_req = len(role_requirements)
    match_pct = int((len(already_have) / total_req * 100)) if total_req > 0 else 0

    # Prerequisite-aware roadmap calculation
    roadmap_analysis = filter_gaps_with_prerequisites(target_role, existing_skills, [])

    return {
        "target_role": target_role,
        "already_have": already_have,
        "missing": missing,
        "match_percentage": match_pct,
        "total_required": total_req,
        "acquired_count": len(already_have),
        "gap_count": len(missing),
        "role_category": role_conf.get("category", "Technology"),
        "role_description": role_conf.get("description", ""),
        "roadmap_milestones": roadmap_analysis
    }

