from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated, List
from models import Turno
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# class PostBase(BaseModel):
#     title: str
#     content: str
#     user_id: int

# class UserBase(BaseModel):
#     username: str

# # def get_db():
# #     db = SessionLocal()
# #     try:
# #         yield db
# #     finally:
# #         db.close()

# # db_dependency = Annotated[Session, Depends(get_db)]

# @app.post("/users/", status_code=status.HTTP_201_CREATED)
# async def create_user(user: UserBase, db: db_dependency):
#     db_user = models.User(**user.dict())
#     db.add(db_user)
#     db.commit()
#     return {"message": "Usuario creado exitosamente"}

class TurnoResponse(BaseModel):
    id: int
    hora_inicio: str
    hora_fin: str
    
    class Config:
        orm_mode = True
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/turnos/")
async def read_turnos(db: Session = Depends(get_db)):
    turnos = db.query(Turno).all()
    if not turnos:
        raise HTTPException(status_code=404, detail="No se encontraron turnos")
    return turnos