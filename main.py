from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security.http import HTTPBearer, HTTPBasicCredentials
import os

# Load env vars
if os.environ.get("TOKENS", "dev") == "dev":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path=".env")

TOKENS = os.environ.get("TOKENS", "").split(";")

app = FastAPI()
auth = HTTPBearer()

def allowAuthenticated(authorization: HTTPBasicCredentials = Depends(auth)):
    token = authorization.credentials
    if not token in TOKENS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="A valid token is needed")

@app.post("/pull", dependencies=[Depends(allowAuthenticated)])
def pull(image: str = None):
    if image is None:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                          detail="An image is needded")
    
    return image
    