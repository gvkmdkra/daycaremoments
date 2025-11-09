"""Google Drive Storage Adapter"""

from app.config import Config
import uuid


class GoogleDriveAdapter:
    """Google Drive storage adapter using Drive API"""

    def __init__(self):
        # In production, initialize Google Drive API client
        # from google.oauth2 import service_account
        # from googleapiclient.discovery import build

        # credentials = service_account.Credentials.from_service_account_file(
        #     Config.GOOGLE_CREDENTIALS_FILE,
        #     scopes=['https://www.googleapis.com/auth/drive.file']
        # )
        # self.service = build('drive', 'v3', credentials=credentials)
        # self.folder_id = Config.GOOGLE_DRIVE_FOLDER_ID

        print("Google Drive adapter initialized (demo mode)")

    def upload(self, file_data: bytes, file_name: str, folder: str = "photos") -> str:
        """Upload file to Google Drive"""
        # In production:
        # file_metadata = {
        #     'name': file_name,
        #     'parents': [self.folder_id]
        # }
        # media = MediaIoBaseUpload(io.BytesIO(file_data), mimetype='image/jpeg')
        # file = self.service.files().create(
        #     body=file_metadata,
        #     media_body=media,
        #     fields='id,webViewLink'
        # ).execute()
        # return file.get('webViewLink')

        # Demo mode: return simulated URL
        file_id = str(uuid.uuid4())
        return f"https://drive.google.com/file/d/{file_id}/view"

    def download(self, file_path: str) -> bytes:
        """Download file from Google Drive"""
        # In production:
        # file_id = extract_file_id_from_url(file_path)
        # request = self.service.files().get_media(fileId=file_id)
        # file_data = io.BytesIO()
        # downloader = MediaIoBaseDownload(file_data, request)
        # done = False
        # while not done:
        #     status, done = downloader.next_chunk()
        # return file_data.getvalue()

        return b""  # Demo mode

    def delete(self, file_path: str) -> bool:
        """Delete file from Google Drive"""
        # In production:
        # file_id = extract_file_id_from_url(file_path)
        # self.service.files().delete(fileId=file_id).execute()
        # return True

        return True  # Demo mode

    def list_files(self, folder: str = "photos") -> list:
        """List files in folder"""
        # In production:
        # results = self.service.files().list(
        #     q=f"'{self.folder_id}' in parents",
        #     fields="files(id, name, webViewLink)"
        # ).execute()
        # return [f.get('webViewLink') for f in results.get('files', [])]

        return []  # Demo mode

    def get_url(self, file_path: str) -> str:
        """Get public URL"""
        return file_path
