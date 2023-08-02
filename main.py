from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security.http import HTTPBearer, HTTPBasicCredentials
import uvicorn
import os
import multiprocessing
import subprocess

# Load env vars
if os.environ.get("TOKENS", "dev") == "dev":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path=".env")

TOKENS = os.environ.get("TOKENS", "").split(";")

tasks_queue = multiprocessing.Queue()
tasks_process = None

def execTasks(tasks_queue):
   while True:
      if not tasks_queue.empty():
        command = tasks_queue.get()
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
          

def createTaskProcess():
  global tasks_process
  if tasks_process is None:
    tasks_process = multiprocessing.Process(target=execTasks, args=(tasks_queue,))
    tasks_process.start()
    #tasks_process.join()

app = FastAPI()
auth = HTTPBearer()

def allowAuthenticated(authorization: HTTPBasicCredentials = Depends(auth)):
  token = authorization.credentials
  if not token in TOKENS:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail="A valid token is needed")

@app.post("/compose/update", dependencies=[Depends(allowAuthenticated)])
def pull(dir: str = None):
    if dir is None:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                          detail="A dir is needded")
    
    if " " in dir:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                          detail="A proper dir is needded")
                          
    tasks_queue.put("cd " + dir + " && docker-compose pull && docker-compose up -d")

    createTaskProcess()
    
    return dir

if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)


    