from fastapi import APIRouter
from starlette import status


router = APIRouter(tags=['auth'], prefix='/auth')


@router.get('/google/login/')
async def google_login():
    pass


@router.get('/google/callback/', status_code=status.HTTP_200_OK)
async def google_callback():
    pass


@router.post('/logout')
async def logout():
    pass
