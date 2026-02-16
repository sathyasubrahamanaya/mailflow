import requests
from fastapi import HTTPException
from app.config import settings
import io

def transcribe_audio(
    file_bytes: bytes,
    file_name: str,
    file_content_type: str,
    model: str = "saaras:v2.5",
    language: str = "unknown",
    with_diarization: bool = False,
    num_speakers: int = 1
) -> str:
    """
    Synchronous transcription using requests.
    Compatible with existing email_router.
    """
    SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text-translate"
    SARVAM_API_KEY = settings.SARVAM_API_KEY

    files = {"file": (file_name, io.BytesIO(file_bytes), file_content_type)}
    
    params = {
        "model": model,
        "prompt": "",
        "with_diarization": str(with_diarization).lower(),
        "num_speakers": str(num_speakers),
    }
    
    headers = {
        "api-subscription-key": f"{SARVAM_API_KEY}",
    }

    try:
        print(f"Transcribing {file_name}...")
        response = requests.post(url=SARVAM_API_URL, headers=headers, data=params, files=files)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"API error: {response.text}"
            )
            
        # Safely get transcript
        data = response.json()
        transcript = data.get("transcript", "")
        return str(transcript)
        
    except Exception as e:
        print(f"Transcription Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))