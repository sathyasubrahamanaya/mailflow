from typing import Annotated
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_session
from app.models import User

# 1. Define the security scheme for OpenAPI
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    api_key: Annotated[str, Security(api_key_header)],
    session: Annotated[AsyncSession, Depends(get_session)]
) -> User:
    # 2. Check if the header exists (APIKeyHeader handles auto_error if desired)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required"
        )

    # 3. Query the database using the injected session
    result = await session.execute(
        select(User).where(User.api_key == api_key) # type: ignore
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid API key"
        )
    
    return user
