from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    minio_endpoint: str = "play.min.io:443"
    minio_access_key: str = "Q3AM3UQ867SPQQA43P2F"
    minio_secret_key: str = "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG"
    minio_bucket: str = "fastapi-bucket"
    minio_secure: bool = True

    class Config:
        env_file = ".env"

settings = Settings()