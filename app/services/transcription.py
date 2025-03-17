import httpx
from fastapi import HTTPException, status, UploadFile
from app.config import settings

async def transcribe_audio(
    file: UploadFile,
    model: str = "saaras:v2",
    language: str = "unknown",
    with_timestamps: bool = False,
    with_diarization: bool = False,
    num_speakers: int = 1
):
    SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text-translate"
    SARVAM_API_KEY = settings.SARVAM_API_KEY

   
    
    file_bytes = await file.read()
    

    print("filename--->",file.filename)
    files = {"file": (file.filename, file_bytes, file.content_type)}
    
    params = {
        "body.model": model,
        "prompt":"",
        "with_diarization": str(with_diarization).lower(),
        "num_speakers": num_speakers,
    }
    
    headers = {
        "api-subscription-key": f"{SARVAM_API_KEY}",
        
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            SARVAM_API_URL,
            headers=headers,
            files=files,
            data=params
        )
        
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Sarvam API error: {response.text}"
        )
    print(dict(response.json()).get("transcript",None))
    return dict(response.json()).get("transcript",None)
