from fastapi import HTTPException

def response(status, code, resp):
    if status == True:
        return resp
    
    else:
        raise HTTPException(status_code=code, detail=resp)