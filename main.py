from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Instructor, Turno, Actividades, Alumno, Clase, AlumnoClase
from schemas import InstructorCreate, TurnoCreate, ActividadCreate, AlumnoCreate, ClaseCreate
from pydantic import BaseModel
from typing import Annotated, List
import models
from database import engine, SessionLocal


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

######################################################################
#                           Instructores                             #
######################################################################

@app.get("/instructores/")
async def get_instructors(db: Session = Depends(get_db)):
    instructors = db.query(Instructor).all()
    if not instructors:
        raise HTTPException(status_code=404, detail="No se encontraron instructores")
    return instructors


######################################################################
#                         Rutas de Turnos                           #
######################################################################


@app.get("/turnos/")
async def read_turnos(db: Session = Depends(get_db)):
    turnos = db.query(Turno).all()
    if not turnos:
        raise HTTPException(status_code=404, detail="No se encontraron turnos")
    return turnos