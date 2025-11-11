"""
Reusable Google Drive Connector Package
Can be dropped into any Python project for instant Google Drive integration
"""

from .google_drive_service import GoogleDriveService, get_google_drive_service

__version__ = "1.0.0"
__all__ = ['GoogleDriveService', 'get_google_drive_service']
