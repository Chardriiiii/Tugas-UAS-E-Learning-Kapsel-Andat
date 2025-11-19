from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str # Gunakan email atau NIM
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str