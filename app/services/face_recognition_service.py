"""Face Recognition Service - Identify children in photos"""

import face_recognition
import numpy as np
from PIL import Image
import io
from typing import List, Dict, Optional
from app.database import get_db
from app.database.models import Child, Photo


class FaceRecognitionService:
    """Face recognition service using face_recognition library"""

    def __init__(self):
        self.tolerance = 0.6  # Lower = more strict
        self.model = "hog"  # Can be 'hog' or 'cnn' (cnn is more accurate but slower)

    def encode_face(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Extract face encoding from image

        Args:
            image_data: Image bytes

        Returns:
            Face encoding array or None if no face found
        """
        try:
            # Load image
            image = face_recognition.load_image_file(io.BytesIO(image_data))

            # Find faces
            face_locations = face_recognition.face_locations(image, model=self.model)

            if not face_locations:
                return None

            # Get encoding for first face
            encodings = face_recognition.face_encodings(image, face_locations)

            if encodings:
                return encodings[0]

            return None

        except Exception as e:
            print(f"Face encoding error: {e}")
            return None

    def encode_faces_multiple(self, image_data: bytes) -> List[np.ndarray]:
        """
        Extract all face encodings from image (for group photos)

        Args:
            image_data: Image bytes

        Returns:
            List of face encodings
        """
        try:
            image = face_recognition.load_image_file(io.BytesIO(image_data))
            face_locations = face_recognition.face_locations(image, model=self.model)

            if not face_locations:
                return []

            encodings = face_recognition.face_encodings(image, face_locations)
            return encodings

        except Exception as e:
            print(f"Multiple face encoding error: {e}")
            return []

    def compare_faces(self, known_encoding: np.ndarray, unknown_encoding: np.ndarray) -> bool:
        """
        Compare two face encodings

        Args:
            known_encoding: Known face encoding
            unknown_encoding: Unknown face encoding

        Returns:
            True if faces match
        """
        try:
            results = face_recognition.compare_faces(
                [known_encoding],
                unknown_encoding,
                tolerance=self.tolerance
            )
            return results[0] if results else False

        except Exception as e:
            print(f"Face comparison error: {e}")
            return False

    def identify_child(self, face_encoding: np.ndarray, daycare_id: str) -> Optional[str]:
        """
        Identify which child matches the face encoding

        Args:
            face_encoding: Face encoding to identify
            daycare_id: Daycare ID to search within

        Returns:
            Child ID if match found, None otherwise
        """
        try:
            with get_db() as db:
                # Get all children with face encodings in this daycare
                children = db.query(Child).filter(
                    Child.daycare_id == daycare_id,
                    Child.face_encoding.isnot(None)
                ).all()

                for child in children:
                    # Compare with stored encoding
                    if child.face_encoding:
                        known_encoding = np.frombuffer(child.face_encoding, dtype=np.float64)

                        if self.compare_faces(known_encoding, face_encoding):
                            return child.id

                return None

        except Exception as e:
            print(f"Child identification error: {e}")
            return None

    def identify_children_in_photo(self, image_data: bytes, daycare_id: str) -> List[str]:
        """
        Identify all children in a photo

        Args:
            image_data: Image bytes
            daycare_id: Daycare ID

        Returns:
            List of child IDs found in photo
        """
        identified_children = []

        # Get all face encodings from photo
        face_encodings = self.encode_faces_multiple(image_data)

        # Try to identify each face
        for encoding in face_encodings:
            child_id = self.identify_child(encoding, daycare_id)
            if child_id and child_id not in identified_children:
                identified_children.append(child_id)

        return identified_children

    def register_child_face(self, child_id: str, image_data: bytes) -> bool:
        """
        Register a child's face for future recognition

        Args:
            child_id: Child ID
            image_data: Image bytes containing child's face

        Returns:
            True if successful
        """
        try:
            # Get face encoding
            encoding = self.encode_face(image_data)

            if encoding is None:
                return False

            # Store encoding in database
            with get_db() as db:
                child = db.query(Child).filter(Child.id == child_id).first()

                if child:
                    # Convert numpy array to bytes for storage
                    child.face_encoding = encoding.tobytes()
                    db.commit()
                    return True

                return False

        except Exception as e:
            print(f"Face registration error: {e}")
            return False

    def auto_tag_photo(self, photo_id: str) -> List[str]:
        """
        Automatically tag children in a photo

        Args:
            photo_id: Photo ID

        Returns:
            List of child IDs found in photo
        """
        try:
            with get_db() as db:
                photo = db.query(Photo).filter(Photo.id == photo_id).first()

                if not photo:
                    return []

                # Download image (in production, this would fetch from storage)
                # For now, we'll return empty as this requires actual image data
                # image_data = download_from_storage(photo.url)

                # Identify children
                # child_ids = self.identify_children_in_photo(image_data, photo.daycare_id)

                # Update photo with identified children
                # if child_ids:
                #     photo.child_id = child_ids[0]  # Main child
                #     db.commit()

                # return child_ids

                return []

        except Exception as e:
            print(f"Auto-tagging error: {e}")
            return []

    def get_face_locations(self, image_data: bytes) -> List[Dict[str, int]]:
        """
        Get bounding boxes for all faces in image

        Args:
            image_data: Image bytes

        Returns:
            List of face locations as dicts with top, right, bottom, left keys
        """
        try:
            image = face_recognition.load_image_file(io.BytesIO(image_data))
            locations = face_recognition.face_locations(image, model=self.model)

            return [
                {"top": top, "right": right, "bottom": bottom, "left": left}
                for top, right, bottom, left in locations
            ]

        except Exception as e:
            print(f"Face location error: {e}")
            return []


# Singleton instance
_face_recognition_service = None


def get_face_recognition_service() -> FaceRecognitionService:
    """Get face recognition service singleton"""
    global _face_recognition_service
    if _face_recognition_service is None:
        _face_recognition_service = FaceRecognitionService()
    return _face_recognition_service
