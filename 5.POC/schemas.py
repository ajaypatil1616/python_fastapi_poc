from pydantic import BaseModel, EmailStr, Field, validator, ValidationError, field_validator
from typing import List, Optional
from datetime import datetime, date
from fastapi import HTTPException,status
import re


class PatientBase(BaseModel):
    name : str = Field(None, min_length=1, max_length= 25, pattern= r'[a-zA-Z\s]')

class PatientCreate(PatientBase):    
    dob : date  = None
    email : Optional[EmailStr] = None
    phone_number : str = Field(None, pattern= r'^\+?1?\d{10}$') 
    disease : str = None
    doctor_id : int = 15
    is_active : bool = True
    
    @field_validator('dob', mode='before')
    def parse_dob(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                raise HTTPException(status_code =400,detail='use DD/MM/YYYY this format ')
        return value
    
   

class PatientAll(PatientCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DoctorBase(BaseModel):      
    name : str = Field(None, min_length=1, max_length= 25, pattern=r'[a-zA-Z\s]')
    
class DoctorCreate(DoctorBase):
    email : Optional[EmailStr] 
    specialization :str = None
    phone_number :str = Field(None, pattern= r'^\+?1?\d{10}$', description='phone number error') 
    password : str 
    
    @validator('password')
    def validate_password(cls, value):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*+=])[A-Za-z\d!@#$%^&*+=]{8,}$'
        if not re.match(pattern, value):
            raise ValueError('Password must be 8 long, include at least one uppercase, one lowercase ,one digit, and one special character.')
        return value


class DoctorResponse(DoctorBase):
    email : Optional[EmailStr] 
    specialization :str = None
    phone_number :str = Field(None, pattern= r'^\+?1?\d{10}$', description='phone number error') 
        
  
  
class DoctorAll(DoctorCreate):
    id : int = None
    
    created_at : datetime
    updated_at : datetime
    patients : List[PatientAll]
    
    class Config():
        from_attributes = True
        
    
class Token(BaseModel):
   access_token : str
   
   
class TokenData(BaseModel):
    username: Optional[str] = None
    
class EmailData(BaseModel):
    email : EmailStr 

class ResetPassword(BaseModel):
    email : EmailStr
    otp : int
    new_password : str
    
    @validator('new_password')
    def validate_password(cls, value):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*+=])[A-Za-z\d!@#$%^&*+=]{8,}$'
        if not re.match(pattern, value):
            raise ValueError('Password must be 8 long, include at least one uppercase, one lowercase ,one digit, and one special character.')
        return value