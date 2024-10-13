from src.openai_wrapper import OpenAIClient

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from databases import Database
from typing import List

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
DATABASE_URL = "postgres://default:JOK5XYs4SlPe@ep-plain-morning-a43ixkme-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"

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


@app.post("/api/describe-image")
async def describe_image(image: ImageData):
    if not image.image_data.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="Invalid image data URL")

    res = client.send_camera(image.image_data)

    if "|" in res:
        feature, comment = res.split("|")
        feature = feature.strip()
        comment = comment.strip()

        # If successful, return a simple confirmation message
        return {
            "feature": feature,
            "message": comment
        }

    else:
        return {
            "feature": None,
            "message": res
        }

    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=f"Error processing image data: {str(e)}")


class ReportData(BaseModel):
    type: str
    comment: str
    image: str
    latitude: float
    longitude: float
    timestamp: float


class Incident(BaseModel):
    reports: List[int]
    latitude: float
    longitude: float
    time_created: float
    latest_updated: float


@app.post("/api/submit-report")
async def submit_report(report: ReportData):
    # try:

    # Insert into all_reports
    query = """
        INSERT INTO all_reports (type, comment, image, latitude, longitude, timestamp)
        VALUES (:type, :comment, :image, :latitude, :longitude, :timestamp)
        RETURNING id
    """
    values = {
        "type": report.type,
        "comment": report.comment,
        "image": report.image,
        "latitude": report.latitude,
        "longitude": report.longitude,
        "timestamp": report.timestamp,
    }
    report_id = await database.execute(query=query, values=values)

    # Check for nearby, pre-existing incidents (10 foot radius)
    radius = 10 / 5280 / 60  # Convert 10 feet to degrees (approximation)

    query = """
    SELECT id, reports, latitude, longitude FROM incidents
    WHERE ST_DWithin(
        ST_SetSRID(ST_MakePoint(longitude, latitude), 4326),
        ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326),
        :radius
    )
    """
    values = {
        "latitude": report.latitude,
        "longitude": report.longitude,
        "radius": radius * 1609.34  # Convert degrees to meters
    }
    incident = await database.fetch_one(query=query, values=values)

    if incident:
        # Update existing incident
        incident_id = incident["id"]
        reports = incident["reports"] + [report_id]
        avg_latitude = (
            incident["latitude"] * len(incident["reports"]) + report.latitude) / len(reports)
        avg_longitude = (
            incident["longitude"] * len(incident["reports"]) + report.longitude) / len(reports)
        query = """
        UPDATE incidents
        SET reports = :reports, latitude = :latitude, longitude = :longitude, latest_updated = :latest_updated
        WHERE id = :id
        """
        values = {
            "id": incident_id,
            "reports": reports,
            "latitude": avg_latitude,
            "longitude": avg_longitude,
            "latest_updated": report.timestamp
        }
        await database.execute(query=query, values=values)
    else:
        # Create new incident
        query = """
        INSERT INTO incidents (reports, latitude, longitude, time_created, latest_updated)
        VALUES (:reports, :latitude, :longitude, :time_created, :latest_updated)
        """
        values = {
            "reports": [report_id],
            "latitude": report.latitude,
            "longitude": report.longitude,
            "time_created": report.timestamp,
            "latest_updated": report.timestamp
        }
        await database.execute(query=query, values=values)

    return {"message": "Report created successfully!"}

    # except Exception as e:
    #     raise HTTPException(
    #         status_code=400, detail=f"Error creating report: {str(e)}")


@app.post("/api/get-letter")
async def get_letter(report: ReportData):

    letter = client.write_letter(
        issue=report.type,
        title="Representative",
        name="Ayanna Pressley"
    )
    subject, body = letter.split('\n', 1)

    return {
        "subject": subject,
        "message": body
    }


# Load tweets from the file
with open("./src/tweets.txt", "r", encoding="utf8") as file:
    tweets = file.read().split(" |\n")

# Create a counter to keep track of the current tweet index
tweet_index = 0
@app.get("/api/tweet")
async def get_next_tweet():
    global tweet_index
    tweet = tweets[tweet_index % len(tweets)]
    tweet_index += 1

    return {"tweet": tweet}


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
