import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Planificador FCE UBA", layout="wide", initial_sidebar_state="expanded")

# --- DATA: PLANES DE ESTUDIO (Extraído de tus fotos) ---
# Definimos el Primer Tramo (Común a casi todas)
primer_tramo_ids = [241, 242, 243, 244, 245, 246]
materias_data = {
    241: {"nombre": "Análisis Matemático I", "tramo": 1},
    242: {"nombre": "Economía", "tramo": 1},
    243: {"nombre": "Sociología", "tramo": 1},
    244: {"nombre": "Metodología de las Cs. Soc.", "tramo": 1},
    245: {"nombre": "Álgebra", "tramo": 1},
    246: {"nombre": "Hist. Econ. y Soc. Gral.", "tramo": 1},
    # Segundo Tramo - Contador
    248: {"nombre": "Estadística I", "tramo": 2, "corr": [241], "carrera": "Contador"},
    247: {"nombre": "Teoría Contable", "tramo": 2, "corr": [242], "carrera": "Contador"},
    250: {"nombre": "Microeconomía I", "tramo": 2, "corr": [242], "carrera": "Contador"},
    249: {"nombre": "Hist. Econ. y Soc. Arg.", "tramo": 2, "corr": [246], "carrera": "Contador"},
    251: {"nombre": "Instituciones de Dcho. Público", "tramo": 2, "corr": [244], "carrera": "Contador"},
    252: {"nombre": "Administración General", "tramo": 2, "corr": [243], "carrera": "Contador"},
    276: {"nombre": "Cálculo Financiero", "tramo": 2, "corr": [248], "carrera": "Contador"},
    351: {"nombre": "Sistemas Contables", "tramo": 2, "corr": [247], "carrera": "Contador"},
    353: {"nombre": "Sistemas de Costos", "tramo": 2, "corr": [247], "carrera": "Contador"},
    274: {"nombre": "Sistemas Administrativos", "tramo": 2, "corr": [252], "carrera": "Contador"},
    279: {"nombre": "Adm. Financiera", "tramo": 2, "corr": [276], "carrera": "Contador"},
}

# --- DATA: OFERTA ACADÉMICA (Extraído de tus capturas del PDF) ---
oferta_real = [
    # Administracion General (252)
    {"id": 252, "curso": "Grondona (1)", "dias": "Lu/Ju", "horario": "19-21", "sede": "Paternal"},
    {"id": 252, "curso": "Kastika (8)", "dias": "Lu/Ju", "horario": "07-09", "sede": "San Isidro"},
    {"id": 252, "curso": "Moroni (11)", "dias": "Lu/Ju", "horario": "07-09", "sede": "Paternal"},
    {"id": 252, "curso": "Kastika (98)", "dias": "Ma", "horario": "13-15", "sede": "Virtual"},
    # Sistemas Administrativos (274)
    {"id": 274, "curso": "Alcain (1)", "dias": "Lu/Ju", "horario": "17-19", "sede": "Cordoba"},
    {"id": 274, "curso": "Chahin (14)", "dias": "Lu/Ju", "horario": "21-23", "sede": "Cordoba"},
    {"id": 274, "curso": "Gilli (18)", "dias": "Lu/Ju", "horario": "09-11", "sede": "Cordoba"},
    # Administracion Financiera (279)
    {"id": 279, "curso": "Aire (8)", "dias": "Ma/Vi/Sa", "horario": "19-21", "sede": "Cordoba"},
    {"id": 279, "curso": "Fernandez (13)", "dias": "Ma/Vi/Sa", "horario": "17-19", "sede": "Cordoba"},
]

# --- INTERFAZ ---
st.sidebar.image("https://www.economicas.uba.ar/wp-content/uploads/2016/03/logo-fce-300x127.png", width=150)
st.title("🛡️ Asistente de Inscripción FCE UBA")

carrera = st.sidebar.selectbox("Seleccioná tu carrera:", ["Contador Público", "Lic. en Administración", "Lic. en Sistemas"])

st.sidebar.subheader("Paso 1: ¿Qué ya aprobaste?")
aprobadas_codes = []
# Primer tramo
with st.sidebar.expander("Primer Tramo (CBC/FCE)"):
    for code in primer_tramo_ids:
        if st.checkbox(f"{materias_data[code]['nombre']} ({code})", key=f"check_{code}"):
            aprobadas_codes.append(code)

primer_tramo_completo = all(c in aprobadas_codes for c in primer_tramo_ids)

# Segundo tramo
with st.sidebar.expander("Segundo Tramo / Profesional"):
    if not primer_tramo_completo:
        st.warning("Debés completar el 1er tramo para marcar estas.")
    for code, info in materias_data.items():
        if info["tramo"] == 2:
            if st.checkbox(f"{info['nombre']} ({code})", key=f"check_{code}", disabled=not primer_tramo_completo):
                aprobadas_codes.append(code)

# --- FILTROS DE PREFERENCIA ---
st.sidebar.subheader("Paso 2: Preferencias de Cursada")
sedes = st.sidebar.multiselect("Sedes preferidas:", ["Cordoba", "Paternal", "San Isidro", "Pilar", "Avellaneda", "Virtual"], default=["Cordoba", "Virtual"])
dias_libres = st.sidebar.multiselect("Días que NO podés cursar:", ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa"])

# --- RESULTADOS ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Materias Habilitadas")
    habilitadas = []
    
    for code, info in materias_data.items():
        if code in aprobadas_codes:
            continue
            
        # Lógica de correlatividades
        if info["tramo"] == 2 and not primer_tramo_completo:
            continue
            
        if "corr" in info:
            if all(c in aprobadas_codes for c in info["corr"]):
                habilitadas.append(code)
                st.success(f"**{info['nombre']}** ({code})")
        elif info["tramo"] == 1:
            habilitadas.append(code)
            st.info(f"**{info['nombre']}** ({code})")

with col2:
    st.header("Cursos Disponibles")
    st.caption("Filtrados por tus correlativas y sedes")
    
    cursos_finales = []
    for c in oferta_real:
        if c["id"] in habilitadas and c["sede"] in sedes:
            # Filtro básico de días libres
            pasa_filtro_dias = True
            for d in dias_libres:
                if d in c["dias"]:
                    pasa_filtro_dias = False
            
            if pasa_filtro_dias:
                cursos_finales.append({
                    "Materia": materias_data[c["id"]]["nombre"],
                    "Cátedra (Curso)": c["curso"],
                    "Días": c["dias"],
                    "Horario": c["horario"],
                    "Sede": c["sede"]
                })
    
    if cursos_finales:
        st.table(pd.DataFrame(cursos_finales))
    else:
        st.warning("No hay cursos que coincidan con tus filtros o aún no habilitaste materias del tramo profesional.")

st.info("💡 Consejo: Esta app te ayuda a planificar, pero recordá siempre verificar en el sistema de inscripciones (MiEcon) antes de confirmar.")
