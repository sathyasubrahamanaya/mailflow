from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.future import select
from app.models import User
from app.api.auth.schemas import UserCreate
from app.database import get_session
from app.config import settings
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class LoginCreate(BaseModel):
    username:str
    password:str

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_user_by_username(session, username: str):
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_email(session, email: str):
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def authenticate_user(session, username: str, password: str)-> User:
    user = await get_user_by_username(session, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, session=Depends(get_session)):
    if await get_user_by_username(session, user.username):
       return JSONResponse({"Message":"username already registred","Data":{},"ErrorCode":1})
    existing_user = await get_user_by_email(session,user.email)
    if existing_user:
        return JSONResponse({"Message":"email already exists","Data":{},"ErrorCode":1})
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return JSONResponse({"Message":"success","Data":{"user_id":db_user.id},"ErrorCode":0})


@router.post("/login")
async def login(credentials:LoginCreate, session=Depends(get_session)):
    user = await authenticate_user(session, credentials.username, credentials.password)
    if not user:
       return JSONResponse({"Message":"incorrect username or password","Data": {},"ErrorCode":1})
    else:
      return JSONResponse({"Message":"suceess","Data": {"api_key": user.api_key},"ErrorCode":0})

