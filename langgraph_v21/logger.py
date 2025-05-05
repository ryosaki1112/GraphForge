import json, datetime, pathlib
def log(event:str,payload:dict,logfile:pathlib.Path):
    payload['event']=event
    payload['ts']=datetime.datetime.utcnow().isoformat()
    logfile.parent.mkdir(parents=True,exist_ok=True)
    with logfile.open("a",encoding="utf-8") as f:
        f.write(json.dumps(payload,ensure_ascii=False)+"\n")
