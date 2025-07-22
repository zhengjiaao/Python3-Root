import io
from datetime import timedelta
from typing import List, Optional
from minio import Minio
from minio.error import S3Error
import hashlib
from pathlib import Path
from minio.commonconfig import CopySource


class MinioFileManager:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = True):
        """Initialize MinIO client with connection parameters"""
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    # ========== Bucket Operations ==========
    def create_bucket(self, bucket_name: str) -> bool:
        """Create bucket if not exists"""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                return True
            return False
        except S3Error:
            return False

    def remove_bucket(self, bucket_name: str) -> bool:
        """Remove empty bucket"""
        try:
            self.client.remove_bucket(bucket_name)
            return True
        except S3Error:
            return False

    def bucket_exists(self, bucket_name: str) -> bool:
        """Check if bucket exists"""
        try:
            return self.client.bucket_exists(bucket_name)
        except S3Error:
            return False

    def list_buckets(self) -> List[str]:
        """List all bucket names"""
        try:
            return [bucket.name for bucket in self.client.list_buckets()]
        except S3Error:
            return []

    def empty_bucket(self, bucket_name: str) -> bool:
        """Delete all objects in bucket"""
        try:
            objects = self.list_objects(bucket_name)
            for obj in objects:
                self.delete_object(bucket_name, obj)
            return True
        except S3Error:
            return False

    # ========== Object Operations ==========
    def upload_file(self, bucket_name: str, object_name: str,
                   file_path: str, content_type: str = "application/octet-stream") -> bool:
        """Upload file with optional content type"""
        try:
            self.client.fput_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type
            )
            return True
        except (S3Error, FileNotFoundError):
            return False

    def download_file(self, bucket_name: str, object_name: str,
                    file_path: str) -> bool:
        """Download object to file"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            self.client.fget_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=file_path
            )
            return True
        except S3Error:
            return False

    def upload_bytes(self, bucket_name: str, object_name: str,
                    data: bytes, content_type: str = "application/octet-stream") -> bool:
        """Upload bytes data as object"""
        try:
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=io.BytesIO(data),
                length=len(data),
                content_type=content_type
            )
            return True
        except S3Error:
            return False

    def download_bytes(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """Download object as bytes"""
        try:
            response = self.client.get_object(bucket_name, object_name)
            return response.read()
        except S3Error:
            return None
        finally:
            response.close()
            response.release_conn()

    def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        """List objects with optional prefix filter"""
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error:
            return []

    def object_exists(self, bucket_name: str, object_name: str) -> bool:
        """Check if object exists"""
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False

    def get_object_size(self, bucket_name: str, object_name: str) -> Optional[int]:
        """Get object size in bytes"""
        try:
            obj_info = self.client.stat_object(bucket_name, object_name)
            return obj_info.size
        except S3Error:
            return None

    def delete_object(self, bucket_name: str, object_name: str) -> bool:
        """Delete object from bucket"""
        try:
            if not self.object_exists(bucket_name, object_name):
                return False
            self.client.remove_object(bucket_name, object_name)
            return True
        except S3Error:
            return False

    def copy_object(self, source_bucket: str, source_object: str,
                    dest_bucket: str, dest_object: str) -> bool:
        """Copy object within MinIO"""
        try:
            self.client.copy_object(
                dest_bucket,
                dest_object,
                CopySource(source_bucket, source_object)  # 使用 CopySource
            )
            return True
        except S3Error:
            return False

    # ========== URL Operations ==========
    def generate_presigned_url(self, bucket_name: str, object_name: str,
                             expiry_days: int = 7) -> Optional[str]:
        """Generate presigned GET URL"""
        if not self.object_exists(bucket_name, object_name):
            return None
        try:
            return self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=timedelta(days=expiry_days)
            )
        except S3Error:
            return None

    def generate_presigned_put_url(self, bucket_name: str, object_name: str,
                                 expiry_days: int = 1) -> Optional[str]:
        """Generate presigned PUT URL"""
        try:
            return self.client.presigned_put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=timedelta(days=expiry_days)
            )
        except S3Error:
            return None

    # ========== File Operations ==========
    def verify_file_integrity(self, bucket_name: str, object_name: str,
                            local_path: str) -> bool:
        """Verify file integrity using ETag/MD5"""
        try:
            remote_info = self.client.stat_object(bucket_name, object_name)
            remote_hash = remote_info.etag.replace('"', '')

            local_hash = self._calculate_md5(local_path)
            return remote_hash == local_hash
        except (S3Error, FileNotFoundError):
            return False

    @staticmethod
    def _calculate_md5(file_path: str) -> str:
        """Calculate file MD5 hash"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
