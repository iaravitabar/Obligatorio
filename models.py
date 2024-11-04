from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Time
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(255), unique=True)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    content = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id'))

class Turno(Base):
    __tablename__ = "turnos"
    
    id = Column(Integer, primary_key=True, index=True)
    hora_inicio = Column(Time)
    hora_fin = Column(Time)
