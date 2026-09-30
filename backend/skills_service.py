"""
skills_service.py
-----------------
Comprehensive skill catalog, extraction, categorization, and gap analysis
for SkillPath AI.
"""

import re
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional, Any, Set
from data import ROLE_SKILLS, TOPICS, MODULE_KEYS
from roles_config import (
    filter_gaps_with_prerequisites, get_role_config,
    DSA_MODULE_KEYS, DSA_MODULE_ALIASES
)

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


def normalize_skill_string(s: str) -> str:
    """Strip punctuation, spaces, and lowercase for robust fuzzy skill matching."""
    if not s:
        return ""
    return re.sub(r'[^a-z0-9+#]', '', s.lower().strip())


def skills_match(skill_a: str, skill_b: str) -> bool:
    """Checks if two skill strings represent the same technical skill."""
    norm_a = normalize_skill_string(skill_a)
    norm_b = normalize_skill_string(skill_b)
    if not norm_a or not norm_b:
        return False
    if norm_a == norm_b:
        return True

    aliases = {
        "restapi": "restapis",
        "restapis": "restapi",
        "react": "reactjs",
        "reactjs": "react",
        "node": "nodejs",
        "nodejs": "node",
        "vue": "vuejs",
        "vuejs": "vue",
        "aws": "awscloud",
        "awscloud": "aws",
        "git": "github",
        "github": "git",
        "k8s": "kubernetes",
        "kubernetes": "k8s",
        "dsa": "datastructuresalgorithms",
        "datastructures": "datastructuresalgorithms",
        "algorithms": "datastructuresalgorithms",
        "datastructuresandalgorithms": "datastructuresalgorithms",
        "datastructuresalgorithms": "datastructuresalgorithms",
        "cicd": "cicdpipelines",
        "cicdpipelines": "cicd",
        "prometheus": "prometheusgrafana",
        "grafana": "prometheusgrafana",
        "prometheusgrafana": "prometheus",
        "qa": "qatesting",
        "testing": "qatesting",
        "qatesting": "testing",
        "js": "javascript",
        "ts": "typescript",
        "py": "python"
    }
    if aliases.get(norm_a) == norm_b or aliases.get(norm_b) == norm_a:
        return True

    if len(norm_a) >= 4 and len(norm_b) >= 4:
        if norm_a in norm_b or norm_b in norm_a:
            return True

    return False


def calculate_role_readiness(
    target_role: str,
    user_state,
    all_quizzes: Optional[List[Any]] = None
) -> Tuple[int, Dict[str, Any]]:
    """
    Role Readiness represents how much of the skill set required for the user's selected
    target role has been acquired by the user.

    The calculation MUST include:
    1. Skills extracted from the user's uploaded resume.
    2. Skills acquired through SkillPath AI learning (topics with completed modules).
    3. Skills demonstrated through quizzes/assessments where applicable (score >= 60%).
    4. Skills/topics completed in the curriculum.
    5. The skills required for the selected target role.

    Distinguishes:
    - Resume Skill: Extracted from resume
    - Learned Skill: Completed modules in SkillPath AI
    - Mastered Skill: All modules completed or quiz score >= 70%
    - Required Skill: Required for target role
    """
    role_conf = get_role_config(target_role or "DevOps Engineer")
    required_skills = role_conf.get("skills", [])
    if not required_skills:
        roadmap = role_conf.get("roadmap", [])
        required_skills = [m["topic"] for m in roadmap] if roadmap else ROLE_SKILLS.get(target_role, ["Git", "Linux", "Docker", "Python"])

    extracted_skills = (user_state.extracted_skills if user_state else None) or []
    module_prog = (getattr(user_state, "module_progress", None) or getattr(user_state, "progress", None) if user_state else None) or {}

    # Extract quiz validated topics
    quiz_passed_topics = set()
    quiz_high_topics = set()
    if all_quizzes:
        for q in all_quizzes:
            topic = getattr(q, "topic", None)
            score = getattr(q, "quiz_score", 0.0) or 0.0
            if topic:
                if score >= 60.0:
                    quiz_passed_topics.add(topic)
                if score >= 70.0:
                    quiz_high_topics.add(topic)

    # Determine learned & mastered topics from SkillPath AI
    learned_topics = set(quiz_passed_topics)
    mastered_topics = set(quiz_high_topics)

    for topic, prog in module_prog.items():
        is_dsa = topic in ("Data Structures & Algorithms", "DSA")
        mod_keys = DSA_MODULE_KEYS if is_dsa else MODULE_KEYS
        resolved_prog = {}
        for k, v in prog.items():
            eff_k = DSA_MODULE_ALIASES.get(k, k) if is_dsa else k
            resolved_prog[eff_k] = v

        completed_count = sum(1 for m in mod_keys if resolved_prog.get(m) == "completed")
        if completed_count > 0:
            learned_topics.add(topic)
        if completed_count == len(mod_keys) and len(mod_keys) > 0:
            mastered_topics.add(topic)

    # Evaluate each required skill for the target role
    possessed_skills = []
    missing_skills = []
    detailed_skills = []

    for req in required_skills:
        in_resume = any(skills_match(req, s) for s in extracted_skills)
        in_learned = any(skills_match(req, t) for t in learned_topics)
        in_mastered = any(skills_match(req, t) for t in mastered_topics)

        is_possessed = in_resume or in_learned or in_mastered

        if in_mastered:
            acquisition_type = "Mastered Skill"
            evidence = "100% Curriculum Completed or Demonstrated Mastery (Score ≥ 70%)"
        elif in_learned:
            acquisition_type = "Learned Skill"
            evidence = "Acquired through SkillPath AI learning modules / passed quiz"
        elif in_resume:
            acquisition_type = "Resume Skill"
            evidence = "Extracted from Uploaded Resume"
        else:
            acquisition_type = "Required Skill (Missing)"
            evidence = f"Required for {target_role}"

        skill_item = {
            "skill": req,
            "possessed": is_possessed,
            "acquisition_type": acquisition_type,
            "status": acquisition_type,
            "evidence": evidence,
            "is_in_resume": in_resume,
            "is_learned": in_learned,
            "is_mastered": in_mastered
        }
        detailed_skills.append(skill_item)

        if is_possessed:
            possessed_skills.append(req)
        else:
            missing_skills.append(req)

    total_req = len(required_skills)
    readiness_pct = int(round((len(possessed_skills) / total_req * 100))) if total_req > 0 else 0

    return readiness_pct, {
        "target_role": target_role,
        "readiness_pct": readiness_pct,
        "total_required": total_req,
        "acquired_count": len(possessed_skills),
        "possessed_count": len(possessed_skills),
        "missing_count": len(missing_skills),
        "possessed_skills": possessed_skills,
        "missing_skills": missing_skills,
        "detailed_skills": detailed_skills,
        "extracted_skills": extracted_skills,
        "learned_topics": list(learned_topics),
        "mastered_topics": list(mastered_topics)
    }


def calculate_topics_mastered(target_role: str, user_state) -> int:
    """
    Topics Mastered = number of completed modules in the user's assigned curriculum.
    Do NOT calculate from video counts, quizzes attempted, or raw topics.
    Only counts completed modules in the target role's curriculum.
    """
    if not user_state:
        return 0

    progress = getattr(user_state, "module_progress", None) or getattr(user_state, "progress", None) or {}
    if not progress:
        return 0

    role_conf = get_role_config(target_role or "DevOps Engineer")
    roadmap = role_conf.get("roadmap", [])
    roadmap_topics = [m["topic"] for m in roadmap] if roadmap else TOPICS

    completed_modules = 0

    for topic in roadmap_topics:
        is_dsa = topic in ("Data Structures & Algorithms", "DSA")
        mod_keys = DSA_MODULE_KEYS if is_dsa else MODULE_KEYS
        topic_prog = progress.get(topic, {})
        if is_dsa:
            resolved = {DSA_MODULE_ALIASES.get(k, k): v for k, v in topic_prog.items()}
            topic_prog = resolved

        for m in mod_keys:
            if topic_prog.get(m) == "completed":
                completed_modules += 1

    return completed_modules


def calculate_curriculum_progress(target_role: str, user_state) -> int:
    """
    Progress of the candidate in the learning journey of that assigned curriculum (percentage).
    """
    if not user_state:
        return 0

    role_conf = get_role_config(target_role or "DevOps Engineer")
    roadmap = role_conf.get("roadmap", [])
    if not roadmap:
        return 0

    progress = getattr(user_state, "module_progress", None) or getattr(user_state, "progress", None) or {}
    total_roadmap_modules = 0
    completed_modules = 0

    for m in roadmap:
        topic = m.get("topic")
        is_dsa = topic in ("Data Structures & Algorithms", "DSA")
        mod_keys = DSA_MODULE_KEYS if is_dsa else MODULE_KEYS
        total_roadmap_modules += len(mod_keys)

        t_prog = progress.get(topic, {})
        if is_dsa:
            resolved = {DSA_MODULE_ALIASES.get(k, k): v for k, v in t_prog.items()}
            t_prog = resolved
        completed_modules += sum(1 for mk in mod_keys if t_prog.get(mk) == "completed")

    if total_roadmap_modules == 0:
        return 0
    return int(round((completed_modules / total_roadmap_modules) * 100))


def format_learning_time(hours: float) -> str:
    """
    Formats decimal hours into 'Xh Ym' format (e.g. 12.5833 -> '12h 35m', 0.0 -> '0h 00m').
    """
    if not hours or hours <= 0:
        return "0h 00m"
    total_minutes = int(round(float(hours) * 60))
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h}h {m:02d}m"


def calculate_user_streak(active_days: Optional[List[str]], current_date_str: Optional[Any] = None, *args, **kwargs) -> int:
    """
    Streak represents consecutive days on which the user actively works/learns in SkillPath AI.
    1 streak = 1 active working/learning day.
    Multiple sessions on the same calendar day count as 1 active day.
    Resets to 1 if consecutive sequence was broken.
    """
    if not active_days:
        return 0

    date_set: Set[date] = set()
    for d in active_days:
        if isinstance(d, str) and len(d) >= 10:
            try:
                date_set.add(datetime.strptime(d[:10], "%Y-%m-%d").date())
            except ValueError:
                pass
        elif isinstance(d, (date, datetime)):
            date_set.add(d if isinstance(d, date) else d.date())

    if not date_set:
        return 0

    ref = kwargs.get("ref_date") or current_date_str
    if isinstance(ref, datetime):
        today = ref.date()
    elif isinstance(ref, date):
        today = ref
    elif isinstance(ref, str) and len(ref) >= 10:
        try:
            today = datetime.strptime(ref[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            today = datetime.utcnow().date()
    else:
        today = datetime.utcnow().date()

    # Anchor to today if active today; anchor to yesterday if active yesterday (active day pending today).
    # If neither today nor yesterday, consecutive streak is broken (returns 0).
    if today in date_set:
        anchor = today
    elif (today - timedelta(days=1)) in date_set:
        anchor = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    check_date = anchor
    while check_date in date_set:
        streak += 1
        check_date -= timedelta(days=1)

    return streak


def record_active_learning_day(user_state, client_date_str: Optional[str] = None) -> int:
    """
    Records the user's active calendar date and recalculates their streak.
    Ensures multiple sessions on the same calendar day do not duplicate streak days.
    Returns the updated streak.
    """
    if client_date_str and len(client_date_str) >= 10:
        date_str = client_date_str[:10]
    else:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    active_days = list(user_state.active_days or [])
    if date_str not in active_days:
        active_days.append(date_str)
        user_state.active_days = active_days

    user_state.last_activity_date = date_str
    user_state.last_accessed_at = datetime.utcnow().isoformat()
    new_streak = calculate_user_streak(active_days, date_str)
    user_state.current_streak = new_streak
    return new_streak


