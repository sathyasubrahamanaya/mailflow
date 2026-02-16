from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional
from app.models import User
from app.middleware.auth_middleware import get_current_user
from app.services.vector_service import vector_db
# Assuming you are using the standard transcription service we fixed
from app.services.transcription_v2 import transcribe_audio 
from app.schemas import APIResponse, SearchResultData, ListResultData, NoteItem
from fastapi.responses import JSONResponse
from app.services.notes_agent import generate_smart_note

router = APIRouter(prefix="/notes", tags=["Notes"])

# --- 1. LIST ALL NOTES ---
@router.get("/all", response_model=APIResponse[ListResultData[NoteItem]])
async def list_notes(
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Get all notes for the current user.
    """
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID not found")

        notes = await vector_db.list_all_notes(user_id=current_user.id, limit=limit)

        return APIResponse(
            Message="success",
            Data=ListResultData(results=notes),
            ErrorCode=0
        )
    except Exception as e:
        return JSONResponse({"Message": str(e), "ErrorCode": 1}, status_code=500)

# --- SAVE NOTE (CREATE) ---
@router.post("/save", response_model=APIResponse)
async def save_note(
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Save a new note. The Agent generates the full markdown content.
    """
    raw_transcription = ""
    
    try:
        # 1. Get Audio Text
        if file:
            safe_filename = file.filename or "unknown.wav"
            safe_content_type = file.content_type or "audio/wav"
            file_bytes = await file.read()
            
            # Synchronous call
            transcribed_text = transcribe_audio(
                file_bytes=file_bytes,
                file_name=safe_filename,
                file_content_type=safe_content_type
            )
            if transcribed_text:
                raw_transcription = str(transcribed_text)
        
        # 2. Check for content
        if not raw_transcription and not content:
             return JSONResponse({"Message": "No content provided", "ErrorCode": 1}, status_code=400)

        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID not found")

        # 3. CALL THE AGENT (Returns String)
        # It merges audio text + user text into one professional note
        final_smart_note = await generate_smart_note(
            transcribed_text=raw_transcription,
            user_text=content
        )

        # 4. Save to Vector DB
        note_id = await vector_db.upsert_note(
            user_id=current_user.id,
            content=final_smart_note # Saving the agent's output directly
        )

        return APIResponse(
            Message="Note processed and saved",
            Data={"note_id": note_id, "content": final_smart_note},
            ErrorCode=0
        )
    except Exception as e:
        return JSONResponse({"Message": str(e), "ErrorCode": 1}, status_code=500)


# --- 3. SEARCH NOTES ---
@router.post("/search", response_model=APIResponse[SearchResultData[NoteItem]])
async def search_notes(
    file: Optional[UploadFile] = File(None),
    query_text: Optional[str] = Form(None),
    limit: int = Form(10),
    current_user: User = Depends(get_current_user)
):
    """
    Search notes using Voice or Text.
    """
    search_query: str = ""
    try:
        if file:
            safe_filename = file.filename or "unknown.wav"
            safe_content_type = file.content_type or "audio/wav"

            file_bytes = await file.read()
            # Synchronous call (no await)
            transcribed_text = transcribe_audio(
                file_bytes=file_bytes,
                file_name=safe_filename,
                file_content_type=safe_content_type
            )
            if transcribed_text:
                search_query += str(transcribed_text)

        if query_text:
            if search_query: search_query += " "
            search_query += str(query_text)
            
        if not search_query.strip():
            return JSONResponse({"Message": "Empty search query", "ErrorCode": 1}, status_code=400)

        if current_user.id is None:
             raise HTTPException(status_code=400, detail="User ID not found")

        # Search
        results = await vector_db.search_notes(
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
        return JSONResponse({"Message": str(e), "ErrorCode": 1}, status_code=500)

# --- 4. UPDATE NOTE (NEW) ---
@router.put("/update", response_model=APIResponse)
async def update_note(
    note_id: str = Form(...),  # Required field
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Updates an existing note. Overwrites content with new Text or Voice.
    """
    final_content: str = ""
    
    try:
        # 1. Handle Voice Input
        if file:
            safe_filename = file.filename or "unknown.wav"
            safe_content_type = file.content_type or "audio/wav"
            
            file_bytes = await file.read()
            
            # Synchronous call
            transcribed_text = transcribe_audio(
                file_bytes=file_bytes,
                file_name=safe_filename,
                file_content_type=safe_content_type
            )
            
            if transcribed_text:
                final_content += str(transcribed_text)
        
        # 2. Handle Text Input
        if content:
            if final_content:
                final_content += " "
            final_content += str(content)

        if not final_content.strip():
             return JSONResponse({"Message": "No content provided for update", "ErrorCode": 1}, status_code=400)

        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID not found")

        # 3. Update Vector DB (Upsert with existing ID)
        updated_id = await vector_db.upsert_note(
            user_id=current_user.id,
            content=final_content,
            note_id=note_id  # Passing the ID forces an update
        )

        return APIResponse(
            Message="Note updated successfully",
            Data={"note_id": updated_id, "content": final_content},
            ErrorCode=0
        )
    except Exception as e:
        return JSONResponse({"Message": f"Update failed: {str(e)}", "ErrorCode": 1}, status_code=500)


# --- 5. DELETE NOTE ---
@router.delete("/delete/{note_id}", response_model=APIResponse)
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a specific note by ID.
    """
    try:
        await vector_db.delete_note(note_id)
        
        return APIResponse(
            Message="Note deleted successfully",
            Data={"note_id": note_id},
            ErrorCode=0
        )
    except Exception as e:
        return JSONResponse({
            "Message": f"Failed to delete note: {str(e)}", 
            "ErrorCode": 1
        }, status_code=500)