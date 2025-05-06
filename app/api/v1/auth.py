from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.auth.auth import authenticate_user
from app.auth.auth import create_access_token, hash_password
from app.models.users import Users

router = APIRouter()

@router.post("/register/")
async def register(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(Users).filter(Users.username == username).first()
    if existing_user:
        return {"message": "User already exists"}
    hashed_password = hash_password(password)
    role = "Admin" if username.lower() == "jami" else "User"
    new_user = Users(username=username, hashed_password=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    
    return {"message": "User registered successfully"}

@router.post("/token/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = authenticate_user(db, form_data.username, form_data.password) 

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=60) 
    )

    return {"access_token": access_token, "token_type": "bearer"}
