# Imports 
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_sqlalchemy import db

from typing import Optional, List

from passlib.context import CryptContext
from jose import JWTError, jwt

import models
import schemas
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
import os

# Loding .env file
load_dotenv('.env')

# extracting data from .env
SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])

pwd_context = CryptContext(schemes = ['bcrypt'], deprecated='auto')

#creating hash password 
def get_password_hash(password):
    return pwd_context.hash(password)

#verify password (returns True or False)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# creating access token for doctor
def create_access_token(data: dict, 
                        expires_delta : Optional[timedelta]=None):
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else :
        expire = datetime.utcnow() + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    
    data.update({"exp":expire})
    
    access_token = jwt.encode(data, SECRET_KEY, algorithm= ALGORITHM)
    return access_token


# getting user based on email
def get_user(db : Session, email : str):
    return db.query(models.Doctor).filter(models.Doctor.email == email).first()

# authenticating user 
def authenticate_user(db : Session, email : str, password : str):
    user = get_user(db, email)
    if not user :
        return False
    if not verify_password(password, user.password):
        return False
    return user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')
# decoding token and getting user 
async def get_current_user(token : str = Depends(oauth2_scheme)):
    
    credential_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail= "Your token is Invalid",
        headers= {'WWW-Authenticate' :'Bearer'}
    )
    try :
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email : str = payload.get('email')
        if not email :
            raise credential_exception
        
        token_data = schemas.TokenData(username= email)
    except JWTError :
         raise credential_exception
     
    user = get_user(db.session, email= token_data.username)
    
    if not user :
        raise credential_exception
    return user

async def get_current_active_user(current_user : models.Doctor = Depends(get_current_user)):
    return current_user 
     