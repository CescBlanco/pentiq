import streamlit as st
from streamlit_extras.steps import steps
import re

from auth import login, crear_usuario, cerrar_acceso, usuario_existe, email_existe

def comprobar_fuerza_password(password):

    puntos = 0
    requisitos = []

    # Longitud
    if len(password) >= 8:
        puntos += 1
        requisitos.append("✅ Mínimo 8 caracteres")
    else:
        requisitos.append("❌ Mínimo 8 caracteres")


    # Mayúscula
    if re.search(r"[A-Z]", password):
        puntos += 1
        requisitos.append("✅ Una letra mayúscula")
    else:
        requisitos.append("❌ Una letra mayúscula")


    # Minúscula
    if re.search(r"[a-z]", password):
        puntos += 1
        requisitos.append("✅ Una letra minúscula")
    else:
        requisitos.append("❌ Una letra minúscula")


    # Número
    if re.search(r"[0-9]", password):
        puntos += 1
        requisitos.append("✅ Un número")
    else:
        requisitos.append("❌ Un número")


    # Símbolo
    if re.search(r"[@$!%*?&]", password):
        puntos += 1
        requisitos.append("✅ Un símbolo (@$!%*?&)")
    else:
        requisitos.append("❌ Un símbolo (@$!%*?&)")


    return puntos, requisitos

def limpiar_registro():

    st.session_state.registro = {
        "username": "",
        "password": "",
        "nombre": "",
        "apellido": "",
        "sexo": "Hombre",
        "edad": 18,
        "pais": "",
        "email": ""
    }

    # Reiniciar componente steps
    if "registro_steps" in st.session_state:
        del st.session_state["registro_steps"]


st.set_page_config(
    page_title="Resultados fútbol",
    page_icon="⚽",
    layout="centered"
)


st.title("⚽ Resultados de las 5 grandes ligas")


# ======================================================
# INICIALIZAR SESSION STATE
# ======================================================

if "registro" not in st.session_state:

    st.session_state.registro = {
        "username": "",
        "password": "",
        "nombre": "",
        "apellido": "",
        "sexo": "Hombre",
        "edad": 18,
        "pais": "",
        "email": ""
    }

# ======================================================
# USUARIO NO LOGUEADO
# ======================================================
#   
if "usuario" not in st.session_state:

    option = st.segmented_control('\n\n', 
                           ['Iniciar sesión', 'Crear cuenta'], default= 'Iniciar sesión')

    # ----------------------------
    # LOGIN
    # ----------------------------

    if option == "Iniciar sesión":

        with st.form("login"):

            username = st.text_input(
                "Usuario"
            )

            password = st.text_input(
                "Contraseña",
                type="password"
            )

            entrar = st.form_submit_button(
                "Entrar"
            )


        if entrar:


            usuario = login(
                username,
                password
            )


            if usuario:

                st.session_state.usuario = usuario

                st.success(
                    f"Bienvenido {usuario['nombre']} 👋"
                )

                st.rerun()


            else:

                st.error(
                    "Usuario o contraseña incorrectos"
                )



    # ----------------------------
    # REGISTRO
    # ----------------------------

    else:

        izquierda, derecha = st.columns((1, 3))

        with izquierda:

            s = steps(
                [
                    "Acceso",
                    "Datos",
                    "Confirmación"
                ],
                icons=["1", "2", "3"],
                key="registro_steps"
            )

        with derecha:

            # ------------------------------------------
            # PASO 1
            # ------------------------------------------

            with s[0]:

                st.progress(33)
                
                st.subheader("🔐 Datos de acceso")


                username = st.text_input(
                    "Nombre de usuario",
                    value=st.session_state.registro["username"]
                )


                password = st.text_input(
                    "Contraseña",
                    type="password"
                )


                puntos, requisitos = comprobar_fuerza_password(password)


                if password:

                    if puntos <= 2:

                        st.error("🔴 Contraseña débil")

                    elif puntos <= 4:

                        st.warning("🟡 Contraseña media")

                    else:

                        st.success("🟢 Contraseña fuerte")


                    st.progress(
                        puntos / 5
                    )


                    for requisito in requisitos:

                        st.caption(requisito)



                password2 = st.text_input(
                    "Confirmar contraseña",
                    type="password"
                )


                siguiente = st.button(
                    "Siguiente ➜"
                )


                if siguiente:


                    if username.strip() == "":

                        st.error(
                            "Introduce un nombre de usuario."
                        )


                    elif puntos < 5:

                        st.error(
                            "La contraseña debe cumplir todos los requisitos."
                        )


                    elif password != password2:

                        st.error(
                            "Las contraseñas no coinciden."
                        )


                    elif usuario_existe(username):

                        st.error(
                            "Ese usuario ya existe."
                        )


                    else:

                        st.session_state.registro["username"] = username.strip().lower()

                        st.session_state.registro["password"] = password

                        s.next()


            # ------------------------------------------
            # PASO 2
            # ------------------------------------------

            with s[1]:

                st.progress(66)

                with st.form("paso2"):

                    nombre = st.text_input(
                        "Nombre",
                        value=st.session_state.registro["nombre"]
                    )

                    apellido = st.text_input(
                        "Apellido",
                        value=st.session_state.registro["apellido"]
                    )

                    sexo = st.selectbox(
                        "Sexo",
                        [
                            "Hombre",
                            "Mujer",
                            "Otro"
                        ]
                    )

                    edad = st.number_input(
                        "Edad",
                        min_value=1,
                        max_value=120,
                        value=st.session_state.registro["edad"]
                    )

                    pais = st.text_input(
                        "País",
                        value=st.session_state.registro["pais"]
                    )

                    c1, c2 = st.columns(2)

                    with c1:

                        volver = st.form_submit_button(
                            "⬅ Atrás"
                        )

                    with c2:

                        siguiente = st.form_submit_button(
                            "Siguiente ➜"
                        )

                if volver:

                    s.previous()

                if siguiente:

                    if nombre == "" or apellido == "" or pais == "":

                        st.error(
                            "Completa todos los campos."
                        )

                    else:

                        st.session_state.registro["nombre"] = nombre
                        st.session_state.registro["apellido"] = apellido
                        st.session_state.registro["sexo"] = sexo
                        st.session_state.registro["edad"] = edad
                        st.session_state.registro["pais"] = pais

                        s.next()


            # ------------------------------------------
            # PASO 3
            # ------------------------------------------

            with s[2]:

                st.progress(100)

                with st.form("paso3"):

                    email = st.text_input(
                        "Correo electrónico",
                        value=st.session_state.registro["email"]
                    )

                    st.divider()

                    st.subheader("Resumen")

                    st.write(
                        f"**Usuario:** {st.session_state.registro['username']}"
                    )

                    st.write(
                        f"**Nombre:** {st.session_state.registro['nombre']} {st.session_state.registro['apellido']}"
                    )

                    st.write(
                        f"**País:** {st.session_state.registro['pais']}"
                    )

                    c1, c2 = st.columns(2)

                    with c1:

                        volver = st.form_submit_button(
                            "⬅ Atrás"
                        )

                    with c2:

                        crear = st.form_submit_button(
                            "Crear cuenta"
                        )

                if volver:

                    s.previous()

                if crear:

                    if not re.match(
                        r"[^@]+@[^@]+\.[^@]+",
                        email
                    ):

                        st.error(
                            "Introduce un correo válido."
                        )

                    elif email_existe(email):

                        st.error(
                            "Ese correo ya está registrado."
                        )

                    else:

                        st.session_state.registro["email"] = email

                        crear_usuario(
                            st.session_state.registro["username"],
                            st.session_state.registro["password"],
                            st.session_state.registro["nombre"],
                            st.session_state.registro["apellido"],
                            st.session_state.registro["sexo"],
                            st.session_state.registro["edad"],
                            st.session_state.registro["pais"],
                            st.session_state.registro["email"]
                        )

                        usuario = login(
                            st.session_state.registro["username"],
                            st.session_state.registro["password"]
                        )

                        st.session_state.usuario = usuario

                        st.success(
                            "¡Cuenta creada correctamente!"
                        )

                        limpiar_registro()


                        st.rerun()


# ======================================================
# USUARIO LOGUEADO
# ======================================================

else:

    usuario = st.session_state.usuario

    st.sidebar.title("Perfil")

    st.sidebar.write(
        f"👤 {usuario['nombre']} {usuario['apellido']}"
    )

    st.sidebar.write(
        f"🌍 {usuario['pais']}"
    )

    if st.sidebar.button("Cerrar sesión"):

        cerrar_acceso(
            usuario["acceso_id"]
        )

        del st.session_state.usuario

        limpiar_registro()
        
        st.rerun()

    st.subheader("🏠 Inicio")

    st.write(
        f"Bienvenido **{usuario['nombre']}**."
    )

    st.info(
        "Aquí aparecerán los resultados de la Premier League, LaLiga, Serie A, Bundesliga y Ligue 1."
    )