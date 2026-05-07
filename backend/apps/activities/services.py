from __future__ import annotations

from apps.activities.models import Activity

PREDEFINED_ACTIVITIES = [
    {"title": "Read 10 pages", "description": "Light reading session.", "category": "reading", "difficulty": "easy", "estimated_duration_minutes": 15},
    {"title": "Read 100 pages", "description": "Long-form reading session.", "category": "reading", "difficulty": "medium", "estimated_duration_minutes": 120},
    {"title": "Study one chapter", "description": "Focused chapter revision.", "category": "study", "difficulty": "medium", "estimated_duration_minutes": 90},
    {"title": "Prepare for final exam", "description": "Intensive revision block.", "category": "study", "difficulty": "extreme", "estimated_duration_minutes": 240},
    {"title": "30-minute workout", "description": "Moderate exercise routine.", "category": "workout", "difficulty": "medium", "estimated_duration_minutes": 30},
    {"title": "Marathon training", "description": "High-endurance workout block.", "category": "workout", "difficulty": "extreme", "estimated_duration_minutes": 180},
    {"title": "Fix bug", "description": "Resolve a non-trivial defect.", "category": "coding", "difficulty": "medium", "estimated_duration_minutes": 60},
    {"title": "Build authentication system", "description": "Complex backend feature build.", "category": "coding", "difficulty": "extreme", "estimated_duration_minutes": 240},
    {"title": "Clean desk", "description": "Quick area reset.", "category": "cleaning", "difficulty": "easy", "estimated_duration_minutes": 15},
    {"title": "Deep clean apartment", "description": "Thorough cleaning session.", "category": "cleaning", "difficulty": "hard", "estimated_duration_minutes": 180},
]


def seed_predefined_activities() -> int:
    created = 0
    for item in PREDEFINED_ACTIVITIES:
        _, was_created = Activity.objects.get_or_create(
            title=item["title"],
            is_predefined=True,
            defaults=item,
        )
        if was_created:
            created += 1
    return created
