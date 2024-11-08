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

@app.post("/instructores/", response_model=InstructorCreate)
async def create_instructor(instructor: InstructorCreate, db: Session = Depends(get_db)):
    db_instructor = db.query(Instructor).filter(Instructor.ci == instructor.ci).first()
    if db_instructor:
        raise HTTPException(status_code=400, detail="Instructor con esta CI ya existe")
    new_instructor = Instructor(
        ci=instructor.ci,
        nombre=instructor.nombre,
        apellido=instructor.apellido
    )
    db.add(new_instructor)
    db.commit()
    db.refresh(new_instructor)
    return new_instructor

#ins x ci
@app.get("/instructores/{ci}")
async def get_instructor(ci: str, db: Session = Depends(get_db)):
    instructor = db.query(Instructor).filter(Instructor.ci == ci).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    return instructor

@app.put("/instructores/{ci}")
async def update_instructor(ci:str, updated_data: InstructorCreate, db: Session = Depends(get_db)):
    instructor = db.query(Instructor).filter(Instructor.ci == ci).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    
    instructor.nombre = updated_data.nombre
    instructor.apellido = updated_data.apellido
    
    db.commit()
    db.refresh(instructor)
    return instructor

@app.delete("/instructores/{ci}")
async def delete_instructor(ci: str, db: Session = Depends(get_db)):
    instructor = db.query(Instructor).filter(Instructor.ci == ci).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    db.delete(instructor)
    db.commit()
    return {"message": "Instructor eliminado exitosamente"}

######################################################################
#                         Rutas de Turnos                           #
######################################################################


@app.get("/turnos/")
async def read_turnos(db: Session = Depends(get_db)):
    turnos = db.query(Turno).all()
    if not turnos:
        raise HTTPException(status_code=404, detail="No se encontraron turnos")
    return turnos