from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from sqlmodel import select
from app.models import SupportQuery, Feedback, User
from app.database import get_session
from app.middleware.auth_middleware import APIKeySecurity
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter(prefix="/support", tags=["Support"])

class SupportQueryCreate(BaseModel):
    query_text: str

class FeedbackCreate(BaseModel):
    rating: int
    comment: str
class FeedbackResponseIndividual(BaseModel):
    user_name:str
    user_id:int
    rating:int
    comment:str|None
    comment_time:str
class FeedbackResponse(BaseModel):
    feedbacks:list[FeedbackResponseIndividual]

class QueryReply(BaseModel):
    query_id:int
    reply:str

class SupportQueryResponse(BaseModel):
    id: int
    user_id: int
    query_text: str
    status: str
    reply:str|None
    reply_time:str|None =None

class AllQueries(BaseModel):
    queries:list[SupportQueryResponse]

@router.post("/queries/create", status_code=status.HTTP_201_CREATED)
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
    return JSONResponse({"Message": "Query submitted", "Data":{},"ErrorCode":0})

@router.post("/queries/get")
async def get_all_queries(
    current_user:User= Depends(APIKeySecurity()),
    session=Depends(get_session)):
    if current_user.is_admin:
        statement = select(SupportQuery)
    else:
        statement = select(SupportQuery).where(SupportQuery.user_id==current_user.id)
    result = await session.execute(statement)
    queries:list[SupportQuery] = result.scalars().all()
    if len(queries)>0:
        queries.reverse()
        all_queries = [SupportQueryResponse(id=query.id,user_id=query.user_id,query_text=query.query_text,status = query.status,reply=query.reply,reply_time=datetime.strftime(query.created_at,format= "%#d %b %I:%M%p")) for query in queries]
        print("queries-->",all_queries)
        return JSONResponse({"Message": "success", "Data":AllQueries(queries=all_queries).model_dump(),"ErrorCode":0})
    else:
        return JSONResponse({"Message": "success", "Data":"No queries found","ErrorCode":0})
    


@router.post("/queries/reply")
async def reply_query(
    query_request:QueryReply,
    current_user:User= Depends(APIKeySecurity()),
    session=Depends(get_session)):

    query_stmt = select(SupportQuery).where(SupportQuery.id == query_request.query_id)
    query_result = await session.execute(query_stmt)
    query:SupportQuery|None = query_result.scalar_one_or_none()
    if query and current_user.is_admin:
        query.reply = query_request.reply
        query.status="closed"
        query.created_at = datetime.now()
        session.add(query)
        await session.commit()
        await session.refresh(query)
        return JSONResponse({"Message": "query reply success", "Data":{},"ErrorCode":0})
    else:
        return JSONResponse({"Message": "no such query found or you don't have permission to reply", "Data":{},"ErrorCode":1})


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: User = Depends(APIKeySecurity()),
    session=Depends(get_session)
):
    new_feedback = Feedback(
        user_id=current_user.id,
        user_name= current_user.name,
        rating=feedback.rating,
        comment=feedback.comment
    )
    session.add(new_feedback)
    await session.commit()
    await session.refresh(new_feedback)
    return JSONResponse({"Message": "Feedback submitted", "Data":{},"ErrorCode":0})


@router.post("/feedback/get_all")
async def get_all_feedback(
    current_user: User = Depends(APIKeySecurity()),
    session=Depends(get_session)
):
    statement = select(Feedback)
    result = await session.execute(statement)
    feedbacks:list[Feedback]|None = result.scalars().all()
    if feedbacks and len(feedbacks)>0:
        feedbackresponse = [FeedbackResponseIndividual(user_name=feedback.user_name,user_id=feedback.user_id,rating=feedback.rating,comment=feedback.comment,comment_time=datetime.strftime(feedback.created_at,"%d/%m/%Y %H:%M:%S")) for feedback in feedbacks]
        return JSONResponse({"Message":"success","Data":FeedbackResponse(feedbacks=feedbackresponse).model_dump(),"ErrorCode":0})
    
    else:
        return JSONResponse({"Message":"No feedbacks found","Data":{},"ErrorCode":0})

