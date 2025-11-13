"""Face Recognition Service - Identify persons in photos"""

import numpy as np
from PIL import Image
import io
from typing import List, Dict, Optional
from app.database import get_db
from app.database.models import Person, Photo

# Try to import face_recognition, fallback to mock if not available
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("WARNING: face_recognition not installed. Using mock implementation.")
    print("To enable real face recognition:")
    print("  1. Install CMake from cmake.org")
    print("  2. pip install face_recognition")


class FaceRecognitionService:
    """Face recognition service using face_recognition library"""

    def __init__(self):
        self.tolerance = 0.6  # Lower = more strict
        self.model = "hog"  # Can be 'hog' or 'cnn' (cnn is more accurate but slower)
        self.mock_mode = not FACE_RECOGNITION_AVAILABLE

    def encode_face(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Extract face encoding from image

        Args:
            image_data: Image bytes

        Returns:
            Face encoding array or None if no face found
        """
        if self.mock_mode:
            # Mock implementation - return random encoding
            return np.random.rand(128)

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
        if self.mock_mode:
            # Mock implementation - return one random encoding
            return [np.random.rand(128)]

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

    def identify_person(self, face_encoding: np.ndarray, organization_id: str) -> Optional[str]:
        """
        Identify which person matches the face encoding

        Args:
            face_encoding: Face encoding to identify
            organization_id: Organization ID to search within

        Returns:
            Person ID if match found, None otherwise
        """
        try:
            with get_db() as db:
                # Get all persons with face encodings in this organization
                persons = db.query(Person).filter(
                    Person.organization_id == organization_id
                ).all()

                best_match_id = None
                best_match_distance = float('inf')

                for person in persons:
                    # Check if person has face encodings (JSON list)
                    if not person.face_encodings or len(person.face_encodings) == 0:
                        continue

                    # Compare with each stored encoding
                    for stored_encoding_list in person.face_encodings:
                        try:
                            known_encoding = np.array(stored_encoding_list, dtype=np.float64)

                            # Compare faces and get distance
                            matches = face_recognition.compare_faces(
                                [known_encoding],
                                face_encoding,
                                tolerance=self.tolerance
                            )

                            if matches[0]:
                                # Calculate face distance for best match
                                distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                                if distance < best_match_distance:
                                    best_match_distance = distance
                                    best_match_id = person.id

                        except Exception as e:
                            print(f"Error comparing encoding: {e}")
                            continue

                return best_match_id

        except Exception as e:
            print(f"Person identification error: {e}")
            return None

    def identify_persons_in_photo(self, image_data: bytes, organization_id: str) -> List[str]:
        """
        Identify all persons in a photo

        Args:
            image_data: Image bytes
            organization_id: Organization ID

        Returns:
            List of person IDs found in photo
        """
        identified_persons = []

        # Get all face encodings from photo
        face_encodings = self.encode_faces_multiple(image_data)

        # Try to identify each face
        for encoding in face_encodings:
            person_id = self.identify_person(encoding, organization_id)
            if person_id and person_id not in identified_persons:
                identified_persons.append(person_id)

        return identified_persons

    def train_person(self, person_id: str, training_images: List[bytes]) -> Dict[str, any]:
        """
        Train face recognition for a person using multiple training photos (minimum 3 recommended)

        Args:
            person_id: Person ID
            training_images: List of image bytes containing person's face

        Returns:
            Dictionary with success status and details
        """
        result = {
            "success": False,
            "encodings_added": 0,
            "total_encodings": 0,
            "failed_images": 0,
            "error": None
        }

        try:
            all_encodings = []

            # Extract encodings from each training image
            for image_data in training_images:
                encoding = self.encode_face(image_data)
                if encoding is not None:
                    # Convert to list for JSON storage
                    all_encodings.append(encoding.tolist())
                else:
                    result["failed_images"] += 1

            if not all_encodings:
                result["error"] = "No faces detected in training images"
                return result

            # Store encodings in database
            with get_db() as db:
                person = db.query(Person).filter(Person.id == person_id).first()

                if person:
                    # Update face encodings (append to existing or create new)
                    existing_encodings = person.face_encodings or []
                    person.face_encodings = existing_encodings + all_encodings
                    db.commit()

                    result["success"] = True
                    result["encodings_added"] = len(all_encodings)
                    result["total_encodings"] = len(person.face_encodings)
                    return result
                else:
                    result["error"] = "Person not found"
                    return result

        except Exception as e:
            result["error"] = str(e)
            print(f"Face training error: {e}")
            return result

    def get_face_locations(self, image_data: bytes) -> List[Dict[str, int]]:
        """
        Get bounding boxes for all faces in image

        Args:
            image_data: Image bytes

        Returns:
            List of face locations as dicts with top, right, bottom, left keys
        """
        if self.mock_mode:
            # Mock implementation - return one fake face location
            return [{"top": 100, "right": 300, "bottom": 300, "left": 100}]

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
