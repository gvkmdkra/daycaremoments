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

    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize Google Drive service

        Args:
            credentials_path: Path to OAuth2 credentials.json or service account JSON
            token_path: Path to store OAuth2 token (for user authentication)
        """
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError(
                "Google Drive dependencies not installed. "
                "Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )

        self.credentials_path = credentials_path or os.getenv('GOOGLE_DRIVE_CREDENTIALS', 'credentials.json')
        self.token_path = token_path or os.getenv('GOOGLE_DRIVE_TOKEN', 'token.json')
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
        Authenticate using service account (app-wide access)

        Returns:
            True if authentication successful
        """
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Service account credentials not found: {self.credentials_path}"
            )

        creds = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=self.SCOPES
        )

        self.creds = creds
        self.service = build('drive', 'v3', credentials=creds)
        return True

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


# Singleton instance
_gdrive_service = None

def get_google_drive_service(credentials_path: str = None, token_path: str = None) -> GoogleDriveService:
    """
    Get Google Drive service instance (singleton)

    Args:
        credentials_path: Path to credentials file
        token_path: Path to token file

    Returns:
        GoogleDriveService instance
    """
    global _gdrive_service
    if _gdrive_service is None:
        _gdrive_service = GoogleDriveService(credentials_path, token_path)
    return _gdrive_service
