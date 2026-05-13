import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ESTÉTICA ZEN ---
st.set_page_config(page_title="FCE UBA - Planificador Oficial", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8FAFC; }
    .stApp { background-color: #F8FAFC; }
    .materia-card { 
        background: white; padding: 20px; border-radius: 15px; 
        border: 1px solid #E2E8F0; margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .status-badge {
        padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 600;
    }
    .alta { background-color: #DCFCE7; color: #166534; }
    .media { background-color: #FEF9C3; color: #854D0E; }
    .baja { background-color: #FEE2E2; color: #991B1B; }
    .sidebar-content { padding: 10px; }
    /* Estilo para los botones */
    .stButton>button {
        width: 100%; border-radius: 10px; background-color: white; border: 1px solid #E2E8F0;
        color: #475569; transition: all 0.3s;
    }
    .stButton>button:hover { border-color: #94A3B8; background-color: #F1F5F9; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS MAESTRA (Subjects) ---
DB_MATERIAS = {
    241: "Análisis Matemático I", 242: "Economía", 243: "Sociología", 244: "Metodología de las Cs. Soc.", 
    245: "Álgebra", 246: "Hist. Económica y Social Gral.", 247: "Teoría Contable", 248: "Estadística I", 
    249: "Hist. Económica y Social Arg.", 250: "Microeconomía I", 251: "Inst. del Derecho Público", 
    252: "Administración General", 254: "Sociología de las Organizaciones", 255: "Análisis Contable", 
    256: "Inst. de Gobierno y Economía Política", 262: "Macroeconomía I", 272: "Análisis Matemático II", 
    273: "Inst. de Derecho Privado", 274: "Sistemas Administrativos", 275: "Tecnología de la Información", 
    276: "Cálculo Financiero", 278: "Macroeconomía y Política Económica", 279: "Administración Financiera", 
    283: "Macroeconomía II", 286: "Microeconomía II", 288: "Matemática para Economistas", 291: "Microeconomía para Economistas", 
    351: "Sistemas Contables", 353: "Sistemas de Costos", 354: "Derecho del Trabajo y Seg. Social", 355: "Auditoría", 
    356: "Teoría y Técnica Impositiva I", 357: "Teoría y Técnica Impositiva II", 362: "Gestión y Costos (Contadores)", 
    453: "Admin. de la Producción", 462: "Derecho Empresarial", 463: "Gestión de Tecnologías Digitales", 
    464: "Gestión de Costos", 465: "Métodos Predictivos para la Gestión", 466: "Administración de Operaciones", 
    467: "Gestión del Talento", 468: "Administración Tributaria", 469: "Marketing", 470: "Ciencias de la Decisión", 
    471: "Planeamiento Estratégico", 472: "Dirección General", 473: "Práctica Profesional", 489: "Liderazgo Organizacional",
    540: "Análisis Estadístico", 542: "Matemática Aplicada I", 543: "Econometría I", 544: "Matemática Aplicada II",
    548: "Dinero, Crédito y Bancos", 601: "Matemática Financiera y Actuarial", 602: "Análisis Estadístico II",
    662: "Seguridad Inf. y Auditoría", 663: "Sistemas de Datos", 751: "Estadística Actuarial", 1352: "Contabilidad Financiera",
    1275: "Intro. a la Tecnol. de la Inf.", 1374: "Contab. Gubernamental", 1601: "Ingeniería de Software"
}

PLANES_CARRERA = {
    "Contador Público": [245, 241, 242, 246, 244, 243, 248, 252, 250, 247, 249, 251, 275, 278, 276, 274, 351, 353, 279, 1352, 362, 273, 355, 1374, 354, 356, 357, 1361],
    "Lic. en Administración": [245, 241, 242, 246, 252, 254, 248, 247, 250, 463, 274, 462, 276, 464, 278, 467, 466, 465, 468, 279, 469, 470, 471, 473, 472, 489],
    "Lic. en Sistemas": [241, 242, 245, 246, 252, 254, 248, 274, 250, 247, 1275, 464, 278, 276, 279, 1601, 663, 662],
    "Lic. en Economía": [245, 241, 242, 246, 255, 256, 540, 542, 262, 291, 544, 283, 548, 543, 286],
    "Actuario": [245, 241, 242, 246, 255, 256, 540, 542, 262, 602, 601, 751, 544, 279, 753]
}

# Correlatividades actualizadas según las flechas de tus fotos
CORR = {
    247: [242], 248: [241], 249: [246], 250: [242], 251: [244], 274: [252], 276: [248], 278: [250], 
    279: [276], 351: [247], 353: [247], 1352: [351, 353], 355: [1352], 356: [251, 1352], 
    362: [353], 463: [245], 464: [247], 465: [248], 466: [463], 467: [276], 468: [278], 
    469: [467], 471: [279], 540: [241], 542: [241, 245], 544: [542], 601: [540, 542], 
    602: [540, 542], 751: [544, 602], 1601: [1275]
}

# --- 2. OFERTA REAL (PROCESADA DE LAS 68 PÁGINAS DEL PDF) ---
# [ID, DOCENTE, BLOQUE, SEDE, MIN_RANKING_HISTORICO]
OFERTA = [
    [252, "GRONDONA", "19-21", "Paternal", 150.0], [252, "KASTIKA", "07-09", "San Isidro", 136.2],
    [252, "MORONI", "09-11", "Paternal", 140.0], [274, "ALCAIN", "17-19", "Córdoba", 163.0],
    [274, "CANALS", "09-11", "Córdoba", 118.4], [274, "GILLI", "09-11", "Córdoba", 155.0],
    [279, "AIRE", "19-21", "Córdoba", 171.1], [279, "FRECHERO", "21-23", "Córdoba", 167.1],
    [355, "GALLEGO TINTO", "07-09", "Córdoba", 186.9], [355, "MONTANINI", "19-21", "Córdoba", 192.5],
    [276, "SCIAC CALUGA", "07-09", "Córdoba", 154.8], [276, "TASAT", "09-11", "Córdoba", 179.6],
    [276, "FREGEIRO", "17-19", "Córdoba", 153.4], [276, "BARONE", "19-21", "Paternal", 139.3],
    [466, "SCAMPINI", "07-09", "Córdoba", 173.1], [466, "LORENA SANCHEZ", "19-21", "Córdoba", 170.8],
    [467, "HUBER", "19-21", "Córdoba", 141.2], [467, "MAZZA", "17-19", "Córdoba", 136.7],
    [469, "ALTIERI", "11-13", "Córdoba", 160.0], [469, "NUÑEZ", "17-19", "Córdoba", 165.0],
    [470, "BONATTI", "17-19", "Córdoba", 183.5], [470, "CARRO", "19-21", "Córdoba", 175.7],
    [751, "LANDRO", "09-11", "Córdoba", 181.6], [543, "CALICCHIO", "19-21", "Córdoba", 185.0],
    [247, "CAMPO", "07-09", "Córdoba", 130.0], [351, "PAHLEN", "09-11", "Córdoba", 130.9],
    [471, "CORTI", "17-19", "Avellaneda", 211.8], [1358, "CRISTOBAL", "15-17", "Córdoba", 204.1]
]

# --- 3. LÓGICA DE DATOS ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_v8_zen")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "", "rank": 500.0, "car": "Contador Público", "aprob": [], "sedes": ["Córdoba"]}

with st.sidebar:
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.title("👤 Perfil")
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    u_car = st.selectbox("Carrera:", list(PLANES_CARRERA.keys()), index=list(PLANES_CARRERA.keys()).index(saved["car"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.subheader("✅ Materias Aprobadas")
    plan_codes = PLANES_CARRERA[u_car]
    aprobadas = []
    
    search = st.text_input("Buscar materia...")
    for c in plan_codes:
        nombre = DB_MATERIAS.get(c, f"Materia {c}")
        if search.lower() in nombre.lower():
            reqs = CORR.get(c, [])
            faltan = [r for r in reqs if r not in aprobadas]
            bloqueada = len(faltan) > 0 and c not in saved["aprob"]
            if st.checkbox(f"{nombre}", value=(c in saved["aprob"]), key=f"s_{c}", disabled=bloqueada):
                aprobadas.append(c)
    
    if st.button("💾 Guardar Cambios"):
        data = {"reg": "", "rank": u_rank, "car": u_car, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_v8_zen", json.dumps(data))
        st.toast("Progreso guardado correctamente")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. CUERPO PRINCIPAL ---
st.title(f"Planificador {u_car}")

tab1, tab2 = st.tabs(["🧩 Armado", "📊 Carrera"])

with tab1:
    col_left, col_right = st.columns([1, 1.5])
    
    with col_left:
        st.subheader("Seleccioná qué querés cursar")
        hab = {c: DB_MATERIAS[c] for c in plan_codes if c not in aprobadas and all(r in aprobadas for r in CORR.get(c, []))}
        elegidas = st.multiselect("Materias habilitadas:", options=list(hab.keys()), format_func=lambda x: f"{hab[x]} ({x})")
        
        st.subheader("Horarios Disponibles")
        bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
        u_bl = [b for b in bloques if st.checkbox(f"Bloque {b}", value=True, key=f"bl_{b}")]

    with col_right:
        st.subheader("Opciones de Cátedras")
        if elegidas:
            filtrada = [o for o in OFERTA if o[0] in elegidas and o[3] in u_sedes and o[2] in u_bl]
            if filtrada:
                for c in filtrada:
                    diff = u_rank - c[4]
                    prob_text = "Alta" if diff > 25 else "Media" if diff > -15 else "Baja"
                    prob_class = "alta" if diff > 25 else "media" if diff > -15 else "baja"
                    
                    st.markdown(f"""
                        <div class="materia-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 600; font-size: 1.1em;">{DB_MATERIAS[c[0]]}</span>
                                <span class="status-badge {prob_class}">Probabilidad {prob_text}</span>
                            </div>
                            <div style="color: #64748B; margin-top: 8px; font-size: 0.95em;">
                                <b>Docente:</b> {c[1]} <br>
                                <b>Sede:</b> {c[3]} | <b>Horario:</b> {c[2]} hs <br>
                                <span style="font-size: 0.85em;">Corte histórico: {c[4]}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay opciones para los filtros seleccionados.")
        else:
            st.info("Elegí materias habilitadas a la izquierda para ver las opciones de cursada.")

with tab2:
    st.subheader("Estado General")
    for c in plan_codes:
        nombre = DB_MATERIAS.get(c, "N/A")
        is_aprob = "✅" if c in aprobadas else "🟢" if all(r in aprobadas for r in CORR.get(c, [])) else "🔒"
        st.text(f"{is_aprob} {nombre} ({c})")
