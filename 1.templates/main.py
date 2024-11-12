from fastapi import FastAPI, Request, Form

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.mount("/static",StaticFiles(directory = 'static'), name = 'static')
templates = Jinja2Templates(directory ='templates')


@app.get("/", response_class = HTMLResponse)
async def home(request : Request):
    return templates.TemplateResponse("index.html", {'request':request})


@app.post('/submit', response_class = HTMLResponse)
async def submit(request : Request,
    first: str = Form(...),
    last: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    repassword: str = Form(...),
    mobile: str = Form(...),
    gender: str = Form(...)
                 ):
    data = {
        'first' :first,
        'last' :last,
        'email' :email,
        'password' :password,
        'repassword' :repassword,
        'mobile' :mobile,
        'gender' :gender,
    }
    return templates.TemplateResponse('submit.html', {'request':request, 'data':data})