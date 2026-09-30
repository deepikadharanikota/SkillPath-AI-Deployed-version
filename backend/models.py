from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True, nullable=True)
    supabase_id = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)

class UserState(Base):
    __tablename__ = "user_states"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    target_role = Column(String)
    extracted_skills = Column(JSON) # list of skills
    current_topic = Column(String)
    current_difficulty = Column(String)
    current_module = Column(String)
    module_progress = Column(JSON) # dict: {topic: {intro: "active", core: "locked", summary: "locked"}}
    fatigue = Column(Float, default=0.0)

    # ── Resume & Skill persistence ──
    resume_filename = Column(String, nullable=True)
    resume_uploaded_at = Column(String, nullable=True)
    resume_file_path = Column(String, nullable=True)
    resume_text = Column(String, nullable=True)
    extracted_skills_categorized = Column(JSON, nullable=True)  # dict by category

    # ── Video completion & Adaptive tracking ──
    video_progress = Column(JSON, default=dict)    # dict: {topic: {module: [completed_video_ids]}}
    topic_ability = Column(JSON, default=dict)     # dict: {topic: {abilityLevel, videoLevel, quizLevel, quizAverage, videosCompleted, lastScore}}
    recommended_topics = Column(JSON, nullable=True) # list of structured Groq recommendations
    last_video_id = Column(String, nullable=True)
    last_video_title = Column(String, nullable=True)
    last_video_position_seconds = Column(Float, default=0.0)
    last_accessed_at = Column(String, nullable=True)

    # ── DSA Personalization & Research Tracking ──
    dsa_language = Column(String, default="Python", nullable=True) # "C++", "Java", "Python"
    initial_performance_category = Column(String, nullable=True)   # "below_average", "average", "excellent" (fixed cohort)
    current_ability = Column(Float, default=0.5)                   # adaptive ability level (0.0 - 1.0)
    created_at = Column(String, nullable=True)                     # ISO timestamp
    updated_at = Column(String, nullable=True)                     # ISO timestamp

    # ── Dashboard tracking fields ──
    total_learning_hours = Column(Float, default=0.0)
    current_streak = Column(Integer, default=0)
    last_activity_date = Column(String, nullable=True)   # ISO date "YYYY-MM-DD"
    active_days = Column(JSON, default=list, nullable=True)  # List of unique active calendar dates ["YYYY-MM-DD"]
    completed_projects = Column(Integer, default=0)
    badges = Column(JSON, nullable=True)                 # list of badge dicts

    user = relationship("User")

class QuizHistory(Base):
    __tablename__ = "quiz_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    topic = Column(String, index=True)
    module_key = Column(String)
    difficulty = Column(String)
    quiz_score = Column(Float)
    code_score = Column(Float, default=0.0)
    reward = Column(Float, default=0.0)

    # ── Detailed Quiz Result Fields ──
    quiz_id = Column(String, index=True, nullable=True)
    questions = Column(JSON, nullable=True)        # [{question, options, correctAnswer, explanation}]
    user_answers = Column(JSON, nullable=True)     # {questionIndex: answer}
    correct_answers = Column(JSON, nullable=True)  # {questionIndex: answer}
    score = Column(Integer, default=0)             # Correct count
    total_questions = Column(Integer, default=0)
    percentage = Column(Float, default=0.0)
    unanswered = Column(Integer, default=0)
    completed_at = Column(String, nullable=True)   # ISO timestamp

class LearningActivity(Base):
    """Chronological log of user learning events for the dashboard timeline."""
    __tablename__ = "learning_activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    activity_type = Column(String)       # "started_course", "completed_module", "completed_skill", "earned_badge", "completed_project", "changed_dsa_language", "changed_target_role"
    title = Column(String)
    description = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    created_at = Column(String, index=True) # ISO timestamp "YYYY-MM-DDTHH:MM:SS"
