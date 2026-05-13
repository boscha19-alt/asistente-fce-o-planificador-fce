import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="FCE UBA - Planificador Real", layout="wide")
cookie_manager = stx.CookieManager()

# --- 1. PLANES DE ESTUDIO ACTUALIZADOS (SEGÚN TUS FOTOS) ---
CBC = {
    241: ["Análisis Matemático I", []], 242: ["Economía", []], 243: ["Sociología", []],
    244: ["Metodología de las Cs. Soc.", []], 245: ["Álgebra", []], 246: ["Historia Econ. y Soc. Gral.", []]
}

PLANES = {
    "Contador Público": {
        247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 249: ["Hist. Econ. y Soc. Arg.", [246]],
        250: ["Microeconomía I", [242]], 251: ["Inst. de Derecho Público", [244]], 252: ["Administración General", [243]],
        276: ["Cálculo Financiero", [248]], 351: ["Sistemas Contables", [247]], 353: ["Sistemas de Costos", [247]],
        274: ["Sistemas Administrativos", [252]], 279: ["Administración Financiera", [276]], 1352: ["Contab. Financiera", [351]],
        355: ["Auditoría", [1352]], 356: ["Teoría y Tec. Imp. I", [1352]], 357: ["Teoría y Tec. Imp. II", [356]],
        1374: ["Contab. Gubernamental", [1352, 362]], 362: ["Gestión y Costos", [353]], 1361: ["Práctica Prof.", [355, 357]]
    },
    "Lic. en Administración": {
        247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]],
        252: ["Admin. General", [243]], 463: ["Gestión Tec. Digitales", [245]], 274: ["Sistemas Administrativos", [252]],
        464: ["Gestión de Costos", [247]], 278: ["Macro y Pol. Econ.", [250]], 467: ["Gestión del Talento", [252]],
        466: ["Admin. de Operaciones", [463]], 279: ["Admin. Financiera", [276]], 469: ["Marketing", [467]],
        471: ["Planeamiento Estratégico", [279, 469]], 472: ["Dirección General", [471]]
    },
    "Lic. en Economía": {
        272: ["Análisis Matemático II", [241, 245]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]],
        262: ["Macroeconomía I", [250]], 288: ["Matemática para Economistas", [272]], 286: ["Microeconomía II", [250, 272]],
        283: ["Macroeconomía II", [262]], 543: ["Econometría I", [248, 283]], 556: ["Finanzas Públicas", [262]]
    },
    "Actuario (Admin)": {
        248: ["Estadística I", [241]], 276: ["Cálculo Financiero", [248]], 277: ["Estadística II", [248]],
        601: ["Matemática Financiera", [276]], 751: ["Estadística Actuarial", [277]], 753: ["Biometría Act.", [751]],
        754: ["Seguros Personales", [601]], 755: ["Seguros Patrimoniales", [601, 751]]
    },
    "Actuario (Econ)": {
        272: ["Análisis Matemático II", [241, 245]], 277: ["Estadística II", [248]], 601: ["Matemática Financiera", [276]],
        751: ["Estadística Actuarial", [277]], 753: ["Biometría Actuarial", [751]]
    }
}

# --- 2. BASE DE DATOS DE OFERTA CON CORTES REALES (Extraídos de tus fotos) ---
# Formato: [ID, Cátedra, Horario, Sede, Ranking Corte, Registro Corte]
OFERTA_REAL = [
    [466, "Scampini", "07-09", "Córdoba", 173.1, 898636],
    [466, "Lorena Sanchez", "19-21", "Córdoba", 170.8, 897297],
    [279, "Frechero", "21-23", "Córdoba", 167.1, 904593],
    [284, "Fernandez Maria", "07-09", "Avellaneda", 118.0, 914145],
    [355, "Gallego Tinto", "07-09", "Córdoba", 186.9, 908546],
    [276, "Sciaccaluga", "07-09", "Córdoba", 154.8, 904388],
    [276, "Tasat", "09-11", "Córdoba", 179.6, 864043],
    [276, "Pizarro", "07-09", "San Isidro", 150.5, 902412],
    [276, "Barone", "19-21", "Paternal", 139.3, 909931],
    [751, "Landro", "09-11", "Córdoba", 181.6, 901495],
    [278, "Gesualdo", "09-11", "Córdoba", 131.4, 915420],
    [489, "Indelicato", "17-19", "Córdoba", 136.2, 918158],
    [274, "Canals", "09-11", "Córdoba", 118.4, 917868],
    [351, "Pahlen", "09-11", "Córdoba", 130.9, 915679],
    [1358, "Cristobal", "15-17", "Córdoba", 204.1, 900993],
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved_data = cookies.get("fce_pro_vfinal")
if saved_data:
    try: saved_data = json.loads(saved_data)
    except: saved_data = None
if not saved_data:
    saved_data = {"registro": "", "ranking": 500, "carrera": "Contador Público", "aprobadas": [], "sedes": ["Córdoba"]}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("👤 Mi Perfil")
    user_reg = st.text_input("N° Registro:", value=saved_data["registro"])
    user_rank = st.number_input("Mi Ranking:", value=float(saved_data["ranking"]))
    user_carrera = st.selectbox("Carrera:", list(PLANES.keys()), index=list(PLANES.keys()).index(saved_data["carrera"]))
    user_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved_data.get("sedes", ["Córdoba"]))
    
    st.subheader("✅ Materias Aprobadas")
    aprobadas = []
    with st.expander("Primer Tramo"):
        for cod, info in CBC.items():
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"c_{cod}"): aprobadas.append(cod)
    
    cbc_ok = all(c in aprobadas for c in CBC.keys())
    with st.expander("Ciclo Profesional", expanded=cbc_ok):
        for cod, info in PLANES[user_carrera].items():
            faltan = [c for c in info[1] if c not in aprobadas]
            dis = not cbc_ok or len(faltan) > 0
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"s_{cod}", disabled=dis and cod not in saved_data["aprobadas"]):
                aprobadas.append(cod)
            if dis and cod not in saved_data["aprobadas"]: st.caption(f"Falta: {faltan if cbc_ok else 'CBC'}")

    if st.button("💾 GUARDAR"):
        data = {"registro": user_reg, "ranking": user_rank, "carrera": user_carrera, "aprobadas": aprobadas, "sedes": user_sedes}
        cookie_manager.set("fce_pro_vfinal", json.dumps(data))
        st.success("¡Guardado!")

# --- 5. LÓGICA DE CURSADA ---
st.title("🧩 Planificador FCE UBA - Cortes Reales")

mats_hab = {cod: info[0] for cod, info in {**CBC, **PLANES[user_carrera]}.items() 
            if cod not in aprobadas and (cod in CBC or (cbc_ok and all(c in aprobadas for c in info[1])))}

st.header("1. ¿Qué querés cursar ahora?")
elegidas = st.multiselect("Elegí de tus habilitadas:", options=list(mats_hab.keys()), format_func=lambda x: f"{mats_hab[x]} ({x})")

st.header("2. Tus Horarios Disponibles")
bloques_posibles = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
cols_h = st.columns(8)
user_bloques = [b for i, b in enumerate(bloques_posibles) if cols_h[i].checkbox(b, value=True)]

if elegidas:
    st.header("3. Opciones sugeridas (Sin choques)")
    # Filtrar oferta real por lo elegido y filtros del user
    oferta_f = [o for o in OFERTA_REAL if o[0] in elegidas and o[3] in user_sedes and o[2] in user_bloques]
    
    cursos_por_m = []
    for m_id in elegidas:
        c_m = [o for o in oferta_f if o[0] == m_id]
        if c_m: cursos_por_m.append(c_m)

    if len(cursos_por_m) == len(elegidas):
        combos = list(product(*cursos_por_m))
        validos = []
        for combo in combos:
            ocupado = set()
            choque = False
            for c in combo:
                # Simulación de días para detección de choques (puedes expandir esto)
                slot = (c[2]) # Si es el mismo bloque, asumimos que puede haber choque
                if slot in ocupado: choque = True; break
                ocupado.add(slot)
            if not choque: validos.append(combo)

        if validos:
            for i, combo in enumerate(validos[:3]):
                with st.expander(f"OPCIÓN {i+1}", expanded=(i==0)):
                    cols = st.columns(len(combo))
                    for idx, c in enumerate(combo):
                        # Semáforo de probabilidad REAL
                        prob = "🟢 Alta" if user_rank > c[4]+20 else "🟡 Media" if user_rank > c[4]-20 else "🔴 Baja"
                        reg_msg = f"Reg. Máx: {c[5]}"
                        cols[idx].info(f"**{mats_hab[c[0]]}**\n\n{c[1]}\n\n{c[2]} hs\n\nSede: {c[3]}\n\nRanking Corte: {c[4]}\n\n**Prob: {prob}**")
        else:
            st.error("No hay combinaciones sin choque de horarios. Intentá elegir otros bloques o sedes.")
else:
    st.info("Elegí materias en la barra lateral o en el paso 1.")
