import base64
import os
import re

import requests
from openai import OpenAI

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv

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

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
if not OPENAI_KEY:
    raise Exception("API_KEY not found in .env file")


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
        print(image)
        # Extract base64 data from the data URL
        image_data_base64 = re.sub('^data:image/.+;base64,', '', image.image_data)
        # print(image_data_base64)
        # Decode the base64 string to make sure it's valid
        decoded_image = base64.b64decode(image_data_base64)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_KEY}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What’s in this image?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{decoded_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # If successful, return a simple confirmation message
        return {"message": "This is a pothole!"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image data: {str(e)}")
