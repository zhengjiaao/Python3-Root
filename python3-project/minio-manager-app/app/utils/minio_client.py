from minio import Minio
from minio.error import S3Error
from ..config import settings

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        if not self.client.bucket_exists(settings.minio_bucket):
            self.client.make_bucket(settings.minio_bucket)

    def upload_file(self, file, file_name: str):
        try:
            self.client.put_object(
                settings.minio_bucket,
                file_name,
                file.file,
                length=-1,
                part_size=10*1024*1024
            )
            return True
        except S3Error:
            return False

    def download_file(self, file_name: str):
        try:
            return self.client.get_object(settings.minio_bucket, file_name)
        except S3Error:
            return None

    def delete_file(self, file_name: str):
        try:
            self.client.remove_object(settings.minio_bucket, file_name)
            return True
        except S3Error:
            return False