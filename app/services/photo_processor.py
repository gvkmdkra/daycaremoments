"""
Photo Processing Service - Automated photo processing with face recognition and AI
Processes uploaded photos, detects faces, matches persons, and generates AI descriptions
"""

from typing import List, Dict, Optional
from datetime import datetime

from app.database import get_db
from app.database.models import Photo, Person
from app.services.face_recognition_service import get_face_recognition_service
from app.services.llm_service import get_llm_service


class PhotoProcessor:
    """Process photos with face recognition and AI description generation"""

    def __init__(self):
        self.face_service = get_face_recognition_service()
        self.llm_service = get_llm_service()

    def process_uploaded_photo(
        self,
        photo_id: str,
        image_data: bytes,
        uploader_id: str
    ) -> Dict[str, any]:
        """
        Process a single uploaded photo with face detection, recognition, and AI analysis

        Args:
            photo_id: Photo ID in database
            image_data: Raw image bytes
            uploader_id: User ID of uploader (staff)

        Returns:
            Processing result dictionary with:
                - success: bool
                - faces_detected: int
                - persons_identified: List[str]
                - description: str
                - error: str (if any)
        """
        result = {
            "success": False,
            "faces_detected": 0,
            "persons_identified": [],
            "description": "",
            "error": None
        }

        try:
            with get_db() as db:
                # Get photo record
                photo = db.query(Photo).filter(Photo.id == photo_id).first()
                if not photo:
                    result["error"] = "Photo not found"
                    return result

                # Step 1: Detect all faces in the image
                face_locations = self.face_service.get_face_locations(image_data)
                result["faces_detected"] = len(face_locations)

                # Step 2: Identify persons in the photo
                identified_person_ids = self.face_service.identify_persons_in_photo(
                    image_data,
                    photo.organization_id
                )
                result["persons_identified"] = identified_person_ids

                # Step 3: If persons identified, process and generate description
                if identified_person_ids:
                    # Use first identified person as primary
                    primary_person_id = identified_person_ids[0]
                    photo.person_id = primary_person_id

                    # Get person details for context
                    person = db.query(Person).filter(Person.id == primary_person_id).first()
                    person_name = person.name if person else "the child"

                    # Prepare context for AI analysis
                    photo_context = {
                        "child_name": person_name,
                        "time_of_day": datetime.now().strftime("%H:%M"),
                        "location": None,
                        "detected_objects": []
                    }

                    # Generate natural description
                    description = self.llm_service.generate_activity_description(photo_context)
                    photo.ai_description = description
                    result["description"] = description
                else:
                    # No persons identified - still generate generic description
                    photo_context = {
                        "child_name": "the children",
                        "time_of_day": datetime.now().strftime("%H:%M"),
                        "location": None,
                        "detected_objects": []
                    }
                    description = self.llm_service.generate_activity_description(photo_context)
                    photo.ai_description = description
                    result["description"] = description

                # Commit all changes
                db.commit()
                result["success"] = True

                return result

        except Exception as e:
            result["error"] = str(e)
            print(f"Error processing photo {photo_id}: {e}")
            import traceback
            traceback.print_exc()
            return result

    def process_batch(
        self,
        photo_ids: List[str],
        image_data_map: Dict[str, bytes],
        uploader_id: str
    ) -> Dict[str, any]:
        """
        Process multiple photos in batch

        Args:
            photo_ids: List of photo IDs to process
            image_data_map: Dictionary mapping photo_id to image bytes
            uploader_id: User ID of uploader

        Returns:
            Batch processing summary
        """
        summary = {
            "total": len(photo_ids),
            "successful": 0,
            "failed": 0,
            "faces_detected": 0,
            "persons_identified": set(),
            "results": []
        }

        for photo_id in photo_ids:
            image_data = image_data_map.get(photo_id)
            if not image_data:
                summary["failed"] += 1
                continue

            result = self.process_uploaded_photo(photo_id, image_data, uploader_id)
            summary["results"].append({
                "photo_id": photo_id,
                "result": result
            })

            if result["success"]:
                summary["successful"] += 1
                summary["faces_detected"] += result["faces_detected"]
                summary["persons_identified"].update(result["persons_identified"])
            else:
                summary["failed"] += 1

        # Convert set to list for JSON serialization
        summary["persons_identified"] = list(summary["persons_identified"])

        return summary


# Singleton instance
_photo_processor = None


def get_photo_processor() -> PhotoProcessor:
    """Get photo processor singleton"""
    global _photo_processor
    if _photo_processor is None:
        _photo_processor = PhotoProcessor()
    return _photo_processor
