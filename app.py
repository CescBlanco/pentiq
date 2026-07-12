import streamlit as st
from database import supabase
from auth import login, crear_usuario

st.title("Resultados de las 5 grandes ligas")

st.write("Mi aplicación de fútbol")
if "usuario" not in st.session_state:

    opcion = st.radio(
        "Selecciona",
        ["Iniciar sesión", "Crear cuenta"]
    )


    if opcion == "Iniciar sesión":

        username = st.text_input("Usuario")
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
                st.success("Bienvenido")
                st.rerun()

            else:
                st.error("Usuario o contraseña incorrectos")



    else:

        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        username = st.text_input("Nombre de usuario")
        password = st.text_input(
            "Contraseña",
            type="password"
        )

        sexo = st.selectbox(
            "Sexo",
            ["Hombre","Mujer","Otro"]
        )

        edad = st.number_input(
            "Edad",
            min_value=1,
            max_value=120
        )

        pais = st.text_input("País")
        email = st.text_input("Email")


        if st.button("Crear cuenta"):

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

            st.success("Usuario creado")
            
respuesta = supabase.table("usuarios").select("*").execute()

st.write(respuesta.data)
