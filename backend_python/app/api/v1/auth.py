from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/auth/token")
def login_token(username: str, password: str):
    # Mock: autenticação
    if username == "admin" and password == "admin":
        return {"access_token": "mocktoken", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@router.get("/auth/verify")
def verify_token(token: str = Depends(oauth2_scheme)):
    # Mock: verificação de token
    if token == "mocktoken":
        return {"status": "valid"}
    raise HTTPException(status_code=401, detail="Token inválido")