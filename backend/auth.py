from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session

from models import User

router = APIRouter(prefix="/api/auth")


def get_current_user(request: Request, db: Session) -> User:
    raise HTTPException(status_code=501, detail="auth #9 implements this")


@router.post("/register")
async def register_stub():
    raise HTTPException(status_code=501, detail="auth #9 implements this")


@router.post("/login")
async def login_stub():
    raise HTTPException(status_code=501, detail="auth #9 implements this")
