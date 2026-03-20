from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.models.nutricionista import Nutricionista


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
router = APIRouter()


def _verify_password_legacy_sha256(plain_password: str, hashed_password: str) -> bool:
    digest = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(digest, hashed_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False

    if hashed_password.startswith("$2"):
        return pwd_context.verify(plain_password, hashed_password)

    return _verify_password_legacy_sha256(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_nutricionista_by_email(db: Session, email: str) -> Nutricionista | None:
    return db.query(Nutricionista).filter(Nutricionista.email == email).first()


def serialize_user(user: Nutricionista) -> dict[str, str | int | None]:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.nome,
        "tenant_id": user.tenant_id,
        "role": user.papel,
        "plan": user.plano,
        "status": user.status,
    }


def authenticate_nutricionista(
    db: Session, email: str, password: str
) -> Nutricionista | None:
    user = get_nutricionista_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None

    if not user.password_hash.startswith("$2"):
        user.password_hash = get_password_hash(password)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def create_token(
    data: dict, expires_delta: timedelta, token_type: str = "access"
) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    return create_token(
        data,
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(data: dict) -> str:
    return create_token(
        data,
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


def build_auth_response(user: Nutricionista) -> dict[str, object]:
    claims = {
        "sub": user.email,
        "role": user.papel,
        "tenant_id": user.tenant_id,
        "user_id": user.id,
    }
    return {
        "access_token": create_access_token(claims),
        "refresh_token": create_refresh_token(claims),
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": serialize_user(user),
    }


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") not in {None, "access"}:
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = get_nutricionista_by_email(db, email)
    if user is None or user.status != "active":
        raise credentials_exception
    return user


@router.post("/auth/token")
def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_nutricionista(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    auth_response = build_auth_response(user)
    return {
        "access_token": auth_response["access_token"],
        "token_type": auth_response["token_type"],
    }


@router.post("/auth/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_nutricionista(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return build_auth_response(user)


@router.post("/auth/register")
def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    existing = get_nutricionista_by_email(db, register_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    new_user = Nutricionista(
        nome=register_data.username,
        email=register_data.email,
        password_hash=get_password_hash(register_data.password),
        plano="basic",
        tipo_user="nutri",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuário registrado", "id": new_user.id}


@router.get("/auth/verify")
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") not in {None, "access"}:
            raise JWTError()
        email: str = payload.get("sub")
        if email is None:
            raise JWTError()
        return {"status": "valid", "email": email}
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Token inválido") from exc


@router.get("/auth/me")
def me(current_user: Nutricionista = Depends(get_current_user)):
    return serialize_user(current_user)


@router.post("/auth/refresh")
def refresh(refresh_data: RefreshRequest):
    try:
        payload = jwt.decode(
            refresh_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise JWTError()
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Refresh token inválido") from exc

    claims = {
        "sub": payload.get("sub"),
        "role": payload.get("role", "nutri"),
        "tenant_id": payload.get("tenant_id"),
        "user_id": payload.get("user_id"),
    }
    return {
        "access_token": create_access_token(claims),
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/auth/logout", status_code=204)
def logout():
    return None
