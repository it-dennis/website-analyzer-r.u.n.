from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routes import router

load_dotenv()

import os

app = FastAPI(title="R.U.N. API", version="1.0.0")

_origins_env = os.getenv("ALLOWED_ORIGINS", "")
_extra_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
_allowed_origins = ["http://localhost:5173", "http://localhost:3000", "http://localhost"] + _extra_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
