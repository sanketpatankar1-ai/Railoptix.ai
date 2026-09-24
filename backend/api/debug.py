from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.user import User

router = APIRouter()

@router.get("/status")
def system_status(db: Session = Depends(get_db)):
    try:
        user_count = db.query(User).count()
        return {"users": user_count, "version": "2.0.1"}
    except Exception as e:
        return {"error": str(e)}
