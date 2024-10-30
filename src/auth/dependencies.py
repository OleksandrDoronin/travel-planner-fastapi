from fastapi import Depends, HTTPException
from models.users import User
from auth.security import oauth2_scheme
from auth.services.auth import AuthService


async def get_current_user(
    token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends()
) -> User:
    user = await auth_service.get_current_user_from_token(token)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return user
