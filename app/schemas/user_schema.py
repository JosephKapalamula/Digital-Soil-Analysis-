from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    # The role determines if they can input data or just view reports
    role: str = Field(default="agent", description="Role: agent, admin, or analyst")
class LoginRequest(BaseModel): 
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel): 
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True # Allows Pydantic to read SQLAlchemy models
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # Never store raw passwords! Use bcrypt in the backend before saving.
    hashed_password = Column(String, nullable=False)
    
    # Authorization roles
    role = Column(String, default="agent") # agent, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


