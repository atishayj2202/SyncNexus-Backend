import os
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


app = FastAPI(title="Google Solution Challenge Backend", version="0.1.0")

origins = os.environ["CORS_ORIGINS"].split(",")


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        start_time = time.time()

        try:
            response = await call_next(request)
        except HTTPException as exc:
            response = exc

        end_time = time.time()
        process_time = end_time - start_time
        print(
            f"Request {request.method} {request.url} processed in {process_time:.5f} seconds"
        )

        return response


app.add_middleware(TimingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
