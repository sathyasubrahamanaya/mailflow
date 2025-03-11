from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.future import select
from app.models import SupportQuery, Feedback, User
from app.database import get_session
from app.middleware.auth_middleware import APIKeySecurity

router = APIRouter(prefix="/support", tags=["Support"])

class SupportQueryCreate(BaseModel):
    query_text: str

class FeedbackCreate(BaseModel):
    rating: int
    comment: str

@router.post("/queries", status_code=status.HTTP_201_CREATED)
async def create_support_query(
    query: SupportQueryCreate,
    current_user: User = Depends(APIKeySecurity()),
    session=Depends(get_session)
):
    new_query = SupportQuery(
        user_id=current_user.id,
        query_text=query.query_text
    )
    session.add(new_query)
    await session.commit()
    await session.refresh(new_query)
    return {"message": "Support query created", "query_id": new_query.id}

@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: User = Depends(APIKeySecurity()),
    session=Depends(get_session)
):
    new_feedback = Feedback(
        user_id=current_user.id,
        rating=feedback.rating,
        comment=feedback.comment
    )
    session.add(new_feedback)
    await session.commit()
    await session.refresh(new_feedback)
    return {"message": "Feedback submitted", "feedback_id": new_feedback.id}