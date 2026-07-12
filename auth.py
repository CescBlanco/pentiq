import bcrypt
from database import supabase
from datetime import datetime

def crear_usuario(username, password, nombre, apellido, sexo, edad, pais, email):

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


    resultado = supabase.table("usuarios").insert({
        "username": username,
        "password_hash": password_hash,
        "nombre": nombre,
        "apellido": apellido,
        "sexo": sexo,
        "edad": edad,
        "pais": pais,
        "email": email
    }).execute()


    return resultado



def registrar_acceso(usuario_id):

    # Crear registro de sesión
    resultado = (
        supabase
        .table("accesos")
        .insert({
            "usuario_id": usuario_id
        })
        .execute()
    )


    # Guardamos el id de esta sesión
    acceso_id = resultado.data[0]["id"]


    # Obtener accesos actuales del usuario
    usuario = (
        supabase
        .table("usuarios")
        .select("accesos")
        .eq("id", usuario_id)
        .execute()
    )


    accesos_actuales = usuario.data[0]["accesos"]


    # Sumar uno al contador total
    supabase.table("usuarios").update({
        "accesos": accesos_actuales + 1
    }).eq(
        "id",
        usuario_id
    ).execute()


    # Devolver la sesión creada
    return acceso_id


def login(username, password):

    usuario = (
        supabase
        .table("usuarios")
        .select("*")
        .eq("username", username)
        .execute()
    )


    # Usuario no encontrado
    if len(usuario.data) == 0:
        return None


    datos = usuario.data[0]


    password_correcta = bcrypt.checkpw(
        password.encode("utf-8"),
        datos["password_hash"].encode("utf-8")
    )


    if password_correcta:

        acceso_id = registrar_acceso(datos["id"])

        return {
            "id": datos["id"],
            "username": datos["username"],
            "nombre": datos["nombre"],
            "apellido": datos["apellido"],
            "pais": datos["pais"],
            "acceso_id": acceso_id
        }


    return None

def cerrar_acceso(acceso_id):

    ahora = datetime.now()


    acceso = (
        supabase
        .table("accesos")
        .select("fecha_acceso")
        .eq("id", acceso_id)
        .execute()
    )


    fecha_inicio = datetime.fromisoformat(
        acceso.data[0]["fecha_acceso"]
    )


    tiempo = int(
        (ahora - fecha_inicio).total_seconds()
    )


    supabase.table("accesos").update({
        "fecha_fin": ahora.isoformat(),
        "tiempo_segundos": tiempo
    }).eq(
        "id",
        acceso_id
    ).execute()