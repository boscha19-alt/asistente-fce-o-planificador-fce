import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Asistente FCE UBA Total", layout="wide")

# --- BASE DE DATOS EXTENDIDA DE MATERIAS ---
# 1er Tramo (Ciclo General - Común)
primer_tramo = {
    241: "Análisis Matemático I", 242: "Economía", 243: "Sociología",
    244: "Metodología de las Cs. Soc.", 245: "Álgebra", 246: "Hist. Econ. y Soc. Gral."
}

# Diccionario Maestro de Materias (Segundo Tramo y Ciclo Profesional)
materias_master = {
    # CONTADOR PÚBLICO
    "Contador Público": {
        248: {"nombre": "Estadística I", "corr": [241]},
        247: {"nombre": "Teoría Contable", "corr": [242]},
        250: {"nombre": "Microeconomía I", "corr": [242]},
        249: {"nombre": "Hist. Econ. y Soc. Arg.", "corr": [246]},
        251: {"nombre": "Inst. de Derecho Público", "corr": [244]},
        252: {"nombre": "Administración General", "corr": [243]},
        276: {"nombre": "Cálculo Financiero", "corr": [248]},
        351: {"nombre": "Sistemas Contables", "corr": [247]},
        353: {"nombre": "Sistemas de Costos", "corr": [247]},
        278: {"nombre": "Microeconomía y Pol. Econ.", "corr": [250]},
        1359: {"nombre": "Derecho Económico", "corr": [251]},
        275: {"nombre": "Tecnología de la Información", "corr": [252]},
        274: {"nombre": "Sistemas Administrativos", "corr": [252]},
        279: {"nombre": "Adm. Financiera", "corr": [276]},
        1352: {"nombre": "Contabilidad Financiera", "corr": [351]},
        362: {"nombre": "Gestión y Costos (Contadores)", "corr": [353]},
        273: {"nombre": "Inst. de Derecho Privado", "corr": [1359]},
        1330: {"nombre": "Contab. Social y Ambiental", "corr": [1352]},
        355: {"nombre": "Auditoría", "corr": [1352]},
        1374: {"nombre": "Contab. Gubernamental", "corr": [1352, 362]},
        354: {"nombre": "Derecho del Trabajo y Seg. Soc.", "corr": [273]},
        356: {"nombre": "Teoría y Técnica Impositiva I", "corr": [1352, 1330]},
        357: {"nombre": "Teoría y Técnica Impositiva II", "corr": [356]},
        1360: {"nombre": "Dcho. Crediticio, Bursátil e Insol.", "corr": [273]},
        1358: {"nombre": "Taller Actuación Judicial", "corr": [355, 357]},
        1361: {"nombre": "Práctica Profesional (Contador)", "corr": [355, 357, 1360]}
    },
    # LIC. EN ADMINISTRACIÓN
    "Lic. en Administración": {
        248: {"nombre": "Estadística I", "corr": [241]},
        247: {"nombre": "Teoría Contable", "corr": [242]},
        250: {"nombre": "Microeconomía I", "corr": [242]},
        463: {"nombre": "Gestión de Tec. Digitales", "corr": [245]},
        274: {"nombre": "Sistemas Administrativos", "corr": [252]},
        462: {"nombre": "Derecho Empresarial", "corr": [251]},
        276: {"nombre": "Cálculo Financiero", "corr": [248]},
        464: {"nombre": "Gestión de Costos", "corr": [247]},
        278: {"nombre": "Macroeconomía y Pol. Econ.", "corr": [250]},
        467: {"nombre": "Gestión del Talento", "corr": [252]},
        466: {"nombre": "Administración de Operaciones", "corr": [463]},
        465: {"nombre": "Métodos Predictivos", "corr": [276, 464]},
        468: {"nombre": "Administración Tributaria", "corr": [464, 278]},
        279: {"nombre": "Administración Financiera", "corr": [276]},
        469: {"nombre": "Marketing", "corr": [467]},
        470: {"nombre": "Ciencias de la Decisión", "corr": [465]},
        471: {"nombre": "Planeamiento Estratégico", "corr": [279, 469]},
        472: {"nombre": "Dirección General", "corr": [471]}
    },
    # LIC. EN SISTEMAS
    "Lic. en Sistemas": {
        247: {"nombre": "Teoría Contable", "corr": [242]},
        1275: {"nombre": "Intro. a la Tec. de la Inf.", "corr": [245]},
        248: {"nombre": "Estadística I", "corr": [241]},
        249: {"nombre": "Hist. Econ. y Soc. Arg.", "corr": [246]},
        274: {"nombre": "Sistemas Administrativos", "corr": [252]},
        250: {"nombre": "Microeconomía I", "corr": [242]},
        464: {"nombre": "Gestión de Costos", "corr": [247]},
        1601: {"nombre": "Ingeniería de Software", "corr": [1275]},
        1653: {"nombre": "Tecnol. de Computadores", "corr": [1275]},
        661: {"nombre": "Lógica Simbólica", "corr": [244]},
        278: {"nombre": "Macro y Pol. Econ.", "corr": [250]},
        276: {"nombre": "Cálculo Financiero", "corr": [248]},
        658: {"nombre": "Metodología de Sist. de Inf.", "corr": [1601]},
        655: {"nombre": "Tecnol. de Comunicaciones", "corr": [1653]},
        1652: {"nombre": "Teoría de Lenguajes", "corr": [661]},
        279: {"nombre": "Adm. Financiera", "corr": [276]},
        1603: {"nombre": "Derecho Informático I", "corr": [274]},
        740: {"nombre": "Redes Informáticas", "corr": [655]},
        1654: {"nombre": "Construc. de Aplicaciones", "corr": [1652]},
        663: {"nombre": "Sistemas de Datos", "corr": [658]},
        662: {"nombre": "Seguridad Informática", "corr": [663]}
    },
    # LIC. EN ECONOMÍA
    "Lic. en Economía": {
        248: {"nombre": "Estadística I", "corr": [241]},
        250: {"nombre": "Microeconomía I", "corr": [242]},
        272: {"nombre": "Análisis Matemático II", "corr": [241, 245]},
        249: {"nombre": "Hist. Econ. y Soc. Arg.", "corr": [246]},
        262: {"nombre": "Macroeconomía I", "corr": [250]},
        253: {"nombre": "Matemática para Econ.", "corr": [272]},
        277: {"nombre": "Estadística II", "corr": [248]},
        286: {"nombre": "Microeconomía II", "corr": [250, 272]},
        283: {"nombre": "Macroeconomía II", "corr": [262, 253]},
        556: {"nombre": "Finanzas Públicas", "corr": [262]},
        543: {"nombre": "Econometría", "corr": [277, 283]}
    }
}

# --- OFERTA ACADÉMICA (Simulada según el PDF) ---
oferta_simulada = [
    {"id": 252, "curso": "Grondona", "dias": "Lu/Ju", "inicio": 19, "fin": 21, "sede": "Paternal"},
    {"id": 274, "curso": "Alcain", "dias": "Ma/Vi", "inicio": 19, "fin": 21, "sede": "Cordoba"},
    {"id": 355, "curso": "Canetti", "dias": "Lu/Mi/Ju", "inicio": 17, "fin": 19, "sede": "Cordoba"},
    {"id": 471, "curso": "Corti", "dias": "Ma/Vi/Sa", "inicio": 9, "fin": 11, "sede": "Cordoba"},
    {"id": 662, "curso": "Gil Pablo", "dias": "Ma/Vi/Sa", "inicio": 19, "fin": 21, "sede": "Cordoba"},
]

# --- INTERFAZ ---
st.title("🛡️ Sistema Integral de Inscripción FCE UBA")

carrera_sel = st.sidebar.selectbox("Seleccioná tu Carrera:", list(materias_master.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("📌 1. Marcar Materias Aprobadas")

aprobadas = []
with st.sidebar.expander("Primer Tramo (General)", expanded=False):
    for cod, nom in primer_tramo.items():
        if st.checkbox(f"{nom} ({cod})", key=f"p_{cod}"):
            aprobadas.append(cod)

primer_tramo_ok = all(c in aprobadas for c in primer_tramo.keys())

# Segundo y Profesional
materias_plan = materias_master[carrera_sel]
with st.sidebar.expander("Ciclo Profesional", expanded=True):
    if not primer_tramo_ok:
        st.warning("Completá el 1er tramo primero.")
    for cod, info in materias_plan.items():
        # Deshabilitar si no tiene las correlativas
        tiene_corr = all(c in aprobadas for c in info["corr"])
        if st.checkbox(f"{info['nombre']} ({cod})", key=f"s_{cod}", disabled=not tiene_corr and not cod in aprobadas):
            aprobadas.append(cod)

st.sidebar.markdown("---")
st.sidebar.subheader("🕒 2. Filtros de Cursada")
rango_h = st.sidebar.slider("Horario Disponible:", 7, 23, (17, 23))
sedes_sel = st.sidebar.multiselect("Sedes:", ["Cordoba", "Paternal", "San Isidro", "Pilar", "Virtual"], default=["Cordoba", "Virtual"])

# --- LÓGICA DE HABILITACIÓN ---
habilitadas_ids = []
if not primer_tramo_ok:
    for cod in primer_tramo.keys():
        if cod not in aprobadas: habilitadas_ids.append(cod)
else:
    for cod, info in materias_plan.items():
        if cod not in aprobadas:
            if all(c in aprobadas for c in info["corr"]):
                habilitadas_ids.append(cod)

# --- VISUALIZACIÓN ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Materias que podés cursar ahora")
    for h in habilitadas_ids:
        nom = primer_tramo.get(h) or materias_plan.get(h, {}).get("nombre")
        st.success(f"📖 **{nom}** ({h})")

with col2:
    st.header("Cursos y Horarios sugeridos")
    cursos_finales = [c for c in oferta_simulada if c["id"] in habilitadas_ids and c["sede"] in sedes_sel and c["inicio"] >= rango_h[0] and c["fin"] <= rango_h[1]]
    
    if cursos_finales:
        df = pd.DataFrame(cursos_finales)
        df['Materia'] = df['id'].apply(lambda x: primer_tramo.get(x) or materias_plan.get(x, {}).get('nombre'))
        st.dataframe(df[['Materia', 'curso', 'dias', 'inicio', 'fin', 'sede']], use_container_width=True)
    else:
        st.info("No hay cursos cargados que coincidan con tus filtros.")

st.warning("⚠️ Nota: Esta aplicación utiliza una base de datos parcial de horarios. Para la inscripción oficial, consultá siempre el Sistema de Ranking de la FCE.")
