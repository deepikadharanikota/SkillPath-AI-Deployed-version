"""
quiz.py
-------
Router for Groq-powered adaptive quiz generation, strict video-completion gating,
grading with score and explanation breakdown, and dynamic ability adaptation.
"""

import os
import json
import uuid
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional
import httpx
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from pydantic import BaseModel

from database import get_db
from redis_client import get_session, redis_client
import models
from data import QUIZ_BANK, TOPICS, MODULE_KEYS, MODULE_STRUCTURE, VIDEO_DB
from roles_config import get_topic_syllabus, DSA_MODULE_KEYS, DSA_MODULE_ALIASES
from skills_service import record_active_learning_day

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

DIFFICULTY_MAP = {
    "beginner": "easy",
    "intermediate": "medium",
    "advanced": "hard"
}

from auth_utils import get_current_user

async def _generate_groq_quiz_questions(
    topic: str,
    module: str,
    difficulty: str,
    target_role: str = "DevOps Engineer",
    existing_skills: List[str] = None,
    skill_gaps: List[str] = None,
    language: Optional[str] = None,
    user_ability: float = 0.5,
    performance: str = "average"
) -> List[Dict]:
    """Generates exactly 15 tailored quiz questions via Groq API strictly relevant to the topic and target role."""
    if not GROQ_API_KEY:
        return []

    skills_str = ", ".join(existing_skills or []) or "None listed"
    gaps_str = ", ".join(skill_gaps or []) or "None identified"

    # Fetch syllabus focus and subtopics for this module
    syl_info = get_topic_syllabus(topic) or {}
    mod_info = syl_info.get("modules", {}).get(module, {})
    mod_title = mod_info.get("title", f"Module: {module.capitalize()}")
    mod_focus = mod_info.get("focus", "")
    subtopics_list = ", ".join(mod_info.get("subtopics", []))

    VALID_DSA_LANG_MAP = {
        "c": "C",
        "cpp": "C++",
        "c++": "C++",
        "python": "Python",
        "java": "Java"
    }

    is_dsa = topic in ("Data Structures & Algorithms", "DSA")
    effective_lang = VALID_DSA_LANG_MAP.get(str(language).lower(), "Python") if (is_dsa or language) else None
    other_languages = [l for l in ["C", "C++", "Python", "Java"] if l != effective_lang] if effective_lang else []

    dsa_header = ""
    if is_dsa and effective_lang:
        dsa_header = f"""
Domain: DSA
Topic: {topic}
Programming Language: {effective_lang}
User Ability: {user_ability}
Difficulty: {difficulty.capitalize()}
Previous Performance: {performance}

CRITICAL PROGRAMMING LANGUAGE REQUIREMENT:
Generate a 15-question DSA quiz on {topic} ({mod_title}).
Language: {effective_lang}
Difficulty: {difficulty.capitalize()}
User Ability: {user_ability}

Use {effective_lang} syntax and {effective_lang} code examples.
Do not use {', '.join(other_languages)}, JavaScript, TypeScript, C#, Go, Rust, Kotlin, or any other language.
"""

    prompt = f"""You are a senior technical examiner for SkillPath AI. Generate a rigorous, adaptive 15-question multiple choice quiz for:
Topic: {topic}
Module: {mod_title}
Module Focus: {mod_focus or module.capitalize()}
Module Subtopics: {subtopics_list or 'Core engineering principles'}
Difficulty Level: {difficulty.capitalize()}
{dsa_header}
Learner Context:
- Target Career Role: {target_role}
- Current Skills: {skills_str}
- Identified Skill Gaps: {gaps_str}

CRITICAL RULES:
1. Generate EXACTLY 15 distinct, high-quality questions (numbered 1 to 15).
2. ALL 15 questions MUST test practical knowledge of '{topic}', specifically contextualized to the duties of a '{target_role}'.
3. DO NOT ask questions about unrelated domains (e.g., if Topic is Docker, DO NOT ask about HTML, CSS, or Machine Learning; test Dockerfiles, volumes, compose, and containers).
4. Difficulty distribution: 5 beginner/easy, 5 intermediate/medium, and 5 advanced/hard questions matching the {difficulty.capitalize()} level progression.
5. Each question MUST have exactly 4 distinct options.
6. Exactly one option must be the strictly correct answer.
7. Provide a clear, educational explanation for why that option is correct.
8. Return ONLY a valid JSON array of 15 objects with no markdown fences, no backticks, and no extra text.
{f"9. For all code questions and syntax, strictly use {effective_lang} syntax and {effective_lang} code examples. Do not use {', '.join(other_languages)}, JavaScript, TypeScript, C#, Go, Rust, Kotlin, or any other language." if (is_dsa and effective_lang) else ""}

JSON format:
[
  {{
    "question": "Clear technical question prompt here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": "Exact matching string of correct option",
    "difficulty": "{difficulty}",
    "explanation": "Detailed explanation of why this answer is correct."
  }}
]"""

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "You output only clean, valid JSON array containing exactly 15 quiz objects."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 3200
                }
            )

        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            parsed = json.loads(content.strip())
            if isinstance(parsed, list):
                valid_questions = []
                for q in parsed:
                    if "question" in q and "options" in q and "correctAnswer" in q:
                        opts = [str(o) for o in q["options"]]
                        if q["correctAnswer"] in opts and len(opts) == 4:
                            valid_questions.append({
                                "question": q["question"],
                                "options": opts,
                                "correctAnswer": q["correctAnswer"],
                                "difficulty": q.get("difficulty", difficulty),
                                "explanation": q.get("explanation", "Correct answer based on course concepts.")
                            })
                if len(valid_questions) >= 10:
                    return valid_questions
    except Exception as e:
        logging.warning(f"Groq quiz generation exception: {e}")

    return []

def _fallback_quiz_questions(topic: str, difficulty: str) -> List[Dict]:
    """Fallback question generation guaranteeing EXACTLY 15 questions relevant to the topic."""
    bank = list(QUIZ_BANK.get(topic, []))
    if not bank:
        # Check case-insensitive match
        matched_key = next((k for k in QUIZ_BANK if k.lower() == topic.lower()), None)
        if matched_key:
            bank = list(QUIZ_BANK[matched_key])
        else:
            bank = list(QUIZ_BANK.get("Docker", []))

    selected = list(bank)

    # If topic bank has fewer than 15, repeat from this bank to stay topic-relevant
    if len(selected) < 15 and selected:
        while len(selected) < 15:
            selected.extend(list(bank))

    selected = selected[:15]

    questions = []
    for q in selected:
        opts = list(q["opts"])
        ans_idx = q["ans"]
        correct_text = opts[ans_idx] if 0 <= ans_idx < len(opts) else opts[0]
        random.shuffle(opts)

        questions.append({
            "question": q["q"],
            "options": opts,
            "correctAnswer": correct_text,
            "difficulty": q.get("level", difficulty),
            "explanation": q.get("explanation", f"Correct answer is '{correct_text}'.")
        })
    return questions

@router.get("/generate")
async def generate_quiz(
    topic: str,
    module: str = "intro",
    difficulty: Optional[str] = None,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates EXACTLY 15 questions for a module.
    STRICT GATING: Verifies that required course videos have been completed!
    """
    res = await db.execute(select(models.UserState).filter(models.UserState.user_id == user.id))
    user_state = res.scalars().first()
    if not user_state:
        raise HTTPException(status_code=404, detail="User state not found")

    is_dsa_topic = topic in ("Data Structures & Algorithms", "DSA")
    eff_module = DSA_MODULE_ALIASES.get(module, module) if is_dsa_topic else module

    # 1. Strict video completion check
    video_prog = dict(user_state.video_progress or {})
    topic_vids = video_prog.get(topic, {})
    completed_vids = topic_vids.get(eff_module, topic_vids.get(module, []))

    required_count = 1 if is_dsa_topic else (2 if eff_module in ("core", "advanced") else 1)
    eff_diff = difficulty or user_state.current_difficulty or "beginner"
    avail_vids = VIDEO_DB.get(topic, {}).get(eff_diff, {}).get(eff_module, [])
    if 0 < len(avail_vids) < required_count:
        required_count = len(avail_vids)
    elif len(avail_vids) == 0:
        required_count = 1

    if len(completed_vids) < required_count:
        raise HTTPException(
            status_code=403,
            detail=f"Quiz Locked: Complete all required videos for {topic} ({eff_module}) before unlocking the quiz. ({len(completed_vids)}/{required_count} completed)"
        )

    # 2. Determine adaptive difficulty & context
    ability_info = (user_state.topic_ability or {}).get(topic, {})
    chosen_difficulty = difficulty or ability_info.get("videoLevel", user_state.current_difficulty or "beginner")

    from skills_service import compute_skill_gap
    gap_data = compute_skill_gap(user_state.extracted_skills or [], user_state.target_role or "Machine Learning Engineer")

    # 3. Generate questions (Groq AI with robust fallback, exactly 15 questions)
    raw_dsa_lang = getattr(user_state, "dsa_language", "Python") or "Python"
    VALID_DSA_LANG_MAP = {
        "c": "C",
        "cpp": "C++",
        "c++": "C++",
        "python": "Python",
        "java": "Java"
    }
    dsa_lang = VALID_DSA_LANG_MAP.get(raw_dsa_lang.lower(), "Python")
    user_ability = getattr(user_state, "current_ability", 0.5) or 0.5
    user_perf = getattr(user_state, "initial_performance_category", "average") or "average"

    questions = await _generate_groq_quiz_questions(
        topic,
        eff_module,
        chosen_difficulty,
        target_role=user_state.target_role or "Machine Learning Engineer",
        existing_skills=gap_data.get("already_have", []),
        skill_gaps=gap_data.get("missing", []),
        language=dsa_lang,
        user_ability=user_ability,
        performance=user_perf
    )

    # If Groq didn't return a full 15 questions, supplement or fallback
    fallback_qs = _fallback_quiz_questions(topic, chosen_difficulty)
    if len(questions) < 15:
        # Fill remaining slots up to 15
        needed = 15 - len(questions)
        questions.extend(fallback_qs[:needed])

    # Guarantee exactly 15
    questions = questions[:15]

    # 4. Create quiz session in Redis
    quiz_id = str(uuid.uuid4())
    stored_payload = {
        "quiz_id": quiz_id,
        "topic": topic,
        "module": eff_module,
        "difficulty": chosen_difficulty,
        "language": dsa_lang if is_dsa_topic else None,
        "questions": questions
    }
    await redis_client.set(f"quiz:{quiz_id}", json.dumps(stored_payload), ex=3600)

    # 5. Return sanitized questions to client (without exposing answers)
    client_questions = []
    for idx, q in enumerate(questions):
        client_questions.append({
            "id": idx,
            "question": q["question"],
            "options": q["options"],
            "difficulty": q.get("difficulty", chosen_difficulty)
        })

    dsa_code_map = {"C": "c", "C++": "cpp", "Python": "python", "Java": "java"}

    return {
        "quiz_id": quiz_id,
        "topic": topic,
        "module": eff_module,
        "difficulty": chosen_difficulty,
        "language": dsa_lang if is_dsa_topic else None,
        "dsa_language": dsa_lang if is_dsa_topic else None,
        "dsa_lang_code": dsa_code_map.get(dsa_lang, "python") if is_dsa_topic else None,
        "total_questions": len(client_questions),
        "questions": client_questions
    }

class QuizSubmitPayload(BaseModel):
    quiz_id: str
    topic: str
    module: str
    answers: Dict[str, str] # { "0": "User Chosen Answer", ... }

@router.post("/submit")
async def submit_quiz(
    payload: QuizSubmitPayload,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates submitted quiz, generates itemized answer review, saves detailed history,
    and updates adaptive difficulty for both quizzes and videos.
    """
    quiz_raw = await redis_client.get(f"quiz:{payload.quiz_id}")
    if not quiz_raw:
        # Check if already submitted and saved in DB
        hist_res = await db.execute(select(models.QuizHistory).filter(models.QuizHistory.quiz_id == payload.quiz_id))
        existing_hist = hist_res.scalars().first()
        if existing_hist:
            return {
                "quiz_id": payload.quiz_id,
                "already_submitted": True,
                "score": existing_hist.score,
                "total_questions": existing_hist.total_questions,
                "percentage": existing_hist.percentage,
                "questions": existing_hist.questions
            }
        raise HTTPException(status_code=400, detail="Quiz session expired or not found. Please restart quiz.")

    quiz_data = json.loads(quiz_raw)
    questions = quiz_data["questions"]
    total = len(questions)

    score = 0
    incorrect_count = 0
    unanswered_count = 0
    detailed_questions = []
    correct_answers_dict = {}

    for idx, q in enumerate(questions):
        idx_str = str(idx)
        raw_ans = str(payload.answers.get(idx_str, payload.answers.get(idx, "")) or "").strip()
        correct_ans = q["correctAnswer"].strip()
        correct_answers_dict[idx_str] = correct_ans

        is_unanswered = (raw_ans == "__UNANSWERED__" or not raw_ans or raw_ans == "No Answer Selected" or raw_ans.lower() == "none")
        if is_unanswered:
            unanswered_count += 1
            is_correct = False
            user_display_ans = "Not answered"
        else:
            is_correct = (raw_ans.lower() == correct_ans.lower())
            if is_correct:
                score += 1
            else:
                incorrect_count += 1
            user_display_ans = raw_ans

        detailed_questions.append({
            "id": idx,
            "question": q["question"],
            "userAnswer": user_display_ans,
            "correctAnswer": correct_ans,
            "isCorrect": is_correct,
            "isUnanswered": is_unanswered,
            "difficulty": q.get("difficulty", quiz_data["difficulty"]),
            "explanation": q.get("explanation", f"Correct answer is {correct_ans}.")
        })

    percentage = round((score / total * 100), 1) if total > 0 else 0.0
    correct_count = score

    # Performance Level Assessment
    if percentage >= 85:
        performance_level = "Exceptional"
    elif percentage >= 70:
        performance_level = "Strong"
    elif percentage >= 50:
        performance_level = "Satisfactory"
    else:
        performance_level = "Needs Improvement"

    # Fetch UserState for adaptation and progress
    res = await db.execute(select(models.UserState).filter(models.UserState.user_id == user.id))
    user_state = res.scalars().first()
    if not user_state:
        user_state = models.UserState(user_id=user.id)
        db.add(user_state)

    # ── Adaptive Engine ──
    # Adjust video and quiz difficulty based on performance
    topic = payload.topic
    ability_map = dict(user_state.topic_ability or {})
    topic_ability = dict(ability_map.get(topic, {}))
    current_level = topic_ability.get("videoLevel", user_state.current_difficulty or "beginner")

    if percentage >= 85:
        if current_level == "beginner":
            next_diff = "intermediate"
        elif current_level == "intermediate":
            next_diff = "advanced"
        else:
            next_diff = "advanced"
        next_quiz_level = "hard"
        feedback = f"Outstanding performance ({percentage}%)! Difficulty advanced to {next_diff.capitalize()} for more challenging material."
    elif percentage >= 70:
        next_diff = current_level
        next_quiz_level = "medium" if current_level != "advanced" else "hard"
        feedback = f"Good grasp of concepts ({percentage}%). Maintaining {current_level.capitalize()} level to reinforce mastery."
    elif percentage >= 50:
        next_diff = current_level
        next_quiz_level = "medium"
        feedback = f"Passing score ({percentage}%). Further review recommended before advancing."
    else:
        if current_level == "advanced":
            next_diff = "intermediate"
        else:
            next_diff = "beginner"
        next_quiz_level = "easy"
        feedback = f"Score ({percentage}%). Course video recommendations adjusted to {next_diff.capitalize()} to build core fundamentals."

    attempts = topic_ability.get("attempts", 0) + 1
    prev_avg = topic_ability.get("quizAverage", percentage)
    new_avg = round((prev_avg * (attempts - 1) + percentage) / attempts, 1)

    topic_ability.update({
        "abilityLevel": next_diff.capitalize(),
        "videoLevel": next_diff,
        "quizLevel": next_quiz_level,
        "quizAverage": new_avg,
        "lastScore": percentage,
        "attempts": attempts,
        "updatedAt": datetime.utcnow().isoformat()
    })
    ability_map[topic] = topic_ability
    user_state.topic_ability = ability_map
    user_state.current_difficulty = next_diff

    # Update Module Progress
    is_dsa_topic = topic in ("Data Structures & Algorithms", "DSA")
    eff_mod_keys = DSA_MODULE_KEYS if is_dsa_topic else MODULE_KEYS
    eff_module = DSA_MODULE_ALIASES.get(payload.module, payload.module) if is_dsa_topic else payload.module

    now_iso = datetime.utcnow().isoformat()
    progress = dict(user_state.module_progress or {})
    default_mod_dict = {m: ("active" if idx == 0 else "locked") for idx, m in enumerate(eff_mod_keys)}
    topic_prog = dict(progress.get(topic, default_mod_dict))
    for m in eff_mod_keys:
        topic_prog.setdefault(m, "locked")

    module_passed = percentage >= 60
    if module_passed:
        topic_prog[eff_module] = "completed"
        # Unlock next module
        if eff_module in eff_mod_keys:
            curr_idx = eff_mod_keys.index(eff_module)
            if curr_idx + 1 < len(eff_mod_keys):
                next_mod = eff_mod_keys[curr_idx + 1]
                if topic_prog.get(next_mod) != "completed":
                    topic_prog[next_mod] = "active"
                    user_state.current_module = next_mod
        progress[topic] = topic_prog
        user_state.module_progress = progress

    # Streak & Active Learning Day
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    record_active_learning_day(user_state, today_str)

    # Persist in QuizHistory
    history_entry = models.QuizHistory(
        user_id=user.id,
        topic=topic,
        module_key=eff_module,
        difficulty=quiz_data["difficulty"],
        quiz_score=percentage,
        code_score=100.0 if module_passed else 50.0,
        reward=percentage / 100.0,
        quiz_id=payload.quiz_id,
        questions=detailed_questions,
        user_answers=payload.answers,
        correct_answers=correct_answers_dict,
        score=correct_count,
        total_questions=total,
        percentage=percentage,
        unanswered=unanswered_count,
        completed_at=now_iso
    )
    db.add(history_entry)

    # Research cohort initial performance category (immutable baseline)
    if not getattr(user_state, "initial_performance_category", None):
        if percentage >= 75:
            user_state.initial_performance_category = "excellent"
        elif percentage >= 50:
            user_state.initial_performance_category = "average"
        else:
            user_state.initial_performance_category = "below_average"

    # Dynamic current ability adaptation (EMA)
    prev_ability = getattr(user_state, "current_ability", 0.5) or 0.5
    user_state.current_ability = round(0.7 * float(prev_ability) + 0.3 * (percentage / 100.0), 3)

    # Invalidate dashboard insights and learning caches in Redis for instant synchronization
    try:
        await redis_client.delete(f"dashboard_insights:{user.id}")
        await redis_client.delete(f"learning_resume:{user.id}")
        await redis_client.delete(f"dashboard_summary:{user.id}")
    except Exception as e:
        logging.warning(f"Error invalidating cache: {e}")

    # Activity Log
    act = models.LearningActivity(
        user_id=user.id,
        activity_type="completed_quiz",
        title=f"Completed {topic} ({payload.module.capitalize()}) Quiz",
        description=f"Scored {score}/{total} ({percentage}%) - {performance_level}",
        topic=topic,
        created_at=now_iso
    )
    db.add(act)

    await db.commit()

    return {
        "success": True,
        "quiz_id": payload.quiz_id,
        "topic": topic,
        "module": payload.module,
        "difficulty": quiz_data["difficulty"],
        "score": score,
        "total_questions": total,
        "percentage": percentage,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "unanswered_count": unanswered_count,
        "performance_level": performance_level,
        "adaptive_feedback": feedback,
        "next_difficulty": next_diff,
        "module_passed": module_passed,
        "questions": detailed_questions,
        "completed_at": now_iso
    }

@router.get("/{quiz_id}/results")
async def get_quiz_results(
    quiz_id: str,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves stored quiz results by quiz_id."""
    res = await db.execute(
        select(models.QuizHistory)
        .filter(models.QuizHistory.quiz_id == quiz_id, models.QuizHistory.user_id == user.id)
    )
    hist = res.scalars().first()
    if not hist:
        raise HTTPException(status_code=404, detail="Quiz result not found")

    questions_list = hist.questions or []
    tot = hist.total_questions or len(questions_list) or 15
    corr = hist.score or sum(1 for q in questions_list if q.get("isCorrect"))
    unans = sum(1 for q in questions_list if q.get("isUnanswered"))
    incorr = max(0, tot - corr - unans)

    return {
        "quiz_id": hist.quiz_id,
        "topic": hist.topic,
        "module": hist.module_key,
        "difficulty": hist.difficulty,
        "score": corr,
        "total_questions": tot,
        "percentage": hist.percentage or hist.quiz_score or round(corr / tot * 100, 1),
        "correct_count": corr,
        "incorrect_count": incorr,
        "unanswered_count": unans,
        "questions": questions_list,
        "completed_at": hist.completed_at
    }

@router.get("/history")
async def get_quiz_history(
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns past quiz attempts for the user."""
    res = await db.execute(
        select(models.QuizHistory)
        .filter(models.QuizHistory.user_id == user.id)
        .order_by(models.QuizHistory.id.desc())
        .limit(20)
    )
    history = res.scalars().all()
    return {
        "history": [
            {
                "id": h.id,
                "quiz_id": h.quiz_id,
                "topic": h.topic,
                "module": h.module_key,
                "difficulty": h.difficulty,
                "score": h.score,
                "total_questions": h.total_questions,
                "percentage": h.percentage or h.quiz_score,
                "completed_at": h.completed_at
            }
            for h in history
        ]
    }
