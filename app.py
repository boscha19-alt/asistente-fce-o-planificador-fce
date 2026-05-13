import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Asistente FCE UBA", layout="wide")
cookie_manager = stx.CookieManager()

# --- 1. GRAN BASE DE DATOS DE MATERIAS (PLANES DE ESTUDIO) ---
# Estructura: ID: [Nombre, [Correlativas IDs]]
# Primer Tramo (Común)
CBC = {
    241: ["Análisis Matemático I", []],
    242: ["Economía", []],
    243: ["Sociología", []],
    244: ["Metodología de las Cs. Soc.", []],
    245: ["Álgebra", []],
    246: ["Historia Econ. y Soc. Gral.", []]
}

# Diccionario de Carreras
PLANES = {
    "Contador Público": {
        247: ["Teoría Contable", [242]],
        248: ["Estadística I", [241]],
        249: ["Hist. Econ. y Soc. Arg.", [246]],
        250: ["Microeconomía I", [242]],
        251: ["Inst. de Derecho Público", [244]],
        252: ["Administración General", [243]],
        274: ["Sistemas Administrativos", [252]],
        275: ["Tecnol. de la Información", [252]],
        276: ["Cálculo Financiero", [248]],
        278: ["Micro y Política Econ.", [250]],
        351: ["Sistemas Contables", [247]],
        353: ["Sistemas de Costos", [247]],
        1359: ["Derecho Económico", [251]],
        273: ["Inst. de Derecho Privado", [1359]],
        279: ["Administración Financiera", [276]],
        1352: ["Contabilidad Financiera", [351]],
        362: ["Gestión y Costos", [353]],
        355: ["Auditoría", [1352]],
        1330: ["Contab. Social y Ambiental", [1352]],
        354: ["Dcho. Trabajo y Seg. Soc.", [273]],
        356: ["Teoría y Tec. Imp. I", [1352]],
        357: ["Teoría y Tec. Imp. II", [356]],
        1360: ["Dcho. Crediticio y Bursátil", [273]],
        1361: ["Práctica Profesional", [355, 357]]
    },
    "Lic. en Administración": {
        247: ["Teoría Contable", [242]],
        248: ["Estadística I", [241]],
        250: ["Microeconomía I", [242]],
        463: ["Gestión de Tec. Digitales", [245]],
        274: ["Sistemas Administrativos", [252]],
        462: ["Derecho Empresarial", [251]],
        276: ["Cálculo Financiero", [248]],
        464: ["Gestión de Costos", [247]],
        278: ["Macro y Pol. Econ.", [250]],
        467: ["Gestión del Talento", [252]],
        466: ["Admin. de Operaciones", [463]],
        279: ["Admin. Financiera", [276]],
        469: ["Marketing", [467]],
        471: ["Planeamiento Estratégico", [279, 469]],
        472: ["Dirección General", [471]]
    },
    "Lic. en Sistemas de Información": {
        1275: ["Intro. a la Tecnol. Inf.", [245]],
        247: ["Teoría Contable", [242]],
        248: ["Estadística I", [241]],
        274: ["Sistemas Administrativos", [252]],
        1601: ["Ingeniería de Software", [1275]],
        1653: ["Tecnol. de Computadores", [1275]],
        661: ["Lógica Simbólica", [244]],
        658: ["Metodología Sist. Inf.", [1601]],
        655: ["Tecn. Comunicaciones", [1653]],
        740: ["Redes Informáticas", [655]],
        663: ["Sistemas de Datos", [658]],
        662: ["Seguridad Informática", [663]]
    },
    "Lic. en Economía": {
        272: ["Análisis Matemático II", [241, 245]],
        248: ["Estadística I", [241]],
        250: ["Microeconomía I", [242]],
        262: ["Macroeconomía I", [250]],
        277: ["Estadística II", [248]],
        286: ["Microeconomía II", [250, 272]],
        283: ["Macroeconomía II", [262]],
        543: ["Econometría", [277, 283]],
        556: ["Finanzas Públicas", [262]]
    },
    "Actuario (Administración)": {
        248: ["Estadística I", [241]],
        247: ["Teoría Contable", [242]],
        276: ["Cálculo Financiero", [248]],
        277: ["Estadística II", [248]],
        601: ["Mat. Fin. y Actuarial", [276]],
        751: ["Estadística Actuarial", [277]],
        753: ["Biometría Actuarial", [751]],
        755: ["Seguros Patrimoniales", [601]]
    },
    "Actuario (Economía)": {
        272: ["Análisis Matemático II", [241, 245]],
        248: ["Estadística I", [241]],
        250: ["Microeconomía I", [242]],
        276: ["Cálculo Financiero", [248]],
        277: ["Estadística II", [248]],
        601: ["Mat. Fin. y Actuarial", [276]],
        751: ["Estadística Actuarial", [277]],
        753: ["Biometría Actuarial", [751]]
    }
}

# --- 2. LÓGICA DE PERSISTENCIA (COOKIES) ---
cookies = cookie_manager.get_all()
saved_data = cookies.get("fce_v3_data")
if saved_data:
    try: saved_data = json.loads(saved_data)
    except: saved_data = None
if not saved_data:
    saved_data = {"registro": "", "ranking": 500, "carrera": "Contador Público", "aprobadas": []}

# --- 3. INTERFAZ ---
st.title("⚖️ Asistente de Inscripción - FCE UBA")

with st.sidebar:
    st.header("👤 Mi Perfil")
    user_reg = st.text_input("N° de Registro:", value=saved_data["registro"])
    user_rank = st.number_input("Mi Ranking:", value=int(saved_data["ranking"]))
    user_carrera = st.selectbox("Carrera:", list(PLANES.keys()), index=list(PLANES.keys()).index(saved_data["carrera"]))
    
    st.subheader("✅ Marcar Aprobadas")
    # Mostrar CBC
    aprobadas = []
    with st.expander("Primer Tramo (CBC)", expanded=True):
        for cod, info in CBC.items():
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"c_{cod}"):
                aprobadas.append(cod)
    
    # Mostrar Profesional
    cbc_completo = all(c in aprobadas for c in CBC.keys())
    with st.expander("Ciclo Profesional", expanded=cbc_completo):
        for cod, info in PLANES[user_carrera].items():
            # Lógica de correlativas para el checkbox
            faltan = [c for c in info[1] if c not in aprobadas]
            disabled = not cbc_completo or len(faltan) > 0
            
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"s_{cod}", disabled=disabled and cod not in saved_data["aprobadas"]):
                aprobadas.append(cod)
            if disabled and cod not in saved_data["aprobadas"]:
                st.caption(f"🔒 Bloqueada. Faltan: {faltan if cbc_completo else 'CBC Completo'}")

    if st.button("💾 GUARDAR MI PROGRESO"):
        data = {"registro": user_reg, "ranking": user_rank, "carrera": user_carrera, "aprobadas": aprobadas}
        cookie_manager.set("fce_v3_data", json.dumps(data))
        st.success("Guardado en este navegador.")

# --- 4. FILTROS Y RESULTADOS ---
tab1, tab2 = st.tabs(["📊 Mi Plan de Estudios", "🕒 Oferta y Horarios"])

with tab1:
    st.header(f"Plan de {user_carrera}")
    # Mostrar todas las materias y su estado
    data_plan = []
    for cod, info in {**CBC, **PLANES[user_carrera]}.items():
        estado = "✅ Aprobada" if cod in aprobadas else "⏳ Pendiente"
        # Chequear si puede cursar
        faltan = [c for c in info[1] if c not in aprobadas]
        if cod in aprobadas: 
            p_cursar = "Ya cursada"
        elif not cbc_completo and cod not in CBC.keys():
            p_cursar = "🔒 Falta CBC"
        elif len(faltan) == 0:
            p_cursar = "🟢 Habilitada"
        else:
            p_cursar = f"🔴 Falta: {faltan}"
            
        data_plan.append({"Código": cod, "Materia": info[0], "Estado": estado, "Inscripción": p_cursar})
    
    st.table(pd.DataFrame(data_plan))

with tab2:
    st.header("Cursos Sugeridos")
    # Filtro de bloques
    st.subheader("¿En qué horarios podés?")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols = st.columns(8)
    user_bloques = []
    for i, b in enumerate(bloques):
        if cols[i].checkbox(b, value=True): user_bloques.append(b)

    # Oferta simulada (Esto se puede expandir)
    oferta = [
        {"id": 252, "m": "Admin General", "c": "Cátedra A", "h": "07-09", "s": "Cordoba", "corte": 400},
        {"id": 274, "m": "Sistemas Admin", "c": "Cátedra B", "h": "19-21", "s": "Cordoba", "corte": 750},
        {"id": 248, "m": "Estadística I", "c": "Cátedra C", "h": "09-11", "s": "Paternal", "corte": 300},
        {"id": 355, "m": "Auditoría", "c": "Cátedra D", "h": "17-19", "s": "Cordoba", "corte": 900},
    ]
    
    # Habilitadas para inscribir
    habilitadas = [cod for cod, info in PLANES[user_carrera].items() if cod not in aprobadas and all(c in aprobadas for c in info[1]) and cbc_completo]
    # Sumar las del CBC que falten
    habilitadas += [cod for cod in CBC.keys() if cod not in aprobadas]

    res = [o for o in oferta if o["id"] in habilitadas and o["h"] in user_bloques]
    
    if res:
        for r in res:
            diff = user_rank - r["corte"]
            color = "green" if diff > 100 else "orange" if diff > -50 else "red"
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:10px">
                <b>{r['m']}</b> - {r['c']} <br>
                📍 Sede: {r['s']} | ⏰ Horario: {r['h']} <br>
                Probabilidad: <span style="color:{color}">● {('Alta' if color=='green' else 'Media' if color=='orange' else 'Baja')}</span> (Corte: {r['corte']})
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay cursos disponibles para tus materias habilitadas en esos horarios.")
