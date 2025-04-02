from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, File
from app.models import User, ChatHistory
from app.middleware.auth_middleware import APIKeySecurity
from app.services.agno_agent import generate_email
from app.services.transcription import transcribe_audio
from app.database import get_session
from app.services.utils import clean_response,remove_escapes,remove_think_sections
import json
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/email", tags=["Email"])



@router.post("/generate")
async def generate_email_endpoint(
    file: UploadFile|None = File(default=None),
    transcribed_text: str|None =Form(default=None),
    recipient_name: str|None =Form(default=None),
    recipient_email: str|None =Form(default=None),
    current_user: User = Depends(APIKeySecurity())
):
    try:
        transcribe_audio_content=""
        if file:
           file_bytes = await file.read()
           print("filename",file.filename,len(file_bytes))

           transcribe_audio_content =  transcribe_audio(file_bytes,file.filename,file.content_type) 
        print("transcribed_audio",transcribe_audio_content)
        if transcribed_text!=None:
           
           transcription_str = transcribed_text  
        else:
            transcription_str = str(transcribe_audio_content)
        if transcribe_audio_content!=None and transcribed_text!=None:
            transcription_str = str(transcribe_audio_content) + "**body modification instruction**"+transcribed_text

        email_content= await generate_email(
            transcribed_text=transcription_str+ f"**sender info** this email sent by is {current_user.name}",
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            user_session_id=current_user.username + f"__{current_user.id}"
        )
        return JSONResponse({"Message":"success","Data":{"email_content":json.loads(email_content.replace('\n', ''))},"ErrorCode":0 })
    except Exception as e:
        return JSONResponse({"Message":f"Error generating email: {str(e)}","Data":{},"ErrorCode":1 })
       
