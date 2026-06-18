from fastapi import FastAPI

from app.api.routes.auth import router as auth_router


app = FastAPI(title="LexIA API", version="0.1.0")
app.include_router(auth_router, prefix="/api/v1")
