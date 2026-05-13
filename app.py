import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Planificador FCE UBA - Ciclo Completo", layout="wide")
cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS DE MATERIAS (PLANES INTEGRALES) ---
# [Nombre, [Correlativas IDs]]
CBC = {
    241: ["Análisis Matemático I", []], 242: ["Economía", []], 243: ["Sociología", []],
    244: ["Metodología de las Cs. Soc.", []], 245: ["Álgebra", []], 246: ["Historia Econ. y Soc. Gral.", []]
}

PLANES = {
    "Contador Público": {
        247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 249: ["Hist. Econ. y Soc. Arg.", [246]],
        250: ["Microeconomía I", [242]], 251: ["Inst. de Derecho Público", [244]], 252: ["Administración General", [243]],
        274: ["Sistemas Administrativos", [252]], 275: ["Tecnol. de la Información", [252]], 276: ["Cálculo Financiero", [248]],
        278: ["Micro y Política Econ.", [250]], 351: ["Sistemas Contables", [247]], 353: ["Sistemas de Costos", [247]],
        1359: ["Derecho Económico", [251]], 273: ["Inst. de Derecho Privado", [1359]], 279: ["Administración Financiera", [276]],
        1352: ["Contabilidad Financiera", [351]], 362: ["Gestión y Costos", [353]], 355: ["Auditoría", [1352]],
        1330: ["Contab. Social y Ambiental", [1352]], 354: ["Dcho. Trabajo y Seg. Soc.", [273]], 
        356: ["Teoría y Tec. Imp. I", [1352]], 357: ["Teoría y Tec. Imp. II", [356]], 
        1360: ["Dcho. Crediticio y Bursátil", [273]], 1374: ["Contab. Gubernamental", [1352]],
        1358: ["Taller Actuación Judicial", [355, 357]], 1361: ["Práctica Profesional", [355, 357, 1360]]
    },
    "Lic. en Administración": {
        247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]],
        463: ["Gestión de Tec. Digitales", [245]], 252: ["Admin. General", [243]], 274: ["Sistemas Administrativos", [252]],
        462: ["Derecho Empresarial", [251]], 276: ["Cálculo Financiero", [248]], 464: ["Gestión de Costos", [247]],
        278: ["Macro y Pol. Econ.", [250]], 467: ["Gestión del Talento", [252]], 466: ["Admin. de Operaciones", [463]],
        465: ["Métodos Predictivos", [276, 464]], 468: ["Admin. Tributaria", [464, 278]], 279: ["Admin. Financiera", [276]],
        469: ["Marketing", [467]], 470: ["Ciencias de la Decisión", [465]], 471: ["Planeamiento Estratégico", [279, 469]],
        472: ["Dirección General", [471]], 473: ["Práctica Profesional Admin.", [471]]
    },
    "Lic. en Sistemas de Información": {
        1275: ["Intro. a la Tecnol. Inf.", [245]], 247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]],
        274: ["Sistemas Administrativos", [252]], 1601: ["Ingeniería de Software", [1275]], 1653: ["Tecnol. de Computadores", [1275]],
        661: ["Lógica Simbólica", [244]], 658: ["Metodología Sist. Inf.", [1601]], 655: ["Tecn. Comunicaciones", [1653]],
        740: ["Redes Informáticas", [655]], 1652: ["Teoría de Lenguajes", [661]], 1654: ["Construc. de Aplicaciones", [1652]],
        663: ["Sistemas de Datos", [658]], 662: ["Seguridad Informática", [663]], 1799: ["Gestión de Recursos IT", [658]]
    },
    "Lic. en Economía": {
        272: ["Análisis Matemático II", [241, 245]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]],
        262: ["Macroeconomía I", [250]], 253: ["Matemática para Econ.", [272]], 277: ["Estadística II", [248]],
        286: ["Microeconomía II", [250, 272]], 283: ["Macroeconomía II", [262, 253]], 556: ["Finanzas Públicas", [262]],
        543: ["Econometría", [277, 283]], 547: ["Estructura Econ. Arg.", [262]], 554: ["Crecimiento Econ.", [283]],
        558: ["Economía Internacional", [286, 283]]
    },
    "Actuario (Administración)": {
        248: ["Estadística I", [241]], 247: ["Teoría Contable", [242]], 276: ["Cálculo Financiero", [248]],
        277: ["Estadística II", [248]], 601: ["Matemática Financiera", [276]], 751: ["Estadística Actuarial", [277]],
        752: ["Análisis Numérico", [272]], 753: ["Biometría Actuarial", [751]], 754: ["Seguros Personales", [601, 753]],
        755: ["Seguros Patrimoniales", [601, 751]], 756: ["Fondos de Jubilaciones", [753]], 757: ["Equilibrio Actuarial", [755, 756]]
    },
    "Actuario (Economía)": {
        272: ["Análisis Matemático II", [241, 245]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]],
        277: ["Estadística II", [248]], 253: ["Matemática para Econ.", [272]], 262: ["Macroeconomía I", [250]],
        276: ["Cálculo Financiero", [248]], 601: ["Matemática Financiera", [276]], 751: ["Estadística Actuarial", [277]],
        753: ["Biometría Actuarial", [751]], 754: ["Seguros Personales", [601]], 755: ["Seguros Patrimoniales", [601, 751]]
    }
}

# --- 2. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved_data = cookies.get("fce_pro_v1")
if saved_data:
    try: saved_data = json.loads(saved_data)
    except: saved_data = None
if not saved_data:
    saved_data = {"registro": "", "ranking": 500, "carrera": "Contador Público", "aprobadas": [], "sedes": ["Córdoba"]}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("👤 Mi Perfil")
    user_reg = st.text_input("N° Registro:", value=saved_data["registro"])
    user_rank = st.number_input("Mi Ranking:", value=int(saved_data["ranking"]))
    user_carrera = st.selectbox("Carrera:", list(PLANES.keys()), index=list(PLANES.keys()).index(saved_data["carrera"]))
    user_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved_data.get("sedes", ["Córdoba"]))
    
    st.subheader("✅ Materias Aprobadas")
    aprobadas = []
    with st.expander("Primer Tramo (CBC)", expanded=True):
        for cod, info in CBC.items():
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"c_{cod}"): aprobadas.append(cod)
    
    cbc_completo = all(c in aprobadas for c in CBC.keys())
    with st.expander("Ciclo Profesional", expanded=cbc_completo):
        mats_plan = PLANES[user_carrera]
        for cod, info in mats_plan.items():
            faltan = [c for c in info[1] if c not in aprobadas]
            disabled = not cbc_completo or len(faltan) > 0
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"s_{cod}", disabled=disabled and cod not in saved_data["aprobadas"]):
                aprobadas.append(cod)
            if disabled and cod not in saved_data["aprobadas"]:
                st.caption(f"🔒 Faltan: {faltan if cbc_completo else 'CBC'}")

    if st.button("💾 GUARDAR PROGRESO"):
        data = {"registro": user_reg, "ranking": user_rank, "carrera": user_carrera, "aprobadas": aprobadas, "sedes": user_sedes}
        cookie_manager.set("fce_pro_v1", json.dumps(data))
        st.success("¡Guardado!")

# --- 4. GENERADOR DE HORARIOS ---
st.title("🧩 Armador de Cuatrimestre FCE")

# Materias Habilitadas para cursar
mats_habilitadas = {}
for cod, info in {**CBC, **PLANES[user_carrera]}.items():
    if cod not in aprobadas:
        if cod in CBC or (cbc_completo and all(c in aprobadas for c in info[1])):
            mats_habilitadas[cod] = info[0]

st.header("1. ¿Qué querés cursar?")
preferidas = st.multiselect("Elegí tus materias habilitadas:", 
                            options=list(mats_habilitadas.keys()), 
                            format_func=lambda x: f"{mats_habilitadas[x]} ({x})")

st.header("2. Tus Horarios Disponibles")
bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
cols = st.columns(8)
user_bloques = []
for i, b in enumerate(bloques):
    if cols[i].checkbox(b, value=True, key=f"time_{b}"): user_bloques.append(b)

# --- OFERTA Y COMBOS (Simulada para testear) ---
oferta = [
    {"id": 252, "m": "Admin Gral", "c": "Kastika", "dias": ["Lu", "Ju"], "h": "07-09", "s": "Córdoba", "corte": 450},
    {"id": 252, "m": "Admin Gral", "c": "Grondona", "dias": ["Lu", "Ju"], "h": "19-21", "s": "Paternal", "corte": 380},
    {"id": 274, "m": "Sist. Admin", "c": "Alcain", "dias": ["Ma", "Vi"], "h": "19-21", "s": "Córdoba", "corte": 550},
    {"id": 248, "m": "Estadística I", "c": "Cantoni", "dias": ["Ma", "Vi"], "h": "07-09", "s": "Córdoba", "corte": 620},
    {"id": 272, "m": "Análisis II", "c": "Aromi", "dias": ["Lu", "Ju"], "h": "17-19", "s": "Córdoba", "corte": 700},
    {"id": 751, "m": "Estad. Actuarial", "c": "Lopez", "dias": ["Mi", "Sa"], "h": "09-11", "s": "Córdoba", "corte": 300},
]

if preferidas:
    st.header("3. Opciones de Armado (Sin superposición)")
    # Filtrar oferta por materias elegidas, sedes y bloques horarios
    oferta_f = [o for o in oferta if o["id"] in preferidas and o["s"] in user_sedes and o["h"] in user_bloques]
    
    # Agrupar por materia
    cursos_por_m = []
    for m_id in preferidas:
        c_m = [o for o in oferta_f if o["id"] == m_id]
        if c_m: cursos_por_m.append(c_m)

    if len(cursos_por_m) == len(preferidas):
        combos = list(product(*cursos_por_m))
        validos = []
        for combo in combos:
            ocupado = set()
            choque = False
            for c in combo:
                for dia in c["dias"]:
                    slot = (dia, c["h"])
                    if slot in ocupado: choque = True; break
                    ocupado.add(slot)
                if choque: break
            if not choque: validos.append(combo)

        if validos:
            for i, combo in enumerate(validos[:3]):
                st.subheader(f"Opción {i+1}")
                cols_c = st.columns(len(combo))
                for idx, curso in enumerate(combo):
                    prob = "🟢" if user_rank > curso["corte"]+50 else "🟡" if user_rank > curso["corte"]-50 else "🔴"
                    cols_c[idx].info(f"**{curso['m']}**\n\n{curso['c']}\n\n{curso['h']} hs\n\nSede: {curso['s']}\n\nProb: {prob}")
        else:
            st.error("No hay combinaciones posibles con esos filtros. Probá habilitando más bloques horarios o sedes.")
