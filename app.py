import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Asistente FCE UBA", layout="wide")
cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS DE MATERIAS (PLANES) ---
CBC = {
    241: ["Análisis Matemático I", []], 242: ["Economía", []], 243: ["Sociología", []],
    244: ["Metodología de las Cs. Soc.", []], 245: ["Álgebra", []], 246: ["Historia Econ. y Soc. Gral.", []]
}

PLANES = {
    "Contador Público": {
        247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 249: ["Hist. Econ. y Soc. Arg.", [246]],
        250: ["Microeconomía I", [242]], 251: ["Inst. de Derecho Público", [244]], 252: ["Administración General", [243]],
        274: ["Sistemas Administrativos", [252]], 275: ["Tecnol. de la Información", [252]], 276: ["Cálculo Financiero", [248]],
        351: ["Sistemas Contables", [247]], 355: ["Auditoría", [1352]], 356: ["Teoría y Tec. Imp. I", [1352]]
    },
    "Lic. en Administración": {
        247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]],
        463: ["Gestión de Tec. Digitales", [245]], 274: ["Sistemas Administrativos", [252]], 469: ["Marketing", [252]]
    },
    "Lic. en Sistemas": {
        1275: ["Intro. a la Tecnol. Inf.", [245]], 248: ["Estadística I", [241]], 1601: ["Ingeniería de Software", [1275]],
        663: ["Sistemas de Datos", [658]], 662: ["Seguridad Informática", [663]]
    },
    "Lic. en Economía": {
        272: ["Análisis Matemático II", [241, 245]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]],
        262: ["Macroeconomía I", [250]], 543: ["Econometría", [277, 283]]
    },
    "Actuario (Admin/Econ)": {
        248: ["Estadística I", [241]], 276: ["Cálculo Financiero", [248]], 277: ["Estadística II", [248]],
        601: ["Mat. Fin. y Actuarial", [276]], 751: ["Estadística Actuarial", [277]]
    }
}

# --- 2. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved_data = cookies.get("fce_v4_data")
if saved_data:
    try: saved_data = json.loads(saved_data)
    except: saved_data = None
if not saved_data:
    saved_data = {"registro": "", "ranking": 500, "carrera": "Contador Público", "aprobadas": [], "sedes": ["Córdoba", "Virtual"]}

# --- 3. INTERFAZ SIDEBAR ---
st.title("🛡️ Planificador de Inscripción FCE")

with st.sidebar:
    st.header("👤 Perfil Alumno")
    user_reg = st.text_input("N° Registro:", value=saved_data["registro"])
    user_rank = st.number_input("Ranking:", value=int(saved_data["ranking"]))
    user_carrera = st.selectbox("Carrera:", list(PLANES.keys()), index=list(PLANES.keys()).index(saved_data["carrera"]))
    
    st.header("🏢 Sedes Preferidas")
    sedes_opciones = ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"]
    # Cargamos las sedes guardadas o por defecto
    user_sedes = st.multiselect("Elegí tus sedes:", sedes_opciones, default=saved_data.get("sedes", ["Córdoba", "Virtual"]))
    
    st.header("✅ Aprobadas")
    aprobadas = []
    with st.expander("Primer Tramo"):
        for cod, info in CBC.items():
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"c_{cod}"):
                aprobadas.append(cod)
    
    cbc_completo = all(c in aprobadas for c in CBC.keys())
    with st.expander("Segundo Tramo / Profesional", expanded=cbc_completo):
        for cod, info in PLANES[user_carrera].items():
            faltan = [c for c in info[1] if c not in aprobadas]
            disabled = not cbc_completo or len(faltan) > 0
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"s_{cod}", disabled=disabled and cod not in saved_data["aprobadas"]):
                aprobadas.append(cod)

    if st.button("💾 GUARDAR TODO"):
        data = {"registro": user_reg, "ranking": user_rank, "carrera": user_carrera, "aprobadas": aprobadas, "sedes": user_sedes}
        cookie_manager.set("fce_v4_data", json.dumps(data))
        st.success("Guardado en navegador.")

# --- 4. CUERPO PRINCIPAL ---
tab1, tab2 = st.tabs(["🕒 Horarios y Sedes", "📊 Estado de Materias"])

with tab1:
    st.subheader("1. ¿En qué horarios podés cursar?")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols = st.columns(8)
    user_bloques = []
    for i, b in enumerate(bloques):
        if cols[i].checkbox(b, value=True, key=f"b_{b}"): user_bloques.append(b)

    st.divider()
    st.subheader("2. Cursos disponibles según tus filtros")
    
    # Oferta Académica ampliada
    oferta = [
        {"id": 252, "m": "Admin Gral", "c": "Grondona", "h": "19-21", "s": "Paternal", "corte": 400},
        {"id": 252, "m": "Admin Gral", "c": "Romero", "h": "09-11", "s": "Pilar", "corte": 200},
        {"id": 252, "m": "Admin Gral", "c": "Moroni", "h": "07-09", "s": "Córdoba", "corte": 550},
        {"id": 274, "m": "Sistemas Admin", "c": "Alcain", "h": "17-19", "s": "Córdoba", "corte": 600},
        {"id": 274, "m": "Sistemas Admin", "c": "Gilli", "h": "09-11", "s": "Córdoba", "corte": 850},
        {"id": 248, "m": "Estadística I", "c": "Cantoni", "h": "19-21", "s": "San Isidro", "corte": 350},
        {"id": 1601, "m": "Ing. Software", "c": "Briano", "h": "09-11", "s": "Virtual", "corte": 450},
    ]
    
    # Materias que el alumno puede cursar
    habilitadas = [cod for cod, info in PLANES[user_carrera].items() if cod not in aprobadas and all(c in aprobadas for c in info[1]) and cbc_completo]
    habilitadas += [cod for cod in CBC.keys() if cod not in aprobadas]

    # FILTRO FINAL: Materia habilitada + Bloque Horario + Sede
    res = [o for o in oferta if o["id"] in habilitadas and o["h"] in user_bloques and o["s"] in user_sedes]

    if res:
        for r in res:
            diff = user_rank - r["corte"]
            color = "green" if diff > 100 else "orange" if diff > -50 else "red"
            st.markdown(f"""
            <div style="border-left: 5px solid {color}; padding:15px; background-color:#f9f9f9; border-radius:10px; margin-bottom:10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05)">
                <span style="font-size:1.2em; font-weight:bold">{r['m']}</span> (Cód: {r['id']}) - <b>Cátedra {r['c']}</b><br>
                📍 <b>Sede: {r['s']}</b> | ⏰ Horario: <b>{r['h']} hs</b><br>
                Probabilidad: <b style="color:{color}">{('Alta' if color=='green' else 'Media' if color=='orange' else 'Baja')}</b> (Corte: {r['corte']})
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No hay cursos que coincidan con tus filtros de Sede y Horario para las materias que podés cursar.")

with tab2:
    st.header("Seguimiento de Carrera")
    data_plan = []
    for cod, info in {**CBC, **PLANES[user_carrera]}.items():
        faltan = [c for c in info[1] if c not in aprobadas]
        status = "✅" if cod in aprobadas else "🟢" if (cbc_completo or cod in CBC) and len(faltan)==0 else "🔒"
        data_plan.append({"Cód": cod, "Estado": status, "Materia": info[0], "Correlativas": info[1]})
    st.table(data_plan)
