from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request):
        authorization = request.headers.get('Authorization')
        if not authorization or 'Bearer' not in authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated'
            )

        try:
            scheme, token = authorization.split(' ')
            if scheme.lower() != 'bearer':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Invalid authentication credentials',
                )
            return HTTPAuthorizationCredentials(scheme=scheme, credentials=token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid authorization format',
            )


custom_bearer_scheme = CustomHTTPBearer()
