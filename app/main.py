import pathlib
import io
import uuid
from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Request,
    File,
    UploadFile
    )
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
import pytesseract

BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"


app = FastAPI()

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
def home_view(request: Request):
    print(request)
    return templates.TemplateResponse("home.html", {"request": request, "abc": 123})

@app.post("/")
async def prediction_view(file:UploadFile = File(...)):
    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
         raise HTTPException(detail="Invalid image", status_code=400)
    preds = pytesseract.image_to_string(img)
    predictions = [x for x in preds.split("\n")]
    return {"results": predictions, "original": preds}


@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(file:UploadFile = File(...)):
    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
         raise HTTPException(detail="Invalid image", status_code=400)
    fname =  pathlib.Path(file.filename)
    fext = fname.suffix #.jpg
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    img.save(dest)
    return dest