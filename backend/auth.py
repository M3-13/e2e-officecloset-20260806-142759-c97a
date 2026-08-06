import os
import re
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import User

router = APIRouter(prefix="/api/auth")

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_GENERIC_ERROR = "Ungültige Anmeldedaten"


def _get_jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET", "")
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET ist nicht konfiguriert")
    return secret


class RegisterRequest(BaseModel):
    model_config = {"extra": "forbid"}
    email: str
    password: str


class LoginRequest(BaseModel):
    model_config = {"extra": "forbid"}
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: int


def hash_password(password: str) -> str:
    return pwd_context.hash(password, rounds=12)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(hours=JWT_EXPIRY_HOURS)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(payload, _get_jwt_secret(), algorithm=JWT_ALGORITHM)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail=_GENERIC_ERROR)
    token = auth_header[len("Bearer ") :]
    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail=_GENERIC_ERROR)
    except JWTError:
        raise HTTPException(status_code=401, detail=_GENERIC_ERROR) from None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=403, detail=_GENERIC_ERROR)
    return user


@router.post("/register", status_code=201, response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if not EMAIL_REGEX.fullmatch(body.email):
        raise HTTPException(status_code=422, detail=_GENERIC_ERROR)
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=409, detail=_GENERIC_ERROR)
    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail=_GENERIC_ERROR)
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return UserResponse(user_id=user.id)
