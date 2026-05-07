from __future__ import annotations

import hashlib
import json
import logging
import math
import re
from dataclasses import asdict, dataclass
from datetime import time

from django.conf import settings
from django.core.cache import cache

from apps.activities.models import Activity

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled by runtime fallback
    OpenAI = None


logger = logging.getLogger(__name__)
AI_CLASSIFIER_CACHE_VERSION = "2026-05-01-openai-v3"

DIFFICULTY_MULTIPLIERS = {
    Activity.Difficulty.EASY: 1.0,
    Activity.Difficulty.MEDIUM: 2.0,
    Activity.Difficulty.HARD: 3.5,
    Activity.Difficulty.EXTREME: 5.0,
}

DIFFICULTY_COMPLETION_BONUS = {
    Activity.Difficulty.EASY: 2,
    Activity.Difficulty.MEDIUM: 6,
    Activity.Difficulty.HARD: 12,
    Activity.Difficulty.EXTREME: 20,
}

DIFFICULTY_ORDER = {
    Activity.Difficulty.EASY: 0,
    Activity.Difficulty.MEDIUM: 1,
    Activity.Difficulty.HARD: 2,
    Activity.Difficulty.EXTREME: 3,
}

XP_CAPS = {
    Activity.Difficulty.EASY: 100,
    Activity.Difficulty.MEDIUM: 250,
    Activity.Difficulty.HARD: 500,
    Activity.Difficulty.EXTREME: 800,
}

CATEGORY_KEYWORDS = {
    "reading": ["read", "pages", "book", "novel", "article", "magazine", "textbook"],
    "study": ["study", "review", "exam", "quiz", "revise", "chapter", "homework", "assignment", "lesson"],
    "workout": ["workout", "stretch", "training", "run", "gym", "exercise", "marathon", "hiit", "cardio", "hike", "hiking", "trek", "trekking", "climb", "climbing", "mountaineering"],
    "coding": ["code", "bug", "feature", "api", "auth", "refactor", "implement", "fix typo", "debug", "backend", "frontend"],
    "cleaning": ["clean", "desk", "room", "apartment", "house", "laundry", "organize", "tidy"],
    "hydration": ["drink water", "water", "hydrate"],
    "cooking": ["cook", "cooking", "bake", "recipe", "meal prep", "grill", "kitchen", "boil", "fry"],
    "meal": ["snack", "breakfast", "lunch", "dinner", "meal", "eat", "groceries", "grocery"],
    "communication": ["call", "phone", "message", "email", "reply", "text", "dm"],
    "meeting": ["meeting", "zoom", "interview", "appointment"],
    "mindfulness": ["meditate", "meditation", "pray", "journal", "breathing"],
    "health": ["medicine", "medication", "meds", "pill", "pills", "tablet", "tablets", "supplement", "vitamin", "doctor", "therapy", "walk", "rest"],
    "design": ["design", "wireframe", "prototype", "figma", "mockup", "ui", "ux"],
    "writing": ["write", "essay", "draft", "article", "blog", "report", "outline"],
    "planning": ["plan", "planning", "schedule", "roadmap", "organize", "arrange", "prepare"],
}

INSTANT_TASK_RULES = {
    "hydration": {
        "difficulty": Activity.Difficulty.EASY,
        "multiplier": 1.0,
        "estimated_duration_minutes": 5,
        "workload": "instant",
        "explanation": "This looks like a quick hydration habit, so AI treats it as an easy instant task.",
    },
    "communication": {
        "difficulty": Activity.Difficulty.EASY,
        "multiplier": 1.0,
        "estimated_duration_minutes": 10,
        "workload": "short",
        "explanation": "Short calls and messages are treated as easy unless the text signals a bigger responsibility.",
    },
    "health": {
        "difficulty": Activity.Difficulty.EASY,
        "multiplier": 1.0,
        "estimated_duration_minutes": 10,
        "workload": "short",
        "explanation": "Simple health reminders like medicine or vitamins are treated as easy habit tasks.",
    },
}

STOPWORDS = {
    "the",
    "a",
    "an",
    "to",
    "for",
    "and",
    "of",
    "my",
    "your",
    "with",
    "on",
    "in",
    "at",
    "from",
}

EASY_HINTS = {
    "drink water",
    "water",
    "snack",
    "call mom",
    "call dad",
    "reply email",
    "check email",
    "take medicine",
    "take my medicine",
    "take meds",
    "medication",
    "pill",
    "supplement",
    "vitamin",
    "stretch",
}

QUICK_ACTION_VERBS = {
    "call",
    "check",
    "confirm",
    "drink",
    "log",
    "message",
    "pay",
    "record",
    "reply",
    "send",
    "submit",
    "take",
    "text",
    "track",
}

PROCESS_ACTION_VERBS = {
    "bake",
    "build",
    "clean",
    "code",
    "cook",
    "cooking",
    "design",
    "develop",
    "exercise",
    "organize",
    "plan",
    "prepare",
    "read",
    "research",
    "review",
    "shop",
    "shopping",
    "study",
    "train",
    "workout",
    "write",
}

QUICK_OBJECT_HINTS = {
    "bill",
    "dad",
    "email",
    "medication",
    "medicine",
    "meds",
    "message",
    "mom",
    "pill",
    "pills",
    "supplement",
    "tablet",
    "tablets",
    "text",
    "vitamin",
    "water",
}

LARGE_SCOPE_HINTS = {
    "apartment",
    "assignment",
    "breakfast",
    "chapter",
    "dinner",
    "exam",
    "feature",
    "groceries",
    "grocery",
    "house",
    "kitchen",
    "lunch",
    "meal",
    "paper",
    "presentation",
    "project",
    "recipe",
    "report",
    "room",
    "system",
    "workout",
}

HARD_HINTS = {
    "build feature",
    "research paper",
    "multiple chapters",
    "deep clean",
    "presentation",
    "project",
    "thesis",
    "refactor",
}

EXTREME_HINTS = {
    "authentication system",
    "final exam",
    "midterm exam",
    "dissertation",
    "capstone",
    "full house cleaning",
    "marathon training",
}

AI_SCHEMA = {
    "name": "task_classification",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "detected_category": {"type": "string", "maxLength": 80},
            "is_quick_task": {"type": "boolean"},
            "estimated_workload": {"type": "string", "maxLength": 30},
            "estimated_duration_minutes": {"type": "integer", "minimum": 1, "maximum": 1440},
            "detected_difficulty": {"type": "string", "enum": ["easy", "medium", "hard", "extreme"]},
            "ai_multiplier": {"type": "number", "minimum": 1.0, "maximum": 2.5},
            "effort_domain": {"type": "string", "enum": ["habit", "administrative", "cognitive", "physical", "creative", "mixed"]},
            "stakes_level": {"type": "string", "enum": ["low", "normal", "high", "critical"]},
            "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "explanation": {"type": "string", "maxLength": 280},
        },
        "required": [
            "detected_category",
            "is_quick_task",
            "estimated_workload",
            "estimated_duration_minutes",
            "detected_difficulty",
            "ai_multiplier",
            "effort_domain",
            "stakes_level",
            "confidence_score",
            "explanation",
        ],
    },
    "strict": True,
}

OPENAI_SYSTEM_PROMPT = """
You classify productivity tasks for a gamified task application.

You must reason like a smart human assistant, not like a keyword matcher.
Use the task title, description, and schedule context to judge what the task really means.

Important rules:
- Distinguish quick point-in-time tasks from tasks that require sustained effort.
- Use schedule context as evidence, but do not blindly assume all long scheduled blocks are hard.
- A long outdoor hike, hard physical training, large deliverables, or major preparation can be hard or extreme.
- Very small actions like drinking water, taking medicine, or replying to an email are quick tasks.
- Infer a clean category label even for novel tasks.
- Estimated duration_minutes should reflect the likely active effort, not just the calendar block.
- ai_multiplier should stay between 1.0 and 2.5 and should increase with scope, difficulty, and exceptional effort.
- effort_domain should describe the main kind of effort: habit, administrative, cognitive, physical, creative, or mixed.
- stakes_level should reflect consequences and pressure: low, normal, high, or critical.
- confidence_score should reflect how confident you are in the classification.
- explanation must be concise: one or two short sentences, no more than 35 words.

Difficulty guidance:
- easy: trivial or lightweight task
- medium: meaningful but normal task
- hard: demanding task requiring strong effort, stamina, or scope
- extreme: unusually demanding, long, high-stakes, or physically/cognitively intense task

Return only structured JSON that matches the schema exactly.
""".strip()


@dataclass
class AIClassificationResult:
    detected_category: str
    estimated_workload: str
    estimated_duration_minutes: int
    detected_difficulty: str
    ai_multiplier: float
    explanation: str
    anomaly_risk_rules: dict
    is_quick_task: bool = False
    provider: str = "fallback_rules"
    effort_domain: str = "mixed"
    stakes_level: str = "normal"
    confidence_score: float = 0.5

    def to_dict(self) -> dict:
        payload = {
            "detected_category": self.detected_category,
            "estimated_workload": self.estimated_workload,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "detected_difficulty": self.detected_difficulty,
            "ai_multiplier": self.ai_multiplier,
            "explanation": self.explanation,
            "anomaly_risk_rules": self.anomaly_risk_rules,
            "is_quick_task": self.is_quick_task,
            "provider": self.provider,
        }
        payload["estimated_xp"] = estimate_xp(
            actual_duration_minutes=self.estimated_duration_minutes,
            detected_difficulty=self.detected_difficulty,
            ai_multiplier=self.ai_multiplier,
        )
        return payload


def extract_number(text: str) -> int | None:
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else None


def tokenize_text(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())


def infer_category(text: str) -> str:
    lowered = text.lower()
    tokens = set(tokenize_text(text))
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if " " in keyword:
                if keyword in lowered:
                    return category
            elif keyword in tokens:
                return category
    return build_dynamic_category_label(text)


def build_dynamic_category_label(text: str) -> str:
    tokens = tokenize_text(text)
    filtered = [token for token in tokens if token not in STOPWORDS]
    if not filtered:
        return "general"
    if len(filtered) >= 2 and filtered[0] in {"plan", "organize", "prepare", "review", "write"}:
        return filtered[1][:40]
    return filtered[0][:40]


def calculate_minutes_between(start_time: time | None, end_time: time | None) -> int | None:
    if not start_time or not end_time:
        return None
    start_total = start_time.hour * 60 + start_time.minute
    end_total = end_time.hour * 60 + end_time.minute
    if end_total <= start_total:
        return None
    return end_total - start_total


def extract_explicit_minutes(text: str) -> int | None:
    minute_match = re.search(r"(\d+)\s*(minute|minutes|min)\b", text)
    hour_match = re.search(r"(\d+)\s*(hour|hours|hr|hrs)\b", text)
    if hour_match:
        return int(hour_match.group(1)) * 60
    if minute_match:
        return int(minute_match.group(1))
    return None


def choose_estimated_duration(*, text: str, planned_duration_minutes: int | None, default_minutes: int) -> int:
    explicit_minutes = extract_explicit_minutes(text)
    if explicit_minutes:
        return explicit_minutes
    if planned_duration_minutes:
        return max(5, planned_duration_minutes)
    return default_minutes


def looks_like_quick_task(text: str) -> bool:
    tokens = tokenize_text(text)
    if not tokens:
        return False

    joined = " ".join(tokens)
    if any(phrase in joined for phrase in EASY_HINTS):
        return True

    if len(tokens) > 4:
        return False

    if any(token in PROCESS_ACTION_VERBS for token in tokens):
        return False

    if tokens[0] not in QUICK_ACTION_VERBS:
        return False

    if any(token in LARGE_SCOPE_HINTS for token in tokens[1:]):
        return False

    return any(token in QUICK_OBJECT_HINTS for token in tokens[1:]) or len(tokens) <= 2


def normalize_category(value: str, *, original_text: str) -> str:
    cleaned = (value or "").strip().lower().replace("/", " ").replace("_", " ")
    cleaned = re.sub(r"[^a-z0-9 -]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return build_dynamic_category_label(original_text)
    return cleaned[:80]


def normalize_workload(value: str) -> str:
    cleaned = (value or "").strip().lower()
    if cleaned in {"instant", "light", "moderate", "heavy", "very heavy", "short"}:
        return cleaned
    return "light" if "quick" in cleaned else "moderate"


def normalize_difficulty(value: str) -> str:
    cleaned = (value or "").strip().lower()
    if cleaned in DIFFICULTY_MULTIPLIERS:
        return cleaned
    return Activity.Difficulty.MEDIUM


def normalize_effort_domain(value: str) -> str:
    cleaned = (value or "").strip().lower()
    if cleaned in {"habit", "administrative", "cognitive", "physical", "creative", "mixed"}:
        return cleaned
    return "mixed"


def normalize_stakes_level(value: str) -> str:
    cleaned = (value or "").strip().lower()
    if cleaned in {"low", "normal", "high", "critical"}:
        return cleaned
    return "normal"


def clamp_duration(value: int | float | str | None, *, fallback: int = 20) -> int:
    try:
        duration = int(value)
    except (TypeError, ValueError):
        duration = fallback
    return max(1, min(duration, 1440))


def clamp_multiplier(value: int | float | str | None, *, difficulty: str) -> float:
    try:
        multiplier = float(value)
    except (TypeError, ValueError):
        multiplier = {
            Activity.Difficulty.EASY: 1.0,
            Activity.Difficulty.MEDIUM: 1.3,
            Activity.Difficulty.HARD: 1.8,
            Activity.Difficulty.EXTREME: 2.3,
        }[difficulty]
    return round(max(1.0, min(multiplier, 2.5)), 2)


def clamp_confidence(value: int | float | str | None) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        confidence = 0.5
    return round(max(0.0, min(confidence, 1.0)), 2)


def choose_higher_difficulty(current: str, minimum: str) -> str:
    return current if DIFFICULTY_ORDER[current] >= DIFFICULTY_ORDER[minimum] else minimum


def ensure_minimum_multiplier(*, difficulty: str, multiplier: float, duration_minutes: int) -> float:
    minimums = {
        Activity.Difficulty.EASY: 1.0,
        Activity.Difficulty.MEDIUM: 1.3,
        Activity.Difficulty.HARD: 1.8,
        Activity.Difficulty.EXTREME: 2.3,
    }
    boosted_minimums = {
        Activity.Difficulty.HARD: 2.0 if duration_minutes >= 180 else minimums[Activity.Difficulty.HARD],
        Activity.Difficulty.EXTREME: 2.5 if duration_minutes >= 300 else 2.4 if duration_minutes >= 180 else minimums[Activity.Difficulty.EXTREME],
    }
    minimum = boosted_minimums.get(difficulty, minimums[difficulty])
    return round(max(multiplier, minimum), 2)


def infer_effort_domain_from_category(category: str) -> str:
    mapping = {
        "hydration": "habit",
        "health": "habit",
        "communication": "administrative",
        "meeting": "administrative",
        "planning": "administrative",
        "reading": "cognitive",
        "study": "cognitive",
        "coding": "cognitive",
        "writing": "creative",
        "design": "creative",
        "workout": "physical",
        "cleaning": "physical",
        "cooking": "mixed",
        "meal": "mixed",
    }
    return mapping.get(category, "mixed")


def infer_stakes_from_difficulty(difficulty: str) -> str:
    if difficulty == Activity.Difficulty.EXTREME:
        return "high"
    if difficulty == Activity.Difficulty.HARD:
        return "normal"
    if difficulty == Activity.Difficulty.EASY:
        return "low"
    return "normal"


def build_result(
    *,
    detected_category: str,
    estimated_workload: str,
    estimated_duration_minutes: int,
    detected_difficulty: str,
    ai_multiplier: float,
    explanation: str,
    is_quick_task: bool,
    provider: str,
    effort_domain: str = "mixed",
    stakes_level: str = "normal",
    confidence_score: float = 0.5,
) -> AIClassificationResult:
    min_expected = max(5, round(estimated_duration_minutes * 0.5))
    max_expected = max(15, round(estimated_duration_minutes * 3))
    return AIClassificationResult(
        detected_category=detected_category,
        estimated_workload=estimated_workload,
        estimated_duration_minutes=estimated_duration_minutes,
        detected_difficulty=detected_difficulty,
        ai_multiplier=ai_multiplier,
        explanation=explanation,
        is_quick_task=is_quick_task,
        provider=provider,
        effort_domain=effort_domain,
        stakes_level=stakes_level,
        confidence_score=confidence_score,
        anomaly_risk_rules={
            "expected_duration_range_minutes": [min_expected, max_expected],
            "xp_cap": XP_CAPS[detected_difficulty],
            "flag_if_duration_over_minutes": max_expected,
            "flag_if_ai_multiplier_over": 2.5,
            "is_quick_task": is_quick_task,
            "ai_provider": provider,
            "stakes_level": stakes_level,
            "effort_domain": effort_domain,
            "ai_confidence": confidence_score,
        },
    )


def calibrate_task_result(
    *,
    result: AIClassificationResult,
    title: str,
    description: str,
    planned_duration_minutes: int | None,
) -> AIClassificationResult:
    duration = max(result.estimated_duration_minutes, planned_duration_minutes or 0)
    difficulty = result.detected_difficulty
    multiplier = float(result.ai_multiplier)
    explanation_additions: list[str] = []
    stakes_level = normalize_stakes_level(result.stakes_level)
    effort_domain = normalize_effort_domain(result.effort_domain)
    confidence_score = clamp_confidence(result.confidence_score)
    workload = result.estimated_workload

    long_session = duration >= 180
    very_long_session = duration >= 300
    marathon_session = duration >= 420
    heavy_workload = workload in {"heavy", "very heavy"}
    high_stakes = stakes_level in {"high", "critical"}
    critical_stakes = stakes_level == "critical"
    demanding_domain = effort_domain in {"physical", "cognitive", "creative", "mixed"} and not result.is_quick_task

    minimum_difficulty = difficulty
    if result.is_quick_task:
        minimum_difficulty = difficulty
    elif critical_stakes and long_session:
        minimum_difficulty = Activity.Difficulty.EXTREME
    elif effort_domain == "physical" and very_long_session:
        minimum_difficulty = Activity.Difficulty.EXTREME
    elif high_stakes and very_long_session:
        minimum_difficulty = Activity.Difficulty.EXTREME
    elif heavy_workload and marathon_session and demanding_domain:
        minimum_difficulty = Activity.Difficulty.EXTREME
    elif (high_stakes and long_session) or (heavy_workload and long_session and demanding_domain):
        minimum_difficulty = Activity.Difficulty.HARD
    elif demanding_domain and very_long_session and difficulty == Activity.Difficulty.MEDIUM:
        minimum_difficulty = Activity.Difficulty.HARD

    updated_difficulty = choose_higher_difficulty(difficulty, minimum_difficulty)
    if updated_difficulty != difficulty:
        difficulty = updated_difficulty
        explanation_additions.append("The estimate was strengthened to reflect the overall effort, duration, and stakes more fairly.")

    multiplier = ensure_minimum_multiplier(
        difficulty=difficulty,
        multiplier=multiplier,
        duration_minutes=duration or result.estimated_duration_minutes,
    )

    if difficulty == Activity.Difficulty.EXTREME and workload in {"light", "moderate"}:
        workload = "very heavy"
    elif difficulty == Activity.Difficulty.HARD and workload in {"light", "moderate"}:
        workload = "heavy"

    explanation = result.explanation
    if explanation_additions:
        explanation = f"{explanation} {' '.join(explanation_additions)}".strip()[:600]

    return build_result(
        detected_category=result.detected_category,
        estimated_workload=workload,
        estimated_duration_minutes=max(result.estimated_duration_minutes, 5),
        detected_difficulty=difficulty,
        ai_multiplier=multiplier,
        explanation=explanation,
        is_quick_task=result.is_quick_task,
        provider=result.provider,
        effort_domain=effort_domain,
        stakes_level=stakes_level,
        confidence_score=confidence_score,
    )


def classify_by_category(
    *,
    category: str,
    text: str,
    number: int | None,
    planned_duration_minutes: int | None,
) -> tuple[str, int, float, str, str, bool]:
    if category in INSTANT_TASK_RULES and looks_like_quick_task(text):
        rule = INSTANT_TASK_RULES[category]
        return (
            rule["difficulty"],
            rule["estimated_duration_minutes"],
            rule["multiplier"],
            rule["workload"],
            rule["explanation"],
            True,
        )

    if category == "cooking":
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=45)
        if any(keyword in text for keyword in ["meal prep", "holiday dinner", "for guests", "dinner party", "batch cook"]):
            return "hard", max(duration, 90), 2.0, "heavy", "AI detected a larger cooking scope from the task text.", False
        return "medium", duration, 1.4, "moderate", "AI treated this as a cooking task that usually takes focused time, not an instant action.", False

    if category == "meal":
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=20)
        if looks_like_quick_task(text) and any(keyword in text for keyword in ["snack", "coffee", "tea"]):
            return "easy", min(duration, 15), 1.0, "light", "AI detected a small food or drink task.", True
        if any(keyword in text for keyword in ["groceries", "grocery", "shopping"]):
            return "medium", max(duration, 30), 1.4, "moderate", "AI detected a meal-related errand rather than an instant task.", False
        return "medium", max(duration, 20), 1.3, "moderate", "AI treated this as a meal-related task that usually takes real time.", False

    if category == "reading":
        pages = number if "page" in text or "pages" in text else None
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=15)
        if pages:
            duration = max(15, math.ceil(pages * 1.2))
        if pages and pages >= 500:
            return "extreme", duration, 2.5, "very heavy", "AI marked this reading task extreme because the text describes a very large page count.", False
        if pages and pages >= 300:
            return "hard", duration, 2.0, "heavy", "AI marked this reading task hard because the text describes a large page count.", False
        if pages and pages >= 100:
            return "medium", duration, 1.4, "moderate", "AI marked this reading task medium because the text describes a substantial page count.", False
        if any(keyword in text for keyword in ["research paper", "dense article", "textbook chapter"]):
            return "medium", max(duration, 30), 1.4, "moderate", "AI saw a more demanding reading context in the task text.", False
        return "easy", duration, 1.0, "light", "AI treated this as a light reading task based on the wording.", False

    if category == "study":
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=60)
        if any(keyword in text for keyword in ["final exam", "midterm exam", "board exam", "comprehensive exam"]):
            return "extreme", max(duration, 180), 2.5, "very heavy", "AI detected major exam preparation in the task text.", False
        if any(keyword in text for keyword in ["multiple chapters", "research", "thesis", "project", "presentation"]):
            return "hard", max(duration, 90), 2.0, "heavy", "AI detected a large study scope from the task text.", False
        if any(keyword in text for keyword in ["chapter", "homework", "assignment", "lesson", "mathematics", "physics", "chemistry"]):
            return "medium", duration, 1.5, "moderate", "AI detected focused study work from the task text.", False
        if any(keyword in text for keyword in ["review notes", "flashcards", "quick review", "summary"]):
            return "easy", min(duration, 30), 1.0, "light", "AI treated this as a light study review task.", False
        return "medium", duration, 1.4, "moderate", "AI treated this as a normal study task based on the text itself, not the time block.", False

    if category == "workout":
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=30)
        if any(keyword in text for keyword in ["everest", "mountaineering", "summit", "alpine climb", "mountain climb"]):
            if planned_duration_minutes and planned_duration_minutes >= 240:
                return "extreme", max(duration, 240), 2.5, "very heavy", "AI fallback detected a major climbing or mountaineering task with sustained physical effort.", False
            return "hard", max(duration, 120), 2.0, "heavy", "AI fallback detected a demanding climbing or mountaineering task.", False
        if any(keyword in text for keyword in ["hike", "hiking", "trek", "trekking", "climb", "climbing"]):
            if planned_duration_minutes and planned_duration_minutes >= 360:
                return "extreme", max(duration, 240), 2.5, "very heavy", "AI fallback detected a long, demanding outdoor endurance activity.", False
            if planned_duration_minutes and planned_duration_minutes >= 120:
                return "hard", max(duration, 120), 2.0, "heavy", "AI fallback detected a sustained outdoor endurance activity.", False
            return "medium", max(duration, 45), 1.5, "moderate", "AI fallback treated this as a meaningful outdoor physical effort.", False
        if "marathon" in text:
            return "extreme", max(duration, 120), 2.5, "very heavy", "AI detected marathon-level training from the task text.", False
        if any(keyword in text for keyword in ["intense", "hiit", "leg day", "strength training"]):
            return "hard", duration, 2.0, "heavy", "AI detected a demanding workout from the task text.", False
        if any(keyword in text for keyword in ["workout", "gym", "exercise", "cardio", "run"]):
            return "medium", duration, 1.4, "moderate", "AI treated this as a regular workout.", False
        return "easy", max(10, min(duration, 20)), 1.0, "light", "AI treated this as a light movement task.", False

    if category == "coding":
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=45)
        if any(keyword in text for keyword in ["authentication system", "platform", "architecture", "distributed", "migration strategy"]):
            return "extreme", max(duration, 180), 2.5, "very heavy", "AI detected a large engineering scope from the task text.", False
        if any(keyword in text for keyword in ["build feature", "implement", "refactor", "integration", "dashboard", "backend", "frontend"]):
            return "hard", max(duration, 90), 2.0, "heavy", "AI detected significant implementation work from the task text.", False
        if any(keyword in text for keyword in ["fix bug", "debug", "endpoint", "bug"]):
            return "medium", duration, 1.5, "moderate", "AI detected debugging or delivery work from the task text.", False
        if any(keyword in text for keyword in ["fix typo", "rename", "copy change"]):
            return "easy", min(duration, 20), 1.0, "light", "AI treated this as a small coding task.", False
        return "medium", duration, 1.4, "moderate", "AI treated this as a normal coding task.", False

    if category == "cleaning":
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=20)
        if any(keyword in text for keyword in ["full house", "entire house"]):
            return "extreme", max(duration, 180), 2.5, "very heavy", "AI detected a full-house cleaning task from the text.", False
        if any(keyword in text for keyword in ["deep clean", "apartment", "garage", "closet overhaul"]):
            return "hard", max(duration, 90), 2.0, "heavy", "AI detected a large cleaning scope from the task text.", False
        if any(keyword in text for keyword in ["clean room", "kitchen", "bathroom"]):
            return "medium", duration, 1.4, "moderate", "AI detected a moderate cleaning task from the text.", False
        return "easy", min(duration, 20), 1.0, "light", "AI treated this as a quick cleaning task.", False

    if category == "meeting":
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=30)
        if any(keyword in text for keyword in ["interview", "client", "presentation"]):
            return "hard", duration, 2.0, "heavy", "AI detected a higher-stakes meeting from the task text.", False
        return "medium", duration, 1.4, "moderate", "AI treated this as a normal meeting task.", False

    if category == "mindfulness":
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=15)
        return "easy", duration, 1.0, "light", "AI treated this as a restorative task.", False

    if category == "writing":
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=45)
        if any(keyword in text for keyword in ["essay", "report", "research paper"]):
            return "hard", max(duration, 90), 2.0, "heavy", "AI detected a substantial writing deliverable from the task text.", False
        return "medium", duration, 1.4, "moderate", "AI treated this as a normal writing task.", False

    if category == "planning":
        duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=25)
        if any(keyword in text for keyword in ["roadmap", "strategy", "quarterly", "launch plan"]):
            return "hard", max(duration, 60), 2.0, "heavy", "AI detected a strategic planning task from the text.", False
        return "medium", duration, 1.3, "moderate", "AI treated this as a planning task with moderate effort.", False

    duration = choose_estimated_duration(text=text, planned_duration_minutes=planned_duration_minutes, default_minutes=20)
    if any(keyword in text for keyword in EXTREME_HINTS):
        return "extreme", max(duration, 120), 2.5, "very heavy", f"AI created the category '{category}' and detected very demanding language in the task text.", False
    if any(keyword in text for keyword in HARD_HINTS):
        return "hard", max(duration, 60), 2.0, "heavy", f"AI created the category '{category}' and detected a substantial scope in the task text.", False
    if looks_like_quick_task(text):
        return "easy", min(duration, 15), 1.0, "light", f"AI created the category '{category}' and detected a quick habit-style task.", True
    return "medium", duration, 1.2, "moderate", f"AI created the category '{category}' because the task did not match an existing label.", False


def classify_task_rules(
    *,
    title: str,
    description: str = "",
    planned_duration_minutes: int | None = None,
) -> AIClassificationResult:
    text = f"{title} {description}".strip().lower()
    number = extract_number(text)
    category = infer_category(text)
    difficulty, duration, multiplier, workload, explanation, is_quick_task = classify_by_category(
        category=category,
        text=text,
        number=number,
        planned_duration_minutes=planned_duration_minutes,
    )
    return build_result(
        detected_category=category,
        estimated_workload=workload,
        estimated_duration_minutes=duration,
        detected_difficulty=difficulty,
        ai_multiplier=multiplier,
        explanation=explanation,
        is_quick_task=is_quick_task,
        provider="fallback_rules",
        effort_domain=infer_effort_domain_from_category(category),
        stakes_level=infer_stakes_from_difficulty(difficulty),
        confidence_score=0.35,
    )


def llm_classifier_enabled() -> bool:
    return bool(
        getattr(settings, "OPENAI_CLASSIFIER_ENABLED", False)
        and getattr(settings, "OPENAI_API_KEY", "")
        and OpenAI is not None
    )


def get_openai_client():
    if not llm_classifier_enabled():
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def build_cache_key(*, title: str, description: str, planned_duration_minutes: int | None) -> str:
    payload = json.dumps(
        {
            "cache_version": AI_CLASSIFIER_CACHE_VERSION,
            "title": title,
            "description": description,
            "planned_duration_minutes": planned_duration_minutes,
            "model": getattr(settings, "OPENAI_CLASSIFIER_MODEL", "gpt-5-mini"),
            "prompt": OPENAI_SYSTEM_PROMPT,
        },
        sort_keys=True,
    )
    return f"ai-classifier:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def build_openai_input(*, title: str, description: str, planned_duration_minutes: int | None) -> str:
    schedule_context = (
        f"Planned active window estimate: {planned_duration_minutes} minutes."
        if planned_duration_minutes
        else "No explicit duration range was provided."
    )
    return "\n".join(
        [
            f"Task title: {title.strip() or '(empty)'}",
            f"Task description: {description.strip() or '(empty)'}",
            schedule_context,
            "Decide whether this is a quick point-in-time task or a sustained effort task.",
            "Infer the category, difficulty, likely active duration, workload, multiplier, and a plain-language explanation.",
            "Keep the explanation short and concrete.",
        ]
    )


def extract_json_object(text: str) -> dict:
    stripped = (text or "").strip()
    if not stripped:
        raise ValueError("Empty structured output.")
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(stripped[start : end + 1])


def parse_openai_response(response) -> dict:
    output_text = getattr(response, "output_text", "") or ""
    if output_text:
        return extract_json_object(output_text)

    output = getattr(response, "output", []) or []
    for item in output:
        content = getattr(item, "content", None) or []
        for block in content:
            text_value = getattr(block, "text", None)
            if text_value:
                return extract_json_object(text_value)

    try:
        payload = response.model_dump()
    except Exception:
        payload = None
    if payload:
        for item in payload.get("output", []) or []:
            for block in item.get("content", []) or []:
                text_value = block.get("text")
                if text_value:
                    return extract_json_object(text_value)
    raise ValueError("No structured output was returned by the OpenAI response.")


def classify_task_with_openai(
    *,
    title: str,
    description: str = "",
    planned_duration_minutes: int | None = None,
) -> AIClassificationResult | None:
    client = get_openai_client()
    if client is None:
        return None

    cache_key = build_cache_key(
        title=title,
        description=description,
        planned_duration_minutes=planned_duration_minutes,
    )
    try:
        cached = cache.get(cache_key)
    except Exception as exc:  # pragma: no cover - cache backend can be unavailable
        logger.warning("AI cache read failed, continuing without cache: %s", exc)
        cached = None
    if cached:
        return build_result(
            detected_category=cached["detected_category"],
            estimated_workload=cached["estimated_workload"],
            estimated_duration_minutes=cached["estimated_duration_minutes"],
            detected_difficulty=cached["detected_difficulty"],
            ai_multiplier=cached["ai_multiplier"],
            explanation=cached["explanation"],
            is_quick_task=cached["is_quick_task"],
            provider="openai_cached",
            effort_domain=cached.get("effort_domain", "mixed"),
            stakes_level=cached.get("stakes_level", "normal"),
            confidence_score=cached.get("confidence_score", 0.5),
        )

    fallback = classify_task_rules(
        title=title,
        description=description,
        planned_duration_minutes=planned_duration_minutes,
    )
    try:
        response = client.responses.create(
            model=getattr(settings, "OPENAI_CLASSIFIER_MODEL", "gpt-5-mini"),
            instructions=OPENAI_SYSTEM_PROMPT,
            input=build_openai_input(
                title=title,
                description=description,
                planned_duration_minutes=planned_duration_minutes,
            ),
            reasoning={"effort": "low"},
            max_output_tokens=900,
            text={"verbosity": "low", "format": {"type": "json_schema", "name": AI_SCHEMA["name"], "schema": AI_SCHEMA["schema"], "strict": True}},
        )
        payload = parse_openai_response(response)
        difficulty = normalize_difficulty(payload.get("detected_difficulty"))
        result = build_result(
            detected_category=normalize_category(payload.get("detected_category", ""), original_text=f"{title} {description}"),
            estimated_workload=normalize_workload(payload.get("estimated_workload", "moderate")),
            estimated_duration_minutes=clamp_duration(payload.get("estimated_duration_minutes"), fallback=fallback.estimated_duration_minutes),
            detected_difficulty=difficulty,
            ai_multiplier=clamp_multiplier(payload.get("ai_multiplier"), difficulty=difficulty),
            explanation=(payload.get("explanation") or fallback.explanation).strip()[:600],
            is_quick_task=bool(payload.get("is_quick_task", False)),
            provider="openai",
            effort_domain=normalize_effort_domain(payload.get("effort_domain", "mixed")),
            stakes_level=normalize_stakes_level(payload.get("stakes_level", "normal")),
            confidence_score=clamp_confidence(payload.get("confidence_score")),
        )
        try:
            cache.set(
                cache_key,
                {
                    "detected_category": result.detected_category,
                    "estimated_workload": result.estimated_workload,
                    "estimated_duration_minutes": result.estimated_duration_minutes,
                    "detected_difficulty": result.detected_difficulty,
                    "ai_multiplier": result.ai_multiplier,
                    "explanation": result.explanation,
                    "is_quick_task": result.is_quick_task,
                    "effort_domain": result.effort_domain,
                    "stakes_level": result.stakes_level,
                    "confidence_score": result.confidence_score,
                },
                timeout=int(getattr(settings, "AI_CLASSIFIER_CACHE_SECONDS", 3600)),
            )
        except Exception as exc:  # pragma: no cover - cache backend can be unavailable
            logger.warning("AI cache write failed, continuing without cache: %s", exc)
        return result
    except Exception as exc:  # pragma: no cover - external transport fallback
        logger.warning("OpenAI classification failed, using fallback rules instead: %s", exc)
        return None


def classify_task(
    *,
    title: str,
    description: str = "",
    planned_duration_minutes: int | None = None,
) -> AIClassificationResult:
    llm_result = classify_task_with_openai(
        title=title,
        description=description,
        planned_duration_minutes=planned_duration_minutes,
    )
    if llm_result is not None:
        return calibrate_task_result(
            result=llm_result,
            title=title,
            description=description,
            planned_duration_minutes=planned_duration_minutes,
        )
    fallback_result = classify_task_rules(
        title=title,
        description=description,
        planned_duration_minutes=planned_duration_minutes,
    )
    if llm_classifier_enabled():
        fallback_result.provider = "fallback_rules_after_openai_error"
        fallback_result.explanation = f"{fallback_result.explanation} OpenAI classification was unavailable, so local fallback rules were used."
        fallback_result.anomaly_risk_rules["ai_provider"] = fallback_result.provider
    return calibrate_task_result(
        result=fallback_result,
        title=title,
        description=description,
        planned_duration_minutes=planned_duration_minutes,
    )


def estimate_xp(*, actual_duration_minutes: int, detected_difficulty: str, ai_multiplier: float) -> int:
    time_xp = (actual_duration_minutes / 3) * DIFFICULTY_MULTIPLIERS[detected_difficulty]
    completion_bonus = DIFFICULTY_COMPLETION_BONUS[detected_difficulty]
    raw_xp = completion_bonus + time_xp
    return round(raw_xp)
