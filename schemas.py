from pydantic import BaseModel
from datetime import time

class ActividadCreate(BaseModel):
    id: int
    descripcion: str
    costo: float

class EquipamientoCreate(BaseModel):
    id_actividad: int
    descripcion: str
    costo: float

class InstructorCreate(BaseModel):
    ci: int
    nombre: str
    apellido: str

class TurnoCreate(BaseModel):
    id: int
    hora_inicio: time
    hora_fin: time

class AlumnoCreate(BaseModel):
    ci: int
    nombre: str
    apellido: str
    fecha_nacimiento: str
    telefono: str
    email: str

class ClaseCreate(BaseModel):
    ci_instructor: int
    id_actividad: int
    id_turno: int
