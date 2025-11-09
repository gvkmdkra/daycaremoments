"""AWS S3 Storage Adapter"""

from app.config import Config
import uuid


class S3Adapter:
    """AWS S3 storage adapter"""

    def __init__(self):
        # In production, initialize boto3 client
        # import boto3
        #
        # self.client = boto3.client(
        #     's3',
        #     aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        #     aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        #     region_name=Config.AWS_REGION
        # )
        # self.bucket_name = Config.S3_BUCKET_NAME

        print("S3 adapter initialized (demo mode)")

    def upload(self, file_data: bytes, file_name: str, folder: str = "photos") -> str:
        """Upload file to S3"""
        # In production:
        # key = f"{folder}/{uuid.uuid4()}_{file_name}"
        # self.client.put_object(
        #     Bucket=self.bucket_name,
        #     Key=key,
        #     Body=file_data,
        #     ContentType='image/jpeg',
        #     ACL='public-read'
        # )
        # return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"

        # Demo mode
        file_id = str(uuid.uuid4())
        return f"https://daycare-photos.s3.amazonaws.com/{folder}/{file_id}_{file_name}"

    def download(self, file_path: str) -> bytes:
        """Download file from S3"""
        # In production:
        # key = extract_key_from_url(file_path)
        # response = self.client.get_object(Bucket=self.bucket_name, Key=key)
        # return response['Body'].read()

        return b""  # Demo mode

    def delete(self, file_path: str) -> bool:
        """Delete file from S3"""
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
        # return [
        #     f"https://{self.bucket_name}.s3.amazonaws.com/{obj['Key']}"
        #     for obj in response.get('Contents', [])
        # ]

        return []  # Demo mode

    def get_url(self, file_path: str) -> str:
        """Get public URL"""
        return file_path
