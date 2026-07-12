import streamlit as st

from auth import login, crear_usuario


st.set_page_config(
    page_title="Resultados fútbol",
    page_icon="⚽"
)


st.title("⚽ Resultados de las 5 grandes ligas")


# ----------------------------
# SI NO ESTÁ LOGUEADO
# ----------------------------

if "usuario" not in st.session_state:


    opcion = st.radio(
        "Selecciona una opción",
        [
            "Iniciar sesión",
            "Crear cuenta"
        ]
    )


    # ----------------------------
    # LOGIN
    # ----------------------------

    if opcion == "Iniciar sesión":


        username = st.text_input(
            "Usuario"
        )


        password = st.text_input(
            "Contraseña",
            type="password"
        )


        if st.button("Entrar"):


            usuario = login(
                username,
                password
            )


            if usuario:

                st.session_state.usuario = usuario

                st.success(
                    f"Bienvenido {usuario['nombre']}"
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


        st.subheader(
            "Crear nueva cuenta"
        )


        nombre = st.text_input(
            "Nombre"
        )


        apellido = st.text_input(
            "Apellido"
        )


        username = st.text_input(
            "Nombre de usuario"
        )


        password = st.text_input(
            "Contraseña",
            type="password"
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
            max_value=120
        )


        pais = st.text_input(
            "País"
        )


        email = st.text_input(
            "Correo electrónico"
        )



        if st.button("Crear cuenta"):


            try:

                crear_usuario(
                    username,
                    password,
                    nombre,
                    apellido,
                    sexo,
                    edad,
                    pais,
                    email
                )


                st.success(
                    "Usuario creado correctamente"
                )


            except Exception as e:

                st.error(
                    "No se pudo crear el usuario"
                )



# ----------------------------
# SI ESTÁ LOGUEADO
# ----------------------------

else:


    usuario = st.session_state.usuario


    # Sidebar

    st.sidebar.title(
        "Perfil"
    )


    st.sidebar.write(
        f"👤 {usuario['nombre']} {usuario['apellido']}"
    )


    st.sidebar.write(
        f"🌍 {usuario['pais']}"
    )



    if st.sidebar.button(
        "Cerrar sesión"
    ):

        del st.session_state.usuario

        st.rerun()



    # Página privada

    st.subheader(
        "🏠 Inicio"
    )


    st.write(
        f"Bienvenido {usuario['nombre']}"
    )


    st.info(
        "Aquí aparecerán los resultados de Premier League, LaLiga, Serie A, Bundesliga y Ligue 1."
    )