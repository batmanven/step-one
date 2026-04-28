import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from app.config import settings
from typing import Optional
import uuid


class S3Service:
    def __init__(self):
        # Only initialize S3 client if credentials are available
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
                config=Config(signature_version='s3v4')
            )
        else:
            self.s3_client = None
        self.bucket = settings.s3_bucket
        self.cdn_bucket = settings.s3_bucket_cdn

    def generate_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600,
        operation: str = "put_object"
    ) -> Optional[str]:
        """Generate a presigned URL for S3 operations"""
        if not self.s3_client:
            return None
        try:
            url = self.s3_client.generate_presigned_url(
                operation,
                Params={'Bucket': self.bucket, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def generate_upload_url(
        self,
        session_id: str,
        filename: str,
        content_type: str,
        expiration: int = 3600
    ) -> dict:
        """Generate presigned URL for direct upload"""
        if not self.s3_client:
            raise Exception("S3 not configured")
        object_key = f"sessions/{session_id}/{filename}"

        try:
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': object_key,
                    'ContentType': content_type
                },
                ExpiresIn=expiration
            )

            return {
                "upload_url": url,
                "file_key": object_key,
                "expires_in": expiration
            }
        except ClientError as e:
            print(f"Error generating upload URL: {e}")
            raise

    def get_file_url(self, object_key: str, expiration: int = 3600) -> Optional[str]:
        """Generate presigned URL for downloading"""
        if not self.s3_client:
            return None
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating download URL: {e}")
            return None

    def delete_file(self, object_key: str) -> bool:
        """Delete a file from S3"""
        if not self.s3_client:
            return False
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=object_key)
            return True
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False

    def file_exists(self, object_key: str) -> bool:
        """Check if a file exists in S3"""
        if not self.s3_client:
            return False
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=object_key)
            return True
        except ClientError:
            return False

    def get_file_metadata(self, object_key: str) -> Optional[dict]:
        """Get metadata for a file"""
        if not self.s3_client:
            return None
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=object_key)
            return {
                "size": response['ContentLength'],
                "content_type": response['ContentType'],
                "last_modified": response['LastModified']
            }
        except ClientError as e:
            print(f"Error getting file metadata: {e}")
            return None


# Singleton instance
s3_service = S3Service()
