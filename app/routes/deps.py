from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user_schema import User, UserLoginRequest
import os
import dotenv
dotenv.load_dotenv() 

# This tells FastAPI to look for a "Bearer <token>" in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")
# print(oauth2_scheme.tokenUrl) 
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print("JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))
        print("JWT_ALGORITHM:", os.getenv("JWT_ALGORITHM"))
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
        email = payload.get("sub")
        
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
 

def check_role(required_role: str):
    # This is the actual function FastAPI will run
    def role_verifier(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Required: {required_role}. Your role: {current_user.role}"
            )
        return current_user
    
    return role_verifier 