from fastapi import Request, HTTPException, status
from sqlalchemy.future import select
from app.database import get_session
from app.models import User

class APIKeySecurity:
    async def __call__(self, request: Request):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="X-API-Key header is required"
            )
        # Use an async loop to get the session
        async for session in get_session():
            result = await session.execute(
                select(User).where(User.api_key == api_key)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )
            return user
