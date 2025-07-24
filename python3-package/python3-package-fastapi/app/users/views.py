from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
# from . import services, schemas, database, models
from . import services, schemas, models
from ..core import database

models.Base.metadata.create_all(bind=database.engine)

users_api = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@users_api.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = services.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return services.create_user(db=db, user=user)


@users_api.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = services.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@users_api.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = services.get_users(db, skip=skip, limit=limit)
    return users


@users_api.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = services.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return services.delete_user(db, user_id=user_id)
