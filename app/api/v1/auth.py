from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.db.session import SessionLocal

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(deps.get_db)):
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password  # You can hash later
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
