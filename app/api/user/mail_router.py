from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from app.middleware.auth_middleware import APIKeySecurity
from app.services.transcription import transcribe_audio as process_transcription
from app.models import User

router = APIRouter(prefix="/user", tags=["User"])

