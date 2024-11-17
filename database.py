import mysql.connector 
from mysql.connector import Error

def get_connection():
    try: 
        connection = mysql.connector.connect(
            host='localhost',
            database='obligatorio',
            user= 'root',
            password= 'rootpassword')
        return connection
    except Error as e:
        print("error al conectar a la base de datos:{e}")
        raise e