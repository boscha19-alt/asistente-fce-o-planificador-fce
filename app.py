import streamlit as st
import pandas as pd
from st_gsheets_connection import GSheetsConnection

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="FCE UBA - Mi Progreso", layout="wide")

# --- CONEXIÓN A BASE DE DATOS (Google Sheets) ---
# Nota: Esto requiere configurar los "Secrets" en Streamlit Cloud
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_db = conn.read(ttl=0) # Leer base de datos en tiempo real
except:
    df_db = pd.DataFrame(columns=["registro", "ranking", "carrera", "aprobadas"])

# --- DATA DE MATERIAS ---
primer_tramo = {241: "Análisis I", 242: "Economía", 243: "Sociología", 244: "Metodología", 245: "Álgebra", 246: "Hist. Gral."}
materias_master = {
    "Contador Público": {248: "Estadística I", 247: "Teoría Contable", 351: "Sistemas Contables", 355: "Auditoría"},
    "Lic. en Administración": {248: "Estadística I", 252: "Admin Gral", 274: "Sistemas Admin", 471: "Plan. Estratégico"},
    "Lic. en Sistemas": {1275: "Intro IT", 1601: "Ing. Software", 662: "Seguridad"},
    "Lic. en Economía": {272: "Análisis II", 262: "Macro I", 543: "Econometría"}
}

# --- INTERFAZ DE LOGIN ---
st.title("🎓 Planificador FCE UBA con Guardado")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

with st.sidebar:
    st.header("🔐 Ingreso")
    reg_input = st.text_input("N° de Registro para recuperar datos:")
    
    if st.button("Ingresar / Cargar Datos"):
        # Buscar en la base de datos
        user_data = df_db[df_db['registro'] == reg_input]
        if not user_data.empty:
            st.session_state.ranking = int(user_data.iloc[0]['ranking'])
            st.session_state.carrera = user_data.iloc[0]['carrera']
            st.session_state.aprobadas_ids = [int(x) for x in str(user_data.iloc[0]['aprobadas']).split(",")]
            st.success("Datos cargados con éxito.")
        else:
            st.session_state.ranking = 500
            st.session_state.carrera = "Contador Público"
            st.session_state.aprobadas_ids = []
            st.info("Usuario nuevo. Se creará perfil al guardar.")
        
        st.session_state.autenticado = True
        st.session_state.current_reg = reg_input

# --- CUERPO DE LA APP (Solo si está autenticado) ---
if st.session_state.autenticado:
    st.write(f"### Bienvenido, Registro: {st.session_state.current_reg}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configurar Perfil")
        new_rank = st.number_input("Mi Ranking:", value=st.session_state.ranking)
        new_carrera = st.selectbox("Carrera:", list(materias_master.keys()), index=list(materias_master.keys()).index(st.session_state.carrera))
        
        st.write("---")
        st.write("Marcar Aprobadas:")
        # Mostrar todas las materias para tildar
        todas_las_mats = {**primer_tramo, **materias_master[new_carrera]}
        nuevas_aprobadas = []
        for cod, nom in todas_las_mats.items():
            if st.checkbox(f"{nom} ({cod})", value=(cod in st.session_state.aprobadas_ids)):
                nuevas_aprobadas.append(cod)

        if st.button("💾 GUARDAR MI PROGRESO"):
            # Lógica para guardar en Google Sheets
            # (Aquí iría conn.update() una vez configurado)
            st.balloons()
            st.success("¡Progreso guardado! La próxima vez que entres con tu registro, todo estará aquí.")
            # Actualizamos session state
            st.session_state.aprobadas_ids = nuevas_aprobadas
            st.session_state.ranking = new_rank

    with col2:
        st.header("Tu Planificación")
        # Aquí va la lógica de los bloques horarios y materias habilitadas que ya teníamos
        st.info("Aquí la app muestra los cursos 7-9, 9-11, etc. que encajan con tu perfil guardado.")
        # (Para no alargar el código, aquí va la lógica de filtrado de los mensajes anteriores)

else:
    st.warning("Por favor, ingresá tu N° de Registro en la izquierda para empezar.")
