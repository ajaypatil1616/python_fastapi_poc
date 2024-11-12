#Imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DB url 
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:1234@localhost:5432/fastapi'

# creating engine with db url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#making session
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind= engine)

#creating Base for models
Base = declarative_base()

# Sets up a context manager using the yield keyword
#this creates a database session (db) using SessionLocal and yields it to the caller. After 
# the execution within the context is completed, the finally block ensures that the 
# session is closed.
# In short connection to DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally :
        db.close()