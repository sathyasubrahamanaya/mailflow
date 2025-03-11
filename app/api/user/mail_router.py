from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from app.middleware.auth_middleware import APIKeySecurity
from app.services.transcription import transcribe_audio as process_transcription
from app.models import User

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/transcribe")
async def transcribe_audio_endpoint(
    file: UploadFile = File(...),
    model: str = "saaras:flash",
    with_timestamps: bool = False,
    with_diarization: bool = False,
    num_speakers: int = 1,
    current_user: User = Depends(APIKeySecurity())
):
   
    if file.content_type not in ["audio/wav", "audio/mp3"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only WAV and MP3 are supported."
        )
    
    try:
        transcription_result = await process_transcription(
            file=file,
            model=model,
            with_timestamps=with_timestamps,
            with_diarization=with_diarization,
            num_speakers=num_speakers
        )
        return transcription_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing transcription: {str(e)}"
        )