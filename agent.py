from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import subprocess


import logging
logging.basicConfig(level=logging.INFO)  # INFO 레벨의 로그부터 출력합니다.
logger = logging.getLogger(__name__)  # 현재 모듈의 로거를 가져옵니


app = FastAPI()

############################################### agent_id-api ########################################################3
class measurement_param(BaseModel):
    source_name : str
    dest_name : str
    startTime : str
    endTime : str
    period : str
    duration : str
    interval : str

@app.get("/status_check")
def agent_status_check() :
    return {"status": "success", "message": "good"}

# Probe 측정개시
@app.post("/run_agent", tags=["agent"])
async def run_agent( param : measurement_param):
    print(param)
    twamp_cmd = ['nohup', 'python', 'twamp_measurement.py', param.source_name, param.dest_name, '0', '0']

    run_cmd = subprocess.Popen(twamp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return {"res" : True, "message" : "Measurement Start:", "PID" : run_cmd.pid}
# /run_agent를 종료시키는 api
# @app.post("/stop_agent", tags=["agent"])
# async def stop_agent(data: measurement_param):
#     print(data)

