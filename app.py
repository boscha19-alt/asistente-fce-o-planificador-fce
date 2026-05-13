import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="FCE UBA - Planificador Oficial", layout="wide")
cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS INTEGRAL DE MATERIAS (Extraída de tus fotos) ---
# Formato: CÓDIGO: ["NOMBRE", [CORRELATIVAS]]
MATERIAS = {
    # Primer Tramo Común (Depende de la carrera)
    241: ["Análisis Matemático I", []], 242: ["Economía", []], 245: ["Álgebra", []], 
    246: ["Hist. Económica y Social Gral.", []], 243: ["Sociología", []], 244: ["Metodología Cs. Sociales", []],
    252: ["Administración General", []], 254: ["Sociología de las Org.", []],
    255: ["Análisis Contable", []], 256: ["Inst. de Gob. y Econ. Política", []],
    1275: ["Intro. a la Tecnol. de la Inf.", [245]],
    
    # Segundo Tramo y Profesional (General)
    247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 249: ["Hist. Econ. y Soc. Arg.", [246]],
    250: ["Microeconomía I", [242]], 251: ["Inst. de Derecho Público", [244]], 274: ["Sistemas Administrativos", [252]],
    276: ["Cálculo Financiero", [248]], 278: ["Macroeconomía y Pol. Econ.", [250]], 279: ["Administración Financiera", [276]],
    272: ["Análisis Matemático II", [241, 245]], 262: ["Macroeconomía I", [250]], 283: ["Macroeconomía II", [262]],
    286: ["Microeconomía II", [250, 272]], 288: ["Matemática para Economistas", [272]], 291: ["Microeconomía p/ Economistas", [542]],
    351: ["Sistemas Contables", [247]], 353: ["Sistemas de Costos", [247]], 355: ["Auditoría", [1352]],
    356: ["Teoría y Técnica Impositiva I", [251, 1352]], 357: ["Teoría y Técnica Impositiva II", [356]],
    362: ["Gestión y Costos (Contadores)", [353]], 462: ["Derecho Empresarial", [251]], 463: ["Gestión de Tecnol. Digitales", [245]],
    464: ["Gestión de Costos", [247]], 465: ["Métodos Predictivos", [248]], 466: ["Administración de Operaciones", [463]],
    467: ["Gestión del Talento", [276]], 468: ["Administración Tributaria", [278]], 469: ["Marketing", [467]],
    470: ["Ciencias de la Decisión", [465]], 471: ["Planeamiento Estratégico", [279]], 472: ["Dirección General", [467, 470]],
    540: ["Análisis Estadístico", [241]], 541: ["Estructura y Pol. Econ. Arg.", [262]], 542: ["Matemática Aplicada I", [241, 245]],
    543: ["Econometría I", [540, 544]], 544: ["Matemática Aplicada II", [542]], 548: ["Dinero y Bancos", [279, 602]],
    556: ["Finanzas Públicas", [291]], 601: ["Matemática Financiera y Act.", [540, 542]], 602: ["Análisis Estadístico II", [540, 542]],
    603: ["Dcho. Fin., Seguros y Seg. Soc.", [462]], 662: ["Seguridad Inf. y Auditoría", [663]], 
    663: ["Sist. de Datos", [661]], 751: ["Estadística Actuarial", [544, 602]], 753: ["Biometría Actuarial", [601, 751, 752]],
    754: ["Teoría Act. Seg. Personales", [753]], 755: ["Teoría Act. Seg. Patrimoniales", [601, 751, 752]],
    756: ["Teoría Act. Fondos de Jub.", [754]], 757: ["Teoría del Equilibrio Act.", [754, 755]],
    758: ["Bases Act. Inversiones", [601, 751]], 1352: ["Contabilidad Financiera", [351, 353]],
    1359: ["Derecho Económico", [251]], 1360: ["Dcho. Crediticio y Bursátil", [273, 354]], 1361: ["Taller de Práctica Prof. Org.", [473]]
}

# --- MAPEADOR DE PLANES SEGÚN IMÁGENES ---
PLANES = {
    "Actuario": [245, 241, 242, 246, 255, 256, 540, 542, 262, 274, 462, 602, 601, 751, 753, 544, 752, 291, 548, 279, 603, 746, 754, 755, 756, 757, 758, 717, 728],
    "Lic. en Sistemas": [241, 242, 245, 246, 252, 254, 248, 274, 250, 247, 249, 1275, 464, 278, 276, 279, 1653, 655, 740, 1652, 1654, 663, 662, 1660, 1601, 658, 1603, 1604, 1799],
    "Lic. en Administración": [245, 241, 242, 246, 252, 254, 248, 247, 250, 463, 274, 462, 276, 464, 278, 467, 466, 465, 468, 279, 469, 470, 471, 473, 472],
    "Contador Público": [245, 241, 242, 246, 244, 243, 248, 252, 250, 247, 249, 251, 275, 278, 276, 274, 351, 353, 1359, 279, 1352, 362, 273, 1330, 355, 1374, 354, 1358, 356, 357, 1360, 1361],
    "Lic. en Economía": [245, 241, 242, 246, 255, 256, 540, 542, 262, 291, 541, 544, 547, 556, 549, 283, 548, 543, 545, 555, 554, 286, 558, 546, 559]
}

# --- 2. OFERTA CON CORTES REALES (Extraídos de tus tablas de ranking) ---
# [ID, DOCENTE, BLOQUE, SEDE, MIN_RANK, MAX_REG]
OFERTA_REAL = [
    [466, "Scampini", "07-09", "Córdoba", 173.1, 898636],
    [355, "Gallego Tinto", "07-09", "Córdoba", 186.9, 908546],
    [276, "Sciaccaluga", "07-09", "Córdoba", 154.8, 904388],
    [751, "Landro", "09-11", "Córdoba", 181.6, 901495],
    [278, "Gesualdo", "09-11", "Córdoba", 131.4, 915420],
    [351, "Pahlen", "09-11", "Córdoba", 130.9, 915679],
    [543, "Calicchio", "19-21", "Córdoba", 185.0, 897120],
    [274, "Canals", "09-11", "Córdoba", 118.4, 917868],
    [466, "Lorena Sanchez", "19-21", "Córdoba", 170.8, 897297]
]

# --- 3. LÓGICA DE PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved_data = cookies.get("fce_v_final_full")
if saved_data:
    try: saved_data = json.loads(saved_data)
    except: saved_data = None
if not saved_data:
    saved_data = {"reg": "", "rank": 500.0, "car": "Contador Público", "aprob": [], "sedes": ["Córdoba"]}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("👤 Mi Perfil")
    u_reg = st.text_input("N° Registro:", value=saved_data["reg"])
    u_rank = st.number_input("Mi Ranking:", value=float(saved_data["rank"]))
    u_car = st.selectbox("Carrera:", list(PLANES.keys()), index=list(PLANES.keys()).index(saved_data["car"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved_data["sedes"])
    
    st.subheader("✅ Marcar Aprobadas")
    plan_actual_codes = PLANES[u_car]
    aprobadas = []
    
    # Buscador para no perderse
    search = st.text_input("🔍 Filtrar materia...")

    for cod in plan_actual_codes:
        nombre = MATERIAS[cod][0]
        if search.lower() in nombre.lower() or search == "":
            # Lógica de bloqueo de checkbox
            faltan = [c for c in MATERIAS[cod][1] if c not in aprobadas]
            disabled = len(faltan) > 0
            if st.checkbox(f"{nombre} ({cod})", value=(cod in saved_data["aprob"]), key=f"ch_{cod}", disabled=disabled and cod not in saved_data["aprob"]):
                aprobadas.append(cod)
            if disabled and cod not in saved_data["aprob"]:
                st.caption(f"🔒 Bloqueada por códigos: {faltan}")

    if st.button("💾 GUARDAR"):
        data_to_save = {"reg": u_reg, "rank": u_rank, "car": u_car, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_v_final_full", json.dumps(data_to_save))
        st.success("Guardado localmente.")

# --- 5. CUERPO PRINCIPAL ---
st.title(f"🚀 Planificador: {u_car}")

tab_plan, tab_horario = st.tabs(["📊 Mi Plan de Estudios", "🧩 Armador de Cuatrimestre"])

with tab_plan:
    st.header("Estado de tu carrera")
    # Tabla de seguimiento
    data_plan = []
    for cod in plan_actual_codes:
        status = "✅ Aprobada" if cod in aprobadas else "🟢 Habilitada" if all(c in aprobadas for c in MATERIAS[cod][1]) else "🔒 Bloqueada"
        data_plan.append({"Cód": cod, "Materia": MATERIAS[cod][0], "Estado": status, "Req": MATERIAS[cod][1]})
    st.table(data_plan)

with tab_horario:
    # 1. Elegir preferidas
    habilitadas = {c: MATERIAS[c][0] for c in plan_actual_codes if c not in aprobadas and all(corr in aprobadas for corr in MATERIAS[c][1])}
    
    st.header("1. ¿Qué materias querés cursar este cuatri?")
    elegidas = st.multiselect("Materias disponibles:", options=list(habilitadas.keys()), format_func=lambda x: f"{habilitadas[x]} ({x})")
    
    # 2. Bloques horarios
    st.header("2. Elegí tus bloques libres")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_b = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_b[i].checkbox(b, value=True, key=f"t_{b}")]

    # 3. Generador de combos
    if elegidas:
        st.header("3. Opciones de armado sin choque")
        # Filtrar oferta real por filtros de usuario
        oferta_f = [o for o in OFERTA_REAL if o[0] in elegidas and o[3] in u_sedes and o[2] in u_bloques]
        
        grupos_materia = []
        for mid in elegidas:
            cursos = [o for o in oferta_f if o[0] == mid]
            if cursos: grupos_materia.append(cursos)
        
        if len(grupos_materia) == len(elegidas):
            combos = list(product(*grupos_materia))
            # Filtrar superposiciones
            validos = [c for c in combos if len(set(x[2] for x in c)) == len(c)]
            
            if validos:
                for i, combo in enumerate(validos[:3]):
                    with st.expander(f"OPCIÓN {i+1}"):
                        cs = st.columns(len(combo))
                        for idx, c in enumerate(combo):
                            # Lógica de probabilidad basada en el ranking real de las fotos
                            diff = u_rank - c[4]
                            color = "green" if diff > 30 else "orange" if diff > -20 else "red"
                            cs[idx].markdown(f"""
                            <div style="background:#f8f9fa; padding:15px; border-radius:10px; border-left:8px solid {color}; box-shadow: 2px 2px 5px #eee">
                                <b>{MATERIAS[c[0]][0]}</b><br>
                                Docente: {c[1]}<br>
                                ⏰ {c[2]} hs | 📍 {c[3]}<br>
                                <hr>
                                Prob: <b style="color:{color}">{('Alta' if color=='green' else 'Media' if color=='orange' else 'Baja')}</b><br>
                                <small>Corte: {c[4]} | Registro: {c[5]}</small>
                            </div>
                            """, unsafe_allow_html=True)
            else: st.error("Esas materias se pisan en el horario.")
        else: st.warning("No hay oferta disponible para todas las materias elegidas con tus filtros.")
