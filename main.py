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
#                             Turnos                                 #
######################################################################


@app.get("/turnos/")
async def read_turnos(db: Session = Depends(get_db)):
    turnos = db.query(Turno).all()
    if not turnos:
        raise HTTPException(status_code=404, detail="No se encontraron turnos")
    return turnos

@app.post("/turnos/", response_model=TurnoCreate)
async def create_turno(turno: TurnoCreate, db: Session = Depends(get_db)):
    new_turno = Turno(
        hora_inicio=turno.hora_inicio,
        hora_fin=turno.hora_fin
    )
    db.add(new_turno)
    db.commit()
    db.refresh(new_turno)
    return new_turno

@app.get("/turnos/{id}", response_model=TurnoCreate)
async def get_turno(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.query(Turno).filter(Turno.id == id).first()
        if not turno:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        return turno
    except Exception as e:    
        print(e)
        raise HTTPException(status_code=404, detail="Turno no encontrado")

@app.put("/turnos/{id}", response_model=TurnoCreate)
async def update_turno(id: int, updated_data: TurnoCreate, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    turno.hora_inicio = updated_data.hora_inicio
    turno.hora_fin = updated_data.hora_fin
    
    db.commit()
    db.refresh(turno)
    return turno

@app.delete("/turnos/{id}")
async def delete_turno (id:int, db:Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    db.delete(turno)
    db.commit()
    return {"message": "Turno eliminado exitosamente"}

######################################################################
#                             Actividades                            #
######################################################################

@app.get("/actividades/")
async def read_actividades(db: Session = Depends(get_db)):
    actividades = db.query(Actividades).all()
    if not actividades:
        raise HTTPException(status_code=404, detail="No se encontraron actividades")
    return actividades

@app.post("/actividades/", response_model=ActividadCreate)
async def create_actividad(actividad: ActividadCreate, db: Session = Depends(get_db)):
    new_actividad = Actividades(
        id=actividad.id,
        descripcion=actividad.descripcion,
        costo=actividad.costo
    )
    db.add(new_actividad)
    db.commit()
    db.refresh(new_actividad)
    return new_actividad

@app.get("/actividades/{id}", response_model=ActividadCreate)
async def get_actividad(id: int, db: Session = Depends(get_db)):
    actividad = db.query(Actividades).filter(Actividades.id == id).first()
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return actividad

@app.put("/actividades/{id}", response_model=ActividadCreate)
async def update_actividad(id: int, updated_data: ActividadCreate, db: Session = Depends(get_db)):
    actividad = db.query(Actividades).filter(Actividades.id == id).first()
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    
    actividad.descripcion = updated_data.descripcion
    actividad.costo = updated_data.costo
    
    db.commit()
    db.refresh(actividad)
    return actividad

@app.delete("/actividades/{id}")
async def delete_actividad(id: int, db: Session = Depends(get_db)):
    actividad = db.query(Actividades).filter(Actividades.id == id).first()
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    db.delete(actividad)
    db.commit()
    return {"message": "Actividad eliminada exitosamente"}

