import streamlit as st
import pandas as pd

# 1. BASE DE DATOS DE LA FCE (Simulando lo que extraerías del PDF)
materias_fce = [
    {"id": 1, "nombre": "Análisis Matemático I", "correlativas": [], "puntos": 4},
    {"id": 2, "nombre": "Economía", "correlativas": [], "puntos": 4},
    {"id": 3, "nombre": "Sistemas Administrativos", "correlativas": [1, 2], "puntos": 4},
    {"id": 4, "nombre": "Estadística I", "correlativas": [1], "puntos": 6},
    {"id": 5, "nombre": "Contabilidad II", "correlativas": [2, 3], "puntos": 6},
    {"id": 6, "nombre": "Microeconomía I", "correlativas": [2, 4], "puntos": 6},
]

# Oferta de cursos (Horarios simulados)
oferta_cursos = [
    {"materia_id": 3, "curso": "Cátedra Perez", "dias": "Lu-Ju", "horario": "09:00-11:00", "sede": "Córdoba"},
    {"materia_id": 3, "curso": "Cátedra Garcia", "dias": "Ma-Vi", "horario": "17:00-19:00", "sede": "Córdoba"},
    {"materia_id": 4, "curso": "Cátedra Gomez", "dias": "Lu-Ju", "horario": "07:00-09:00", "sede": "Paternal"},
    {"materia_id": 5, "curso": "Cátedra Lopez", "dias": "Mi-Sa", "horario": "09:00-11:00", "sede": "Córdoba"},
]

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente FCE UBA", layout="wide")
st.title("🎓 FCE UBA - Planificador de Cuatrimestre")

# Sidebar: Perfil del Alumno
st.sidebar.header("Mi Historial Académico")
materias_nombres = [m["nombre"] for m in materias_fce]
aprobadas = st.sidebar.multiselect("Materias ya aprobadas:", materias_nombres)

aprobadas_ids = [m["id"] for m in materias_fce if m["nombre"] in aprobadas]

st.sidebar.header("Preferencias")
sedes_preferidas = st.sidebar.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro"], default=["Córdoba"])

# --- PANTALLA PRINCIPAL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Materias que podés cursar")
    posibles = []
    for m in materias_fce:
        if m["nombre"] in aprobadas: continue
        puede = all(corr in aprobadas_ids for corr in m["correlativas"])
        if puede:
            posibles.append(m)
            st.success(f"✅ **{m['nombre']}**")
        else:
            st.error(f"❌ **{m['nombre']}** (Faltan correlativas)")

with col2:
    st.subheader("2. Oferta disponible")
    ids_posibles = [m["id"] for m in posibles]
    cursos_filtrados = [c for c in oferta_cursos if c["materia_id"] in ids_posibles and c["sede"] in sedes_preferidas]

    if cursos_filtrados:
        df = pd.DataFrame(cursos_filtrados)
        st.table(df[["curso", "dias", "horario", "sede"]])
    else:
        st.info("Seleccioná materias aprobadas para ver qué podés cursar.")
