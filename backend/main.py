from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import logging
import uvicorn
import os
import datetime
from dotenv import load_dotenv
import base64
from requests.auth import HTTPBasicAuth

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MeetingDetails(BaseModel):
    topic: str
    start_time: str
    duration: int
    access_token: str  # Adjust field name if needed

import requests
import os

def get_access_token():
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    account_id = os.getenv("ACCOUNT_ID")
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    token_url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"
    # Make the POST request to get the access token
    response = requests.post(
        token_url,
        auth=HTTPBasicAuth(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("access_token")
    else:
        logging.error(f"Failed to get access token: {response.text}")
        raise HTTPException(status_code=401, detail="Failed to get access token")


@app.post("/schedule-meeting/")
async def schedule_meeting(details: MeetingDetails):

    try:
        headers = {
            'Authorization': f'Bearer {details.access_token}',
            'Content-Type': 'application/json'
        }
        meeting_data = {
            "topic": details.topic,
            "type": 2,  # Scheduled meeting
            "start_time": details.start_time,
            "duration": details.duration,
            "timezone": "UTC"
        }

        response = requests.post('https://api.zoom.us/v2/users/me/meetings', headers=headers, json=meeting_data)
        response_json = response.json()
        if response.status_code == 201:
            return response_json
        else:
            return {"error": response_json}
    except Exception as e:
        logging.error(f"Error scheduling meeting: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/schedule-weekly-meeting/")
async def schedule_weekly_meeting(request: Request):
    # Check the Authorization header for CRON_SECRET
    if request.headers.get('Authorization') != f'Bearer {os.getenv("CRON_SECRET")}':
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    access_token = get_access_token()
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Set the start time to 5:05 PM UTC on the next Friday
    next_meeting_time = (datetime.datetime.utcnow() + datetime.timedelta(days=(4 - datetime.datetime.utcnow().weekday()) % 7)).replace(hour=17, minute=5, second=0, microsecond=0)
    logging.info(next_meeting_time.isoformat())
    meeting_data = {
        "topic": "Weekly Webinar",
        "type": 2,  # Scheduled meeting
        "start_time": next_meeting_time.isoformat(),
        "duration": 30,
        "timezone": "UTC",
        "agenda": "Weekly project updates",
        "password": "123456",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "mute_upon_entry": True,
            "watermark": True
        }
    }

    try:
        response = requests.post("https://api.zoom.us/v2/users/me/meetings", headers=headers, json=meeting_data)

        response_json = response.json()

        logging.info(response_json)

        if response.status_code == 201:
            print("Error debug 1.")
            return {"message": "Weekly meeting scheduled successfully", "meeting": response_json}
        else:
            print("Error debug 2.")
            return {"error": response_json}
    except Exception as e:
        logging.error(f"Error scheduling weekly meeting: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
