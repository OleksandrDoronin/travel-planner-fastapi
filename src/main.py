from fastapi import FastAPI
from auth.routers import user
from auth.routers import auth


app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
