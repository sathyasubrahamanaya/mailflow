import httpx
from fastapi import HTTPException, status, UploadFile
from app.config import settings

async def transcribe_audio(
    file: UploadFile,
    model: str = "saaras:flash",  
    with_timestamps: bool = False,
    with_diarization: bool = False,
    num_speakers: int = 1
):
    SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text-translate"
    SARVAM_API_KEY = settings.SARVAM_API_KEY

    if file.content_type not in ["audio/wav", "audio/mp3"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only WAV and MP3 are supported."
        )
    
    file_bytes = await file.read()
    
    files = {"file": (file.filename, file_bytes, file.content_type)}
    
    data = {
        "model": model,  
        "with_timestamps": str(with_timestamps).lower(),
        "with_diarization": str(with_diarization).lower(),
        "num_speakers": str(num_speakers)
    }
    
    headers = {
        "api-subscription-key": SARVAM_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            SARVAM_API_URL,
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Sarvam API error: {response.text}"
            )
            
    return response.json()