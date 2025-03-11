from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.future import select
from app.models import User, AdminUser
from app.database import get_session
from app.middleware.auth_middleware import APIKeySecurity
from fastapi.responses import JSONResponse
router = APIRouter(prefix="/admin", tags=["Admin"])

class AdminCreate(BaseModel):
    user_id: int

@router.post("/admins", status_code=status.HTTP_201_CREATED)
async def create_admin(
    admin_data: AdminCreate,
    current_user: User = Depends(APIKeySecurity()),
    session=Depends(get_session)
):
    if current_user.is_admin:
        return JSONResponse({"Message":"you are already admin","Data":{},"ErrorCode":1})
    user = await session.get(User, admin_data.user_id)
    if not user:
         return JSONResponse({"Message":"user not found","Data":{},"ErrorCode":1})
    
    admin = AdminUser(user_id=user.id)
    statement = select(User).where(User.id == admin_data.user_id)
    results = await session.execute(statement)
    current_user_from_db:User = results.scalars().first()
    print("current___user",current_user_from_db)
    if not current_user_from_db:
        return JSONResponse({"Message":"user not found","Data":{},"ErrorCode":1})
    current_user_from_db.is_admin = True
    session.add(current_user_from_db)
    await session.commit()
    await session.refresh(current_user_from_db)
    

    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return JSONResponse({"Message":"Admin added","Data":admin.model_dump(),"ErrorCode":0})
@router.get("/users")
async def get_all_users(
    current_user: User = Depends(APIKeySecurity()),
    session=Depends(get_session)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action"
        )
    result = await session.execute(select(User))
    users = result.scalars().all()
    return {"users": users}




