from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from fastapi import HTTPException

DATABASE_URL = settings.DATABASE_URL

# Only create engine if DATABASE_URL is available
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base = declarative_base()
    
    # Test database connection
    try:
        with engine.connect() as connection:
            print("🚀 Success! Supabase Database is reachable.")
    except Exception as e:
        print(f"❌ Database Connection Failed! Check your DATABASE_URL.")
        print(f"Error details: {e}")
else:
    print("⚠️  DATABASE_URL not set. Database features will be disabled.")
    engine = None
    SessionLocal = None
    Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="Database not available")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()