"""
Google Drive Auto-Sync Service
Monitors Google Drive folder for new photos/videos and automatically:
1. Downloads new media
2. Analyzes with AI (face detection, activity recognition)
3. Creates database entries (photos + activities)
4. Notifies parents
"""

from datetime import datetime
from typing import List, Dict, Optional
import time


class GoogleDriveSyncService:
    """
    Automatic Google Drive synchronization

    Real-time monitoring of daycare camera uploads:
    - Camera uploads photos to Google Drive folder
    - This service polls for new files every N seconds
    - New photos are analyzed and added to database
    - Activities are auto-generated from photo analysis
    """

    def __init__(self, credentials_path: str = None):
        """Initialize with Google Drive credentials"""
        self.credentials_path = credentials_path
        self.last_sync_time = datetime.utcnow()
        self.is_running = False

    def start_monitoring(self, folder_id: str, poll_interval: int = 60):
        """
        Start monitoring Google Drive folder for new uploads

        Args:
            folder_id: Google Drive folder ID to monitor
            poll_interval: Check for new files every N seconds (default: 60)
        """
        self.is_running = True

        while self.is_running:
            try:
                # Get new files since last sync
                new_files = self.get_new_files(folder_id, self.last_sync_time)

                if new_files:
                    print(f"Found {len(new_files)} new files")
                    self.process_new_files(new_files)

                self.last_sync_time = datetime.utcnow()

            except Exception as e:
                print(f"Sync error: {e}")

            # Wait before next poll
            time.sleep(poll_interval)

    def stop_monitoring(self):
        """Stop the monitoring service"""
        self.is_running = False

    def get_new_files(self, folder_id: str, since: datetime) -> List[Dict]:
        """
        Get new files from Google Drive folder since timestamp

        In production: Use Google Drive API
        from googleapiclient.discovery import build
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(
            q=f"'{folder_id}' in parents and modifiedTime > '{since.isoformat()}'",
            fields="files(id, name, mimeType, modifiedTime, webContentLink)"
        ).execute()
        """

        # Placeholder: Returns simulated new files
        return []

    def process_new_files(self, files: List[Dict]):
        """
        Process new files:
        1. Download file
        2. Analyze with AI
        3. Create database entries
        4. Send notifications
        """
        from app.services.photo_analysis import get_photo_analysis_service
        from app.database import get_db
        from app.database.models import Photo, Activity, Child, PhotoStatus

        photo_analyzer = get_photo_analysis_service()

        for file in files:
            try:
                # Download file (in production: use Drive API)
                # file_content = service.files().get_media(fileId=file['id']).execute()

                # Analyze photo with AI
                analysis = photo_analyzer.analyze_with_vision_ai(file['webContentLink'])

                # Detect faces and match to children
                detected_faces = photo_analyzer.detect_faces(file['webContentLink'])

                # Create photo entry
                with get_db() as db:
                    for face in detected_faces:
                        child_id = face.get('child_id')

                        if not child_id:
                            # Try to match face to existing child
                            child_id = self._match_face_to_child(face, db)

                        if child_id:
                            # Create photo record
                            photo = Photo(
                                file_name=file['name'],
                                original_file_name=file['name'],
                                url=file['webContentLink'],
                                thumbnail_url=file.get('thumbnailLink'),
                                caption=analysis['description'],
                                captured_at=datetime.fromisoformat(file['modifiedTime']),
                                child_id=child_id,
                                daycare_id=self._get_child_daycare_id(child_id, db),
                                status=PhotoStatus.PENDING,  # Needs staff approval
                                uploaded_by=None  # Auto-uploaded from camera
                            )
                            db.add(photo)
                            db.flush()

                            # Auto-generate activity from photo
                            activity = Activity(
                                child_id=child_id,
                                daycare_id=photo.daycare_id,
                                staff_id=None,  # AI-generated
                                activity_type=analysis['activity_type'],
                                activity_time=photo.captured_at,
                                notes=f"Auto-detected: {analysis['description']}",
                                mood=analysis['mood']
                            )
                            db.add(activity)

                            db.commit()

                            print(f"✅ Processed: {file['name']} - {analysis['activity_type']}")

            except Exception as e:
                print(f"Error processing {file.get('name', 'unknown')}: {e}")

    def _match_face_to_child(self, face_data: Dict, db) -> Optional[str]:
        """
        Match detected face to child in database using face recognition

        In production: Compare face encoding with stored child.face_encoding
        using face_recognition library or DeepFace
        """
        from app.database.models import Child

        # Placeholder: In production, use actual face matching
        # Example:
        # face_encoding = face_data['encoding']
        # children = db.query(Child).all()
        # for child in children:
        #     if child.face_encoding:
        #         distance = face_recognition.face_distance([child.face_encoding], face_encoding)
        #         if distance < 0.6:  # Match threshold
        #             return child.id

        return None

    def _get_child_daycare_id(self, child_id: str, db) -> str:
        """Get daycare ID for a child"""
        from app.database.models import Child

        child = db.query(Child).filter(Child.id == child_id).first()
        return child.daycare_id if child else None

    def manual_sync(self, folder_id: str):
        """Manually trigger a one-time sync"""
        new_files = self.get_new_files(folder_id, self.last_sync_time)
        self.process_new_files(new_files)
        self.last_sync_time = datetime.utcnow()

        return len(new_files)

    def import_folder(self, folder_id: str, daycare_id: str):
        """
        One-time import of all photos from a Google Drive folder

        Use this for initial setup: import existing photos
        """
        from app.database import get_db
        from app.database.models import Photo, PhotoStatus
        from app.services.photo_analysis import get_photo_analysis_service

        photo_analyzer = get_photo_analysis_service()

        # In production: Get all files from folder
        # service.files().list(q=f"'{folder_id}' in parents")

        files = []  # Placeholder

        imported_count = 0

        with get_db() as db:
            for file in files:
                # Analyze and create photo entry
                analysis = photo_analyzer.analyze_with_vision_ai(file['webContentLink'])

                photo = Photo(
                    file_name=file['name'],
                    original_file_name=file['name'],
                    url=file['webContentLink'],
                    caption=analysis['description'],
                    captured_at=datetime.fromisoformat(file['modifiedTime']),
                    daycare_id=daycare_id,
                    status=PhotoStatus.PENDING
                )
                db.add(photo)
                imported_count += 1

            db.commit()

        return imported_count


# Singleton instance
_gdrive_sync_service = None

def get_gdrive_sync_service():
    """Get Google Drive sync service instance"""
    global _gdrive_sync_service
    if _gdrive_sync_service is None:
        _gdrive_sync_service = GoogleDriveSyncService()
    return _gdrive_sync_service
