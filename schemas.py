from pydantic import BaseModel
from datetime import time, date
from typing import Optional

#### Actividades ####
class ActividadCreate(BaseModel):
    id: Optional[int] = None
    descripcion: str
    costo: float
    emoji: str
    
class ActividadUpdate(BaseModel):
    descripcion: Optional[str] = None
    costo: Optional[float] = None
    
#### Equipamiento ####
class EquipamientoCreate(BaseModel):
    id_actividad: int
    descripcion: str
    costo: float
    
class EquipamientoUpdate(BaseModel):
    description: Optional[str] = None
    costo: Optional[float] = None
    
#### Instructor ####
class InstructorCreate(BaseModel):
    ci: int
    nombre: str
    apellido: str
    
class InstructorUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    
#### Turno ####
class TurnoCreate(BaseModel):
    id: Optional[int] = None
    hora_inicio: time
    hora_fin: time

class TurnoUpdate(BaseModel):
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    
#### Alumno ####
class AlumnoCreate(BaseModel):
    ci: str
    nombre: str
    apellido: str
    fecha_nacimiento: date
    telefono: str
    correo: str
    contrasena: str
    
class AlumnoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None


#### Clase ####
class Clase(BaseModel):
    id: Optional[int] = None
    ci_instructor: str
    id_actividad: int
    id_turno: int
    dictada: bool = False
    
class ClaseUpdate(BaseModel):
    ci_instructor: Optional[int] = None
    id_actividad: Optional[int] = None
    id_turno: Optional[int] = None
    dictada: Optional[bool] = None

