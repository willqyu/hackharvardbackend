import base64
from typing import re

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Us": "Winners"}


class ImageData(BaseModel):
    image_data: str
@app.post("/api/describe-image")
async def describe_image(image: ImageData):
    if not image.data_url.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="Invalid image data URL")

    try:
        # Extract base64 data from the data URL
        image_data_base64 = re.sub('^data:image/.+;base64,', '', image.data_url)

        # Decode the base64 string to make sure it's valid
        _ = base64.b64decode(image_data_base64)

        # If successful, return a simple confirmation message
        return {"message": "This is a pothole!"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image data: {str(e)}")
