from pydantic import BaseModel
from typing import List, Optional, Generic, TypeVar

T = TypeVar('T')

# --- Base Item Models ---

class NoteItem(BaseModel):
    id: str
    user_id: int
    content: str
    type: str = "note"
    score: Optional[float] = None # Optional because 'list_all' won't have scores

class DraftItem(BaseModel):
    id: str
    user_id: int
    subject: Optional[str] = None
    body: Optional[str] = None
    to_email: Optional[str] = None
    recipient_name: Optional[str] = None
    status: str = "draft"
    score: Optional[float] = None

# --- Response Data Wrappers ---

class SearchResultData(BaseModel, Generic[T]):
    """Structure for Search results (includes query string)"""
    query_used: str
    results: List[T]

class ListResultData(BaseModel, Generic[T]):
    """Structure for List results (just the list)"""
    results: List[T]

# --- Top Level API Response ---

class APIResponse(BaseModel, Generic[T]):
    """Generic Wrapper: { Message, Data, ErrorCode }"""
    Message: str
    Data: T
    ErrorCode: int