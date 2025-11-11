"""
Google Drive Integration Module
Reusable service for uploading, downloading, and managing files in Google Drive
"""

import os
import io
from typing import List, Dict, Optional, BinaryIO
from datetime import datetime
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
    from googleapiclient.errors import HttpError
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False


class GoogleDriveService:
    """
    Google Drive Service for file operations

    Features:
    - OAuth2 authentication (user-specific access)
    - Service account authentication (app-wide access)
    - Upload files to specific folders
    - Download files
    - List files with filters
    - Create folders
    - Share files/folders with specific users
    """

    # Google Drive API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',  # Access to files created by this app
        'https://www.googleapis.com/auth/drive',       # Full drive access
    ]

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        service_account_path: Optional[str] = None,
        mode: Optional[str] = None
    ):
        """
        Initialize Google Drive service

        Args:
            credentials_path: Path to OAuth2 credentials.json
            service_account_path: Path to service account JSON file
            token_path: Path to store OAuth2 token (for user authentication)
        """
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError(
                "Google Drive dependencies not installed. "
                "Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )

        self.credentials_path = credentials_path or os.getenv('GOOGLE_DRIVE_CREDENTIALS', 'credentials.json')
        self.token_path = token_path or os.getenv('GOOGLE_DRIVE_TOKEN', 'token.json')
        self.service_account_path = service_account_path or os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT')
        self.mode = mode or os.getenv('GOOGLE_DRIVE_MODE', 'oauth')  # 'oauth' or 'service_account'
        self.service = None
        self.creds = None

    def authenticate_user(self) -> bool:
        """
        Authenticate using OAuth2 (user-specific access)
        Opens browser for user to grant permissions

        Returns:
            True if authentication successful
        """
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Get credentials from: https://console.cloud.google.com/"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for future use
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.creds = creds
        self.service = build('drive', 'v3', credentials=creds)
        return True

    def authenticate_service_account(self) -> bool:
        """
        Authenticate using service account (app-wide access, production mode)
        No user interaction required - uses service account credentials

        Returns:
            True if authentication successful
        """
        if not self.service_account_path:
            raise ValueError("Service account path not configured. Set GOOGLE_DRIVE_SERVICE_ACCOUNT in .env")

        if not os.path.exists(self.service_account_path):
            raise FileNotFoundError(
                f"Service account credentials not found: {self.service_account_path}"
            )

        try:
            creds = service_account.Credentials.from_service_account_file(
                self.service_account_path, scopes=self.SCOPES
            )

            self.creds = creds
            self.service = build('drive', 'v3', credentials=creds)
            return True
        except Exception as e:
            raise RuntimeError(f"Service account authentication failed: {e}")

    def authenticate(self) -> bool:
        """
        Smart authentication - chooses method based on mode configuration

        Modes:
        - 'service_account': Production mode, no user interaction
        - 'oauth': Development/testing mode, requires user consent

        Returns:
            True if authentication successful
        """
        if self.mode == 'service_account':
            return self.authenticate_service_account()
        else:
            return self.authenticate_user()

    def upload_file(
        self,
        file_path: str = None,
        file_content: BinaryIO = None,
        file_name: str = None,
        mime_type: str = None,
        folder_id: str = None,
        description: str = None
    ) -> Dict:
        """
        Upload a file to Google Drive

        Args:
            file_path: Path to local file (if uploading from disk)
            file_content: File-like object (if uploading from memory)
            file_name: Name for the file in Drive
            mime_type: MIME type of file (auto-detected if not provided)
            folder_id: Google Drive folder ID (uploads to root if not provided)
            description: File description

        Returns:
            Dict with file metadata (id, name, webViewLink, etc.)
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate_user() or authenticate_service_account() first")

        # Determine file name and MIME type
        if file_path:
            file_name = file_name or os.path.basename(file_path)
            if not mime_type:
                mime_type = self._get_mime_type(file_path)
        elif not file_name:
            raise ValueError("file_name must be provided when using file_content")

        # Default mime_type if still None
        if not mime_type:
            mime_type = 'application/octet-stream'

        # Prepare file metadata
        file_metadata = {
            'name': file_name,
        }

        if folder_id:
            file_metadata['parents'] = [folder_id]

        if description:
            file_metadata['description'] = description

        # Upload file
        try:
            if file_path:
                media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            else:
                media = MediaIoBaseUpload(file_content, mimetype=mime_type, resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, size, createdTime, webViewLink, webContentLink'
            ).execute()

            return file

        except HttpError as error:
            raise RuntimeError(f"Failed to upload file: {error}")

    def download_file(self, file_id: str, destination_path: str = None) -> bytes:
        """
        Download a file from Google Drive

        Args:
            file_id: Google Drive file ID
            destination_path: Local path to save file (optional)

        Returns:
            File content as bytes
        """
        if not self.service:
            raise RuntimeError("Not authenticated")

        try:
            request = self.service.files().get_media(fileId=file_id)

            if destination_path:
                # Download to file
                fh = io.FileIO(destination_path, 'wb')
                downloader = MediaIoBaseDownload(fh, request)

                done = False
                while not done:
                    status, done = downloader.next_chunk()

                fh.close()

                with open(destination_path, 'rb') as f:
                    return f.read()
            else:
                # Download to memory
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)

                done = False
                while not done:
                    status, done = downloader.next_chunk()

                return fh.getvalue()

        except HttpError as error:
            raise RuntimeError(f"Failed to download file: {error}")

    def list_files(
        self,
        folder_id: str = None,
        query: str = None,
        page_size: int = 100,
        order_by: str = 'modifiedTime desc'
    ) -> List[Dict]:
        """
        List files in Google Drive

        Args:
            folder_id: List files in specific folder
            query: Custom query string (e.g., "mimeType='image/jpeg'")
            page_size: Number of files to return
            order_by: Sort order

        Returns:
            List of file metadata dictionaries
        """
        if not self.service:
            raise RuntimeError("Not authenticated")

        # Build query
        if folder_id:
            q = f"'{folder_id}' in parents"
            if query:
                q += f" and {query}"
        else:
            q = query or ""

        try:
            results = self.service.files().list(
                q=q,
                pageSize=page_size,
                orderBy=order_by,
                fields='files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink)'
            ).execute()

            return results.get('files', [])

        except HttpError as error:
            raise RuntimeError(f"Failed to list files: {error}")

    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Dict:
        """
        Create a folder in Google Drive

        Args:
            folder_name: Name for the new folder
            parent_folder_id: Parent folder ID (creates in root if not provided)

        Returns:
            Folder metadata
        """
        if not self.service:
            raise RuntimeError("Not authenticated")

        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]

        try:
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()

            return folder

        except HttpError as error:
            raise RuntimeError(f"Failed to create folder: {error}")

    def share_file(self, file_id: str, email: str, role: str = 'reader') -> Dict:
        """
        Share a file/folder with a specific user

        Args:
            file_id: File or folder ID
            email: Email address to share with
            role: Permission role ('reader', 'writer', 'commenter', 'owner')

        Returns:
            Permission metadata
        """
        if not self.service:
            raise RuntimeError("Not authenticated")

        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }

        try:
            result = self.service.permissions().create(
                fileId=file_id,
                body=permission,
                fields='id'
            ).execute()

            return result

        except HttpError as error:
            raise RuntimeError(f"Failed to share file: {error}")

    def get_file_metadata(self, file_id: str) -> Dict:
        """
        Get metadata for a specific file

        Args:
            file_id: Google Drive file ID

        Returns:
            File metadata
        """
        if not self.service:
            raise RuntimeError("Not authenticated")

        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink, parents'
            ).execute()

            return file

        except HttpError as error:
            raise RuntimeError(f"Failed to get file metadata: {error}")

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive

        Args:
            file_id: File ID to delete

        Returns:
            True if successful
        """
        if not self.service:
            raise RuntimeError("Not authenticated")

        try:
            self.service.files().delete(fileId=file_id).execute()
            return True

        except HttpError as error:
            raise RuntimeError(f"Failed to delete file: {error}")

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type from file extension"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'

    # ========================================================================
    # Daycare-Specific Methods (Production Features)
    # ========================================================================

    def create_daycare_folder(self, daycare_id: int, daycare_name: str) -> Dict:
        """
        Create isolated folder structure for a daycare

        Structure:
        daycare_{id}_{name}/
        ├── photos/
        ├── documents/
        └── exports/

        Args:
            daycare_id: Unique daycare ID
            daycare_name: Daycare name (sanitized)

        Returns:
            Dict with folder information
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first")

        root_folder_id = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER_ID')
        if not root_folder_id:
            raise ValueError("GOOGLE_DRIVE_ROOT_FOLDER_ID not set in .env")

        # Sanitize folder name
        safe_name = daycare_name.replace(' ', '_').replace('/', '_')
        folder_name = f"daycare_{daycare_id:06d}_{safe_name}"

        # Create main folder
        daycare_folder = self.create_folder(
            folder_name=folder_name,
            parent_folder_id=root_folder_id
        )

        # Create subfolders
        self.create_folder('photos', parent_folder_id=daycare_folder['id'])
        self.create_folder('documents', parent_folder_id=daycare_folder['id'])
        self.create_folder('exports', parent_folder_id=daycare_folder['id'])

        return daycare_folder

    def upload_photo_for_daycare(
        self,
        daycare_id: int,
        file_content: BinaryIO,
        file_name: str,
        year_month: str = None
    ) -> Dict:
        """
        Upload photo to daycare's folder with date organization

        Args:
            daycare_id: Daycare ID
            file_content: Photo file content
            file_name: Photo filename
            year_month: Optional year-month (e.g., '2025-01') for organization

        Returns:
            Dict with uploaded file information
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first")

        # Get daycare folder ID from database
        try:
            from app.database import get_db
            from app.database.models import Daycare

            with get_db() as db:
                daycare = db.query(Daycare).filter_by(id=daycare_id).first()
                if not daycare or not daycare.google_drive_folder_id:
                    raise ValueError("Daycare folder not configured")

                base_folder_id = daycare.google_drive_folder_id
        except ImportError:
            # Fallback if database not available
            base_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

        # Get photos subfolder
        folders = self.list_files(
            folder_id=base_folder_id,
            query="mimeType='application/vnd.google-apps.folder' and name='photos'"
        )

        if not folders:
            photos_folder = self.create_folder('photos', parent_folder_id=base_folder_id)
            photos_folder_id = photos_folder['id']
        else:
            photos_folder_id = folders[0]['id']

        # Create year-month subfolder if needed
        if year_month:
            month_folders = self.list_files(
                folder_id=photos_folder_id,
                query=f"mimeType='application/vnd.google-apps.folder' and name='{year_month}'"
            )

            if not month_folders:
                month_folder = self.create_folder(year_month, parent_folder_id=photos_folder_id)
                target_folder_id = month_folder['id']
            else:
                target_folder_id = month_folders[0]['id']
        else:
            target_folder_id = photos_folder_id

        # Upload file
        result = self.upload_file(
            file_content=file_content,
            file_name=file_name,
            folder_id=target_folder_id
        )

        return result

    def get_storage_usage(self, daycare_id: int) -> Dict:
        """
        Get storage statistics for a daycare

        Args:
            daycare_id: Daycare ID

        Returns:
            Dict with usage statistics
        """
        try:
            from app.database import get_db
            from app.database.models import Daycare

            with get_db() as db:
                daycare = db.query(Daycare).filter_by(id=daycare_id).first()
                if not daycare:
                    raise ValueError("Daycare not found")

                used_mb = getattr(daycare, 'storage_used_mb', 0)
                quota_mb = getattr(daycare, 'storage_quota_mb', 5000)

                return {
                    'used_mb': used_mb,
                    'quota_mb': quota_mb,
                    'percent_used': (used_mb / quota_mb * 100) if quota_mb > 0 else 0,
                    'available_mb': quota_mb - used_mb
                }
        except ImportError:
            # Fallback if database not available
            return {
                'used_mb': 0,
                'quota_mb': 5000,
                'percent_used': 0,
                'available_mb': 5000
            }


# Singleton instance
_gdrive_service = None

def get_google_drive_service(
    credentials_path: str = None,
    token_path: str = None,
    service_account_path: str = None,
    mode: str = None
) -> GoogleDriveService:
    """
    Get Google Drive service instance (singleton)

    Args:
        credentials_path: Path to OAuth credentials file
        token_path: Path to token file
        service_account_path: Path to service account JSON
        mode: Authentication mode ('oauth' or 'service_account')

    Returns:
        GoogleDriveService instance
    """
    global _gdrive_service
    if _gdrive_service is None:
        _gdrive_service = GoogleDriveService(
            credentials_path=credentials_path,
            token_path=token_path,
            service_account_path=service_account_path,
            mode=mode
        )
    return _gdrive_service
