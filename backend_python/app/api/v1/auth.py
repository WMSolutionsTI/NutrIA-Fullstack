from datetime import datetime, timedelta
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.models.nutricionista import Nutricionista

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_nutricionista_by_email(db: Session, email: str):
    return db.query(Nutricionista).filter(Nutricionista.email == email).first()


def authenticate_nutricionista(db: Session, email: str, password: str):
    user = get_nutricionista_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


@router.post("/auth/token")
def login_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_nutricionista(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/register")
def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    existing = get_nutricionista_by_email(db, email)
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    hashed_password = get_password_hash(password)
    new_user = Nutricionista(nome=username, email=email, password_hash=hashed_password, plano="basic")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuário registrado", "id": new_user.id}


@router.get("/auth/verify")
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError()
        return {"status": "valid", "email": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
