from pydantic import BaseModel
from datetime import time, date

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
    ci: str
    nombre: str
    apellido: str
    fecha_nacimiento: date
    telefono: str
    correo: str

class ClaseCreate(BaseModel):
    id: int
    ci_instructor: int
    id_actividad: int
    id_turno: int
    dictada: bool = False
