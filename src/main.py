import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.employee import employee_router
from src.routers.employer import employer_router
from src.routers.user import user_router

app = FastAPI(title="Google Solution Challenge Backend", version="0.2.0-dev12")

origins = os.environ["CORS_ORIGINS"].split(",")


"""class TimingMiddleware(BaseHTTPMiddleware):
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

        return response"""


"""app.add_middleware(TimingMiddleware)"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""@app.middleware("http")
async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as http_exception:
        return http_exception
    except Exception as e:
        return Response(
            content="Internal Server Error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )"""

app.include_router(user_router)
app.include_router(employee_router)
app.include_router(employer_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=80, reload=True)
