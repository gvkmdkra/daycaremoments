"""
LLM Service - Unified interface for AI providers (OpenAI and Gemini)
Generates activity descriptions and analyzes photos for daycare management
"""

from typing import Optional, Dict, List
from app.config import Config
from app.services.llm.openai_adapter import OpenAIAdapter
from app.services.llm.gemini_adapter import GeminiAdapter


class LLMService:
    """Unified LLM service with provider abstraction"""

    def __init__(self):
        """Initialize LLM service with configured provider"""
        self.provider = Config.LLM_PROVIDER.lower()

        if self.provider == "openai":
            self.adapter = OpenAIAdapter()
        elif self.provider == "gemini":
            self.adapter = GeminiAdapter()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_activity_description(
        self,
        photo_context: Dict[str, any]
    ) -> str:
        """
        Generate natural activity description for a photo

        Args:
            photo_context: Dictionary containing:
                - child_name: Name of the child
                - detected_objects: List of objects/activities detected (optional)
                - time_of_day: Time photo was taken (optional)
                - location: Location if available (optional)

        Returns:
            Natural language description of the activity
        """
        child_name = photo_context.get('child_name', 'the child')
        time_of_day = photo_context.get('time_of_day', '')
        location = photo_context.get('location', '')
        detected_objects = photo_context.get('detected_objects', [])

        # Build context for LLM
        context_parts = []
        if time_of_day:
            context_parts.append(f"Time: {time_of_day}")
        if location:
            context_parts.append(f"Location: {location}")
        if detected_objects:
            context_parts.append(f"Visible elements: {', '.join(detected_objects)}")

        context_str = ". ".join(context_parts) if context_parts else "No additional context"

        system_prompt = """You are a warm, professional daycare teacher writing photo descriptions for parents.
Your descriptions should be:
- Natural and engaging (like a teacher would describe)
- 1-2 sentences maximum
- Focus on the child's activity and mood
- Use positive, warm language
- Avoid generic phrases like "captured" or "photo shows"
- Write as if you witnessed the moment

Examples:
- "Emma is enjoying her healthy lunch with friends at the table!"
- "Building colorful towers during creative play time - Emma loves the blue blocks!"
- "Peaceful nap time for Emma after an active morning"
- "Emma is having so much fun painting during art activities!"
"""

        user_prompt = f"""Generate a warm, natural description for this daycare photo.

Child: {child_name}
Context: {context_str}

Write as if you're the teacher sharing this moment with the parents. Keep it brief and warm."""

        try:
            description = self.adapter.chat(
                messages=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            return description.strip()
        except Exception as e:
            print(f"Error generating description: {e}")
            return f"{child_name} during activities at daycare"

    def analyze_photo_activity(
        self,
        photo_data: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Analyze photo to detect activity type and generate metadata

        Args:
            photo_data: Dictionary containing:
                - child_name: Name of the child
                - time_of_day: Time photo was taken
                - detected_objects: Visual elements detected (optional)

        Returns:
            Dictionary containing:
                - activity_type: One of [meal, nap, play, learning, outdoor, art, other]
                - confidence: Confidence score (0-1)
                - mood: Detected mood/emotion (happy, calm, focused, etc.)
                - suggested_duration: Estimated duration in minutes (for activities like naps)
        """
        child_name = photo_data.get('child_name', 'the child')
        time_of_day = photo_data.get('time_of_day', '')
        detected_objects = photo_data.get('detected_objects', [])

        system_prompt = """You are an AI assistant that analyzes daycare photos to categorize activities.
Analyze the provided information and determine the activity type.

Activity types:
- meal: Eating, lunch, snack time, drinking
- nap: Sleeping, resting, quiet time
- play: Playing with toys, free play, recreational activities
- learning: Educational activities, reading, structured learning
- outdoor: Outside activities, playground, nature walks
- art: Drawing, painting, crafts, creative projects
- other: Any activity that doesn't fit above categories

Respond in JSON format:
{
    "activity_type": "meal|nap|play|learning|outdoor|art|other",
    "confidence": 0.0-1.0,
    "mood": "happy|calm|focused|sleepy|excited|curious",
    "suggested_duration": minutes (null if not applicable)
}"""

        context_str = f"Time: {time_of_day}. " if time_of_day else ""
        if detected_objects:
            context_str += f"Visible: {', '.join(detected_objects)}"

        user_prompt = f"""Analyze this daycare moment for {child_name}.
{context_str}

Provide JSON with activity_type, confidence, mood, and suggested_duration."""

        try:
            response = self.adapter.chat(
                messages=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3  # Lower temperature for more consistent categorization
            )

            # Parse JSON response
            import json
            # Extract JSON from response (handle markdown code blocks)
            response_clean = response.strip()
            if response_clean.startswith('```'):
                # Remove markdown code blocks
                lines = response_clean.split('\n')
                response_clean = '\n'.join(lines[1:-1] if len(lines) > 2 else lines)

            result = json.loads(response_clean)

            # Validate activity_type
            valid_types = ['meal', 'nap', 'play', 'learning', 'outdoor', 'art', 'other']
            if result.get('activity_type') not in valid_types:
                result['activity_type'] = 'other'

            return result

        except Exception as e:
            print(f"Error analyzing photo activity: {e}")
            # Return default classification based on time of day
            default_mood = "happy"
            default_type = "play"

            if time_of_day:
                hour = int(time_of_day.split(':')[0]) if ':' in time_of_day else 12
                if 11 <= hour <= 13:
                    default_type = "meal"
                elif 13 <= hour <= 15:
                    default_type = "nap"
                    default_mood = "calm"

            return {
                "activity_type": default_type,
                "confidence": 0.5,
                "mood": default_mood,
                "suggested_duration": None
            }

    def generate_daily_summary(
        self,
        child_name: str,
        activities: List[Dict],
        photo_count: int
    ) -> str:
        """
        Generate a warm daily summary for parents

        Args:
            child_name: Name of the child
            activities: List of activities with type and notes
            photo_count: Number of photos taken today

        Returns:
            Natural narrative summary of the day
        """
        # Build activity summary
        activity_summary = []
        for activity in activities[:10]:  # Limit to recent activities
            activity_summary.append(
                f"- {activity.get('activity_type', 'activity').title()}: "
                f"{activity.get('notes', 'Completed')}"
            )

        activities_text = "\n".join(activity_summary) if activity_summary else "Various activities throughout the day"

        system_prompt = """You are a caring daycare teacher writing a daily summary for parents.
Write in a warm, personal tone as if you're talking directly to the parent.
Keep it conversational and highlight the child's day in 2-3 sentences.
Focus on positive moments and development."""

        user_prompt = f"""Write a warm daily summary for {child_name}'s parent.

Today's activities:
{activities_text}

Photos captured: {photo_count}

Write a brief, warm summary (2-3 sentences) that a parent would love to read."""

        try:
            summary = self.adapter.chat(
                messages=user_prompt,
                system_prompt=system_prompt,
                temperature=0.8
            )
            return summary.strip()
        except Exception as e:
            print(f"Error generating daily summary: {e}")
            return f"{child_name} had a wonderful day at daycare today! We captured {photo_count} special moments throughout the day."

    def enhance_activity_notes(
        self,
        activity_type: str,
        basic_notes: str,
        child_name: str
    ) -> str:
        """
        Enhance basic activity notes with more detail and warmth

        Args:
            activity_type: Type of activity
            basic_notes: Basic notes about the activity
            child_name: Child's name

        Returns:
            Enhanced notes
        """
        if not basic_notes or len(basic_notes.strip()) < 5:
            return basic_notes

        system_prompt = """You are a daycare teacher enhancing activity notes.
Make them warmer and more detailed while keeping them concise.
Maximum 1-2 sentences."""

        user_prompt = f"""Enhance these {activity_type} notes for {child_name}:
"{basic_notes}"

Make it warmer and more descriptive (1-2 sentences)."""

        try:
            enhanced = self.adapter.chat(
                messages=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            return enhanced.strip()
        except Exception as e:
            print(f"Error enhancing notes: {e}")
            return basic_notes


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
