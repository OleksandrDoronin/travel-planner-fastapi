from auth.routers import auth, user
from fastapi import FastAPI


app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
