from auth.routers import google_auth
from fastapi import FastAPI
from logging_config import setup_logging
from middleware import setup_middleware


setup_logging()

app = FastAPI(title='Travel planner API')
setup_middleware(app)


app.include_router(google_auth.router, prefix='/api/v1')
