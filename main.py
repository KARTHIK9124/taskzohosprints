from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn
import threading

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

ACCESS_TOKEN = "1000.ea268fb040ca7857762b2c4b0d686dee.55d25ab701b7abee617e4f5130910f32"
TEAM_ID = "60037147559"


token_lock = threading.Lock()

@app.get("/projects")
def get_projects():
    global ACCESS_TOKEN  
    url = f"https://sprintsapi.zoho.in/zsapi/team/{TEAM_ID}/projects/?action=data&index=1&range=10"
    headers = {"Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if "projectJObj" in data:
            projects = []
            for project_id, project_data in data["projectJObj"].items():
                project = {
                    "id": project_id,
                    "name": project_data[0],  
                    "status": project_data[8],  
                    "start_date": project_data[2],  
                    "end_date": project_data[3],  
                    "owner": data["userDisplayName"].get(project_data[5], "Unknown"),  
                    "group": project_data[11]  
                }
                projects.append(project)

            return {"projects": projects}

        return {"error": "No projects found or invalid response format"}
    
    return {"error": "Failed to fetch projects", "details": response.text}

REFRESH_TOKEN = "1000.74787776cb14d379ea773dc537ce351d.2ea067cb34afcc3f07c78ab12383da99"
CLIENT_ID = "1000.PS1UXMVCIM4L1JRGX3O7SXHZRZOG3X"
CLIENT_SECRET = "401ec19aad942b65a1083585e9611948bf7977447b"
REDIRECT_URI = "https://www.google.com"

@app.get("/refresh_token")
def refresh_token():
    global ACCESS_TOKEN 

    url = "https://accounts.zoho.in/oauth/v2/token"  
    data = {
        'refresh_token': REFRESH_TOKEN,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'refresh_token'
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        json_response = response.json()
        
        if "access_token" in json_response:
            new_access_token = json_response["access_token"]

            with token_lock:
                ACCESS_TOKEN = new_access_token  
            
            return {"access_token": ACCESS_TOKEN}
        else:
            return {"error": "Response did not contain access_token", "details": json_response}
    else:
        return {"error": "Failed to refresh access token", "status": response.status_code, "details": response.json()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)