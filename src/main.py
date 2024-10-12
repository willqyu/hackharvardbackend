from src.openai_wrapper import OpenAIClient

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from databases import Database


app = FastAPI()

client = OpenAIClient()

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

# Database URL (replace with your actual database URL)
DATABASE_URL = "postgresql://myuser:mypassword@localhost/mydb"

# Create a Database instance
database = Database(DATABASE_URL)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def read_root():
    return {"Us": "Winners"}


class ImageData(BaseModel):
    image_data: str


class ReportData(BaseModel):
    type: str
    comment: str
    image: str
    latitude: float
    longitude: float
    time_created: str = None
    last_updated: str = None
    resolved: bool = False


@app.post("/api/describe-image")
async def describe_image(image: ImageData):
    if not image.image_data.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="Invalid image data URL")

    res = client.send_camera(image.image_data)

    feature, comment = res.split("|")
    feature = feature.strip()
    comment = comment.strip()

    # If successful, return a simple confirmation message
    return {
        "feature": feature,
        "message": comment
    }

    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=f"Error processing image data: {str(e)}")


class LocationData(BaseModel):
    latitude: float
    longitude: float


locations = []


@app.post("/api/save-location")
async def save_location(location: LocationData):
    try:
        locations.append(location)
        return {"message": "Location saved successfully",
                "location": location}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error saving location: {str(e)}")


@app.get("api/locations")
async def get_locations():
    return locations
