import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_URL_TEST: str = os.getenv("DATABASE_URL_TEST")
    
    JWT_PRIVATE_KEY: str = os.getenv(
        "JWT_PRIVATE_KEY",
        "-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgbiXM7P+xUoUiD1VE\nEKiF/rL2k4wItN8Qmf8gMWD6PHuhRANCAAQIqB/QUUEFEZW/vPpMz46HjCsAOZ8H\nnTqLjf8FOXMuSm74RAm96OFb31d/3FBTjlO0SHf5xN3faXD/ZrULt6df\n-----END PRIVATE KEY-----",
    )
    
    PASSWORD_SALT: str = os.getenv("PASSWORD_SALT", "$2b$12$HkooQn9UnD.vYbWtsaxro.")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAX_DEPLOYMENT_ATTEMPTS: int = 3
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_USERNAME = os.getenv("REDIS_USERNAME", "")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_DATABASE = int(os.getenv("REDIS_DATABASE", 0))
    REDIS_PROTOCOL = os.getenv("REDIS_PROTOCOL", "redis")
    REDIS_SSL_PARAMS = os.getenv("REDIS_SSL_PARAMS", "")
    
settings = Settings()
