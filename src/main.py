from fastapi import FastAPI

from src.auth.routers import auth, user
from src.middleware import setup_middleware


app = FastAPI(title='Travel planner API')
setup_middleware(app)


app.include_router(user.router, prefix='/api/v1')
app.include_router(auth.router, prefix='/api/v1')
