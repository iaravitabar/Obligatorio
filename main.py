from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import pymysql
from typing import List
import datetime
from pydantic import BaseModel
from database import get_connection
from schemas import Clase, Alumno, Login, AlumnoClase, EquipamientoCreate, InstructorCreate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

######################################################################
#                         Login-Register                             #
######################################################################

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de la Escuela de Deportes de Nieve"}

@app.post("/alumnos/")
async def create_alumno(alumno: Alumno):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar si la cédula ya existe
            cursor.execute("SELECT ci FROM alumnos WHERE ci = %s", (alumno.ci,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Alumno con esta CI ya existe")
            
            # Insertar nuevo alumno
            cursor.execute(
                """
                INSERT INTO alumnos (ci, nombre,apellido, correo, telefono, fecha_nacimiento) 
                VALUES (%s, %s,%s, %s, %s, %s)
                """,
                (alumno.ci, alumno.nombre, alumno.apellido, alumno.correo, alumno.telefono, alumno.fecha_nacimiento),
            )
            connection.commit()
            return {"message": "Alumno creado exitosamente"}
    finally:
        connection.close()

@app.post("/login/")
async def login(request: Login):
    ci = request.ci
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT ci, nombre FROM alumnos WHERE ci = %s", (ci,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            return {"message": "Inicio de sesión exitoso", "nombre": result[0]}
    finally:
        connection.close()


@app.get("/actividades/")
async def get_actividades():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM actividades")
            actividades = cursor.fetchall()
            if not actividades:
                raise HTTPException(status_code=404, detail="No se encontraron actividades")
            return actividades
    finally:
        connection.close()
        
@app.get("/actividades/{id}")
async def get_actividad(id: int):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM actividades WHERE id = %s", (id,))
            actividad = cursor.fetchone()
            if not actividad:
                raise HTTPException(status_code=404, detail="Actividad no encontrada")
            return actividad
    finally:
        connection.close()

@app.post("/clases/")
async def create_clase(clase: Clase):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar si el instructor, actividad y turno existen (usando JOINs)
            query_verify = """
                SELECT 
                    i.ci AS instructor_ci, 
                    a.id AS actividad_id, 
                    t.id AS turno_id
                FROM 
                    instructores i
                JOIN 
                    actividades a ON a.id = %s
                JOIN 
                    turnos t ON t.id = %s
                WHERE 
                    i.ci = %s
            """
            cursor.execute(query_verify, (clase.id_actividad, clase.id_turno, clase.ci_instructor))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(
                    status_code=400, 
                    detail="Instructor, actividad o turno no válidos"
                )

            # Verificar si ya existe una clase en ese turno para el instructor
            query_check = """
                SELECT * FROM clase 
                WHERE ci_instructor = %s AND id_turno = %s
            """
            cursor.execute(query_check, (clase.ci_instructor, clase.id_turno))
            existing_clase = cursor.fetchone()

            if existing_clase:
                raise HTTPException(
                    status_code=400,
                    detail="El instructor ya tiene una clase en este turno"
                )

            # Crear la clase
            query_insert = """
                INSERT INTO clase (ci_instructor, id_actividad, id_turno, dictada)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(
                query_insert,
                (clase.ci_instructor, clase.id_actividad, clase.id_turno, clase.dictada),
            )
            connection.commit()

            # Obtener el ID generado automáticamente
            clase_id = cursor.lastrowid
            return {"message": "Clase creada exitosamente", "clase_id": clase_id}
    finally:
        connection.close()
        
@app.get("/instructores/")
async def get_instructores():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT ci, nombre FROM instructores")
            instructores = cursor.fetchall()
            return instructores
    finally:
        connection.close()
        
@app.get("/turnos/")
async def get_turnos():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Convertir los segundos a formato HH:MM:SS
            cursor.execute("""
                SELECT id, 
                       SEC_TO_TIME(hora_inicio) AS hora_inicio, 
                       SEC_TO_TIME(hora_fin) AS hora_fin
                FROM turnos
            """)
            turnos = cursor.fetchall()
            return [{"id": turno[0], "hora_inicio": turno[1], "hora_fin": turno[2]} for turno in turnos]
    finally:
        connection.close()
        
        
@app.post("/inscripciones/")
async def inscripciones(data: dict):
    """
    Verifica si la clase existe, y si no, la crea. Luego inscribe al alumno.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Extraer datos del request
            ci_alumno = data["ci_alumno"]
            id_actividad = data["id_actividad"]
            ci_instructor = data["ci_instructor"]
            id_turno = data["id_turno"]  # Usamos el ID del turno directamente
            id_equipamiento = data.get("id_equipamiento", None)

            # Validar si el instructor ya tiene otra clase en este turno
            query_instructor_turno = """
                SELECT * FROM clase
                WHERE ci_instructor = %s AND id_turno = %s
            """
            cursor.execute(query_instructor_turno, (ci_instructor, id_turno))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="El instructor ya tiene una clase en este turno"
                )

            # Validar si el alumno ya está inscrito en otra clase en este turno
            query_alumno_turno = """
                SELECT * FROM alumno_clase ac
                JOIN clase c ON ac.id_clase = c.id
                WHERE ac.ci_alumno = %s AND c.id_turno = %s
            """
            cursor.execute(query_alumno_turno, (ci_alumno, id_turno))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="El alumno ya está inscrito en otra clase en este turno"
                )

            # Validar si ya existe una clase con el mismo instructor, actividad y turno
            query_clase_existente = """
                SELECT id FROM clase
                WHERE ci_instructor = %s AND id_actividad = %s AND id_turno = %s
            """
            cursor.execute(query_clase_existente, (ci_instructor, id_actividad, id_turno))
            clase_existente = cursor.fetchone()

            if not clase_existente:
                # Crear la clase si no existe
                query_crear_clase = """
                    INSERT INTO clase (ci_instructor, id_actividad, id_turno, dictada)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_crear_clase, (ci_instructor, id_actividad, id_turno, False))
                connection.commit()
                clase_id = cursor.lastrowid
            else:
                clase_id = clase_existente[0]

            # Inscribir al alumno en la clase
            query_inscribir_alumno = """
                INSERT INTO alumno_clase (id_clase, ci_alumno, id_equipamiento)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_inscribir_alumno, (clase_id, ci_alumno, id_equipamiento))
            connection.commit()

            return {"message": "Alumno inscrito exitosamente en la clase", "id_clase": clase_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        connection.close()

@app.post("/equipamientos/")
async def crear_equipamiento(equipamiento: EquipamientoCreate):
    """
    Crea un nuevo registro en la tabla `equipamiento`.
    Valida que `id_actividad` exista en la tabla `actividades`.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar si la actividad existe
            cursor.execute("SELECT id FROM actividades WHERE id = %s", (equipamiento.id_actividad,))
            actividad = cursor.fetchone()
            if not actividad:
                raise HTTPException(status_code=404, detail="Actividad no encontrada")

            # Insertar el nuevo equipamiento
            cursor.execute(
                """
                INSERT INTO equipamiento (id_actividad, descripcion, costo)
                VALUES (%s, %s, %s)
                """,
                (equipamiento.id_actividad, equipamiento.descripcion, equipamiento.costo),
            )
            connection.commit()

            # Obtener el ID generado automáticamente
            nuevo_id = cursor.lastrowid
            return {
                "message": "Equipamiento creado exitosamente",
                "id": nuevo_id,
                "id_actividad": equipamiento.id_actividad,
                "descripcion": equipamiento.descripcion,
                "costo": equipamiento.costo
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el equipamiento: {str(e)}")
    finally:
        connection.close()
        
@app.delete("/equipamientos/{equipamiento_id}")
async def eliminar_equipamiento(equipamiento_id: int):
    """
    Elimina un registro de la tabla `equipamiento` por su ID.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar si el equipamiento existe
            cursor.execute("SELECT id FROM equipamiento WHERE id = %s", (equipamiento_id,))
            equipamiento = cursor.fetchone()
            if not equipamiento:
                raise HTTPException(status_code=404, detail="Equipamiento no encontrado")

            # Eliminar el equipamiento
            cursor.execute("DELETE FROM equipamiento WHERE id = %s", (equipamiento_id,))
            connection.commit()

            return {
                "message": "Equipamiento eliminado exitosamente",
                "id": equipamiento_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el equipamiento: {str(e)}")
    finally:
        connection.close()



        
@app.get("/clases/")
async def obtener_clases():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM clase")
            clases = cursor.fetchall()
            return [{"id": c[0], "ci_instructor": c[1], "id_actividad": c[2], "id_turno": c[3], "dictada": c[4]} for c in clases]
    finally:
        connection.close()
@app.get("/equipamientos/")
async def obtener_equipamientos():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM equipamiento")
            equipamientos = cursor.fetchall()
            return [{"id": e[0], "id_actividad": e[1], "descripcion": e[2], "costo": float(e[3])} for e in equipamientos]
    finally:
        connection.close()
        
        
        
@app.post("/instructores/")
async def create_instructor(instructor: InstructorCreate):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar si la CI ya existe
            cursor.execute("SELECT * FROM instructores WHERE ci = %s", (instructor.ci,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Instructor con esta CI ya existe")
            
            # Insertar el nuevo instructor
            cursor.execute(
                "INSERT INTO instructores (ci, nombre, apellido) VALUES (%s, %s, %s)",
                (instructor.ci, instructor.nombre, instructor.apellido)
            )
            connection.commit()
            return {"message": "Instructor creado exitosamente"}
    finally:
        connection.close()
######################################################################
#                           Instructores                             #
######################################################################

# @app.get("/instructores/")
# async def get_instructors():
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Instructor")
#             instructors = cursor.fetchall()
#             if not instructors:
#                 raise HTTPException(status_code=404, detail="No se encontraron instructores")
#             return instructors
#     finally:
#         connection.close()


# @app.get("/instructores/{ci}")
# async def get_instructor(ci: str):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Instructor WHERE ci = %s", (ci,))
#             instructor = cursor.fetchone()
#             if not instructor:
#                 raise HTTPException(status_code=404, detail="Instructor no encontrado")
#             return instructor
#     finally:
#         connection.close()

# @app.put("/instructores/{ci}")
# async def update_instructor(ci: str, nombre: str, apellido: str):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Instructor WHERE ci = %s", (ci,))
#             if not cursor.fetchone():
#                 raise HTTPException(status_code=404, detail="Instructor no encontrado")
            
#             cursor.execute(
#                 "UPDATE Instructor SET nombre = %s, apellido = %s WHERE ci = %s",
#                 (nombre, apellido, ci)
#             )
#             connection.commit()
#             return {"message": "Instructor actualizado exitosamente"}
#     finally:
#         connection.close()

# @app.delete("/instructores/{ci}")
# async def delete_instructor(ci: str):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Instructor WHERE ci = %s", (ci,))
#             if not cursor.fetchone():
#                 raise HTTPException(status_code=404, detail="Instructor no encontrado")
            
#             cursor.execute("DELETE FROM Instructor WHERE ci = %s", (ci,))
#             connection.commit()
#             return {"message": "Instructor eliminado exitosamente"}
#     finally:
#         connection.close()

# ######################################################################
# #                             Turnos                                 #
# ######################################################################

# @app.get("/turnos/")
# async def get_turnos():
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Turno")
#             turnos = cursor.fetchall()
#             if not turnos:
#                 raise HTTPException(status_code=404, detail="No se encontraron turnos")
#             return turnos
#     finally:
#         connection.close()

# @app.post("/turnos/")
# async def create_turno(hora_inicio: str, hora_fin: str):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "INSERT INTO Turno (hora_inicio, hora_fin) VALUES (%s, %s)",
#                 (hora_inicio, hora_fin)
#             )
#             connection.commit()
#             return {"message": "Turno creado exitosamente"}
#     finally:
#         connection.close()

# @app.get("/turnos/{id}")
# async def get_turno(id: int):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Turno WHERE id = %s", (id,))
#             turno = cursor.fetchone()
#             if not turno:
#                 raise HTTPException(status_code=404, detail="Turno no encontrado")
#             return turno
#     finally:
#         connection.close()

# @app.put("/turnos/{id}")
# async def update_turno(id: int, hora_inicio: str, hora_fin: str):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Turno WHERE id = %s", (id,))
#             if not cursor.fetchone():
#                 raise HTTPException(status_code=404, detail="Turno no encontrado")
            
#             cursor.execute(
#                 "UPDATE Turno SET hora_inicio = %s, hora_fin = %s WHERE id = %s",
#                 (hora_inicio, hora_fin, id)
#             )
#             connection.commit()
#             return {"message": "Turno actualizado exitosamente"}
#     finally:
#         connection.close()

# @app.delete("/turnos/{id}")
# async def delete_turno(id: int):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Turno WHERE id = %s", (id,))
#             if not cursor.fetchone():
#                 raise HTTPException(status_code=404, detail="Turno no encontrado")
            
#             cursor.execute("DELETE FROM Turno WHERE id = %s", (id,))
#             connection.commit()
#             return {"message": "Turno eliminado exitosamente"}
#     finally:
#         connection.close()
        
######################################################################
#                             Actividades                             #
######################################################################


# @app.post("/actividades/")
# async def create_actividad(id: int, descripcion: str, costo: float):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "INSERT INTO Actividades (id, descripcion, costo) VALUES (%s, %s, %s)",
#                 (id, descripcion, costo)
#             )
#             connection.commit()
#             return {"message": "Actividad creada exitosamente"}
#     finally:
#         connection.close()


# @app.put("/actividades/{id}")
# async def update_actividad(id: int, descripcion: str, costo: float):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Actividades WHERE id = %s", (id,))
#             if not cursor.fetchone():
#                 raise HTTPException(status_code=404, detail="Actividad no encontrada")
            
#             cursor.execute(
#                 "UPDATE Actividades SET descripcion = %s, costo = %s WHERE id = %s",
#                 (descripcion, costo, id)
#             )
#             connection.commit()
#             return {"message": "Actividad actualizada exitosamente"}
#     finally:
#         connection.close()

# @app.delete("/actividades/{id}")
# async def delete_actividad(id: int):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Actividades WHERE id = %s", (id,))
#             if not cursor.fetchone():
#                 raise HTTPException(status_code=404, detail="Actividad no encontrada")
            
#             cursor.execute("DELETE FROM Actividades WHERE id = %s", (id,))
#             connection.commit()
#             return {"message": "Actividad eliminada exitosamente"}
#     finally:
#         connection.close()

# ######################################################################
# #                               Alumnos                              #
# ######################################################################

# @app.get("/alumnos/")
# async def get_alumnos():
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Alumno")
#             alumnos = cursor.fetchall()
#             if not alumnos:
#                 raise HTTPException(status_code=404, detail="No se encontraron alumnos")
#             return alumnos
#     finally:
#         connection.close()


# @app.get("/alumnos/{ci}")
# async def get_alumno(ci: str):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Alumno WHERE ci = %s", (ci,))
#             alumno = cursor.fetchone()
#             if not alumno:
#                 raise HTTPException(status_code=404, detail="Alumno no encontrado")
#             return alumno
#     finally:
#         connection.close()

# @app.put("/alumnos/{ci}")
# async def update_alumno(ci: str, nombre: str, apellido: str, fecha_nacimiento: str, telefono: str, correo: str):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Alumno WHERE ci = %s", (ci,))
#             if not cursor.fetchone():
#                 raise HTTPException(status_code=404, detail="Alumno no encontrado")
            
#             cursor.execute(
#                 "UPDATE Alumno SET nombre = %s, apellido = %s, fecha_nacimiento = %s, telefono = %s, correo = %s WHERE ci = %s",
#                 (nombre, apellido, fecha_nacimiento, telefono, correo, ci)
#             )
#             connection.commit()
#             return {"message": "Alumno actualizado exitosamente"}
#     finally:
#         connection.close()

# @app.delete("/alumnos/{ci}")
# async def delete_alumno(ci: str):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Alumno WHERE ci = %s", (ci,))
#             if not cursor.fetchone():
#                 raise HTTPException(status_code=404, detail="Alumno no encontrado")
            
#             cursor.execute("DELETE FROM Alumno WHERE ci = %s", (ci,))
#             connection.commit()
#             return {"message": "Alumno eliminado exitosamente"}
#     finally:
#         connection.close()

# ######################################################################
# #                               Clases                               #
# ######################################################################

# @app.get("/clases/")
# async def get_clases():
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Clase")
#             clases = cursor.fetchall()
#             if not clases:
#                 raise HTTPException(status_code=404, detail="No se encontraron clases")
#             return clases
#     finally:
#         connection.close()

# @app.post("/clases/")
# async def create_clase(ci_instructor: str, id_actividad: int, id_turno: int, dictada: bool):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "SELECT * FROM Clase WHERE ci_instructor = %s AND id_turno = %s",
#                 (ci_instructor, id_turno)
#             )
#             if cursor.fetchone():
#                 raise HTTPException(status_code=400, detail="El instructor ya tiene una clase en este turno")
            
#             cursor.execute(
#                 "INSERT INTO Clase (ci_instructor, id_actividad, id_turno, dictada) VALUES (%s, %s, %s, %s)",
#                 (ci_instructor, id_actividad, id_turno, dictada)
#             )
#             connection.commit()
#             return {"message": "Clase creada exitosamente"}
#     finally:
#         connection.close()

# @app.get("/clases/{id}")
# async def get_clase(id: int):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Clase WHERE id = %s", (id,))
#             clase = cursor.fetchone()
#             if not clase:
#                 raise HTTPException(status_code=404, detail="Clase no encontrada")
#             return clase
#     finally:
#         connection.close()

# @app.put("/clases/{id}")
# async def update_clase(id: int, ci_instructor: str, id_actividad: int, id_turno: int, dictada: bool):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Clase WHERE id = %s", (id,))
#             if not cursor.fetchone():
#                 raise HTTPException(status_code=404, detail="Clase no encontrada")
            
#             cursor.execute(
#                 "UPDATE Clase SET ci_instructor = %s, id_actividad = %s, id_turno = %s, dictada = %s WHERE id = %s",
#                 (ci_instructor, id_actividad, id_turno, dictada, id)
#             )
#             connection.commit()
#             return {"message": "Clase actualizada exitosamente"}
#     finally:
#         connection.close()

# @app.delete("/clases/{id}")
# async def delete_clase(id: int):
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM Clase WHERE id = %s", (id,))
#             clase = cursor.fetchone()
#             if not clase:
#                 raise HTTPException(status_code=404, detail="Clase no encontrada")
            
#             if clase[3]:  # Asume que `dictada` está en la posición 3
#                 raise HTTPException(status_code=400, detail="No se puede eliminar una clase dictada")
            
#             cursor.execute("DELETE FROM Clase WHERE id = %s", (id,))
#             connection.commit()
#             return {"message": "Clase eliminada exitosamente"}
#     finally:
#         connection.close()
