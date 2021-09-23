
#Este sirve para poder extraer una imagen en el form data
# @app.post("/")
# async def prediction_view(file:UploadFile = File(...), authorization = Header(None), settings:Settings = Depends(get_settings)):
#     verify_auth(authorization, settings)
#     bytes_str = io.BytesIO(await file.read())
#     try:
#         img = Image.open(bytes_str)
#     except:
#         raise HTTPException(detail="Invalid image", status_code=400)
#     preds = pytesseract.image_to_string(img)
#     predictions = [x for x in preds.split("\n")]
#     return {"results": predictions, "original": preds}
