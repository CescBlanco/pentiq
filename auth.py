import bcrypt
from database import supabase


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

    supabase.table("accesos").insert({
        "usuario_id": usuario_id
    }).execute()



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

        # Guardamos el acceso
        registrar_acceso(datos["id"])

        # Devolvemos solo los datos necesarios
        return {
            "id": datos["id"],
            "username": datos["username"],
            "nombre": datos["nombre"],
            "apellido": datos["apellido"],
            "pais": datos["pais"]
        }


    return None