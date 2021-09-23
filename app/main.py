import pathlib
import io
import uuid
import jwt
import base64
from functools import lru_cache
from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Depends,
    Request,
    File,
    UploadFile,
    Body
)
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from PIL import Image
import pytesseract


class Settings(BaseSettings):
    app_auth_token: str
    debug: bool = False
    echo_active: bool = False
    app_auth_token_prod: str = None
    skip_auth: bool = False

    class Config:
        env_file = ".env"


@lru_cache(8)
def get_settings():
    return Settings()


settings = get_settings()
DEBUG = settings.debug


BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"


app = FastAPI()

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)  # http GET -> JSON
def home_view(request: Request, settings: Settings = Depends(get_settings)):
    print(settings.debug)
    return templates.TemplateResponse("home.html", {"request": request, "abc": 123})


def verify_auth(authorization=Header(None), settings: Settings = Depends(get_settings)):
    """
    Authorization: Bearer <token>
    {"authorization": "Bearer <token>"}
    """
    if settings.debug and settings.skip_auth:
        return
    if authorization is None:
        raise HTTPException(detail="Invalid endpoint", status_code=401)
    label, token = authorization.split()
    try:
        jwt.decode(token, settings.app_auth_token, algorithms=["HS256"])
    except:
        raise HTTPException(detail="Invalid endpoint", status_code=401)


@app.post("/")
def prediction_view(file: str = Body(...), authorization=Header(None), settings: Settings = Depends(get_settings)):
    verify_auth(authorization, settings)
    print(file)
    bytes_str = io.BytesIO(base64.b64decode(file))
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid image", status_code=400)
    preds = pytesseract.image_to_string(img)
    predictions = [x for x in preds.split("\n")]
    return {"results": predictions, "original": preds}


@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(file: UploadFile = File(...)):
    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid image", status_code=400)
    fname = pathlib.Path(file.filename)
    fext = fname.suffix  # .jpg
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    img.save(dest)
    return dest
