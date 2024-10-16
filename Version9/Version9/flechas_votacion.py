import pymysql
from tkinter import messagebox
from datetime import datetime
import time
from conexion import crear_conexion

partida_id=1
user_id=None

# Get Command ID from the database (comandos_referencia table)
def obtener_id_comando(direccion):
    conexion = crear_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                query = "SELECT ID_comando FROM comandos_referencia WHERE comando = %s"
                cursor.execute(query, (direccion,))
                resultado = cursor.fetchone()
                if resultado:
                    return resultado[0]
                else:
                    print(f"Error: No se encontró el ID para el comando: {direccion}")
                    return None
        except pymysql.MySQLError as e:
            print(f"Error al obtener ID del comando: {e}")
        finally:
            conexion.close()
    return None

# Register the vote using the stored procedure
def registrar_voto(direccion, id_usuario, votacion_activa):
    # Votacion activa no sirve para los esclavos solo para el maestro (falta función sacar tiempo votación)
    if votacion_activa:
        conexion = crear_conexion()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    # Call stored procedure registrar_voto
                    cursor.callproc('registrar_voto', (id_usuario, direccion, partida_id))
                    conexion.commit()
                    print(f"Voto registrado: {direccion} por el usuario {id_usuario}")
            except pymysql.MySQLError as e:
                print(f"Error al registrar el voto: {e}")
            finally:
                conexion.close()
    else:
        messagebox.showerror("Error", "La votación no está activa en este momento. Espere el próximo ciclo.")


# Call the stored procedure to count votes and register the result
def contar_y_registrar_resultado():
    conexion = crear_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                # Call stored procedure contar_y_registrar_resultado
                cursor.callproc('voto_ganador', (partida_id,))
                resultado = cursor.fetchone()
                print(resultado)
                # Check if the result is NULL
                if resultado and resultado[0]:
                    comando_ganador = resultado[0]
                    print(f"Resultado registrado: {comando_ganador}")
                    return comando_ganador
                else:
                    return None

        except pymysql.MySQLError as e:
            print(f"Error al contar los votos: {e}")
            return None
        finally:
            conexion.close()

# Call the stored procedure to clean up the old votes
def limpiar_votos():
    conexion = crear_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                cursor.callproc('limpiar_votos', (partida_id,))
                conexion.commit()
                print("Votos antiguos eliminados.")
        except pymysql.MySQLError as e:
            print(f"Error al limpiar los votos: {e}")
        finally:
            conexion.close()

def votar(direction, id_usuario, votacion_activa):
    registrar_voto(direction, id_usuario, votacion_activa)

def lock_table_votos():
    conexion = crear_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                cursor.execute("LOCK TABLES votos WRITE;")
                conexion.commit()
                print("Table votos locked for writing.")
        except pymysql.MySQLError as e:
            print(f"Error al bloquear la tabla votos: {e}")
        finally:
            conexion.close()

def unlock_table_votos():
    conexion = crear_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                cursor.execute("UNLOCK TABLES;")
                conexion.commit()
                print("Table votos unlocked.")
        except pymysql.MySQLError as e:
            print(f"Error al desbloquear la tabla votos: {e}")
        finally:
            conexion.close()