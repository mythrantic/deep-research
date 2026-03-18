from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
from urllib.parse import urlparse

try:
    import boto3
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

@dataclass
class StorageConfig:
    provider: str  # 'local', 's3'
    connection_string: str = None
    container_name: str = None
    local_path: str = None
    credentials: dict = None
    uri: str = None  # Add support for direct URIs
    
    def __post_init__(self):
        """Parse URI if provided"""
        if self.uri:
            parsed = urlparse(self.uri)
            if parsed.scheme == 'file':
                self.provider = 'local'
                self.local_path = parsed.path
            elif parsed.scheme == 's3':
                self.provider = 's3'
                self.credentials = {'bucket': parsed.netloc}

class StorageProvider(ABC):
    @abstractmethod
    def get_uri(self) -> str:
        """Return the URI for LanceDB to connect to"""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Test if the connection is valid"""
        pass

class LocalStorageProvider(StorageProvider):
    def __init__(self, config: StorageConfig):
        self.path = config.local_path or "lancedb_data"
        os.makedirs(self.path, exist_ok=True)

    def get_uri(self) -> str:
        return self.path
    
    def validate_connection(self) -> bool:
        return os.path.exists(self.path)
    
class S3StorageProvider(StorageProvider):
    def __init__(self, config: StorageConfig):
        if not S3_AVAILABLE:
            raise ImportError(
                "AWS dependencies not installed. Install with: pip install boto3"
            )
        import boto3
        self.bucket = config.credentials.get('bucket')
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.credentials.get('access_key'),
            aws_secret_access_key=config.credentials.get('secret_key')
        )

    def get_uri(self) -> str:
        return f"s3://{self.bucket}"
    
    def validate_connection(self) -> bool:
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
            return True
        except Exception:
            return False

def create_storage_provider(config: StorageConfig) -> StorageProvider:
    providers = {
        'local': LocalStorageProvider,
        's3': S3StorageProvider
    }
    provider_class = providers.get(config.provider.lower())
    if not provider_class:
        raise ValueError(f"Unsupported storage provider: {config.provider}")
    return provider_class(config)