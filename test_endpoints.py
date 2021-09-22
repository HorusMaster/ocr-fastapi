from os import path
from fastapi import responses
import shutil
import io
from fastapi.testclient import TestClient
from app.main import UPLOAD_DIR, app, BASE_DIR, get_settings
from PIL import Image, ImageChops
client = TestClient(app)

def test_get_home():
    response = client.get("/")
    assert response.text != "<h1>Hello world</h1>"
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']

def test_invalid_file_upload_error():
    response = client.post("/")
    assert response.status_code == 422
    assert "application/json" in response.headers['content-type']

def test_echo_upload():
    img_saved_path = BASE_DIR / "images"
    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None
        response = client.post("/img-echo/", files={"file": open(path, 'rb')})
        if img is None:
            assert response.status_code == 400
        else:
            # Returning a valid image
            assert response.status_code == 200
            r_stream = io.BytesIO(response.content)
            echo_img = Image.open(r_stream)
            difference = ImageChops.difference(echo_img, img).getbbox()
            assert difference is None
    # time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)


def test_prediction_upload():
    img_saved_path = BASE_DIR / "images"
    settings = get_settings()
    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None
        response = client.post("/",
            files={"file": open(path, 'rb')},
            headers={"Authorization": f"JWT {settings.app_auth_token}"}
        )
        if img is None:
            assert response.status_code == 400
        else:
            # Returning a valid image
            assert response.status_code == 200
            data = response.json()
            assert len(data.keys()) == 2