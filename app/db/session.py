from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
   
try:
    with engine.connect() as connection:
        print("🚀 Success! Supabase Database is reachable.")
except Exception as e:
    print(f"❌ Database Connection Failed! Check your DATABASE_URL.")
    print(f"Error details: {e}")

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()