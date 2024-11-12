# Import 
import models
import schemas
from models import *

from fastapi import FastAPI, requests, Form, HTTPException, Depends,status
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import JSONResponse, HTMLResponse

import os
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from auth2 import *
import schemas
from auth2 import get_current_active_user

import mailtrap_email
from random import randint

load_dotenv('.env')

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url = os.environ['DATABASE_URI'] )


# Create doctor     
@app.post("/doctor", response_model=schemas.DoctorResponse)
async def create_doctor(doctor_data: schemas.DoctorCreate):
    try:
        hashed_password = get_password_hash(doctor_data.password)
        doctor_data.password = hashed_password
        
        new_doctor = models.Doctor(**doctor_data.dict())
        db.session.add(new_doctor)
        db.session.commit()
        db.session.refresh(new_doctor)
        
        return new_doctor
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        db.session.close()  

## JWT Log in
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    
    user = authenticate_user(db.session, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"email": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, }

# get all doctors 
@app.get("/doctors")
async def get_all_doctors(
    current_user: models.Doctor = Depends(get_current_active_user)
):
    try:
        doctors_list = db.session.query(models.Doctor).all()
        return doctors_list
    except Exception as e:
        raise HTTPException(status_code= 400, detail=str(e))
    finally:
        db.session.close()

# get doctor by id 
@app.get('/doctor/{id}')
async def get_doctor_by_id(id : int,
                           current_user : models.Doctor = Depends(get_current_active_user)):
    
    try:
        doctor = db.session.query(models.Doctor).filter(models.Doctor.id == id).first()
        
        if not doctor :
            return {"ERROR" :"Doctor not FOund"}
        return doctor
    except Exception as e:
         raise HTTPException(status_code= 400, detail=str(e))
    finally:
        db.session.close()

     
# update the doctor 
@app.put('/doctor/{id}')
async def update_doctor(id : int,
                        updated_data : schemas.DoctorCreate,
                        current_user : models.Doctor = Depends(get_current_active_user)):
    try :
         doctor = db.session.query(models.Doctor).filter(models.Doctor.id == id).first()
        
         if doctor is None:
             return {"ERROR" : "Doctor not Found"}
        #  print(updated_data)
        #  print(type(updated_data))
         doctor.name = updated_data.name
         doctor.email = updated_data.email
         doctor.specialization = updated_data.specialization
         doctor.phone_number = updated_data.phone_number
         
         hashed_password = get_password_hash(updated_data.password)
         doctor.password = hashed_password
         
         db.session.commit()
         db.session.refresh(doctor)
         return doctor
    except Exception as e :
         raise HTTPException(status_code= 400, detail=str(e))
    finally:
        db.session.close()

# delete doctor 
@app.delete("/doctor/{id}")
def delete_doctor(id : int,
                  current_user :models.Doctor = Depends(get_current_active_user) ):
    try:
        doctor = db.session.query(models.Doctor).filter(models.Doctor.id == id ).first()
        if not doctor:
            raise HTTPException(status_code= 400, detail=f"doctor not FOund with id {id}")
        db.session.delete(doctor)
        db.session.commit()
        return {"SUCCESS":f"doctor with id {id} has been deleted"}
    except Exception as e:
        raise HTTPException(status_code= 400, detail=str(e))
    finally:
        db.session.close()

# patch the doctor 
@app.patch("/doctor/{id}", response_model= schemas.DoctorResponse)
def partial_updating_doctor(id : int,
                            updated_data : schemas.DoctorCreate,
                            current_user : models.Doctor = Depends(get_current_active_user)):
    try:
        doctor = db.session.query(models.Doctor).filter(models.Doctor.id == id).first()
        if not doctor :
            raise  HTTPException(status_code= 400, detail=f"no doctor found with id {id}")
    
        for key, value in updated_data.dict(exclude_unset= True).items():
            if hasattr(doctor, key):
                setattr(doctor, key,value)
        if updated_data.password :
            doctor.password = get_password_hash(updated_data.password)
        db.session.commit()
        db.session.refresh(doctor)     
        return doctor 
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code= 400, detail= str(e))
    finally:
        db.session.close()
    
# forgot password api
@app.post('/forgot-password/otp')
async def send_otp_email(email : schemas.EmailData):
    try:
        doctor = db.session.query(models.Doctor).filter(models.Doctor.email == email.email).first()
        if not doctor :
            raise HTTPException(status_code=400, detail=f"doctor with email {email.email} does not exists")
        
        otp = randint(100000,999999)    
   
        subject = 'reset password using OTP'
        body = f'you otp is {otp}'
    
        mailtrap_email.send_email(email.email, subject, body)
        
        otp_user = db.session.query(models.OTP).filter(models.OTP.email == email.email).first()
        if otp_user :
            otp_user.otp = otp
            db.session.commit()
            db.session.refresh(otp_user)
            return {"success": "OTP send to your email id"}
            
        otp_data = models.OTP(otp = otp, email = email.email)
        db.session.add(otp_data)
        db.session.commit()
        db.session.refresh(otp_data)
        return {"success": "OTP send to your email id"}
    except Exception as e :
        db.session.rollback()
        raise HTTPException(status_code= 400, detail=str(e))
    finally :
        db.session.close()

  
  
@app.post("/forgot-password/reset")
async def reset_password(data :schemas.ResetPassword):
    try:
        otp_obj = db.session.query(models.OTP).filter(models.OTP.email == data.email).first()
    
        if otp_obj is None:
            raise HTTPException(status_code= 400, detail=f"Your OTP is not generated please try again")
        if data.otp != otp_obj.otp:
            raise HTTPException(status_code=400, detail=f"your otp is incorrect")
        
        db.session.delete(otp_obj)
        db.session.commit()
        
        doctor_obj = db.session.query(models.Doctor).filter(models.Doctor.email == data.email).first()
        doctor_obj.password = get_password_hash(data.new_password)
        db.session.commit()
        return {"success": "YOur password updated successfully"}
    except Exception as e :
        db.session.rollback()
        raise HTTPException(status_code= 400, detail=str(e))
    finally :
        db.session.close()


## Patients apis
##

# Post patient 
@app.post("/patient", response_model=schemas.PatientCreate)
async def create_patient(patient_data: schemas.PatientCreate,
                         current_user : models.Doctor = Depends(get_current_active_user)):
    try:
              
        doctor_id = current_user.id
        new_patient = Patient(**patient_data.dict())
        
        new_patient_dict = new_patient.__dict__
        new_patient_dict['dob'] = new_patient.dob.strftime('%d/%m/%Y')
        
        new_patient_dict['doctor_id'] = doctor_id
        
        db.session.add(new_patient)
        db.session.commit() # which executes an SQL 
        db.session.refresh(new_patient)
        
        
        return new_patient_dict 
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.session.close()
        

# get all Patients
@app.get('/patients', response_model = List[schemas.PatientAll])
async def get_all_patients(current_user : models.Doctor = Depends(get_current_active_user)):
    try:
        doctor_id = current_user.id
        patients_all = db.session.query(models.Patient).filter(models.Patient.doctor_id == doctor_id,
                                                               models.Patient.is_active == True).all()
        
        return patients_all
    except Exception as e :
        raise HTTPException(status_code= 400, detail=str(e))
    finally:
        db.session.close()
        

# get patient by id
@app.get('/patient/{id}',response_model = schemas.PatientAll)
async def get_patient_by_id(id : int,
                            current_user : models.Doctor = Depends(get_current_active_user)):
    try:
        doctor_id = current_user.id
               
        patient = db.session.query(models.Patient).filter(models.Patient.id == id,
                                                          models.Patient.is_active == True).first()
        
        if not patient:
            raise HTTPException(status_code= 400, detail=f"id {id} not found")
        
        if doctor_id != patient.doctor_id :
            raise HTTPException(status_code= 400, detail=" you don't have access to  this patient")
        
        return patient
    except Exception as e:
        raise HTTPException(status_code= 400, detail= str(e))
    finally:
         db.session.close()

# PUT :update patient 
@app.put('/patient/{id}', response_model= schemas.PatientAll)
async def update_patient(id : int, updated_data : schemas.PatientCreate,
                         current_user : models.Doctor = Depends(get_current_active_user)):
    try :
        doctor_id = current_user.id
        
        patient = db.session.query(models.Patient).filter(models.Patient.id == id).first()
        
        if not patient:
            raise HTTPException(status_code=400, detail=f"patien with id {id} not found")
        if doctor_id != patient.doctor_id:
            raise HTTPException(status_code= 400, detail=f"you do not have access to this patient with id {id}")
        
        for field in updated_data.dict(exclude_unset= True):
            if hasattr(patient, field):
                setattr(patient, field, getattr(updated_data,field))
                
        patient.__dict__['doctor_id'] = doctor_id    
                   
        db.session.commit()
        db.session.refresh(patient)
        return patient
        
    except Exception as e :
        db.session.rollback()
        raise HTTPException(status_code= 404, detail=str(e))
    finally:
        db.session.close()

# delete patient 
@app.delete("/patient/{id}")
async def delete_patient(id : int,
                         current_user : models.Doctor = Depends(get_current_active_user)):
    try:
        doctor_id = current_user.id
        
        patient = db.session.query(models.Patient).filter(models.Patient.id == id).first()
        
        if not patient:
            raise HTTPException(status_code=400, detail= f"patient with id {id} is not found")
        if not (doctor_id == patient.doctor_id):
            raise HTTPException(status_code= 400, detail=f"you don't have access to delete this patient")
        
        db.session.delete(patient)
        db.session.commit()
        return {"success":f"patient with id {id} is deleted successfully"}
    except Exception as e :
        raise HTTPException(status_code=404, detail= str(e))
    finally:
        db.session.close()
        
# soft delete patient
@app.delete("/soft_delete/{id}")
async def soft_delete_patient(id : int,
                              current_user : models.Doctor = Depends(get_current_active_user)):
    try :
        patient = db.session.query(models.Patient).filter(models.Patient.id == id ).first()
        
        if not patient :
            raise HTTPException(status_code= 400, detail=f"NO patient found with id {id}")
        if patient.doctor_id != current_user.id :
            raise HTTPException(status_code= 400, detail=f"You do not have access to this patient")
        if patient.is_active == False :
            raise HTTPException(status_code= 400, detail= f"ALready is soft deleted")
        
        patient.is_active = False
        db.session.commit()
        db.session.refresh(patient)
        return {'sucess': f"patient with id {id} is now soft deleted"}
    except Exception as e :
        db.session.rollback()
        raise HTTPException(status_code= 400, detail= str(e))
    finally:
        db.session.close()

# soft delete reverse 
@app.delete("/reverse_soft_delete/{id}", response_model= schemas.PatientAll)
async def reverse_soft_delete(id : int,
                              current_user : models.Doctor = Depends(get_current_active_user)):
    try:
        patient = db.session.query(models.Patient).filter(models.Patient.id == id).first()
        if not patient :
            raise HTTPException(status_code= 400, detail= f"No patient found with id {id}")
        if not (current_user.id == patient.doctor_id):
            raise HTTPException(status_code= 400, detail= f"You do not have permision to this")
        if patient.is_active == True:
            raise HTTPException(status_code= 200, detail=f"the patient with id {id} is alreday active")
        
        patient.is_active = True
        db.session.commit()
        db.session.refresh(patient)
        return patient
    except Exception as e :
        db.session.rollback()
        raise HTTPException(status_code= 400 , detail= str(e))
    finally:
        db.session.close()
        
        
# patch : partially update
@app.patch("/patient/{id}", response_model= schemas.PatientAll)
async def partially_update_patient( update_patient_data :schemas.PatientCreate,
                                   id : int, 
                                   current_user : models.Doctor = Depends(get_current_active_user),
                                  ):
    try:
        doctor_id = current_user.id
        
        patient = db.session.query(models.Patient).filter(models.Patient.id == id).first()
        
        if not patient:
            raise HTTPException(status_code=400, detail= f"patient with id {id} is not found")
        if not (patient.doctor_id == doctor_id) :
            raise HTTPException(status_code=400, detail=f"you don't have access to PATCH this patient")
        
        for key,value in update_patient_data.dict(exclude_unset=True).items():
            if hasattr(patient, key):
                setattr(patient,key, value)
        
        db.session.commit()
        db.session.refresh(patient)
        return patient
    except Exception as e :
        raise HTTPException(status_code=404, detail= str(e))
    finally:
        db.session.close()

#ADD Patient to specific id
@app.post("/add_patient/{id}", response_model= schemas.PatientCreate)
async def create_patient_at_specific_id(id:int,
                                        patient_data : schemas.PatientCreate,
                                        current_user : models.Doctor = Depends(get_current_active_user)):
    
   try:
        patient = db.session.query(models.Patient).filter(models.Patient.id == id).first()
        if patient :
            raise HTTPException(status_code= 400, detail=f"patient with id :{id} already exists please find some other id")

        patient_data_dict = patient_data.dict()
        patient_data_dict['id'] = id
        patient_data_dict['doctor_id'] = current_user.id
        
        new_patient =  models.Patient(**patient_data_dict)
        db.session.add(new_patient)
        db.session.commit()
        db.session.refresh(new_patient)
        return new_patient
    
   except Exception as e:
       raise HTTPException(status_code= 400, detail= str(e))    
   finally :
       db.session.close()

# get patients under specific doctor
@app.get("/doctor/{id}/patients", response_model= List[schemas.PatientAll])
async def get_all_patients_under_specific_doctor(id : int,
                                                 current_user : models.Doctor = Depends(get_current_active_user)):
    try:
        doctor = db.session.query(models.Doctor).filter(models.Doctor.id == id).first()
        if not doctor :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"doctor not found with id {id}")
        return doctor.patients
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        db.session.close()
        
