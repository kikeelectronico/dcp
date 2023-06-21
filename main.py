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
        task = tasks_queue.get()
        print(task)
        if "dapi-pull" in task:
          image = task.split(":")[1]
          command = "docker pull " + image
          process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
          process.wait()
          print(process.returncode)

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
                          
    tasks_queue.put("dapi-pull:" + image)

    global tasks_process
    if tasks_process is None:
      tasks_process = multiprocessing.Process(target=execTasks, args=(tasks_queue,))
      tasks_process.start()
      #tasks_process.join()
    
    return image

if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)


    