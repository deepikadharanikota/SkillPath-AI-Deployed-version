"""
dashboard.py
------------
Backend API router for the Learning Journey Dashboard.
Provides endpoints for overview metrics, skill progress, activity history,
AI-generated insights (via Groq), and personalized recommendations.
All endpoints require authentication via the existing session token header.
"""

import os
import json
import logging
from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from database import get_db
from redis_client import get_session, redis_client
import models
from data import TOPICS, MODULE_KEYS, MODULE_STRUCTURE, ROLE_SKILLS, ROLES
from skills_service import (
    compute_skill_gap, calculate_role_readiness, calculate_topics_mastered,
    format_learning_time, calculate_user_streak
)
from roles_config import (
    get_role_config, get_role_roadmap, filter_gaps_with_prerequisites, TOPIC_SYLLABUS,
    DSA_MODULE_KEYS, DSA_MODULE_ALIASES, get_dsa_modules_def
)

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# ─── Auth dependency (unified Supabase JWT & Session auth) ───────────────────
from auth_utils import get_current_user


# ─── Helper: get user state with safe defaults ────────────────────────────
async def _get_user_state(user_id: int, db: AsyncSession):
    result = await db.execute(select(models.UserState).filter(models.UserState.user_id == user_id))
    state = result.scalars().first()
    return state


def _safe_progress(state):
    """Return module_progress dict with safe fallback."""
    if not state or not state.module_progress:
        return {}
    return state.module_progress


def _compute_overall_progress(module_progress: dict) -> dict:
    """Compute overall and per-topic progress from module_progress JSON."""
    total_modules = sum(len(DSA_MODULE_KEYS) if t in ("Data Structures & Algorithms", "DSA") else len(MODULE_KEYS) for t in TOPICS)
    completed_modules = 0
    topics_completed = 0
    topics_in_progress = 0
    topic_details = {}

    for topic in TOPICS:
        is_dsa = topic in ("Data Structures & Algorithms", "DSA")
        mod_keys = DSA_MODULE_KEYS if is_dsa else MODULE_KEYS
        topic_prog = module_progress.get(topic, {})
        if is_dsa:
            resolved_prog = {}
            for k, v in topic_prog.items():
                eff_k = DSA_MODULE_ALIASES.get(k, k)
                resolved_prog[eff_k] = v
            topic_prog = resolved_prog

        topic_completed = sum(1 for m in mod_keys if topic_prog.get(m) == "completed")
        topic_total = len(mod_keys)
        pct = int((topic_completed / topic_total) * 100) if topic_total > 0 else 0

        completed_modules += topic_completed

        if topic_completed == topic_total and topic_completed > 0:
            topics_completed += 1
        elif topic_completed > 0 or any(topic_prog.get(m) == "active" for m in mod_keys):
            topics_in_progress += 1

        # Determine level
        if pct >= 67:
            level = "Advanced"
        elif pct >= 34:
            level = "Intermediate"
        else:
            level = "Beginner"

        topic_details[topic] = {
            "completed_modules": topic_completed,
            "total_modules": topic_total,
            "progress_pct": pct,
            "level": level,
            "module_status": {m: topic_prog.get(m, "locked") for m in mod_keys},
        }

    overall_pct = int((completed_modules / total_modules) * 100) if total_modules > 0 else 0

    return {
        "overall_pct": overall_pct,
        "completed_modules": completed_modules,
        "total_modules": total_modules,
        "topics_completed": topics_completed,
        "topics_in_progress": topics_in_progress,
        "topic_details": topic_details,
    }


# ─── Badge definitions & checker ──────────────────────────────────────────
BADGE_DEFINITIONS = [
    {"id": "first_module", "name": "First Steps", "icon": "🌱", "description": "Completed your first module", "condition": lambda s, h: h >= 1},
    {"id": "five_modules", "name": "Getting Serious", "icon": "📚", "description": "Completed 5 modules", "condition": lambda s, h: h >= 5},
    {"id": "ten_modules", "name": "Knowledge Seeker", "icon": "🔥", "description": "Completed 10 modules", "condition": lambda s, h: h >= 10},
    {"id": "first_topic", "name": "Topic Master", "icon": "🏆", "description": "Fully completed a topic", "condition": lambda s, h: _count_completed_topics(s) >= 1},
    {"id": "three_topics", "name": "Triple Threat", "icon": "⭐", "description": "Fully completed 3 topics", "condition": lambda s, h: _count_completed_topics(s) >= 3},
    {"id": "five_hours", "name": "Dedicated Learner", "icon": "⏰", "description": "Spent 5+ hours learning", "condition": lambda s, h: (s.total_learning_hours or 0) >= 5},
    {"id": "ten_hours", "name": "Marathon Learner", "icon": "🏅", "description": "Spent 10+ hours learning", "condition": lambda s, h: (s.total_learning_hours or 0) >= 10},
    {"id": "streak_3", "name": "On a Roll", "icon": "🔥", "description": "3-day learning streak", "condition": lambda s, h: (s.current_streak or 0) >= 3},
    {"id": "streak_7", "name": "Week Warrior", "icon": "💪", "description": "7-day learning streak", "condition": lambda s, h: (s.current_streak or 0) >= 7},
    {"id": "high_scorer", "name": "Quiz Champion", "icon": "🎯", "description": "Scored 90%+ on a quiz", "condition": None},  # checked separately in learning.py
]


def _count_completed_topics(state) -> int:
    progress = _safe_progress(state)
    count = 0
    for topic in TOPICS:
        is_dsa = topic in ("Data Structures & Algorithms", "DSA")
        mod_keys = DSA_MODULE_KEYS if is_dsa else MODULE_KEYS
        topic_prog = progress.get(topic, {})
        if is_dsa:
            resolved_prog = {DSA_MODULE_ALIASES.get(k, k): v for k, v in topic_prog.items()}
            topic_prog = resolved_prog
        if all(topic_prog.get(m) == "completed" for m in mod_keys) and len(topic_prog) > 0:
            count += 1
    return count


def check_and_award_badges(state, quiz_count: int) -> list:
    """Check badge conditions and award any newly earned badges. Returns list of newly awarded badge dicts."""
    existing_badges = state.badges or []
    existing_ids = {b["id"] for b in existing_badges}
    new_badges = []

    for badge_def in BADGE_DEFINITIONS:
        if badge_def["id"] in existing_ids:
            continue
        if badge_def["condition"] is None:
            continue  # special badges handled elsewhere
        try:
            if badge_def["condition"](state, quiz_count):
                badge = {
                    "id": badge_def["id"],
                    "name": badge_def["name"],
                    "icon": badge_def["icon"],
                    "description": badge_def["description"],
                    "earned_at": datetime.utcnow().isoformat(),
                }
                new_badges.append(badge)
        except Exception:
            pass

    return new_badges


# ─── Modular Section Builders for Single Source of Truth ───────────────────
def _build_dsa_info(state, progress, role_conf):
    VALID_DSA_LANG_MAP = {
        "c": ("C", "c"),
        "cpp": ("C++", "cpp"),
        "c++": ("C++", "cpp"),
        "python": ("Python", "python"),
        "java": ("Java", "java")
    }
    raw_dsa_lang = (getattr(state, "dsa_language", None) or "").strip().lower() if state else ""
    has_selected = raw_dsa_lang in VALID_DSA_LANG_MAP
    dsa_lang_name, dsa_lang_code = VALID_DSA_LANG_MAP.get(raw_dsa_lang, ("Python", "python"))

    dsa_prog = progress.get("Data Structures & Algorithms", {}) or progress.get("DSA", {}) if progress else {}
    resolved_dsa_prog = {}
    for k, v in dsa_prog.items():
        eff_k = DSA_MODULE_ALIASES.get(k, k)
        resolved_dsa_prog[eff_k] = v

    dsa_completed = sum(1 for m in DSA_MODULE_KEYS if resolved_dsa_prog.get(m) == "completed")
    total_dsa_modules = len(DSA_MODULE_KEYS)
    dsa_pct = int((dsa_completed / total_dsa_modules) * 100) if total_dsa_modules else 0

    current_dsa_mod = "module_1"
    for m in DSA_MODULE_KEYS:
        if resolved_dsa_prog.get(m) != "completed":
            current_dsa_mod = m
            break

    dsa_modules_def = get_dsa_modules_def()
    dsa_mod_map = {mod["key"]: mod for mod in dsa_modules_def}
    current_mod_title = dsa_mod_map.get(current_dsa_mod, {}).get("title", current_dsa_mod)
    dsa_gaps = [mod.get("title", m) for mod in dsa_modules_def if resolved_dsa_prog.get(mod["key"]) != "completed"]

    target_role = (state.target_role if state else None) or "DevOps Engineer"
    is_target_role = target_role.lower().strip() in (
        "data structures & algorithms", "dsa", "data structures & algorithms (dsa)", "dsa specialist", "data structures and algorithms"
    )

    return {
        "dsa_language": dsa_lang_name,
        "dsaLanguage": dsa_lang_code,
        "dsa_lang_code": dsa_lang_code,
        "has_selected_language": has_selected,
        "dsa_progress_pct": dsa_pct,
        "completed_modules_count": dsa_completed,
        "total_modules_count": total_dsa_modules,
        "current_dsa_module": current_dsa_mod,
        "current_dsa_module_title": current_mod_title,
        "current_dsa_topic": "Data Structures & Algorithms",
        "dsa_modules": dsa_modules_def,
        "dsa_skill_gaps": dsa_gaps,
        "is_target_role": is_target_role,
        "is_relevant": is_target_role,
        "target_role": target_role,
        "navigate_url": f"/learning/Data%20Structures%20%26%20Algorithms?module={current_dsa_mod}"
    }


def _build_skills_data(state, progress, stats, all_quizzes, target_role, role_conf):
    roadmap_topics = [m["topic"] for m in role_conf.get("roadmap", [])]
    extracted_skills_lower = {s.lower().strip() for s in ((state.extracted_skills if state else None) or [])}
    video_prog = (state.video_progress or {}) if state else {}

    known_list = []
    learning_list = []
    needs_improvement_list = []
    missing_list = []
    skills_list = []

    quiz_history = [{"topic": q.topic, "quizScore": q.quiz_score} for q in all_quizzes]

    for topic in TOPICS:
        topic_prog = progress.get(topic, {})
        completed_modules = sum(1 for m in MODULE_KEYS if topic_prog.get(m) == "completed")
        total_modules = len(MODULE_KEYS)
        pct = int((completed_modules / total_modules) * 100) if total_modules > 0 else 0

        t_vids = video_prog.get(topic, {})
        watched_count = sum(len(v_list) for v_list in t_vids.values())

        topic_quizzes = [q for q in all_quizzes if q.topic == topic]
        avg_score = round(sum(q.quiz_score for q in topic_quizzes) / len(topic_quizzes), 1) if topic_quizzes else 0
        has_quiz = len(topic_quizzes) > 0

        t_lower = topic.lower().strip()
        is_in_resume = (t_lower in extracted_skills_lower) or any(t_lower in s or s in t_lower for s in extracted_skills_lower)
        is_in_progress = (completed_modules > 0 or watched_count > 0 or (state and state.current_topic == topic) or any(topic_prog.get(m) == "active" for m in MODULE_KEYS)) and pct < 100
        is_completed = (pct == 100)
        is_role_req = (topic in roadmap_topics)

        knowledge = compute_topic_knowledge(
            topic,
            (state.extracted_skills if state else None) or [],
            progress,
            quiz_history
        )

        if has_quiz and avg_score < 60:
            category = "Needs Improvement"
            evidence = f"Quiz: {avg_score}% average (needs review)"
        elif is_completed:
            category = "Known"
            if has_quiz:
                evidence = f"Course Completed + Quiz: {avg_score}%"
            else:
                evidence = "Course Completed (100%)"
        elif has_quiz and avg_score >= 70:
            category = "Known"
            evidence = f"Demonstrated in Quiz: {avg_score}%"
        elif is_in_resume:
            category = "Known"
            evidence = "Extracted from Resume"
        elif is_in_progress:
            category = "Learning"
            if watched_count > 0:
                evidence = f"In Progress: {watched_count} videos watched, {completed_modules}/{total_modules} modules completed"
            else:
                evidence = f"In Progress: {completed_modules}/{total_modules} modules completed"
        elif is_role_req:
            category = "Missing"
            evidence = f"Required for {target_role}"
        else:
            category = "Missing"
            evidence = "Elective Skill"

        if pct >= 67 or (has_quiz and avg_score >= 85):
            level = "Advanced"
        elif pct >= 34 or (has_quiz and avg_score >= 65) or is_in_resume:
            level = "Intermediate"
        else:
            level = "Beginner"

        item = {
            "topic": topic,
            "category": category,
            "evidence": evidence,
            "progress_pct": pct,
            "level": level,
            "completed_modules": completed_modules,
            "total_modules": total_modules,
            "avg_quiz_score": avg_score,
            "quizzes_taken": len(topic_quizzes),
            "knowledge_score": round(knowledge * 100, 1),
            "module_status": {m: topic_prog.get(m, "locked") for m in MODULE_KEYS},
            "is_current": bool(state and state.current_topic == topic),
            "is_role_requirement": is_role_req,
            "navigate_url": f"/learning/{topic}?module=intro"
        }

        skills_list.append(item)
        if category == "Known":
            known_list.append(item)
        elif category == "Learning":
            learning_list.append(item)
        elif category == "Needs Improvement":
            needs_improvement_list.append(item)
        else:
            missing_list.append(item)

    skills_list.sort(key=lambda s: (-int(s["is_current"]), -s["progress_pct"]))
    readiness_pct, readiness_details = calculate_role_readiness(target_role, state, all_quizzes)

    return {
        "skills": skills_list,
        "categorized": {
            "known": known_list,
            "learning": learning_list,
            "needs_improvement": needs_improvement_list,
            "missing": missing_list
        },
        "summary": {
            "total": len(skills_list),
            "known_count": len(known_list),
            "learning_count": len(learning_list),
            "needs_improvement_count": len(needs_improvement_list),
            "missing_count": len(missing_list),
            "role_readiness_pct": readiness_pct,
            "role_readiness_details": readiness_details
        },
        "target_role": target_role
    }


def _build_quiz_analysis_data(quizzes):
    if not quizzes:
        return {
            "has_quiz_data": False,
            "total_quizzes_taken": 0,
            "average_quiz_score": 0.0,
            "highest_score": 0.0,
            "lowest_score": 0.0,
            "strengths": [],
            "weaknesses": [],
            "topic_analysis": [],
            "recent_quizzes": [],
            "message": "No quizzes taken yet. Complete a video and take a 15-question quiz to see analytics!"
        }

    total_quizzes = len(quizzes)
    scores = [q.quiz_score for q in quizzes]
    avg_score = round(sum(scores) / total_quizzes, 1)
    high_score = round(max(scores), 1)
    low_score = round(min(scores), 1)

    topic_map = {}
    for q in quizzes:
        topic_map.setdefault(q.topic, []).append(q)

    topic_analysis = []
    strengths = []
    weaknesses = []

    for t, q_list in topic_map.items():
        t_scores = [item.quiz_score for item in q_list]
        t_avg = round(sum(t_scores) / len(t_scores), 1)
        latest = q_list[0]

        if t_avg >= 75:
            status = "Strong"
            strengths.append({"topic": t, "score": t_avg})
        elif t_avg < 60:
            status = "Needs Review"
            weaknesses.append({"topic": t, "score": t_avg})
        else:
            status = "Good"

        topic_analysis.append({
            "topic": t,
            "attempts": len(q_list),
            "average_score": t_avg,
            "latest_score": round(latest.quiz_score, 1),
            "latest_difficulty": latest.difficulty or "beginner",
            "latest_module": latest.module_key or "intro",
            "status": status
        })

    topic_analysis.sort(key=lambda x: -x["average_score"])

    recent_quizzes = []
    for q in quizzes[:10]:
        recent_quizzes.append({
            "id": q.id,
            "topic": q.topic,
            "module_key": q.module_key,
            "difficulty": q.difficulty,
            "quiz_score": q.quiz_score,
            "code_score": q.code_score,
            "reward": q.reward
        })

    return {
        "has_quiz_data": True,
        "total_quizzes_taken": total_quizzes,
        "average_quiz_score": avg_score,
        "highest_score": high_score,
        "lowest_score": low_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "topic_analysis": topic_analysis,
        "recent_quizzes": recent_quizzes
    }


def _build_roadmap_data(state, progress, stats, target_role, role_conf):
    completed_topics = [t for t in TOPICS if stats["topic_details"].get(t, {}).get("progress_pct", 0) == 100]
    extracted_skills = (state.extracted_skills if state else None) or []
    existing_skills_lower = {s.lower().strip() for s in extracted_skills}

    milestones = []
    for milestone in role_conf.get("roadmap", []):
        t = milestone["topic"]
        t_lower = t.lower().strip()

        t_detail = stats["topic_details"].get(t, {})
        pct = t_detail.get("progress_pct", 0)

        is_completed = pct == 100
        is_in_resume = (t_lower in existing_skills_lower) or any(t_lower in s or s in t_lower for s in existing_skills_lower)
        is_in_prog = pct > 0

        prereqs = milestone.get("prerequisites", [])
        unmet_prereqs = []
        for p in prereqs:
            p_lower = p.lower().strip()
            p_satisfied = (p_lower in existing_skills_lower) or any(p_lower in s for s in existing_skills_lower) or (p in completed_topics)
            if not p_satisfied:
                unmet_prereqs.append(p)

        if is_completed:
            status = "completed"
            action = "Review Content"
        elif is_in_prog:
            status = "in_progress"
            action = "Continue Learning"
        elif is_in_resume:
            status = "mastered_via_resume"
            action = "Review Advanced"
        elif len(unmet_prereqs) > 0:
            status = "locked"
            action = f"Requires {', '.join(unmet_prereqs)}"
        else:
            status = "ready_to_learn"
            action = "Start Learning"

        mod_status = t_detail.get("module_status", {})
        target_mod = "intro"
        for m in MODULE_KEYS:
            if mod_status.get(m) in ("active", "locked") and mod_status.get(m) != "completed":
                target_mod = m
                break

        milestones.append({
            "topic": t,
            "title": milestone.get("title", t),
            "description": milestone.get("description", ""),
            "prerequisites": prereqs,
            "unmet_prerequisites": unmet_prereqs,
            "progress_pct": pct,
            "status": status,
            "action_label": action,
            "target_module": target_mod,
            "navigate_url": f"/learning/{t}?module={target_mod}",
            "syllabus": TOPIC_SYLLABUS.get(t)
        })

    mastered_count = sum(1 for m in milestones if m["status"] in ("completed", "mastered_via_resume"))
    remaining_count = sum(1 for m in milestones if m["status"] not in ("completed", "mastered_via_resume"))

    return {
        "target_role": target_role,
        "category": role_conf.get("category", "Technology"),
        "description": role_conf.get("description", ""),
        "role_description": role_conf.get("description", ""),
        "total_milestones": len(milestones),
        "mastered_count": mastered_count,
        "remaining_count": remaining_count,
        "milestones": milestones
    }


def _build_recommendations_data(state, progress, stats, target_role, role_conf):
    completed_topics = [t for t in TOPICS if stats["topic_details"].get(t, {}).get("progress_pct", 0) == 100]
    in_prog_topics = [t for t in TOPICS if 0 < stats["topic_details"].get(t, {}).get("progress_pct", 0) < 100]
    existing_skills_lower = {s.lower().strip() for s in ((state.extracted_skills if state else None) or [])}

    roadmap = role_conf.get("roadmap", [])
    recs = []

    # 1. Continue active topic if in progress
    if state and state.current_topic and state.current_topic not in completed_topics:
        pct = stats["topic_details"].get(state.current_topic, {}).get("progress_pct", 0)
        recs.append({
            "topic": state.current_topic,
            "title": f"Continue {state.current_topic}",
            "description": f"You're {pct}% through. Keep up your momentum!",
            "priority": "high",
            "difficulty": state.current_difficulty or "intermediate"
        })

    # 2. Iterate through role roadmap in sequential prerequisite order
    for milestone in roadmap:
        t = milestone["topic"]
        t_lower = t.lower().strip()
        already_known = (t_lower in existing_skills_lower) or any(t_lower in s for s in existing_skills_lower)
        if already_known or t in completed_topics or any(r["topic"] == t for r in recs):
            continue

        prereqs = milestone.get("prerequisites", [])
        unmet = [p for p in prereqs if p.lower().strip() not in existing_skills_lower and p not in completed_topics]

        if not unmet:
            recs.append({
                "topic": t,
                "title": f"Learn {t}",
                "description": milestone.get("description") or f"Core required milestone for {target_role}.",
                "priority": "high",
                "difficulty": "intermediate"
            })
        else:
            for p in unmet:
                if p in TOPICS and not any(r["topic"] == p for r in recs) and p not in completed_topics:
                    recs.append({
                        "topic": p,
                        "title": f"Learn {p} (Prerequisite for {t})",
                        "description": f"Essential foundation needed before advancing to {t}.",
                        "priority": "high",
                        "difficulty": "beginner"
                    })

        if len(recs) >= 4:
            break

    # 3. Add other in-progress topics
    for t in in_prog_topics:
        if not any(r["topic"] == t for r in recs) and len(recs) < 5:
            recs.append({
                "topic": t,
                "title": f"Resume {t}",
                "description": "Continue where you left off on this topic.",
                "priority": "medium",
                "difficulty": "intermediate"
            })

    if not recs:
        recs.append({
            "topic": roadmap[0]["topic"] if roadmap else "Python",
            "title": f"Start {roadmap[0]['topic'] if roadmap else 'Python'}",
            "description": f"Begin your learning path for {target_role}.",
            "priority": "high",
            "difficulty": "beginner"
        })

    enriched = []
    seen = set()
    for r in recs:
        t = r["topic"]
        if t in seen:
            continue
        seen.add(t)

        t_detail = stats["topic_details"].get(t, {})
        pct = t_detail.get("progress_pct", 0)

        if pct == 100:
            status = "completed"
            action = "Review Content"
        elif pct > 0:
            status = "in_progress"
            action = "Continue Learning"
        else:
            status = "not_started"
            action = "Start Learning"

        mod_status = t_detail.get("module_status", {})
        target_mod = "intro"
        for m in MODULE_KEYS:
            if mod_status.get(m) in ("active", "locked") and mod_status.get(m) != "completed":
                target_mod = m
                break

        nav_url = f"/learning/{t}?module={target_mod}"
        if state and t == state.current_topic and state.last_video_id and pct < 100:
            pos = int(state.last_video_position_seconds or 0)
            nav_url = f"/learning/{t}?module={target_mod}&video={state.last_video_id}&t={pos}"
            action = "Resume Course"
            r_title = f"Resume {t}"
            r_desc = f"Continue watching '{state.last_video_title or t}' ({pct}% complete)"
        else:
            r_title = r.get("title", f"Learn {t}")
            r_desc = r.get("description", f"Target topic for {target_role}")

        enriched.append({
            "topic": t,
            "title": r_title,
            "description": r_desc,
            "priority": r.get("priority", "medium"),
            "difficulty": r.get("difficulty", "intermediate"),
            "progress_pct": pct,
            "status": status,
            "action_label": action,
            "target_module": target_mod,
            "navigate_url": nav_url,
            "syllabus": TOPIC_SYLLABUS.get(t)
        })

    return enriched[:6]


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT: /dashboard/summary (Consolidated, Ultra-fast <20ms single fetch)
# ═══════════════════════════════════════════════════════════════════════════
@router.get("/summary")
async def dashboard_summary(
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    state = await _get_user_state(user.id, db)
    progress = _safe_progress(state)
    stats = _compute_overall_progress(progress)

    # 1. Quizzes
    quiz_result = await db.execute(
        select(models.QuizHistory)
        .filter(models.QuizHistory.user_id == user.id)
        .order_by(models.QuizHistory.id.desc())
    )
    all_quizzes = quiz_result.scalars().all()
    quiz_count = len(all_quizzes)

    # 2. Timeline / Recent Activities
    act_result = await db.execute(
        select(models.LearningActivity)
        .filter(models.LearningActivity.user_id == user.id)
        .order_by(models.LearningActivity.created_at.desc())
        .limit(15)
    )
    activities = act_result.scalars().all()
    timeline_list = [
        {
            "id": act.id,
            "type": act.activity_type,
            "title": act.title,
            "description": act.description,
            "topic": act.topic,
            "created_at": act.created_at,
        }
        for act in activities
    ]

    # 3. Role & Dynamic Role Readiness
    target_role = (state.target_role if state else None) or "DevOps Engineer"
    role_conf = get_role_config(target_role)
    roadmap = role_conf.get("roadmap", [])
    roadmap_topics = [m["topic"] for m in roadmap]

    role_readiness_pct, readiness_details = calculate_role_readiness(target_role, state, all_quizzes)
    topics_mastered = calculate_topics_mastered(target_role, state)
    streak = calculate_user_streak(state.active_days if state else [], state.last_activity_date if state else None)
    formatted_learning_time = format_learning_time(state.total_learning_hours if state else 0.0)

    # 4. Continuation course
    continue_course = None
    if state and state.current_topic:
        c_topic = state.current_topic
        c_detail = stats["topic_details"].get(c_topic, {})
        if c_detail.get("progress_pct", 0) < 100:
            active_mod = state.current_module or "intro"
            pos_sec = float(state.last_video_position_seconds or 0.0)
            continue_course = {
                "topic": c_topic,
                "module": active_mod,
                "video_id": state.last_video_id,
                "video_title": state.last_video_title or f"{c_topic} - Module {active_mod.capitalize()}",
                "position_seconds": pos_sec,
                "formatted_position": f"{int(pos_sec // 60):02d}:{int(pos_sec % 60):02d}",
                "progress_pct": c_detail.get("progress_pct", 0),
                "last_accessed_at": state.last_accessed_at,
                "navigate_url": f"/learning/{c_topic}?module={active_mod}&video={state.last_video_id or ''}&t={int(pos_sec)}"
            }

    if not continue_course and roadmap_topics:
        next_topic = roadmap_topics[0]
        for t in roadmap_topics:
            t_detail = stats["topic_details"].get(t, {})
            if t_detail.get("progress_pct", 0) < 100:
                next_topic = t
                break
        continue_course = {
            "topic": next_topic,
            "module": "intro",
            "video_id": None,
            "video_title": f"Start learning {next_topic} for {target_role}",
            "position_seconds": 0.0,
            "formatted_position": "00:00",
            "progress_pct": stats["topic_details"].get(next_topic, {}).get("progress_pct", 0),
            "last_accessed_at": state.last_accessed_at if state else None,
            "navigate_url": f"/learning/{next_topic}?module=intro"
        }

    # 5. Modular sections
    dsa_info = _build_dsa_info(state, progress, role_conf)
    skills_data = _build_skills_data(state, progress, stats, all_quizzes, target_role, role_conf)
    recommendations_list = _build_recommendations_data(state, progress, stats, target_role, role_conf)
    roadmap_data = _build_roadmap_data(state, progress, stats, target_role, role_conf)
    quiz_analysis_data = _build_quiz_analysis_data(all_quizzes)

    # Overview Metrics (derived deterministically from persistent state)
    overview_data = {
        "username": user.username,
        "has_started": bool(state),
        "overall_progress": formatted_learning_time,
        "learning_time": formatted_learning_time,
        "learning_time_formatted": formatted_learning_time,
        "overall_learning_time": formatted_learning_time,
        "topics_mastered": topics_mastered,
        "completed_modules": topics_mastered,
        "total_modules": stats["total_modules"],
        "topics_completed": topics_mastered,
        "topics_in_progress": stats["topics_in_progress"],
        "total_learning_hours": round(state.total_learning_hours or 0.0, 2) if state else 0.0,
        "current_streak": streak,
        "completed_projects": state.completed_projects or 0 if state else 0,
        "target_role": target_role,
        "extracted_skills": state.extracted_skills or [] if state else [],
        "role_readiness_pct": role_readiness_pct,
        "role_readiness_details": readiness_details,
        "continue_course": continue_course,
        "dsa_language": dsa_info["dsa_language"],
        "initial_performance_category": getattr(state, "initial_performance_category", None) if state else None,
        "current_ability": getattr(state, "current_ability", 0.5) if state else 0.5,
    }

    profile_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "target_role": target_role,
        "dsa_language": dsa_info["dsa_language"],
        "initial_performance_category": getattr(state, "initial_performance_category", None) if state else None,
        "current_ability": getattr(state, "current_ability", 0.5) if state else 0.5,
    }

    return {
        "profile": profile_data,
        "overview": overview_data,
        "dsa_info": dsa_info,
        "skills": skills_data,
        "recommendations": recommendations_list,
        "roadmap": roadmap_data,
        "quiz_analysis": quiz_analysis_data,
        "timeline": timeline_list,
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT: /dashboard/overview
# ═══════════════════════════════════════════════════════════════════════════
@router.get("/overview")
async def dashboard_overview(user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    state = await _get_user_state(user.id, db)
    if not state:
        return {
            "username": user.username,
            "has_started": False,
            "overall_progress": "0h 00m",
            "learning_time": "0h 00m",
            "learning_time_formatted": "0h 00m",
            "overall_learning_time": "0h 00m",
            "topics_mastered": 0,
            "completed_modules": 0,
            "total_modules": 0,
            "topics_completed": 0,
            "topics_in_progress": 0,
            "total_learning_hours": 0.0,
            "current_streak": 0,
            "completed_projects": 0,
            "target_role": None,
            "role_readiness_pct": 0,
            "continue_course": None
        }

    progress = _safe_progress(state)
    stats = _compute_overall_progress(progress)

    # Quizzes
    quiz_res = await db.execute(
        select(models.QuizHistory)
        .filter(models.QuizHistory.user_id == user.id)
    )
    all_quizzes = quiz_res.scalars().all()

    # Target role & Role Readiness
    target_role = state.target_role or "DevOps Engineer"
    role_conf = get_role_config(target_role)
    roadmap = role_conf.get("roadmap", [])
    roadmap_topics = [m["topic"] for m in roadmap]

    role_readiness_pct, readiness_details = calculate_role_readiness(target_role, state, all_quizzes)
    topics_mastered = calculate_topics_mastered(target_role, state)
    streak = calculate_user_streak(state.active_days or [], state.last_activity_date)
    formatted_learning_time = format_learning_time(state.total_learning_hours or 0.0)

    # Current continuation course
    continue_course = None
    if state.current_topic:
        c_topic = state.current_topic
        c_detail = stats["topic_details"].get(c_topic, {})
        if c_detail.get("progress_pct", 0) < 100:
            active_mod = state.current_module or "intro"
            pos_sec = float(state.last_video_position_seconds or 0.0)
            continue_course = {
                "topic": c_topic,
                "module": active_mod,
                "video_id": state.last_video_id,
                "video_title": state.last_video_title or f"{c_topic} - Module {active_mod.capitalize()}",
                "position_seconds": pos_sec,
                "formatted_position": f"{int(pos_sec // 60):02d}:{int(pos_sec % 60):02d}",
                "progress_pct": c_detail.get("progress_pct", 0),
                "last_accessed_at": state.last_accessed_at,
                "navigate_url": f"/learning/{c_topic}?module={active_mod}&video={state.last_video_id or ''}&t={int(pos_sec)}"
            }

    if not continue_course and roadmap_topics:
        next_topic = roadmap_topics[0]
        for t in roadmap_topics:
            t_detail = stats["topic_details"].get(t, {})
            if t_detail.get("progress_pct", 0) < 100:
                next_topic = t
                break
        continue_course = {
            "topic": next_topic,
            "module": "intro",
            "video_id": None,
            "video_title": f"Start learning {next_topic} for {target_role}",
            "position_seconds": 0.0,
            "formatted_position": "00:00",
            "progress_pct": stats["topic_details"].get(next_topic, {}).get("progress_pct", 0),
            "last_accessed_at": state.last_accessed_at,
            "navigate_url": f"/learning/{next_topic}?module=intro"
        }

    return {
        "username": user.username,
        "has_started": True,
        "overall_progress": formatted_learning_time,
        "learning_time": formatted_learning_time,
        "learning_time_formatted": formatted_learning_time,
        "overall_learning_time": formatted_learning_time,
        "topics_mastered": topics_mastered,
        "completed_modules": topics_mastered,
        "total_modules": stats["total_modules"],
        "topics_completed": topics_mastered,
        "topics_in_progress": stats["topics_in_progress"],
        "total_learning_hours": round(state.total_learning_hours or 0.0, 2),
        "current_streak": streak,
        "completed_projects": state.completed_projects or 0,
        "target_role": state.target_role,
        "extracted_skills": state.extracted_skills or [],
        "role_readiness_pct": role_readiness_pct,
        "role_readiness_details": readiness_details,
        "continue_course": continue_course,
        "dsa_language": getattr(state, "dsa_language", "Python") or "Python",
        "initial_performance_category": getattr(state, "initial_performance_category", None),
        "current_ability": getattr(state, "current_ability", 0.5),
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT: /dashboard/progress
# ═══════════════════════════════════════════════════════════════════════════
@router.get("/progress")
async def dashboard_progress(user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    state = await _get_user_state(user.id, db)
    if not state:
        return {"topics": {}, "overall_pct": 0}

    progress = _safe_progress(state)
    stats = _compute_overall_progress(progress)

    return {
        "overall_pct": stats["overall_pct"],
        "topics": stats["topic_details"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT: /dashboard/activity
# ═══════════════════════════════════════════════════════════════════════════
@router.get("/activity")
async def dashboard_activity(user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Fetch all learning activities for this user
    result = await db.execute(
        select(models.LearningActivity)
        .filter(models.LearningActivity.user_id == user.id)
        .order_by(models.LearningActivity.created_at.desc())
        .limit(50)
    )
    activities = result.scalars().all()

    timeline = []
    for act in activities:
        timeline.append({
            "id": act.id,
            "type": act.activity_type,
            "title": act.title,
            "description": act.description,
            "topic": act.topic,
            "created_at": act.created_at,
        })

    # Build weekly learning hours from quiz history (approximate: 0.75 hr per quiz entry)
    quiz_result = await db.execute(
        select(models.QuizHistory).filter(models.QuizHistory.user_id == user.id)
    )
    all_quizzes = quiz_result.scalars().all()

    # Group activity by date from LearningActivity timestamps
    daily_hours = {}
    for act in activities:
        if act.created_at:
            try:
                day = act.created_at[:10]  # "YYYY-MM-DD"
                daily_hours[day] = daily_hours.get(day, 0) + 0.75
            except Exception:
                pass

    # If no activity records yet, estimate from quiz count
    if not daily_hours and all_quizzes:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        daily_hours[today] = len(all_quizzes) * 0.75

    # Build last 14 days chart data
    chart_data = []
    today = datetime.utcnow().date()
    for i in range(13, -1, -1):
        day = (today - timedelta(days=i)).isoformat()
        chart_data.append({"date": day, "hours": round(daily_hours.get(day, 0), 2)})

    return {
        "timeline": timeline,
        "daily_hours": chart_data,
        "total_activities": len(activities),
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT: /dashboard/skills
# ═══════════════════════════════════════════════════════════════════════════
@router.get("/skills")
async def dashboard_skills(user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    state = await _get_user_state(user.id, db)
    progress = _safe_progress(state)
    stats = _compute_overall_progress(progress)
    target_role = (state.target_role if state else None) or "DevOps Engineer"
    role_conf = get_role_config(target_role)

    quiz_result = await db.execute(
        select(models.QuizHistory).filter(models.QuizHistory.user_id == user.id)
    )
    all_quizzes = quiz_result.scalars().all()
    return _build_skills_data(state, progress, stats, all_quizzes, target_role, role_conf)


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT: /dashboard/quiz-analysis
# ═══════════════════════════════════════════════════════════════════════════
@router.get("/quiz-analysis")
async def dashboard_quiz_analysis(user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    quiz_res = await db.execute(
        select(models.QuizHistory)
        .filter(models.QuizHistory.user_id == user.id)
        .order_by(models.QuizHistory.id.desc())
    )
    quizzes = quiz_res.scalars().all()
    return _build_quiz_analysis_data(quizzes)



# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT: /dashboard/insights
# ═══════════════════════════════════════════════════════════════════════════
@router.get("/insights")
async def dashboard_insights(user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    state = await _get_user_state(user.id, db)
    if not state:
        return {"insights": ["Start your learning journey to see personalized AI insights!"], "source": "fallback"}

    # Check Redis cache first
    cache_key = f"dashboard_insights:{user.id}"
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return {"insights": json.loads(cached), "source": "cache"}
    except Exception as e:
        logging.warning(f"Redis get insights error: {e}")

    progress = _safe_progress(state)
    stats = _compute_overall_progress(progress)

    # Get quiz history
    quiz_result = await db.execute(
        select(models.QuizHistory).filter(models.QuizHistory.user_id == user.id)
    )
    all_quizzes = quiz_result.scalars().all()

    # Build context for AI
    completed_topics = [t for t in TOPICS if stats["topic_details"].get(t, {}).get("progress_pct", 0) == 100]
    in_progress_topics = [
        f"{t} ({stats['topic_details'].get(t, {}).get('progress_pct', 0)}%)"
        for t in TOPICS
        if 0 < stats["topic_details"].get(t, {}).get("progress_pct", 0) < 100
    ]
    weak_topics = [
        t for t in TOPICS
        if stats["topic_details"].get(t, {}).get("progress_pct", 0) == 0
        and t in ROLE_SKILLS.get(state.target_role or "", [])
    ]

    # Average scores by topic
    topic_scores = {}
    for q in all_quizzes:
        topic_scores.setdefault(q.topic, []).append(q.quiz_score)
    avg_scores = {t: round(sum(s) / len(s), 1) for t, s in topic_scores.items()}

    context = {
        "username": user.username,
        "target_role": state.target_role,
        "overall_progress": stats["overall_pct"],
        "completed_topics": completed_topics,
        "in_progress_topics": in_progress_topics,
        "weak_topics": weak_topics,
        "total_hours": round(state.total_learning_hours or 0, 1),
        "current_streak": state.current_streak or 0,
        "badges_count": len(state.badges or []),
        "avg_scores_by_topic": avg_scores,
        "total_quizzes_taken": len(all_quizzes),
        "extracted_skills": state.extracted_skills or [],
        "dsa_language": getattr(state, "dsa_language", "Python") or "Python",
        "current_continuation": (
            f"{state.current_topic} ({stats['topic_details'].get(state.current_topic, {}).get('progress_pct', 0)}% completed, module: {state.current_module or 'intro'})"
            if state.current_topic and stats["topic_details"].get(state.current_topic, {}).get("progress_pct", 0) < 100
            else None
        ),
    }

    # Try Groq API for AI insights (with 6.0s timeout and caching)
    if GROQ_API_KEY:
        try:
            insights = await _generate_groq_insights(context)
            if insights:
                try:
                    await redis_client.set(cache_key, json.dumps(insights), ex=600)
                except Exception:
                    pass
                return {"insights": insights, "source": "ai"}
        except Exception as e:
            logging.warning(f"Groq insights skipped or timed out: {e}")

    # Fallback: rule-based insights
    insights = _generate_rule_based_insights(context)
    try:
        await redis_client.set(cache_key, json.dumps(insights), ex=300)
    except Exception:
        pass
    return {"insights": insights, "source": "rule_based"}


async def _generate_groq_insights(context: dict) -> list:
    """Call Groq API to generate personalized learning insights."""
    prompt = f"""You are an AI learning advisor for SkillPath AI. Analyze this learner's data and provide exactly 5 concise, personalized insights.

Learner Data:
- Username: {context['username']}
- Target Role: {context['target_role']}
- Preferred DSA Language: {context.get('dsa_language', 'Python')}
- Overall Progress: {context['overall_progress']}%
- Completed Topics: {', '.join(context['completed_topics']) or 'None yet'}
- In Progress: {', '.join(context['in_progress_topics']) or 'None'}
- Weak/Not Started Topics (needed for role): {', '.join(context['weak_topics']) or 'None'}
- Total Learning Hours: {context['total_hours']}
- Current Streak: {context['current_streak']} days
- Badges Earned: {context['badges_count']}
- Quiz Scores by Topic: {json.dumps(context['avg_scores_by_topic'])}
- Total Quizzes Taken: {context['total_quizzes_taken']}
- Existing Skills: {', '.join(context['extracted_skills'])}

Rules:
1. Be specific to THIS learner's data — no generic advice
2. Reference actual topics, scores, and progress numbers
3. Include 1 strength observation, 1 area for improvement, 1 recommendation, 1 consistency/streak comment, and 1 goal-alignment insight
4. Each insight should be 1-2 sentences max
5. Return ONLY a JSON array of 5 strings, no markdown or extra text

Example format: ["insight 1", "insight 2", "insight 3", "insight 4", "insight 5"]"""

    async with httpx.AsyncClient(timeout=6.0) as client:
        resp = await client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()

        # Parse the JSON array from the response
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        insights = json.loads(content)
        if isinstance(insights, list) and len(insights) > 0:
            return insights[:5]

    return None


def _generate_rule_based_insights(context: dict) -> list:
    """Generate insights using simple rules when Groq is unavailable."""
    insights = []

    if context.get("current_continuation"):
        insights.append(f"Active Course: You're progressing through {context['current_continuation']}. Resuming your active lesson will keep your momentum strong.")

    # 1. Progress insight
    pct = context.get("overall_progress", 0)
    target_role = context.get("target_role", "DevOps Engineer")
    if pct >= 75:
        insights.append(f"Excellent progress! You've completed {pct}% of all available content. You're close to mastering the full curriculum.")
    elif pct >= 40:
        insights.append(f"Good momentum — you're {pct}% through the curriculum. Keep this pace and you'll be well-prepared for a {target_role} role.")
    elif pct > 0:
        insights.append(f"You've made a start at {pct}% overall progress. Building consistency now will accelerate your learning significantly.")
    else:
        insights.append("You haven't started any modules yet. Begin with the recommended topic to kick off your learning journey!")

    # 2. Strength insight
    avg_scores = context.get("avg_scores_by_topic", {})
    extracted_skills = context.get("extracted_skills", [])
    if avg_scores:
        best_topic = max(avg_scores, key=avg_scores.get)
        best_score = avg_scores[best_topic]
        insights.append(f"You're strongest in {best_topic} with an average quiz score of {best_score}%. Great foundation to build on.")
    elif extracted_skills:
        insights.append(f"Your resume shows skills in {', '.join(extracted_skills[:3])}. These will give you a head start.")

    # 3. Improvement area
    weak_topics = context.get("weak_topics", [])
    if weak_topics:
        insights.append(f"For your {target_role} goal, consider starting {weak_topics[0]} — it's a key skill gap to address.")
    elif avg_scores:
        worst_topic = min(avg_scores, key=avg_scores.get)
        worst_score = avg_scores[worst_topic]
        if worst_score < 70:
            insights.append(f"Your {worst_topic} quiz average is {worst_score}%. Revisiting the core concepts could boost your confidence here.")

    # 4. Streak/consistency
    streak = context.get("current_streak", 0)
    if streak >= 7:
        insights.append(f"Amazing! Your {streak}-day streak shows incredible dedication. Consistency is the key to mastery.")
    elif streak >= 3:
        insights.append(f"You're on a {streak}-day learning streak. Keep it going to build strong study habits!")
    else:
        insights.append("Try to study a little each day — even 15 minutes builds powerful habits over time.")

    # 5. Hours insight
    hours = context.get("total_hours", 0)
    if hours >= 10:
        insights.append(f"You've invested {hours} hours in learning. That's serious commitment — keep tracking your progress!")
    elif hours > 0:
        insights.append(f"You've logged {hours} hours so far. Each session brings you closer to your {target_role} goal.")
    else:
        insights.append(f"Start your first module to begin tracking your learning hours toward becoming a {target_role}.")

    return insights[:5]


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT: /dashboard/recommendations
# ═══════════════════════════════════════════════════════════════════════════
async def _generate_groq_topic_recommendations(context: dict) -> list:
    """Calls Groq API to generate personalized structured topic recommendations based on role roadmap and prerequisites."""
    if not GROQ_API_KEY:
        return []

    target_role = context.get('target_role', 'DevOps Engineer')
    role_conf = get_role_config(target_role)
    roadmap = role_conf.get("roadmap", [])

    prompt = f"""You are a senior AI career architect for SkillPath AI.
Analyze this learner's target role, resume, missing skill gaps, and roadmap prerequisites to recommend exactly 3 to 5 next topics to learn.

TARGET CAREER ROLE: {target_role} ({role_conf.get('category', 'Technology')})
ROLE DESCRIPTION: {role_conf.get('description', '')}

ORDERED ROLE ROADMAP (WITH PREREQUISITES):
{json.dumps(roadmap, indent=2)}

LEARNER PROFILE:
- Existing Resume Skills (ALREADY MASTERED): {json.dumps(context['extracted_skills'])}
- Missing Skill Gaps: {json.dumps(context['skill_gaps'])}
- Already Acquired Skills: {json.dumps(context['already_have'])}
- Overall Progress: {context['overall_progress']}%
- Completed Topics: {json.dumps(context['completed_topics'])}
- In-Progress Topics: {json.dumps(context['in_progress_topics'])}
- Quiz Average by Topic: {json.dumps(context['avg_scores_by_topic'])}
- Current Ability Level: {context['ability_level']}

CRITICAL RECOMMENDATION RULES:
1. DO NOT recommend topics the user already has on their resume or has fully completed, unless for advanced revision.
2. RESPECT PREREQUISITES: If a topic requires a prerequisite that the user lacks, recommend the prerequisite first (e.g., Docker before Kubernetes; Linux before Docker).
3. Prioritize missing skills that are highest priority in the target role's roadmap.
4. Each recommended topic must match an actual topic name from the roadmap or TOPICS list.
5. Return ONLY a valid JSON object matching this schema:
{{
  "recommendedTopics": [
    {{
      "topic": "Docker",
      "reason": "Missing core skill for DevOps Engineer; prerequisite for Kubernetes",
      "priority": "high",
      "difficulty": "intermediate"
    }}
  ]
}}"""

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "You output only clean, valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
            )

        if resp.status_code == 200:
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"].strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            parsed = json.loads(raw_text.strip())
            topics_list = parsed.get("recommendedTopics", [])
            valid_recs = []
            for item in topics_list:
                t = item.get("topic")
                if t in TOPICS or any(t.lower() == existing.lower() for existing in TOPICS):
                    # Find exact case match
                    matched_topic = next((ext for ext in TOPICS if ext.lower() == t.lower()), t)
                    valid_recs.append({
                        "topic": matched_topic,
                        "title": f"Master {matched_topic}",
                        "description": item.get("reason", f"Important skill for {target_role}"),
                        "priority": item.get("priority", "medium"),
                        "difficulty": item.get("difficulty", "intermediate")
                    })
            if valid_recs:
                return valid_recs
    except Exception as e:
        logging.warning(f"Groq topic recommendation error: {e}")

    return []


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT: /dashboard/recommendations
# ═══════════════════════════════════════════════════════════════════════════
@router.get("/recommendations")
async def dashboard_recommendations(user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    state = await _get_user_state(user.id, db)
    progress = _safe_progress(state)
    stats = _compute_overall_progress(progress)
    target_role = (state.target_role if state else None) or "DevOps Engineer"
    role_conf = get_role_config(target_role)

    recs = _build_recommendations_data(state, progress, stats, target_role, role_conf)
    if state:
        state.recommended_topics = recs
        await db.commit()
    return {"recommendations": recs}


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT: /dashboard/roadmap
# ═══════════════════════════════════════════════════════════════════════════
@router.get("/roadmap")
async def dashboard_roadmap(user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    state = await _get_user_state(user.id, db)
    target_role = (state.target_role if state else None) or "DevOps Engineer"
    role_conf = get_role_config(target_role)
    progress = _safe_progress(state)
    stats = _compute_overall_progress(progress)
    return _build_roadmap_data(state, progress, stats, target_role, role_conf)


