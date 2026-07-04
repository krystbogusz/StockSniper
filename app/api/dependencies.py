import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from app.core.config import settings

security_basic = HTTPBasic()
security_bearer = HTTPBearer()


async def verify_basic(credentials: HTTPBasicCredentials = Depends(security_basic)):
    correct_username = secrets.compare_digest(
        credentials.username, settings.api_username
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.api_password
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


async def verify_bearer(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
):
    if credentials.credentials != settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
