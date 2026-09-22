from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
import datetime

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    score: int

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    score: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class ExecutionRequest(BaseModel):
    challenge_id: str
    mode: str # "vulnerable" or "safe"
    payload: str

class ExecutionResponse(BaseModel):
    challenge_id: str
    mode: str
    success: bool
    output: str
    raw_trace: str
    flag_captured: Optional[str] = None
    vulnerable_code_snippet: str
    safe_code_snippet: str
    explanation: str

class FlagSubmitRequest(BaseModel):
    challenge_id: str
    flag: str

class FlagSubmitResponse(BaseModel):
    correct: bool
    message: str
    points_awarded: int
    new_total_score: int

class RagExecutionRequest(BaseModel):
    mode: str # "vulnerable" or "safe"
    doc_ids: List[str]
    user_query: str

class McpExecutionRequest(BaseModel):
    user_query: str
