import httpx
from fastapi import HTTPException, status, UploadFile
from app.config import settings
import io
import requests
def transcribe_audio(
    file_bytes: bytes,
    file_name:str,
    file_content_type:str,
    model: str = "saaras:v2",
    language: str = "unknown",
    with_timestamps: bool = False,
    with_diarization: bool = False,
    num_speakers: int = 1
)->dict:
    SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text-translate"
    SARVAM_API_KEY = settings.SARVAM_API_KEY

    files = {"file": (file_name, io.BytesIO(file_bytes), file_content_type)}
    print("started here")
    params = {
        "body.model": model,
        "prompt":"",
        "with_diarization": str(with_diarization).lower(),
        "num_speakers": num_speakers,
    }
    
    headers = {
        "api-subscription-key": f"{SARVAM_API_KEY}",
        
    }

    response = requests.post(url=SARVAM_API_URL,headers=headers,data=params,files=files)
    print("the original response",response.text)
    print("the sarvam response",dict(response.json()).get("transcript",None))
    return dict(response.json()).get("transcript",None)

    
    
    with httpx.Client as client:
        print("working with sarvam")
        response =  client.post(
            SARVAM_API_URL,
            headers=headers,
            files=files,
            data=params
        )
        
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"API error: {response.text}"
        )
    print(dict(response.json()).get("transcript",None))
    return dict(response.json()).get("transcript",None)
