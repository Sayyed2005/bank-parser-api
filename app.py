from fastapi import FastAPI, UploadFile, File, Form
import shutil
from extractor import extract_transactions

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Bank Parser API Running"}


@app.post("/extract")
async def extract(
    file: UploadFile = File(...),
    password: str | None = Form(None)
):

    path = "temp.pdf"

    # save uploaded file
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:

        # send password to extractor
        data = extract_transactions(path, password)

        return {"transactions": data}

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
