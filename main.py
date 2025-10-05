from sys import prefix
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import aqi, mail, newsletter
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()
scheduler = BackgroundScheduler()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(aqi.router, prefix="/api/v1")
app.include_router(mail.router, prefix="/api/v1")
app.include_router(newsletter.router, prefix="/api/v1")

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(
        aqi.schedule_bulk_aqi,
        "cron",
        minute="*"
    )
    if not scheduler.running:
        scheduler.start()
        print("✅ Scheduler started")

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()
    print("🛑 Scheduler stopped")

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
