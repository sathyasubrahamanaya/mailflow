from fastapi import APIRouter, Depends, UploadFile, Form, File
from app.models import User
from app.services.agno_agent import generate_email # type: ignore
from app.middleware.auth_middleware import get_current_user
from app.services.transcription_v2 import transcribe_audio # type: ignore
import json
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/email", tags=["Email"])



@router.post("/generate")
async def generate_email_endpoint(
    file: UploadFile|None = File(default=None),
    transcribed_text: str|None =Form(default=None),
    recipient_name: str|None =Form(default=None),
    recipient_email: str|None =Form(default=None),
    current_user: User = Depends(get_current_user)
):
    try:
        transcribe_audio_content=""
        if file:
           file_bytes = await file.read()
           print("filename",file.filename,len(file_bytes))

           transcribe_audio_content =  transcribe_audio(file_bytes,file.filename,file.content_type)  # type: ignore
        print("transcribed_audio",transcribe_audio_content) # type: ignore
        if transcribed_text!=None:
           
           transcription_str = transcribed_text  
        else:
            transcription_str = str(transcribe_audio_content) # type: ignore
        if transcribe_audio_content!=None and transcribed_text!=None: # type: ignore
            transcription_str = str(transcribe_audio_content) + "**body modification instruction**"+transcribed_text # type: ignore
        

        email_content= await generate_email( # type: ignore
            transcribed_text=transcription_str+ f"**sender info** this email sent by is {current_user.name}",
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            user_session_id=current_user.username + f"__{current_user.id}"
        )

        # With agno v2 output_schema, email_content is a Pydantic Email object
        # Convert to dict for JSON response
        if hasattr(email_content, 'model_dump'): # type: ignore
            email_dict = email_content.model_dump() # type: ignore
        else:
            # Fallback for string responses  
            email_dict = json.loads(email_content.replace('\n', '')) # type: ignore
        
        return JSONResponse({"Message":"success","Data":{"email_content":email_dict},"ErrorCode":0 })
    except Exception as e:
        print("error generating email",e)
        return JSONResponse({"Message":f"Error generating email: {str(e)}","Data":{},"ErrorCode":1 })
       
