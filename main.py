from fastapi import FastAPI, Request
from urllib.parse import quote, unquote
from starlette.responses import RedirectResponse
import redis
import hashlib
import uvicorn


host_ = 'http://example.com:8000'

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)

def unique_8_letter_hash(input_string):
    md5_hash = hashlib.md5(input_string.encode()).hexdigest()
    short_hash = md5_hash[:8].upper()
    return short_hash

app = FastAPI()


@app.get("/api/push/{path_param:path}")    
def push_url(request: Request, path_param: str):
    if not is_valid_url(path_param):
        raise HTTPException(status_code=400, detail="Invalid URL")
    full_url_str = str(request.url)
    split_url = full_url_str.split(f"{host_}/api/push/")[1]
    split_url = quote(split_url)
    short_url = unique_8_letter_hash(split_url)
    if not r.get(split_url):
        r.set(short_url,split_url)
    return {"message": f"{host_}/{short_url}"}

@app.get("/api/pop/{path_param:path}")    
def get_url(request: Request, path_param: str):
    if not is_valid_url(path_param):
        raise HTTPException(status_code=400, detail="Invalid URL")
    full_url_str = str(request.url)
    short_url = full_url_str.split(f"{host_}/api/pop/{host_}/")[1]
    link_restoration = r.get(short_url)
    if link_restoration:
        link_restoration = link_restoration.decode('utf-8')
        return {"message": unquote(link_restoration)}
    else:
        return {"message": "None"}

@app.get("/{path_param:path}")    
def get_url(request: Request):
    full_url_str = str(request.url)
    split_url = full_url_str.split(f"{host_}/")[1]
    link_restoration = r.get(split_url)
    if link_restoration:
        link_restoration = unquote(link_restoration.decode('utf-8'))
        return RedirectResponse(url=link_restoration)
    else:
        return {"message": "None"}

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
