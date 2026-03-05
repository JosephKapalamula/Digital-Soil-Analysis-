import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEE_SERVICE_ACCOUNT_JSON= os.getenv("GEE_SERVICE_ACCOUNT_JSON")
    DATABASE_URL = os.getenv("DATABASE_URL")

settings = Settings()