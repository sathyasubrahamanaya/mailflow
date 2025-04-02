from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.api.auth.authentication import router as auth_router
from app.api.admin.admin_router import router as admin_router
from app.api.user.mail_router import router as user_router
from app.api.support.support_router import router as support_router
from app.api.email.email_router import router as email_router
from app.api.user.contacts import router as contacts_router

app = FastAPI(title="MailFlow",version="0.1.0 Abin Alpha version")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await create_db_and_tables()

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(support_router)
app.include_router(email_router)
app.include_router(contacts_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
