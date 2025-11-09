"""Cloudflare R2 Storage Adapter (S3-compatible)"""

from app.config import Config
import uuid


class R2Adapter:
    """Cloudflare R2 storage adapter"""

    def __init__(self):
        # In production, initialize boto3 client for R2
        # import boto3
        #
        # self.client = boto3.client(
        #     's3',
        #     endpoint_url=Config.R2_ENDPOINT_URL,
        #     aws_access_key_id=Config.R2_ACCESS_KEY_ID,
        #     aws_secret_access_key=Config.R2_SECRET_ACCESS_KEY,
        #     region_name='auto'
        # )
        # self.bucket_name = Config.R2_BUCKET_NAME
        # self.public_url = Config.R2_PUBLIC_URL

        print("R2 adapter initialized (demo mode)")

    def upload(self, file_data: bytes, file_name: str, folder: str = "photos") -> str:
        """Upload file to R2"""
        # In production:
        # key = f"{folder}/{uuid.uuid4()}_{file_name}"
        # self.client.put_object(
        #     Bucket=self.bucket_name,
        #     Key=key,
        #     Body=file_data,
        #     ContentType='image/jpeg'
        # )
        # return f"{self.public_url}/{key}"

        # Demo mode
        file_id = str(uuid.uuid4())
        return f"https://pub-{file_id}.r2.dev/{folder}/{file_name}"

    def download(self, file_path: str) -> bytes:
        """Download file from R2"""
        # In production:
        # key = extract_key_from_url(file_path)
        # response = self.client.get_object(Bucket=self.bucket_name, Key=key)
        # return response['Body'].read()

        return b""  # Demo mode

    def delete(self, file_path: str) -> bool:
        """Delete file from R2"""
        # In production:
        # key = extract_key_from_url(file_path)
        # self.client.delete_object(Bucket=self.bucket_name, Key=key)
        # return True

        return True  # Demo mode

    def list_files(self, folder: str = "photos") -> list:
        """List files in folder"""
        # In production:
        # response = self.client.list_objects_v2(
        #     Bucket=self.bucket_name,
        #     Prefix=folder
        # )
        # return [f"{self.public_url}/{obj['Key']}" for obj in response.get('Contents', [])]

        return []  # Demo mode

    def get_url(self, file_path: str) -> str:
        """Get public URL"""
        return file_path
