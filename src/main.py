import base64
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Define allowed origins (you can specify the actual domains you want to allow)
origins = [
    "http://localhost:3000",  # Example for local frontend running on port 3000
    "http://localhost:8000",  # Example for another local service
    "https://your-frontend-domain.com",  # Example for your actual frontend domain
    "*",  # Allow all domains (use this cautiously in production)
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specified origins
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def read_root():
    return {"Us": "Winners"}


class ImageData(BaseModel):
    image_data: str


@app.post("/api/describe-image")
async def describe_image(image: ImageData):
    if not image.image_data.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="Invalid image data URL")

    try:
        # Extract base64 data from the data URL
        image_data_base64 = re.sub('^data:image/.+;base64,', '', image.image_data)

        # Decode the base64 string to make sure it's valid
        _ = base64.b64decode(image_data_base64)

        # If successful, return a simple confirmation message
        return {"message": "This is a pothole!"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image data: {str(e)}")
