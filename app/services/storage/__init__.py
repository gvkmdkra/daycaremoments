"""Storage Service - Swappable storage backends"""

from app.config import Config


class StorageService:
    """Swappable storage service supporting multiple backends"""

    def __init__(self):
        storage_type = Config.STORAGE_TYPE

        if storage_type == "google_drive":
            from .google_drive_adapter import GoogleDriveAdapter
            self.adapter = GoogleDriveAdapter()
        elif storage_type == "s3":
            from .s3_adapter import S3Adapter
            self.adapter = S3Adapter()
        elif storage_type == "r2":
            from .r2_adapter import R2Adapter
            self.adapter = R2Adapter()
        else:
            from .local_adapter import LocalAdapter
            self.adapter = LocalAdapter()

        self.storage_type = storage_type

    def upload(self, file_data: bytes, file_name: str, folder: str = "photos") -> str:
        """
        Upload file to storage

        Args:
            file_data: File bytes
            file_name: Name of the file
            folder: Folder/prefix for organization

        Returns:
            URL or path to uploaded file
        """
        return self.adapter.upload(file_data, file_name, folder)

    def download(self, file_path: str) -> bytes:
        """
        Download file from storage

        Args:
            file_path: Path or URL to file

        Returns:
            File bytes
        """
        return self.adapter.download(file_path)

    def delete(self, file_path: str) -> bool:
        """
        Delete file from storage

        Args:
            file_path: Path or URL to file

        Returns:
            True if successful
        """
        return self.adapter.delete(file_path)

    def list_files(self, folder: str = "photos") -> list:
        """
        List files in a folder

        Args:
            folder: Folder/prefix to list

        Returns:
            List of file paths/URLs
        """
        return self.adapter.list_files(folder)

    def get_url(self, file_path: str) -> str:
        """
        Get public URL for a file

        Args:
            file_path: Path to file

        Returns:
            Public URL
        """
        return self.adapter.get_url(file_path)


# Singleton instance
_storage_service = None


def get_storage_service():
    """Get storage service singleton"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
