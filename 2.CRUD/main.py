from fastapi import FastAPI, Request, Form
from pydantic import BaseModel
app = FastAPI()


class PatientData(BaseModel):
    name:str
    age:int
    disease :str
    bill :float
    pincode : int
    
@app.get("/patient/{patient_name}")
def get_name(patient_name : str | int = None):
    return {"name": patient_name}

@app.post("/patient/{patient_id}")
def post_patient(patient_id :int,
                  name:str = Form(...),
                  age:int = Form(...),
                  disease :str = Form(...),
                  bill :float = Form(...),
                  pincode : int = Form(...),
                 ):
    data = PatientData(
        name = name,
        age = age,
        disease = disease,
        bill = bill,
        pincode = pincode,
    )
    
    
    return {"patient_id":patient_id,
            "name":data.name,
            "age":data.age,
            "disease":data.disease,
            "bill":data.bill,
            "pincode":data.pincode,
            }
    
@app.put("/update_patient/{patient_id}")
def update_patient(patient_id:int, data : PatientData):
    return {"patient_id":patient_id,
            "name":data.name,
            "age":data.age
            }

