from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routes import upload, dashboard, chat
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agile Digital Scrum Master API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["Upload"])
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(chat.router, tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to Agile Digital Scrum Master API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
