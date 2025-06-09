from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from config import init_db
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from dotenv import load_dotenv
from sqlalchemy import text
from config import get_db


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.commit()
        return {"db": "Healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

