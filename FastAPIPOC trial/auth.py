from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_sqlalchemy import  db

from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

import models
from schemas import TokenData
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
import os

load_dotenv('.env')

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# verifying password return True/False
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# creating  hashed password
def get_password_hash(password):
    return pwd_context.hash(password)

#creating access token (returns encoded token)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    data_copy = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    data_copy.update({"exp": expire})
    
    encoded_jwt = jwt.encode(data_copy, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# getting user based on string
def get_user(db: Session, email: str):
    return db.query(models.Doctor).filter(models.Doctor.email == email).first()


# authenticating user 
def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={'WWW-Authenticate': "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(username=email)
        
    except JWTError:
        raise credentials_exception
    
    user = get_user(db.session, email=token_data.username)
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.Doctor = Depends(get_current_user)):
    return current_user
