from pydantic import BaseModel
class ActividadCreate(BaseModel):
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
    hora_inicio: str
    hora_fin: str

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
