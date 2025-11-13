"""
AI Description Service - Generate descriptions for daycare photos
Wrapper around LLM service for photo description generation
"""

from typing import Dict, List, Optional
from app.services.llm_service import get_llm_service
from datetime import datetime


class AIDescriptionService:
    """Service for generating AI descriptions of daycare activities"""

    def __init__(self):
        """Initialize AI description service"""
        self.llm_service = get_llm_service()

    def generate_photo_description(
        self,
        child_name: str,
        activity_type: Optional[str] = None,
        time_of_day: Optional[str] = None,
        detected_objects: Optional[List[str]] = None
    ) -> str:
        """
        Generate a natural description for a daycare photo

        Args:
            child_name: Name of the child in the photo
            activity_type: Type of activity (meal, nap, play, etc.)
            time_of_day: Time the photo was taken
            detected_objects: List of objects/elements detected in photo

        Returns:
            Natural language description
        """
        photo_context = {
            'child_name': child_name,
            'activity_type': activity_type,
            'time_of_day': time_of_day,
            'detected_objects': detected_objects or []
        }

        return self.llm_service.generate_activity_description(photo_context)

    def analyze_activity(
        self,
        child_name: str,
        time_of_day: Optional[str] = None,
        detected_objects: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Analyze photo to detect activity type

        Args:
            child_name: Name of the child
            time_of_day: Time photo was taken
            detected_objects: Visual elements detected

        Returns:
            Dictionary with activity_type, confidence, mood, suggested_duration
        """
        photo_data = {
            'child_name': child_name,
            'time_of_day': time_of_day,
            'detected_objects': detected_objects or []
        }

        return self.llm_service.analyze_photo_activity(photo_data)

    def generate_daily_summary(
        self,
        child_name: str,
        activities: List[Dict],
        photo_count: int
    ) -> str:
        """
        Generate daily summary for parents

        Args:
            child_name: Name of the child
            activities: List of activities throughout the day
            photo_count: Number of photos taken

        Returns:
            Warm daily summary text
        """
        return self.llm_service.generate_daily_summary(
            child_name,
            activities,
            photo_count
        )

    def enhance_notes(
        self,
        activity_type: str,
        basic_notes: str,
        child_name: str
    ) -> str:
        """
        Enhance basic activity notes with AI

        Args:
            activity_type: Type of activity
            basic_notes: Basic notes
            child_name: Child's name

        Returns:
            Enhanced notes
        """
        return self.llm_service.enhance_activity_notes(
            activity_type,
            basic_notes,
            child_name
        )


# Singleton instance
_ai_description_service = None


def get_ai_description_service() -> AIDescriptionService:
    """Get AI description service singleton"""
    global _ai_description_service
    if _ai_description_service is None:
        _ai_description_service = AIDescriptionService()
    return _ai_description_service
