from fastapi import FastAPI, UploadFile
import shutil
from extractor import extract_transactions

app = FastAPI()

@app.get("/")
def home():
    return {"message":"Bank Parser API Running"}

@app.post("/extract")
async def extract(file: UploadFile):

    path="temp.pdf"

    with open(path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)

    data = extract_transactions(path)

    return {"transactions":data}