from pydantic import BaseModel

class PostBase(BaseModel):
    content : str
    title :str
    
    #Config  is used to configure the behavior of the data model. In this case, 
    # orm_mode = True is set to enable the data model to work in ORM mode, allowing it 
    # to be used with SQLAlchemy's ORM features.
    class Config:
        orm_mode = True

class CreatePost(PostBase):
    class Config:
        orm_mode = True