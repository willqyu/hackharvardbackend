import base64
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from databases import Database

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

    try:
        # Extract base64 data from the data URL
        image_data_base64 = re.sub(
            '^data:image/.+;base64,', '', image.image_data)

        # Decode the base64 string to make sure it's valid
        _ = base64.b64decode(image_data_base64)

        # If successful, return a simple confirmation message
        return {"message": "This is a pothole!"}

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error processing image data: {str(e)}")


@app.post("/api/submit-report")
async def submit__report(report: ReportData):
    try:
        query = """
        INSERT INTO infrastructure_reports (type, comment, image, latitude, longitude, timestamp)
        VALUES (:type, :comment, :image, :latitude, :longitude, :timestamp)
        """
        values = {
            "type": report.type,
            "comment": report.comment,
            "image": report.image,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "timestamp": report.timestamp,
        }
        await database.execute(query=query, values=values)

        return {"message": "Report created successfully!"}

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating report: {str(e)}")
