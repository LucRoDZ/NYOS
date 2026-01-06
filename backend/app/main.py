from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import engine, Base
from app.routers import chat, data

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NYOS APR",
    description="Pharmaceutical Quality Analysis Assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(data.router)


@app.get("/")
async def root():
    return {"status": "NYOS APR API Running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
