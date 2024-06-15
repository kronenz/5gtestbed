from typing import List, Union
from elasticsearch import Elasticsearch, helpers
import subprocess
# from pymongo import MongoClient
from datetime import datetime, timedelta
from pydantic import BaseModel
import time
import sys
import traceback
import json

def save_print_to_file(data, filename="twamp_output.txt") :
    with open(filename, "a") as file :
        print(data, file=file)

def connection(source, target) :
    
    # srcIP -> tarIp 측정해라 명령어
    twping_cmd = ['sudo', 'docker', 'run', '--net', "host", '--rm', "dariomader/twampy", "sender", target, '-c', '2', '-j']

    try : 
        # 측정 명령어 실행시 출력을 twping_output 변수에 저장
        twping_output = subprocess.check_output(twping_cmd, stderr=subprocess.STDOUT, text=True)
    # 오류발생시 오류내용 반환
    except subprocess.CalledProcessError as e:
        print( {"result" : False, "msg" : e.output})
        with open("twamp_output.txt", "a") as file :
            file.write(traceback.format_exc() + "\n")
        exit(1)
    except Exception as e : 
        print({"result" : False, "msg" : e})
        with open("twamp_output.txt", "a") as file :
            file.write(traceback.format_exc() + "\n")
        exit(1)
    
    #측정시간
    save_print_to_file(twping_output, 'twamp_output.txt')
    print(twping_output)
    jsonFormattedData=json.loads('['+twping_output.split('[')[1])
    print(jsonFormattedData)
    save_print_to_file(jsonFormattedData, 'twamp_output.txt')
    timestamp = datetime.utcnow().isoformat()
    #출력을 1줄 단위로 잘라서 listing

    # 측정 결과 저장할 dictionary
    paramResults = ['direction', 'min', 'max', 'avg', 'jitter', 'loss']
    indexResult = ['round-trip time', 'send time', 'reflect time', 'reflector processing time', 'two-way jitter', 
                  'send jitter', 'reflect jitter', 'two-way loss', 'send loss', 'reflect loss']
    
    upload_res=[]
    document = {
        'timestamp': timestamp,
        'source': source,
        'destination': target,
    }
    # elk에 넣을 데이터를 json 형식으로 저장
    for data in jsonFormattedData: 
        if data['direction']=='roundtrip': 
            time_name=indexResult[0]
            jitter_name=indexResult[4]
            loss_name=indexResult[7]
        elif data['direction']=='outbound':
            time_name=indexResult[1]
            jitter_name=indexResult[5]
            loss_name=indexResult[8]
        else:
            time_name=indexResult[2]
            jitter_name=indexResult[6]
            loss_name=indexResult[9]
        document[time_name]=[float(data['min']),float(data['avg']), float(data['max'])]
        document[jitter_name]=float(data['jitter']) 
        document[loss_name]=float(data['loss']) 
    save_print_to_file(document, 'twamp_output.txt')
 
    print(document)
    # elk 접속정보
    es=Elasticsearch("http://10.214.6.10:9200")
    # elk Collection 정보
    es_index = 'stack_repository'
    # elk에 insert
    save_print_to_file("ElK insert try", "twamp_output.txt")
    try :
        index_result = es.index(index=es_index, document=document)
        save_print_to_file("ELK insert success", "twamp_output.txt")
        if index_result['result'] == 'created':
            print('Document indexed successfully.', timestamp)
            # 모든 과정을 오류없이 작동하면 측정결과를 반환
            res = {"result" : True, "msg" : document}

        else:
            # insert 실패시 오류 반환
            print('Failed to index document.')
            res = {"result" : False, "msg" : "Failed to index document."}
    except : 
        save_print_to_file("ELK insert fail", "twamp_output.txt")
        res = {"result" : False, "msg" : "Failed to index document."}
        
        # insert 결과 확인
    return res




source = sys.argv[1]
target = sys.argv[2]
period = int(sys.argv[3])
duration = int(sys.argv[4])
interval = int(sys.argv[5])

# 측정 시작 시간 저장
start_time = time.time() * 1000  # 현재 시간을 milliseconds로 변환
total_count = 0  # 총 측정 횟수 초기화

while True:
    save_print_to_file("Time stamp : " + datetime.utcnow().isoformat() ,"twamp_output.txt")
    current_time = time.time() * 1000  # 현재 시간을 milliseconds로 얻음
    elapsed_time = current_time - start_time  # 경과 시간 계산
    save_print_to_file("current time : " + str(current_time) ,"twamp_output.txt")
    save_print_to_file("elapsed time : " + str(elapsed_time) ,"twamp_output.txt")


  # 20분이 지났는지 확인
    if elapsed_time >= duration * 1000:
        save_print_to_file("wait duration", "twamp_output.txt")
        if elapsed_time >= period * 1000: #1시간 지남
            # 측정 시작 시간 갱신
            save_print_to_file("wait period", "twamp_output.txt")
            start_time = time.time() * 1000
            # 경과 시간 초기화
            elapsed_time = 0 

        time.sleep(1)

    ## 측정 interval 마다
    
    ## 측정하고 

    save_print_to_file("┌────────────────────────────────────────────────────────────┐\n", "twamp_output.txt")
    output = "Another " + str(total_count) + "th " +  "measurement has started\n"
    total_count += 1
    save_print_to_file(output, "twamp_output.txt")
    try :
        try :
            connection_res = connection(source, target)  # 함수 실행
            res = json.dumps(connection_res)
            time.sleep(interval)
        except Exception as e :
            res = traceback.format_exc()
        try :
            with open("twamp_output.txt", "a") as file :
                file.write(res)
                file.write("\n")
        except Exception as e :
            with open("twamp_output.txt", "a") as file :
                file.write("Exception while write log\n")
                file.write(traceback.format_exc() + "\n")
    except Exception as e :
        with open("twamp_output.txt", "a") as file :
            file.write(traceback.format_exc() + "\n")
    save_print_to_file("\n└────────────────────────────────────────────────────────────┘", "twamp_output.txt")
     
     ## 슬립
    time.sleep(interval)

exit(1)
