from datetime import timedelta

from config import settings
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import Token
from security import create_access_token
from services.auth import AuthService


router = APIRouter(prefix='/login', tags=['login'])


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(AuthService),
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username, 'other_custom_data': [1, 2, 3, 4]},
        expires_delta=access_token_expires,
    )
    return {'access_token': access_token, 'token_type': 'bearer'}
