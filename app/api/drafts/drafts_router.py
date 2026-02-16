from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.models import User
from app.middleware.auth_middleware import get_current_user
from app.services.vector_service import vector_db
from app.services.transcription_v2 import transcribe_audio # type: ignore
from app.schemas import APIResponse, SearchResultData, ListResultData, DraftItem
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/drafts", tags=["Drafts"])

# Input Schema for Saving
class DraftSchema(BaseModel):
    subject: str
    body: str
    to_email: Optional[str] = None
    recipient_name: Optional[str] = None
    draft_id: Optional[str] = None

# --- 1. LIST ALL DRAFTS ---
@router.get("/all", response_model=APIResponse[ListResultData[DraftItem]])
async def list_drafts(
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Get all drafts for the current user.
    """
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID not found")

        drafts = await vector_db.list_all_drafts(user_id=current_user.id, limit=limit)
        
        return APIResponse(
            Message="success",
            Data=ListResultData(results=drafts),
            ErrorCode=0
        )
    except Exception as e:
        return JSONResponse({"Message": str(e), "ErrorCode": 1}, status_code=500)

# --- 2. SAVE DRAFT ---
@router.post("/save", response_model=APIResponse)
async def save_draft(
    draft: DraftSchema,
    current_user: User = Depends(get_current_user)
):
    """
    Saves or updates a draft in Qdrant.
    """
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID not found")

        # Convert Pydantic model to dict
        draft_data = draft.model_dump()
        
        # Upsert into Vector DB
        saved_id = await vector_db.upsert_draft(
            user_id=current_user.id,
            draft_data=draft_data,
            draft_id=draft.draft_id
        )
        
        return APIResponse(
            Message="Draft saved successfully",
            Data={"draft_id": saved_id},
            ErrorCode=0
        )
    except Exception as e:
        print(f"Error saving draft: {e}")
        return JSONResponse({
            "Message": f"Failed to save draft: {str(e)}",
            "ErrorCode": 1
        }, status_code=500)

# --- 3. SEARCH DRAFTS ---
@router.post("/search", response_model=APIResponse[SearchResultData[DraftItem]])
async def search_drafts(
    file: Optional[UploadFile] = File(None),
    query_text: Optional[str] = Form(None),
    limit: int = Form(10),
    current_user: User = Depends(get_current_user)
):
    """
    Search drafts using Voice, Text, or Both.
    """
    search_query: str = ""
    
    try:
        # 1. Handle Voice Input
        if file:
            safe_filename = file.filename or "unknown.wav"
            safe_content_type = file.content_type or "audio/wav"
            
            file_bytes = await file.read()
            
            transcribed_text =  transcribe_audio( # type: ignore
                file_bytes=file_bytes,
                file_name=safe_filename,
                file_content_type=safe_content_type
            ) # type: ignore
            if transcribed_text:
                search_query += str(transcribed_text) # type: ignore

        # 2. Handle Text Input
        if query_text:
            if search_query:
                search_query += " "
            search_query += str(query_text)

        if not search_query.strip():
            return JSONResponse({
                "Message": "Please provide audio or text to search.",
                "ErrorCode": 1
            }, status_code=400)

        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID not found")

        # 3. Perform Hybrid Search
        results = await vector_db.search_drafts(
            user_id=current_user.id,
            query=search_query,
            limit=limit 
        )

        return APIResponse(
            Message="success",
            Data=SearchResultData(query_used=search_query, results=results),
            ErrorCode=0
        )

    except Exception as e:
        print(f"Search Error: {e}")
        return JSONResponse({
            "Message": f"Search failed: {str(e)}",
            "ErrorCode": 1
        }, status_code=500)

# --- 4. DELETE DRAFT ---
@router.delete("/delete/{draft_id}", response_model=APIResponse)
async def delete_draft(
    draft_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a draft (e.g., after sending the email).
    """
    try:
        await vector_db.delete_draft(draft_id)
        
        return APIResponse(
            Message="Draft deleted",
            Data={"draft_id": draft_id},
            ErrorCode=0
        )
    except Exception as e:
         return JSONResponse({
            "Message": f"Delete failed: {str(e)}",
            "ErrorCode": 1
        }, status_code=500)