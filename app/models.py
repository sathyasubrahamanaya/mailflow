from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import secrets

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    hashed_password: str
    api_key: str = Field(default_factory=lambda: secrets.token_hex(16), unique=True)
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    support_queries: List["SupportQuery"] = Relationship(back_populates="user")
    feedbacks: List["Feedback"] = Relationship(back_populates="user")
    admin: "AdminUser" = Relationship(back_populates="user")
    contacts: List["Contact"] = Relationship(back_populates="user")
    chat_histories: List["ChatHistory"] = Relationship(back_populates="user")

class AdminUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    
    user: User = Relationship(back_populates="admin")

class SupportQuery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    query_text: str
    status: str = "open"
    reply:str|None 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="support_queries")

class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user_name:str
    rating: int
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="feedbacks")

class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    email: str
    phone: str = None
    
    user: User = Relationship(back_populates="contacts")

class ChatHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    conversation: str  # Full conversation context (as plain text or JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="chat_histories")
