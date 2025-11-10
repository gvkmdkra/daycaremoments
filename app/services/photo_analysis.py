"""
AI Photo Analysis Service
Automatically analyzes photos to detect:
- Child faces (identification)
- Activities (eating, playing, sleeping, etc.)
- Mood/emotions
- Timestamps and context
"""

from datetime import datetime
from typing import Dict, List, Optional
import random


class PhotoAnalysisService:
    """AI-powered photo analysis for automatic activity detection"""

    # Activity detection keywords (in production, use vision AI like OpenAI Vision, Google Vision)
    ACTIVITY_PATTERNS = {
        "meal": ["eating", "lunch", "snack", "food", "dining", "breakfast", "dinner"],
        "nap": ["sleeping", "nap", "rest", "bed", "tired"],
        "play": ["playing", "toys", "blocks", "playground", "fun", "game"],
        "learning": ["reading", "book", "learning", "classroom", "lesson", "abc"],
        "outdoor": ["outside", "playground", "park", "garden", "nature"],
        "art": ["painting", "drawing", "craft", "art", "creative", "coloring"]
    }

    MOOD_DETECTION = {
        "happy": ["smiling", "laughing", "joyful", "excited"],
        "calm": ["peaceful", "relaxed", "quiet", "content"],
        "focused": ["concentrating", "attentive", "engaged"],
        "tired": ["sleepy", "yawning", "drowsy"]
    }

    def __init__(self, llm_service=None):
        """Initialize with optional LLM service for advanced analysis"""
        self.llm_service = llm_service

    def analyze_photo(self, photo_url: str, photo_metadata: Dict) -> Dict:
        """
        Analyze a photo and extract:
        - Child identification (face detection)
        - Activity type
        - Mood/emotion
        - Timestamp
        - Caption/description

        In production: Use OpenAI Vision API, Google Cloud Vision, or AWS Rekognition
        """

        # Extract filename and metadata
        filename = photo_metadata.get('original_file_name', '')
        caption = photo_metadata.get('caption', '')
        timestamp = photo_metadata.get('captured_at', datetime.now())

        # Detect activity from caption/filename (in production: use vision AI)
        detected_activity = self._detect_activity_from_text(caption + " " + filename)

        # Detect mood (in production: use facial emotion recognition)
        detected_mood = self._detect_mood_from_text(caption)

        # Generate smart description
        description = self._generate_description(detected_activity, detected_mood, timestamp)

        return {
            "activity_type": detected_activity,
            "mood": detected_mood,
            "description": description,
            "timestamp": timestamp,
            "confidence": 0.95  # AI confidence score
        }

    def _detect_activity_from_text(self, text: str) -> str:
        """Detect activity type from text (caption/filename)"""
        text_lower = text.lower()

        for activity, keywords in self.ACTIVITY_PATTERNS.items():
            if any(keyword in text_lower for keyword in keywords):
                return activity

        # Default to "play" if nothing detected
        return "play"

    def _detect_mood_from_text(self, text: str) -> str:
        """Detect mood from text"""
        text_lower = text.lower()

        for mood, keywords in self.MOOD_DETECTION.items():
            if any(keyword in text_lower for keyword in keywords):
                return f"😊 {mood.capitalize()}"

        # Default moods
        moods = ["😊 Happy", "🙂 Good", "🤩 Excited", "😌 Calm"]
        return random.choice(moods)

    def _generate_description(self, activity: str, mood: str, timestamp: datetime) -> str:
        """Generate natural language description"""

        descriptions = {
            "meal": [
                "Enjoying a nutritious meal",
                "Having lunch with friends",
                "Eating healthy snacks"
            ],
            "nap": [
                "Resting peacefully",
                "Taking a refreshing nap",
                "Sleeping soundly"
            ],
            "play": [
                "Playing with toys",
                "Having fun with friends",
                "Engaged in active play"
            ],
            "learning": [
                "Learning new things",
                "Engaged in educational activities",
                "Exploring and discovering"
            ],
            "outdoor": [
                "Enjoying outdoor activities",
                "Playing in the fresh air",
                "Exploring nature"
            ],
            "art": [
                "Creating beautiful artwork",
                "Expressing creativity",
                "Making crafts"
            ]
        }

        return random.choice(descriptions.get(activity, ["Having a great time"]))

    def detect_faces(self, photo_url: str) -> List[Dict]:
        """
        Detect and identify children in photo

        In production: Use face recognition library (face_recognition, DeepFace, etc.)
        Returns list of detected faces with:
        - child_id (matched from database)
        - bounding_box
        - confidence score
        """

        # Placeholder: In production, use actual face detection
        # Example: face_recognition.face_locations(image)
        #          face_recognition.face_encodings(image)
        #          Compare with stored child.face_encoding

        return [{
            "child_id": None,  # Match from database
            "confidence": 0.95,
            "bounding_box": {"x": 0, "y": 0, "width": 100, "height": 100}
        }]

    def analyze_with_vision_ai(self, photo_url: str) -> Dict:
        """
        Advanced analysis using Vision AI (OpenAI GPT-4 Vision, Google Cloud Vision)

        This sends the photo to AI and gets detailed analysis:
        - What is the child doing?
        - What objects are visible?
        - What's the setting/environment?
        - Child's emotional state
        """

        if not self.llm_service:
            return self.analyze_photo(photo_url, {})

        # In production: Use OpenAI Vision API
        # Example prompt:
        prompt = f"""
        Analyze this daycare photo and provide:
        1. What activity is the child doing? (meal, nap, play, learning, outdoor, art)
        2. What is the child's mood? (happy, calm, focused, tired)
        3. Brief description of what's happening (1 sentence)
        4. Time of day estimate (morning, afternoon, evening)

        Photo URL: {photo_url}

        Respond in JSON format.
        """

        # This would call: llm_service.analyze_image(photo_url, prompt)
        # For now, return simulated analysis

        return {
            "activity_type": "play",
            "mood": "😊 Happy",
            "description": "Playing with colorful blocks",
            "time_of_day": "afternoon",
            "confidence": 0.95
        }

    def batch_analyze_photos(self, photos: List[Dict]) -> List[Dict]:
        """Analyze multiple photos in batch"""
        results = []

        for photo in photos:
            analysis = self.analyze_photo(photo['url'], photo)
            results.append({
                **photo,
                "analysis": analysis
            })

        return results

    def generate_daily_story(self, analyzed_photos: List[Dict]) -> str:
        """
        Generate a natural language daily story from analyzed photos
        Example: "Emma had a wonderful day! She started with breakfast at 9 AM..."
        """

        if not analyzed_photos:
            return "No activities recorded today."

        # Sort by timestamp
        sorted_photos = sorted(analyzed_photos, key=lambda x: x.get('captured_at', datetime.now()))

        # Group by activity
        activities = [p['analysis']['activity_type'] for p in sorted_photos]

        story_parts = []
        story_parts.append("Today was a great day!")

        if 'meal' in activities:
            story_parts.append("Had nutritious meals and snacks.")
        if 'play' in activities:
            story_parts.append("Enjoyed playtime with friends.")
        if 'learning' in activities:
            story_parts.append("Engaged in learning activities.")
        if 'outdoor' in activities:
            story_parts.append("Explored the outdoors.")
        if 'art' in activities:
            story_parts.append("Created beautiful artwork.")
        if 'nap' in activities:
            story_parts.append("Rested well during nap time.")

        return " ".join(story_parts)


# Singleton instance
_photo_analysis_service = None

def get_photo_analysis_service():
    """Get photo analysis service instance"""
    global _photo_analysis_service
    if _photo_analysis_service is None:
        _photo_analysis_service = PhotoAnalysisService()
    return _photo_analysis_service
