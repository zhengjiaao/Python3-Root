import time
import unittest
import os
import tempfile

from minio_manager import MinioFileManager

class TestMinioManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """初始化测试配置"""
        # cls.BUCKET_NAME = "test-bucket"
        cls.BUCKET_NAME = "test-bucket-" + str(int(time.time()))  # 使用唯一桶名
        cls.OBJECT_NAME = "test-file.txt"
        cls.TEST_CONTENT = b"MinIO Unit Test Content"

        # 使用测试 MinIO 配置（建议通过环境变量配置）
        cls.manager = MinioFileManager(
            endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "Q3AM3UQ867SPQQA43P2F"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG"),
            secure=False
        )

        # 确保网络连通性（可选地）
        try:
            cls.manager.list_buckets()  # 测试连接
        except Exception as e:
            raise unittest.SkipTest(f"MinIO connection failed: {str(e)}")

        # 确保测试桶不存在
        if cls.manager.bucket_exists(cls.BUCKET_NAME):
            cls.manager.empty_bucket(cls.BUCKET_NAME)
            cls.manager.remove_bucket(cls.BUCKET_NAME)

    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        if cls.manager.bucket_exists(cls.BUCKET_NAME):
            cls.manager.empty_bucket(cls.BUCKET_NAME)
            cls.manager.remove_bucket(cls.BUCKET_NAME)

    def setUp(self):
        """每个测试前的准备"""
        # 创建临时文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(self.TEST_CONTENT)
        self.temp_file.close()

    def tearDown(self):
        """每个测试后的清理"""
        # 删除临时文件
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

        # 清理可能创建的测试对象
        if self.manager.bucket_exists(self.BUCKET_NAME):
            objects = self.manager.list_objects(self.BUCKET_NAME)
            for obj in objects:
                self.manager.delete_object(self.BUCKET_NAME, obj)

    # ========== Bucket Tests ==========
    def test_create_bucket(self):
        """测试创建存储桶"""
        # 首次创建应成功
        self.assertTrue(self.manager.create_bucket(self.BUCKET_NAME))
        self.assertTrue(self.manager.bucket_exists(self.BUCKET_NAME))

        # 再次创建应失败
        self.assertFalse(self.manager.create_bucket(self.BUCKET_NAME))

    def test_remove_bucket(self):
        """测试删除存储桶"""
        self.manager.create_bucket(self.BUCKET_NAME)
        self.assertTrue(self.manager.remove_bucket(self.BUCKET_NAME))
        self.assertFalse(self.manager.bucket_exists(self.BUCKET_NAME))

        # 删除不存在的桶应失败
        self.assertFalse(self.manager.remove_bucket("non-existent-bucket"))

    def test_list_buckets(self):
        """测试列出存储桶"""
        self.manager.create_bucket(self.BUCKET_NAME)
        buckets = self.manager.list_buckets()
        self.assertIsInstance(buckets, list)
        self.assertIn(self.BUCKET_NAME, buckets)

    def test_empty_bucket(self):
        """测试清空存储桶"""
        self.manager.create_bucket(self.BUCKET_NAME)
        self.manager.upload_file(self.BUCKET_NAME, self.OBJECT_NAME, self.temp_file.name)

        self.assertTrue(self.manager.empty_bucket(self.BUCKET_NAME))
        self.assertEqual(self.manager.list_objects(self.BUCKET_NAME), [])

    # ========== Object Tests ==========
    def test_upload_download_file(self):
        """测试文件上传下载"""
        self.manager.create_bucket(self.BUCKET_NAME)

        # 上传文件
        self.assertTrue(
            self.manager.upload_file(
                self.BUCKET_NAME,
                self.OBJECT_NAME,
                self.temp_file.name
            )
        )

        # 下载文件
        download_path = self.temp_file.name + ".download"
        self.assertTrue(
            self.manager.download_file(
                self.BUCKET_NAME,
                self.OBJECT_NAME,
                download_path
            )
        )

        # 验证内容
        with open(download_path, "rb") as f:
            self.assertEqual(f.read(), self.TEST_CONTENT)

        os.unlink(download_path)

    def test_upload_download_bytes(self):
        """测试字节数据上传下载"""
        self.manager.create_bucket(self.BUCKET_NAME)

        # 上传字节数据
        test_data = b"Test binary data"
        self.assertTrue(
            self.manager.upload_bytes(
                self.BUCKET_NAME,
                "binary.data",
                test_data
            )
        )

        # 下载字节数据
        downloaded = self.manager.download_bytes(self.BUCKET_NAME, "binary.data")
        self.assertEqual(downloaded, test_data)

    def test_list_objects(self):
        """测试列出对象"""
        self.manager.create_bucket(self.BUCKET_NAME)

        # 上传多个文件
        files = ["file1.txt", "dir/file2.txt", "image.jpg"]
        for f in files:
            self.manager.upload_file(self.BUCKET_NAME, f, self.temp_file.name)

        # 验证列表
        objects = self.manager.list_objects(self.BUCKET_NAME)
        self.assertEqual(set(objects), set(files))

        # 测试前缀过滤
        prefixed = self.manager.list_objects(self.BUCKET_NAME, prefix="dir/")
        self.assertEqual(prefixed, ["dir/file2.txt"])

    def test_object_exists(self):
        """测试对象存在检查"""
        self.manager.create_bucket(self.BUCKET_NAME)
        self.manager.upload_file(self.BUCKET_NAME, self.OBJECT_NAME, self.temp_file.name)

        self.assertTrue(self.manager.object_exists(self.BUCKET_NAME, self.OBJECT_NAME))
        self.assertFalse(self.manager.object_exists(self.BUCKET_NAME, "non-existent-file"))

    def test_get_object_size(self):
        """测试获取对象大小"""
        self.manager.create_bucket(self.BUCKET_NAME)
        self.manager.upload_file(self.BUCKET_NAME, self.OBJECT_NAME, self.temp_file.name)

        size = self.manager.get_object_size(self.BUCKET_NAME, self.OBJECT_NAME)
        self.assertEqual(size, len(self.TEST_CONTENT))

        # 不存在的对象应返回None
        self.assertIsNone(self.manager.get_object_size(self.BUCKET_NAME, "non-existent-file"))

    def test_delete_object(self):
        """测试删除对象"""
        self.manager.create_bucket(self.BUCKET_NAME)
        self.manager.upload_file(self.BUCKET_NAME, self.OBJECT_NAME, self.temp_file.name)

        # 删除前应存在
        self.assertTrue(self.manager.object_exists(self.BUCKET_NAME, self.OBJECT_NAME))

        # 删除操作
        self.assertTrue(self.manager.delete_object(self.BUCKET_NAME, self.OBJECT_NAME))
        self.assertFalse(self.manager.object_exists(self.BUCKET_NAME, self.OBJECT_NAME))

        # 删除不存在的对象应失败，删除不存在对象可能返回True（符合S3规范）
        self.assertFalse(self.manager.delete_object(self.BUCKET_NAME, "non-existent-file"))

    def test_copy_object(self):
        """测试复制对象"""
        self.manager.create_bucket(self.BUCKET_NAME)
        self.manager.upload_file(self.BUCKET_NAME, self.OBJECT_NAME, self.temp_file.name)

        # 复制到新对象
        new_object = "copied-file.txt"
        self.assertTrue(
            self.manager.copy_object(
                self.BUCKET_NAME,
                self.OBJECT_NAME,
                self.BUCKET_NAME,
                new_object
            )
        )

        # 验证复制结果
        self.assertTrue(self.manager.object_exists(self.BUCKET_NAME, new_object))
        original_size = self.manager.get_object_size(self.BUCKET_NAME, self.OBJECT_NAME)
        copied_size = self.manager.get_object_size(self.BUCKET_NAME, new_object)
        self.assertEqual(original_size, copied_size)

    # ========== URL Tests ==========
    def test_presigned_url(self):
        """测试预签名URL"""
        self.manager.create_bucket(self.BUCKET_NAME)
        self.manager.upload_file(self.BUCKET_NAME, self.OBJECT_NAME, self.temp_file.name)

        # 生成预签名URL
        url = self.manager.generate_presigned_url(self.BUCKET_NAME, self.OBJECT_NAME)
        # 预签名URL不验证对象存在性，移除None检查
        # url = self.manager.generate_presigned_url(self.BUCKET_NAME, "non-existent-file")
        self.assertIsNotNone(url)
        self.assertIn(self.BUCKET_NAME, url)
        self.assertIn(self.OBJECT_NAME, url)

        # 不存在的对象应返回None
        self.assertIsNone(
            self.manager.generate_presigned_url(self.BUCKET_NAME, "non-existent-file")
        )

    def test_presigned_put_url(self):
        """测试预签名上传URL"""
        self.manager.create_bucket(self.BUCKET_NAME)

        url = self.manager.generate_presigned_put_url(self.BUCKET_NAME, "upload-target.txt")
        self.assertIsNotNone(url)
        self.assertIn(self.BUCKET_NAME, url)
        self.assertIn("upload-target.txt", url)

    # ========== File Integrity Tests ==========
    def test_file_integrity(self):
        """测试文件完整性验证"""
        self.manager.create_bucket(self.BUCKET_NAME)
        self.manager.upload_file(self.BUCKET_NAME, self.OBJECT_NAME, self.temp_file.name)

        # 相同文件应验证通过
        self.assertTrue(
            self.manager.verify_file_integrity(
                self.BUCKET_NAME,
                self.OBJECT_NAME,
                self.temp_file.name
            )
        )

        # 创建不同内容的文件
        different_file = tempfile.NamedTemporaryFile(delete=False)
        different_file.write(b"Different content")
        different_file.close()

        # 应验证失败
        self.assertFalse(
            self.manager.verify_file_integrity(
                self.BUCKET_NAME,
                self.OBJECT_NAME,
                different_file.name
            )
        )

        os.unlink(different_file.name)

if __name__ == '__main__':
    unittest.main()
