# Importing 
from fastapi import FastAPI, Request, Form
from typing import List

#Depends
#Declare a FastAPI dependency. It takes a single "dependable" callable (like a function). 
#Don't call it directly, FastAPI will call it for you.
from fastapi import HTTPException, Depends 
from sqlalchemy.orm import Session # session fo DB
from starlette import status
from fastapi import APIRouter
import models
import schemas   
from database import get_db
from database import SessionLocal, engine


# table creating in DB
models.Base.metadata.create_all(bind = engine)

app = FastAPI()

# When you define your endpoint and specify the response model, FastAPI will 
# automatically serialize your data according to the Pydantic model you defined.
# Get all the post
@app.get("/posts", response_model = List[schemas.CreatePost])
async def get_all_posts(db : Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# post a  post 
@app.post('/posts', status_code = status.HTTP_201_CREATED, response_model = List[schemas.CreatePost])
async def create_post(post : schemas.CreatePost, db : Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return [new_post]

# get by id 
@app.get("/posts/{id}", response_model = schemas.CreatePost, status_code = status.HTTP_200_OK)
async def get_post_by_id(db : Session = Depends(get_db), id : int = 1):
    
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None :
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"The id: {id} you requested for does not exist")
    return post

@app.delete("/posts/{id}", status_code = status.HTTP_200_OK)
def delete_post(id : int , db : Session = Depends(get_db) ):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    
    if post is None:
         raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST ,detail = f'the id {id} does not exists')
    db.delete(post)
    db.commit()
    return {"message": "Item deleted successfully"}

@app.put('/posts/{id}', response_model = schemas.CreatePost)
def update_post(updated_post_data : schemas.PostBase, id : int, db : Session = Depends(get_db) ):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    
    if post is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail =f'{id} id does not exists')
    
    post.title = updated_post_data.title
    post.content = updated_post_data.content
    # print(updated_post_data)
    # print(type(updated_post_data))
    
    db.commit()
    return  