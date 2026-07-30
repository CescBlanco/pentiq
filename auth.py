import bcrypt
from database import supabase
from datetime import datetime

TIEMPO_MAX_SESION = 1800  # 30 minutos en segundos

def crear_usuario( username, password, nombre, apellido, sexo, edad, pais, email):

    if usuario_existe(username):
        raise ValueError("El nombre de usuario ya existe.")

    if email_existe(email):
        raise ValueError("El correo electrónico ya está registrado.")

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    resultado = (
        supabase
        .table("usuarios")
        .insert({
            "username": username,
            "password_hash": password_hash,
            "nombre": nombre,
            "apellido": apellido,
            "sexo": sexo,
            "edad": edad,
            "pais": pais,
            "email": email
        })
        .execute()
    )

    return resultado





def usuario_existe(username):

    usuario = (
        supabase
        .table("usuarios")
        .select("id")
        .eq("username", username)
        .execute()
    )

    return len(usuario.data) > 0

def email_existe(email):

    usuario = (
        supabase
        .table("usuarios")
        .select("id")
        .eq("email", email)
        .execute()
    )

    return len(usuario.data) > 0

def registrar_acceso(usuario_id):

    # Crear registro de sesión
    resultado = (
        supabase
        .table("accesos")
        .insert({
            "usuario_id": usuario_id,
            "ultima_actividad": datetime.now().isoformat()
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


    accesos_actuales = (
        usuario.data[0]["accesos"]
        or 0
    )


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

        # Cerrar sesiones anteriores que quedaron abiertas
        cerrar_accesos_abiertos(datos["id"])


        # Crear nueva sesión
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

# ======================================================
# CERRAR SESIÓN MANUAL
# ======================================================

def cerrar_acceso(acceso_id):

    ahora = datetime.now()


    acceso = (
        supabase
        .table("accesos")
        .select("fecha_acceso, fecha_fin")
        .eq("id", acceso_id)
        .execute()
    )


    if acceso.data[0]["fecha_fin"] is not None:
        return


    fecha_inicio = datetime.fromisoformat(
        acceso.data[0]["fecha_acceso"]
    )


    tiempo = int(
        (ahora - fecha_inicio).total_seconds()
    )


    if tiempo < 0:
        tiempo = 0


    if tiempo > TIEMPO_MAX_SESION:
        tiempo = TIEMPO_MAX_SESION


    supabase.table("accesos").update({

        "fecha_fin": ahora.isoformat(),

        "tiempo_segundos": tiempo

    }).eq(
        "id",
        acceso_id
    ).execute()

# ======================================================
# LIMPIAR SESIONES ABANDONADAS
# ======================================================

def cerrar_accesos_abiertos(usuario_id):

    ahora = datetime.now()


    accesos = (
        supabase
        .table("accesos")
        .select("*")
        .eq("usuario_id", usuario_id)
        .is_("fecha_fin", "null")
        .execute()
    )


    for acceso in accesos.data:

        fecha_inicio = datetime.fromisoformat(
            acceso["fecha_acceso"]
        )


        tiempo = int(
            (ahora - fecha_inicio).total_seconds()
        )


        if tiempo <= 0:

            continue



        if tiempo > TIEMPO_MAX_SESION:

            tiempo = TIEMPO_MAX_SESION


        supabase.table("accesos").update({

            "fecha_fin": ahora.isoformat(),

            "tiempo_segundos": tiempo

        }).eq(
            "id",
            acceso["id"]
        ).execute()


def actualizar_actividad(acceso_id):

    supabase.table("accesos").update({

        "ultima_actividad": datetime.now().isoformat()

    }).eq(

        "id",
        acceso_id

    ).execute()

def sesion_caducada(acceso_id):

    acceso = (
        supabase
        .table("accesos")
        .select("ultima_actividad")
        .eq("id", acceso_id)
        .execute()
    )

    if len(acceso.data) == 0:
        return True

    if acceso.data[0]["ultima_actividad"] is None:
        return True

    ultima = datetime.fromisoformat(
        acceso.data[0]["ultima_actividad"]
    )

    segundos = (
        datetime.now() - ultima
    ).total_seconds()

    return segundos >= TIEMPO_MAX_SESION