from app.schemas.user_schema import UserCreate, UserResponse, User,LoginRequest
from app.db.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.security import hash_password, decode_access_token, create_access_token,verify_password
from app.routes.deps import check_role

user_router = APIRouter()

@user_router.post("/create-user")
def create_user(req: UserCreate, db: Session = Depends(get_db)):

    try:
        #checking if user already exists
        user = db.query(User).filter(User.email == req.email).first()
        if user:
            raise HTTPException(status_code=400, detail="User already exists")

        #hashing password
        print("hashing password")
        hashed_password = hash_password(req.password)
        print("creating token")
        token = create_access_token({"sub": req.email})
        print("creating user2") 
        new_user = User(
            username=req.username,
            email=req.email,
            hashed_password=hashed_password,
            role=req.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"status":"success", "message": "User created successfully", "token": token,"username": new_user.username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    try:
        #checking if user exists
        user = db.query(User).filter(User.email == req.email).first()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid email or password")
        #checking if password is correct
        if not verify_password(req.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid email or password")
       
        #creating token
        token = create_access_token({"sub": user.email})
        return {"status":"success", "message": "User logged in successfully", "token": token,"username": user.username}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) 
 
@user_router.put("/update-user")
def update_user(req: UserCreate,current_user: User = Depends(check_role("agent")), db: Session = Depends(get_db)):
    try: 
        #checking if user exists
        user = db.query(User).filter(User.email == req.email).first()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")
         
        # print(user)
        #updating user
        user.username = req.username 
        user.email = req.email
        user.hashed_password = hash_password(req.password)
        user.role = req.role
        db.commit()
        db.refresh(user)
         
        return {"status":"success", "message": "User updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
 
@user_router.get("/get-users")
def get_users(current_user: User = Depends(check_role("agent")), db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        return {"status":"success", "message": "Users retrieved successfully", "users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

#deleting user using id 
@user_router.delete("/delete-user")
def delete_user(user_id: int, current_user: User = Depends(check_role("admin")), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")
        db.delete(user) 
        db.commit()
        return {"status":"success", "message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


