from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Contact, User
from app.database import get_session
from app.middleware.auth_middleware import APIKeySecurity
from fastapi.responses import JSONResponse
router = APIRouter(prefix="/contacts", tags=["Contacts"])

class ContactCreate(BaseModel):
    name: str
    email: str
    phone: str = None

class ContactList(BaseModel):
    contacts:list[Contact]

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    current_user: User = Depends(APIKeySecurity()),
    session: AsyncSession = Depends(get_session)
):
    db_contact = Contact(
        user_id=current_user.id,
        name=contact.name,
        email=contact.email,
        phone=contact.phone
    )
    session.add(db_contact)
    await session.commit()
    await session.refresh(db_contact)
    return JSONResponse({"Message":"success","Data":db_contact.model_dump(),"ErrorCode":0})

@router.get("/get")
async def get_contacts(
    current_user: User = Depends(APIKeySecurity()),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Contact).where(Contact.user_id == current_user.id))
    contacts:list[Contact]=result.scalars().all()
    contactlist = ContactList(contacts=contacts)
    return JSONResponse({"Message":"success","Data":contactlist.model_dump(),"ErrorCode":0})

@router.get("/search")
async def search_contacts(
    query: str,
    current_user: User = Depends(APIKeySecurity()),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Contact).where(
            Contact.user_id == current_user.id,
            Contact.name.contains(query) | Contact.email.contains(query)
        )
    )
    contacts:list[Contact]=result.scalars().all()
    contactlist = ContactList(contacts=contacts)
    return JSONResponse({"Message":"success","Data":contactlist.model_dump(),"ErrorCode":0})
