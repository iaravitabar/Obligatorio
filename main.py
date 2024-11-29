from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import pymysql
from typing import List
import datetime
from pydantic import BaseModel
from database import get_connection
from schemas import Clase, Alumno, Login, AlumnoClase, EquipamientoCreate, InstructorCreate
from datetime import datetime


now = datetime.now()

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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


@app.post("/login/")
async def login(request : dict):
    print("hola")
    ci = request.ci
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT ci FROM alumnos WHERE ci = %s", (ci,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            return {"message": "Inicio de sesión exitoso"}
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
        
@app.post("/instructores/")
async def create_instructor(instructor: InstructorCreate):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            #si ci ya existe
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

@app.put("/instructores/{ci}")
async def update_instructor(ci: str, instructor: InstructorCreate):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE instructores SET nombre = %s, apellido = %s WHERE ci = %s",
                           (instructor.nombre, instructor.apellido, ci))
            connection.commit()
            return {"message": "Instructor actualizado exitosamente"}
    finally:
        connection.close()

@app.delete("/instructores/{ci}")
async def delete_instructor(ci: str):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM instructores WHERE ci = %s", (ci,))
            connection.commit()
            return {"message": "Instructor eliminado exitosamente"}
    finally:
        connection.close()
        
######################################################################
#ABM turnos
######################################################################
@app.get("/turnos/")
async def get_turnos():  
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Convertir  segundos a formato HH:MM:SS
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
        
@app.post("/turnos/")
async def create_turno(turno: dict):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO turnos (hora_inicio, hora_fin) VALUES (%s, %s)",
                           (turno["hora_inicio"], turno["hora_fin"]))
            connection.commit()
            return {"message": "Turno creado exitosamente"}
    finally:
        connection.close()

@app.put("/turnos/{id}")
async def update_turno(id: int, turno: dict):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE turnos SET hora_inicio = %s, hora_fin = %s WHERE id = %s",
                           (turno["hora_inicio"], turno["hora_fin"], id))
            connection.commit()
            return {"message": "Turno actualizado exitosamente"}
    finally:
        connection.close()

@app.delete("/turnos/{id}")
async def delete_turno(id: int):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM turnos WHERE id = %s", (id,))
            connection.commit()
            return {"message": "Turno eliminado exitosamente"}
    finally:
        connection.close()

######################################################################
#ABM actividades
######################################################################

@app.get("/actividades/")
async def get_actividades():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM actividades")
            actividades = cursor.fetchall()
            return [{"id": a[0], "descripcion": a[1], "costo": float(a[2])} for a in actividades]
    finally:
        connection.close()

@app.post("/actividades/")
async def create_actividad(actividad: dict):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO actividades (descripcion, costo) VALUES (%s, %s)",
                           (actividad["descripcion"], actividad["costo"]))
            connection.commit()
            return {"message": "Actividad creada exitosamente"}
    finally:
        connection.close()

@app.put("/actividades/{id}")
async def update_actividad(id: int, actividad: dict):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE actividades SET descripcion = %s, costo = %s WHERE id = %s",
                           (actividad["descripcion"], actividad["costo"], id))
            connection.commit()
            return {"message": "Actividad actualizada exitosamente"}
    finally:
        connection.close()

@app.delete("/actividades/{id}")
async def delete_actividad(id: int):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM actividades WHERE id = %s", (id,))
            connection.commit()
            return {"message": "Actividad eliminada exitosamente"}
    finally:
        connection.close()
        
######################################################################
#ABM alumnos
######################################################################
@app.get("/alumnos/")
async def get_alumnos():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM alumnos")
            alumnos = cursor.fetchall()
            return [{"ci": a[0], "nombre": a[1], "apellido": a[2], "fecha_nacimiento": a[3], "telefono": a[4], "correo": a[5]} for a in alumnos]
    finally:
        connection.close()

@app.post("/alumnos/")
async def create_alumno(alumno: Alumno):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # si la cédula ya existe
            cursor.execute("SELECT ci FROM alumnos WHERE ci = %s", (alumno.ci,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Alumno con esta CI ya existe")
            
            # Ins nuevo alumno
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

@app.post("/alumnos/")
async def create_alumno(alumno: Alumno):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO alumnos (ci, nombre, apellido, fecha_nacimiento, telefono, correo) VALUES (%s, %s, %s, %s, %s, %s)",
                           (alumno.ci, alumno.nombre, alumno.apellido, alumno.fecha_nacimiento, alumno.telefono, alumno.correo))
            connection.commit()
            return {"message": "Alumno creado exitosamente"}
    finally:
        connection.close()


@app.put("/alumnos/{ci}")
async def update_alumno(ci: str, alumno: Alumno):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE alumnos SET nombre = %s, apellido = %s, fecha_nacimiento = %s, telefono = %s, correo = %s WHERE ci = %s",
                           (alumno.nombre, alumno.apellido, alumno.fecha_nacimiento, alumno.telefono, alumno.correo, ci))
            connection.commit()
            return {"message": "Alumno actualizado exitosamente"}
    finally:
        connection.close()

@app.delete("/alumnos/{ci}")
async def delete_alumno(ci: str):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM alumnos WHERE ci = %s", (ci,))
            connection.commit()
            return {"message": "Alumno eliminado exitosamente"}
    finally:
        connection.close()

######################################################################

@app.post("/inscripciones/")
async def inscripciones(data: dict):
    """
    Verifica si la clase existe, y si no, la crea. Luego inscribe a los alumnos en la clase existente.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Extraer datos
            alumnos = data["alumnos"]  # Lista de alumnos (ci)
            id_actividad = data["id_actividad"]
            ci_instructor = data["ci_instructor"]
            id_turno = data["id_turno"]
            id_equipamiento = data.get("id_equipamiento")  # Puede ser None

            # Validar si ya existe una clase con el mismo instructor, actividad y turno
            query_clase_existente = """
                SELECT id FROM clase
                WHERE ci_instructor = %s AND id_actividad = %s AND id_turno = %s
            """
            cursor.execute(query_clase_existente, (ci_instructor, id_actividad, id_turno))
            clase_existente = cursor.fetchone()

            if not clase_existente:
                # Crear la clas
                query_crear_clase = """
                    INSERT INTO clase (ci_instructor, id_actividad, id_turno, dictada)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_crear_clase, (ci_instructor, id_actividad, id_turno, False))
                connection.commit()
                clase_id = cursor.lastrowid
            else:
                # Usar la clase existente
                clase_id = clase_existente[0]

            # Inscribir a los alumnos en la clase existente
            for ci_alumno in alumnos:
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
                        detail=f"El alumno con CI {ci_alumno} ya está inscrito en otra clase en este turno."
                    )

                # Inscribir al alumno
                query_inscribir_alumno = """
                    INSERT INTO alumno_clase (id_clase, ci_alumno, id_equipamiento)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(
                    query_inscribir_alumno,
                    (clase_id, ci_alumno, id_equipamiento if id_equipamiento else None), #equip opcional
                )
                connection.commit()

            return {"message": "Alumnos inscritos exitosamente en la clase", "id_clase": clase_id}
    except HTTPException as e:
        raise e
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
            #si actividad existe
            cursor.execute("SELECT id FROM actividades WHERE id = %s", (equipamiento.id_actividad,))
            actividad = cursor.fetchone()
            if not actividad:
                raise HTTPException(status_code=404, detail="Actividad no encontrada")

            # Ins nuevo equipamiento
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
            # si equip existe
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
           
        
#########MODIFICAR CLASES##########

@app.put("/clases/{id_clase}/")
async def modificar_clase(id_clase: int, data: dict):
    """
    Modificar instructor, turno y alumnos de una clase.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Obtener horario de la clase
            query_horario_clase = """
                SELECT t.horario_inicio, t.horario_fin
                FROM clase c
                JOIN turnos t ON c.id_turno = t.id
                WHERE c.id = %s
            """
            cursor.execute(query_horario_clase, (id_clase,))
            horario = cursor.fetchone()

            #validar que la consulta devolvió datos
            if not horario:
                raise HTTPException(status_code=404, detail="Clase o turno no encontrado.")

            #acceder a las columnas como un diccionario
            hora_inicio = horario["hora_inicio"]
            hora_fin = horario["hora_fin"]

            #validar si la clase está en horario activo
            now = datetime.now().time()
            if hora_inicio <= now <= hora_fin:
                raise HTTPException(
                    status_code=400,
                    detail="No se puede modificar la clase durante su horario activo."
                )

            #modi instru
            if "ci_instructor" in data:
                query_modificar_instructor = """
                    UPDATE clase
                    SET ci_instructor = %s
                    WHERE id = %s
                """
                cursor.execute(query_modificar_instructor, (data["ci_instructor"], id_clase))

            #modi turno
            if "id_turno" in data:
                query_modificar_turno = """
                    UPDATE clase
                    SET id_turno = %s
                    WHERE id = %s
                """
                cursor.execute(query_modificar_turno, (data["id_turno"], id_clase))

            #agregar alumnos
            if "agregar_alumnos" in data:
                for ci_alumno in data["agregar_alumnos"]:
                    query_agregar_alumno = """
                        INSERT INTO alumno_clase (id_clase, ci_alumno)
                        VALUES (%s, %s)
                    """
                    cursor.execute(query_agregar_alumno, (id_clase, ci_alumno))

            #quitar alumnos
            if "quitar_alumnos" in data:
                for ci_alumno in data["quitar_alumnos"]:
                    query_quitar_alumno = """
                        DELETE FROM alumno_clase
                        WHERE id_clase = %s AND ci_alumno = %s
                    """
                    cursor.execute(query_quitar_alumno, (id_clase, ci_alumno))

            connection.commit()
            return {"message": "Clase modificada exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        connection.close()



########MODIFICAR ALUMNOS##########
@app.put("/clases/{id_clase}/alumnos/")
async def modificar_alumnos(id_clase: int, data: dict):
    """
    Agregar o quitar alumnos de una clase grupal.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            #validar si la clase está en horario activo
            query_horario_clase = """
                SELECT t.hora_inicio, t.hora_fin
                FROM clase c
                JOIN turnos t ON c.id_turno = t.id
                WHERE c.id = %s
            """
            cursor.execute(query_horario_clase, (id_clase,))
            horario = cursor.fetchone()

            if not horario:
                raise HTTPException(status_code=404, detail="Clase no encontrada.")

            hora_inicio, hora_fin = horario
            now = datetime.now().time()

            if hora_inicio <= now <= hora_fin:
                raise HTTPException(
                    status_code=400,
                    detail="No se puede modificar la clase durante su horario activo."
                )

            #agregar alumnos
            if "agregar" in data:
                for ci_alumno in data["agregar"]:
                    query_agregar_alumno = """
                        INSERT INTO alumno_clase (id_clase, ci_alumno)
                        VALUES (%s, %s)
                    """
                    cursor.execute(query_agregar_alumno, (id_clase, ci_alumno))

            #quitar alumnos
            if "quitar" in data:
                for ci_alumno in data["quitar"]:
                    query_quitar_alumno = """
                        DELETE FROM alumno_clase
                        WHERE id_clase = %s AND ci_alumno = %s
                    """
                    cursor.execute(query_quitar_alumno, (id_clase, ci_alumno))

            connection.commit()
            return {"message": "Alumnos modificados exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        connection.close()

######################################################################
#reportes
######################################################################

@app.get("/reportes/actividades_mas_ingresos/")
async def actividades_mas_ingresos():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT a.descripcion, SUM(ac.costo + e.costo) AS total_ingresos
                FROM actividades a
                JOIN clase c ON a.id = c.id_actividad
                JOIN alumno_clase ac ON c.id = ac.id_clase
                LEFT JOIN equipamiento e ON ac.id_equipamiento = e.id
                GROUP BY a.descripcion
                ORDER BY total_ingresos DESC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            return [{"actividad": r[0], "total_ingresos": float(r[1])} for r in resultados]
    finally:
        connection.close()

@app.get("/reportes/actividades_mas_alumnos/")
async def actividades_mas_alumnos():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT a.descripcion, COUNT(ac.ci_alumno) AS total_alumnos
                FROM actividades a
                JOIN clase c ON a.id = c.id_actividad
                JOIN alumno_clase ac ON c.id = ac.id_clase
                GROUP BY a.descripcion
                ORDER BY total_alumnos DESC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            return [{"actividad": r[0], "total_alumnos": r[1]} for r in resultados]
    finally:
        connection.close()

@app.get("/reportes/turnos_mas_clases/")
async def turnos_mas_clases():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT t.hora_inicio, t.hora_fin, COUNT(c.id) AS total_clases
                FROM turnos t
                JOIN clase c ON t.id = c.id_turno
                GROUP BY t.hora_inicio, t.hora_fin
                ORDER BY total_clases DESC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            return [{"hora_inicio": str(r[0]), "hora_fin": str(r[1]), "total_clases": r[2]} for r in resultados]
    finally:
        connection.close()