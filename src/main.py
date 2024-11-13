from auth.routers import google_auth
from fastapi import FastAPI
from middleware import setup_middleware


app = FastAPI(title='Travel planner API')
setup_middleware(app)


app.include_router(google_auth.router, prefix='/api/v1')
