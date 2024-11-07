from sqlalchemy import Boolean, Column, Integer, String, Float, Time, Date
from database import Base

#tabla de login
class Login(Base):
    __tablename__ = "login"
    
    correo = Column(String(255), primary_key=True)
    constrasena = Column(String(255), nullable=False)

#tabla de actividades
class Actividades(Base):
    __tablename__ = "actividades"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    descpricion = Column(String(255), nullable=False)
    costo = Column(Float(10,2), nullable=False)

#tabla de equipamiento
class Equipamiento(Base):
    __tablename__ = "equipamiento"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_actividad = Column(Integer, ForeignKey('actividades.id',ondelete="CASCADE"), nullable=False)
    descripcion = Column(String(255), nullable=False)
    costo = Column(Float(10,2), nullable=False)

#tabla de instructores
class Instructor(Base):
    __tablename__ = "instructores"
    
    ci = Column(String(10), primary_key=True)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=False)

#tabla de turnos
class Turno(Base):
    __tablename__ = "turnos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hora_inicio = Column(Time)
    hora_fin = Column(Time)

#tabla de alumnos
class Alumno(Base):
    __tablename__ = "alumnos"
    
    ci = Column(String(10), primary_key=True)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=False)
    telefono = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False)
    
#tambla de clase
class Clase(Base):
    __tablename__ = "clase"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ci_instructor = Column(String(10), ForeignKey('instructores.ci',ondelete="CASCADE"), nullable=False)
    id_actividad = Column(Integer, ForeignKey("actividades.id", ondelete="CASCADE"), nullable=False)
    id_turno = Column(Integer, ForeignKey("turnos.id", ondelete="CASCADE"), nullable=False)
    dictada = Column(Boolean, nullable=False, default=False)
    
#tambla de alumno_clase
class AlumnoClase(Base):
    __tablename__ = "alumno_clase"
    
    i_clase = Column(Integer, ForeignKey('clase.id',ondelete="CASCADE"), primary_key=True)
    ci_alumno = Column(String(10), ForeignKey("alumnos.ci", ondelete="CASCADE"), primary_key=True)
    id_equipamiento = Column(Integer, ForeignKey("equipamiento.id"), nullable=True)
   