"""Local Storage Adapter - Store files on local filesystem"""

import os
from pathlib import Path
from app.config import Config
import uuid


class LocalAdapter:
    """Local filesystem storage adapter"""

    def __init__(self):
        self.base_path = Path(Config.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def upload(self, file_data: bytes, file_name: str, folder: str = "photos") -> str:
        """Upload file to local storage"""
        # Create folder if not exists
        folder_path = self.base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_ext = Path(file_name).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = folder_path / unique_name

        # Write file
        with open(file_path, 'wb') as f:
            f.write(file_data)

        # Return relative path
        return str(file_path.relative_to(self.base_path))

    def download(self, file_path: str) -> bytes:
        """Download file from local storage"""
        full_path = self.base_path / file_path

        with open(full_path, 'rb') as f:
            return f.read()

    def delete(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            full_path = self.base_path / file_path
            full_path.unlink()
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def list_files(self, folder: str = "photos") -> list:
        """List files in folder"""
        folder_path = self.base_path / folder

        if not folder_path.exists():
            return []

        files = []
        for file in folder_path.iterdir():
            if file.is_file():
                files.append(str(file.relative_to(self.base_path)))

        return files

    def get_url(self, file_path: str) -> str:
        """Get URL for file (local path)"""
        return f"/uploads/{file_path}"
