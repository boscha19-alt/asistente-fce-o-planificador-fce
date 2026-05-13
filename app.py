import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Planificador FCE UBA", layout="wide")

# --- BASE DE DATOS DE MATERIAS POR CARRERA ---
primer_tramo = {
    241: "Análisis Matemático I",
    242: "Economía",
    243: "Sociología",
    244: "Metodología de las Cs. Soc.",
    245: "Álgebra",
    246: "Hist. Econ. y Soc. Gral."
}

planes = {
    "Contador Público": {
        248: {"nombre": "Estadística I", "corr": [241]},
        247: {"nombre": "Teoría Contable", "corr": [242]},
        250: {"nombre": "Microeconomía I", "corr": [242]},
        252: {"nombre": "Administración General", "corr": [243]},
        351: {"nombre": "Sistemas Contables", "corr": [247]},
        276: {"nombre": "Cálculo Financiero", "corr": [248]},
        274: {"nombre": "Sistemas Administrativos", "corr": [252]},
    },
    "Lic. en Administración": {
        248: {"nombre": "Estadística I", "corr": [241]},
        247: {"nombre": "Teoría Contable", "corr": [242]},
        250: {"nombre": "Microeconomía I", "corr": [242]},
        252: {"nombre": "Administración General", "corr": [243]},
        463: {"nombre": "Gestión de Tec. Digitales", "corr": [245]},
        278: {"nombre": "Macroeconomía y Pol. Econ.", "corr": [250]},
    },
    "Lic. en Economía": {
        248: {"nombre": "Estadística I", "corr": [241]},
        250: {"nombre": "Microeconomía I", "corr": [242]},
        272: {"nombre": "Análisis Matemático II", "corr": [241, 245]},
        262: {"nombre": "Macroeconomía I", "corr": [250]},
    },
    "Actuario (Admin/Econ)": {
        248: {"nombre": "Estadística I", "corr": [241]},
        276: {"nombre": "Cálculo Financiero", "corr": [248]},
        277: {"nombre": "Estadística II", "corr": [248]},
        601: {"nombre": "Mat. Financiera y Actuarial", "corr": [276]},
    },
    "Lic. en Sistemas": {
        247: {"nombre": "Teoría Contable", "corr": [242]},
        1275: {"nombre": "Intro a la Tec. de la Inf. y Com.", "corr": [245]},
        248: {"nombre": "Estadística I", "corr": [241]},
        274: {"nombre": "Sistemas Administrativos", "corr": [252]},
    }
}

# --- OFERTA ACADÉMICA (Horarios de las fotos) ---
oferta_simulada = [
    {"id": 252, "curso": "Grondona (1)", "dias": "Lu/Ju", "inicio": 19, "fin": 21, "sede": "Paternal"},
    {"id": 252, "curso": "Romero (3)", "dias": "Lu/Ju", "inicio": 9, "fin": 11, "sede": "Pilar"},
    {"id": 252, "curso": "Kastika (8)", "dias": "Lu/Ju", "inicio": 7, "fin": 9, "sede": "San Isidro"},
    {"id": 252, "curso": "Kastika (9)", "dias": "Ma/Vi", "inicio": 13, "fin": 15, "sede": "San Isidro"},
    {"id": 274, "curso": "Binetti (1)", "dias": "Lu/Ju", "inicio": 17, "fin": 19, "sede": "Cordoba"},
    {"id": 274, "curso": "Alcain (2)", "dias": "Ma/Vi", "inicio": 19, "fin": 21, "sede": "Cordoba"},
    {"id": 274, "curso": "Gilli (18)", "dias": "Lu/Ju", "inicio": 9, "fin": 11, "sede": "Cordoba"},
    {"id": 250, "curso": "Apella", "dias": "Ma/Vi", "inicio": 7, "fin": 9, "sede": "Cordoba"},
    {"id": 272, "curso": "Aromi", "dias": "Lu/Ju", "inicio": 11, "fin": 13, "sede": "Cordoba"},
]

# --- LÓGICA DE INTERFAZ ---
st.title("🎓 Planificador Académico FCE UBA")

carrera_sel = st.sidebar.selectbox("Seleccioná tu Carrera:", list(planes.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("1. Materias Aprobadas")

aprobadas = []
with st.sidebar.expander("Primer Tramo (Común)", expanded=False):
    for cod, nom in primer_tramo.items():
        if st.checkbox(f"{nom} ({cod})", key=f"p_{cod}"):
            aprobadas.append(cod)

primer_tramo_ok = all(c in aprobadas for c in primer_tramo.keys())

with st.sidebar.expander("Segundo Tramo / Profesional"):
    materias_plan = planes[carrera_sel]
    for cod, info in materias_plan.items():
        if st.checkbox(f"{info['nombre']} ({cod})", key=f"s_{cod}", disabled=not primer_tramo_ok):
            aprobadas.append(cod)

st.sidebar.markdown("---")
st.sidebar.subheader("2. Preferencias de Horario")

# Filtro por banda horaria
turnos = st.sidebar.multiselect("Banda horaria:", ["Mañana (7-13)", "Tarde (13-17)", "Noche (17-23)"], default=["Mañana (7-13)", "Tarde (13-17)", "Noche (17-23)"])

# Filtro por rango exacto
rango_h = st.sidebar.slider("Rango de horas que podés cursar:", 7, 23, (7, 23))

st.sidebar.subheader("3. Otras Preferencias")
sedes_sel = st.sidebar.multiselect("Sedes:", ["Cordoba", "Paternal", "San Isidro", "Pilar", "Avellaneda", "Virtual"], default=["Cordoba", "Virtual", "Paternal"])

# --- PROCESAMIENTO DE HABILITADAS ---
habilitadas_ids = []
if not primer_tramo_ok:
    for cod, nom in primer_tramo.items():
        if cod not in aprobadas: habilitadas_ids.append(cod)
else:
    for cod, info in materias_plan.items():
        if cod not in aprobadas:
            if all(c in aprobadas for c in info["corr"]):
                habilitadas_ids.append(cod)

# --- FILTRADO DE CURSOS ---
cursos_finales = []
for c in oferta_simulada:
    if c["id"] in habilitadas_ids and c["sede"] in sedes_sel:
        # 1. Filtro de Rango Exacto
        if c["inicio"] >= rango_h[0] and c["fin"] <= rango_h[1]:
            
            # 2. Filtro de Turnos (Mañana, Tarde, Noche)
            pasa_turno = False
            if "Mañana (7-13)" in turnos and c["fin"] <= 13: pasa_turno = True
            if "Tarde (13-17)" in turnos and c["inicio"] >= 13 and c["fin"] <= 17: pasa_turno = True
            if "Noche (17-23)" in turnos and c["inicio"] >= 17: pasa_turno = True
            
            if pasa_turno:
                cursos_finales.append(c)

# --- VISUALIZACIÓN ---
st.header(f"Planificación para {carrera_sel}")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Materias Habilitadas")
    if not habilitadas_ids:
        st.info("¡Felicitaciones! No tenés materias pendientes registradas.")
    for h in habilitadas_ids:
        nom = primer_tramo.get(h) or materias_plan.get(h, {}).get("nombre")
        st.write(f"✅ {nom} ({h})")

with col2:
    st.subheader("🕒 Cursos que coinciden con tus horarios")
    if cursos_finales:
        df = pd.DataFrame(cursos_finales)
        df['Materia'] = df['id'].apply(lambda x: primer_tramo.get(x) or materias_plan.get(x, {}).get('nombre'))
        df['Horario'] = df.apply(lambda x: f"{x['inicio']}:00 a {x['fin']}:00 hs", axis=1)
        st.table(df[['Materia', 'curso', 'dias', 'Horario', 'sede']])
    else:
        st.warning("No hay cursos que coincidan con tus filtros de horario o sede.")

st.markdown("---")
st.caption("FCE UBA - Asistente Académico")
