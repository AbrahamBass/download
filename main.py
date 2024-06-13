import io
import time
import uvicorn
from typing import Dict
from pytube import YouTube
from collections import defaultdict
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, status, Request, Response


app = FastAPI()

rate_limit_records: defaultdict = defaultdict(float)


@app.middleware("http")
async def ratelimiter_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    if current_time - rate_limit_records[client_ip] < 1:
        return Response(content="Rate limit exceeded", status_code=429)
    rate_limit_records[client_ip] = current_time
    return await call_next(request)


@app.get("/download/")
async def download(url: str):
    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        stream = io.BytesIO()
        video.stream_to_buffer(stream)
        stream.seek(0)
        return StreamingResponse(stream, media_type='video/mp4')
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred and the request could not be processed."
        )


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info")
