from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
from modules.auth.schema.schemas import LoginRequest, Token
from modules.database import students_db, SECRET_KEY, ALGORITHM

router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: LoginRequest):
    # Cari user (Simple search)
    user = next((u for u in students_db if u["email"] == form_data.username), None)
    
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = create_access_token(data={"sub": user["email"], "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}