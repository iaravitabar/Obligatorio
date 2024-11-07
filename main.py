from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated, List
from models import Turno
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de la Escuela de Deportes de Nieve"}


@app.get("/turnos/")
async def read_turnos(db: Session = Depends(get_db)):
    turnos = db.query(Turno).all()
    if not turnos:
        raise HTTPException(status_code=404, detail="No se encontraron turnos")
    return turnos