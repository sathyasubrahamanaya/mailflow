from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, File
from app.models import User, ChatHistory
from app.middleware.auth_middleware import APIKeySecurity
from app.services.langchain_agent import EmailGenerationAgent
from app.services.transcription import transcribe_audio
from app.database import get_session
from app.services.utils import clean_response,remove_escapes,remove_think_sections


router = APIRouter(prefix="/email", tags=["Email"])

email_agent = EmailGenerationAgent()

@router.post("/generate")
async def generate_email_endpoint(
    file: UploadFile = File(...),
    transcribed_text: str|None =Form(default=None),
    recipient_name: str|None =Form(default=None),
    recipient_email: str|None =Form(default=None),
    current_user: User = Depends(APIKeySecurity())
):
    try:
        
        transcribe_audio_content = await transcribe_audio(file)
        sender_name = current_user.name
        print("transcribed_audio",transcribe_audio_content)
        if transcribed_text!=None:
           
           transcription_str = transcribed_text  
        else:
            transcription_str = str(transcribe_audio_content)
        email_content = email_agent.generate_email(
            transcribed_text=transcription_str+ f"sender's name is {sender_name}",
            recipient_name=recipient_name,
            recipient_email=recipient_email
        )
        
        return {"email_content": email_content}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating email: {str(e)}"
        )

@router.post("/update")
async def update_email(
    recipient_name: str = Form(...),
    recipient_email: str = Form(...),
    conversation_id: int = Form(None),
    input_text: str = Form(None),
    voice_file: UploadFile = File(None),
    current_user: User = Depends(APIKeySecurity()),
    session = Depends(get_session)
):
    if not input_text and not voice_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either input text or voice file must be provided."
        )
    # If voice_file provided, transcribe it to text
    if voice_file and not input_text:
        transcription = await transcribe_audio(
            file=voice_file,
            model="saarika:v2",
            language="unknown"
        )
        new_input = transcription.get("transcription", "")
    else:
        new_input = input_text

    # Retrieve existing conversation if conversation_id provided
    conversation_context = ""
    chat_history = None
    if conversation_id:
        chat_history = await session.get(ChatHistory, conversation_id)
        if chat_history:
            conversation_context = chat_history.conversation

    # Append the new input to the existing conversation context
    updated_conversation = (conversation_context + "\nUser: " + new_input) if conversation_context else new_input

    # Generate the professional email using the updated conversation as context
    email_content = email_agent.generate_email(
        transcribed_text=updated_conversation,
        recipient_name=recipient_name,
        recipient_email=recipient_email
    )

    # Update existing chat history or create a new record
    if chat_history:
        chat_history.conversation = updated_conversation
        await session.commit()
        await session.refresh(chat_history)
    else:
        chat_history = ChatHistory(
            user_id=current_user.id,
            conversation=updated_conversation
        )
        session.add(chat_history)
        await session.commit()
        await session.refresh(chat_history)

    return {"email_content": email_content, "conversation_id": chat_history.id}
