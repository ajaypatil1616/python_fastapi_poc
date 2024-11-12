# Imports 

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer, String, DateTime,Float, func, Date,ForeignKey,Boolean, BigInteger
from sqlalchemy.orm import relationship


#Base for models to extend
Base = declarative_base()


# doctors tables
class Doctor(Base):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index= True, nullable= False)
    email = Column(String, unique=True, nullable= False)
    specialization = Column(String, default='orthopedics', nullable= False)
    phone_number = Column(String, index=True, unique= True, nullable= False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone= True), default=func.now(), onupdate=func.now())
    password = Column(String)
    
    
    patients = relationship("Patient", backref='doctor')

# patients table
class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True, index= True, autoincrement=True)
    name = Column(String, index=True, nullable= False)    
    dob = Column(Date,nullable= False)
    email = Column(String, unique=True, index= True, nullable= False)
    phone_number = Column(String, unique= True,index= True, nullable= False)
    disease = Column(String, index= True, nullable= False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, server_default='TRUE')
    
    doctor_id = Column(Integer,ForeignKey('doctors.id'))

# otp table 
class OTP(Base):
    __tablename__ = 'otp'
    
    id = Column(Integer,primary_key=True, autoincrement= True )
    email = Column(String, index= True, unique= True)
    otp = Column(BigInteger, index= True)
