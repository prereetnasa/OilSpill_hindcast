from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import requests
from hindcast import run_hindcast

TEAM1_DETECT_URL = "https://brown-stored-endangered-univ.trycloudflare.com/detect"


app = FastAPI(
    title="Team 2 Hindcast API",
    description="Oil spill source trajectory and corridor service"
)


@app.get("/")
def home():
    return {
        "status": "running",
        "service": "Team 2 Hindcast API"
    }


@app.post("/hindcast")
def hindcast(request: dict):
    return run_hindcast(request)

@app.post("/process")
def process(
    file: UploadFile = File(...),
    incident_id: str = Form(...)
):
    try:
        # Read the uploaded image
        image_data = file.file.read()

        # Send image to Team 1
        response = requests.post(
            TEAM1_DETECT_URL,
            files={
                "file": (
                    file.filename,
                    image_data,
                    file.content_type or "image/tiff"
                )
            },
            data={
                "incident_id": incident_id
            },
            timeout=180
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Team 1 /detect failed: {response.text}"
            )

        detection_result = response.json()

        # Send Team 1 result to our hindcast model
        hindcast_result = run_hindcast(detection_result)

        return {
            "incident_id": incident_id,
            "detection": detection_result,
            "hindcast": hindcast_result
        }

    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Could not connect to Team 1: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )