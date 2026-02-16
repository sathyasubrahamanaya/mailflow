from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Contact, User
from app.database import get_session
from app.middleware.auth_middleware import get_current_user
from fastapi.responses import JSONResponse
from typing import Optional
router = APIRouter(prefix="/contacts", tags=["Contacts"])

class ContactCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None # type: ignore

class ContactList(BaseModel):
    contacts:list[Contact]

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    db_contact = Contact(
        user_id=current_user.id, #type: ignore
        name=contact.name,
        email=contact.email,
        phone=contact.phone  # type: ignore
    )
    session.add(db_contact)
    await session.commit()
    await session.refresh(db_contact)
    return JSONResponse({"Message":"success","Data":db_contact.model_dump(),"ErrorCode":0})

@router.get("/get")
async def get_contacts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Contact).where(Contact.user_id == current_user.id)) #type: ignore
    contacts:list[Contact]=result.scalars().all() #type: ignore
    contactlist = ContactList(contacts=contacts) 
    return JSONResponse({"Message":"success","Data":contactlist.model_dump(),"ErrorCode":0})

@router.get("/search")
async def search_contacts(
    query: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Contact).where(
            Contact.user_id == current_user.id, # type: ignore
            Contact.name.contains(query) | Contact.email.contains(query) # type: ignore
        )
    )
    contacts:list[Contact]=result.scalars().all() # type: ignore
    contactlist = ContactList(contacts=contacts)
    return JSONResponse({"Message":"success","Data":contactlist.model_dump(),"ErrorCode":0})
