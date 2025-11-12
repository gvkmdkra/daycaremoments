"""
Photo Processing Service - Automated photo processing with face recognition and AI
Processes uploaded photos, detects faces, matches children, and generates AI descriptions
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import io
import json
from PIL import Image

from app.database import get_db
from app.database.models import Photo, Child, Activity, PhotoStatus
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
                - children_identified: List[str]
                - activity_created: bool
                - description: str
                - error: str (if any)
        """
        result = {
            "success": False,
            "faces_detected": 0,
            "children_identified": [],
            "activity_created": False,
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

                # Store face locations
                photo.detected_faces = face_locations
                photo.face_recognition_complete = True

                # Step 2: Extract face encodings
                face_encodings = self.face_service.encode_faces_multiple(image_data)

                # Step 3: Identify children in the photo
                identified_child_ids = []
                for encoding in face_encodings:
                    child_id = self.face_service.identify_child(encoding, photo.daycare_id)
                    if child_id and child_id not in identified_child_ids:
                        identified_child_ids.append(child_id)

                result["children_identified"] = identified_child_ids

                # Step 4: If children identified, process each one
                if identified_child_ids:
                    # Use first identified child as primary
                    primary_child_id = identified_child_ids[0]
                    photo.child_id = primary_child_id
                    photo.auto_tagged = True

                    # Get child details for context
                    child = db.query(Child).filter(Child.id == primary_child_id).first()
                    child_name = f"{child.first_name} {child.last_name}" if child else "the child"

                    # Step 5: Prepare context for AI analysis
                    captured_time = photo.captured_at or photo.uploaded_at
                    time_of_day = captured_time.strftime("%H:%M")

                    photo_context = {
                        "child_name": child.first_name if child else "the child",
                        "time_of_day": time_of_day,
                        "location": photo.location,
                        "detected_objects": []  # Could integrate with object detection in future
                    }

                    # Step 6: Analyze activity type
                    analysis_result = self.llm_service.analyze_photo_activity({
                        "child_name": child.first_name if child else "the child",
                        "time_of_day": time_of_day,
                        "detected_objects": []
                    })

                    activity_type = analysis_result.get("activity_type", "other")
                    mood = analysis_result.get("mood", "happy")
                    suggested_duration = analysis_result.get("suggested_duration")

                    # Step 7: Generate natural description
                    description = self.llm_service.generate_activity_description(photo_context)
                    photo.ai_generated_description = description
                    result["description"] = description

                    # Step 8: Create Activity record
                    activity = Activity(
                        child_id=primary_child_id,
                        daycare_id=photo.daycare_id,
                        staff_id=uploader_id,
                        activity_type=activity_type,
                        activity_time=captured_time,
                        duration_minutes=suggested_duration,
                        notes=description,
                        mood=mood
                    )
                    db.add(activity)
                    db.flush()  # Get activity ID

                    # Link photo to activity
                    photo.activity_id = activity.id
                    result["activity_created"] = True

                    # Step 9: Update photo metadata
                    photo_metadata = photo.photo_metadata or {}
                    photo_metadata.update({
                        "processed_at": datetime.utcnow().isoformat(),
                        "ai_analysis": analysis_result,
                        "children_count": len(identified_child_ids),
                        "processing_version": "1.0"
                    })
                    photo.photo_metadata = photo_metadata

                else:
                    # No children identified - still generate generic description
                    photo_context = {
                        "child_name": "the children",
                        "time_of_day": photo.captured_at.strftime("%H:%M") if photo.captured_at else "",
                        "location": photo.location,
                        "detected_objects": []
                    }
                    description = self.llm_service.generate_activity_description(photo_context)
                    photo.ai_generated_description = description
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
            Batch processing summary:
                - total: int
                - successful: int
                - failed: int
                - faces_detected: int
                - children_identified: set
                - results: List of individual results
        """
        summary = {
            "total": len(photo_ids),
            "successful": 0,
            "failed": 0,
            "faces_detected": 0,
            "children_identified": set(),
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
                summary["children_identified"].update(result["children_identified"])
            else:
                summary["failed"] += 1

        # Convert set to list for JSON serialization
        summary["children_identified"] = list(summary["children_identified"])

        return summary

    def reprocess_photo(self, photo_id: str) -> Dict[str, any]:
        """
        Reprocess an existing photo (useful after adding new children or improving AI)

        Args:
            photo_id: Photo ID to reprocess

        Returns:
            Processing result
        """
        try:
            with get_db() as db:
                photo = db.query(Photo).filter(Photo.id == photo_id).first()
                if not photo:
                    return {"success": False, "error": "Photo not found"}

                # Note: In production, you'd fetch the image from storage
                # For now, this is a placeholder
                return {
                    "success": False,
                    "error": "Reprocessing requires image data from storage (not implemented in this version)"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_processing_stats(self, daycare_id: str, days: int = 7) -> Dict[str, any]:
        """
        Get photo processing statistics for a daycare

        Args:
            daycare_id: Daycare ID
            days: Number of days to look back

        Returns:
            Statistics dictionary
        """
        try:
            with get_db() as db:
                from datetime import timedelta

                cutoff_date = datetime.utcnow() - timedelta(days=days)

                # Total photos uploaded
                total_photos = db.query(Photo).filter(
                    Photo.daycare_id == daycare_id,
                    Photo.uploaded_at >= cutoff_date
                ).count()

                # Photos with face recognition complete
                processed_photos = db.query(Photo).filter(
                    Photo.daycare_id == daycare_id,
                    Photo.uploaded_at >= cutoff_date,
                    Photo.face_recognition_complete == True
                ).count()

                # Auto-tagged photos
                auto_tagged = db.query(Photo).filter(
                    Photo.daycare_id == daycare_id,
                    Photo.uploaded_at >= cutoff_date,
                    Photo.auto_tagged == True
                ).count()

                # Photos with AI descriptions
                ai_described = db.query(Photo).filter(
                    Photo.daycare_id == daycare_id,
                    Photo.uploaded_at >= cutoff_date,
                    Photo.ai_generated_description.isnot(None)
                ).count()

                # Activities auto-created
                auto_activities = db.query(Activity).filter(
                    Activity.daycare_id == daycare_id,
                    Activity.created_at >= cutoff_date,
                    Activity.notes.like("%")  # Has AI-generated notes
                ).count()

                return {
                    "total_photos": total_photos,
                    "processed_photos": processed_photos,
                    "auto_tagged_photos": auto_tagged,
                    "ai_described_photos": ai_described,
                    "auto_created_activities": auto_activities,
                    "processing_rate": round(processed_photos / total_photos * 100, 1) if total_photos > 0 else 0,
                    "auto_tag_rate": round(auto_tagged / total_photos * 100, 1) if total_photos > 0 else 0
                }

        except Exception as e:
            print(f"Error getting processing stats: {e}")
            return {}


# Singleton instance
_photo_processor = None


def get_photo_processor() -> PhotoProcessor:
    """Get photo processor singleton"""
    global _photo_processor
    if _photo_processor is None:
        _photo_processor = PhotoProcessor()
    return _photo_processor
