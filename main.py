from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import aqi

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(aqi.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return "hello from team gamma"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=300,
        access_log=False
    )
