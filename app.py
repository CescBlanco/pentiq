import streamlit as st
from database import supabase


st.title("Resultados de las 5 grandes ligas")

st.write("Mi aplicación de fútbol")

respuesta = supabase.table("usuarios").select("*").execute()

st.write(respuesta.data)
