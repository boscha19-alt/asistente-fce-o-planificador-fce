import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="Inscripción FCE UBA", layout="wide")

# CSS para suavizar la interfaz
st.markdown("""
    <style>
    .main { background-color: #fdfdfd; }
    .stButton>button { border-radius: 20px; border: 1px solid #d1d5db; background-color: white; color: #374151; }
    .stButton>button:hover { background-color: #f9fafb; border-color: #9ca3af; }
    h1, h2, h3 { color: #1f2937; font-weight: 600; }
    .stExpander { border: none !important; box-shadow: none !important; background-color: #f9fafb !important; border-radius: 10px !important; }
    div[data-testid="stExpander"] div[role="button"] p { font-weight: 600; color: #4b5563; }
    .materia-card { background: white; padding: 15px; border-radius: 12px; border: 1px solid #e5e7eb; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS MAESTRA (DEFINICIÓN DE TODAS LAS MATERIAS) ---
# Se agregaron TODAS las materias de tus fotos para evitar el KeyError
DB_MATERIAS = {
    241: "Análisis Matemático I", 242: "Economía", 243: "Sociología", 244: "Metodología de las Cs. Soc.", 
    245: "Álgebra", 246: "Hist. Económica y Social Gral.", 247: "Teoría Contable", 248: "Estadística I", 
    249: "Hist. Económica y Social Arg.", 250: "Microeconomía I", 251: "Inst. del Derecho Público", 
    252: "Administración General", 254: "Sociología de las Organizaciones", 255: "Análisis Contable", 
    256: "Inst. de Gobierno y Economía Política", 262: "Macroeconomía I", 272: "Análisis Matemático II", 
    273: "Inst. de Derecho Privado", 274: "Sistemas Administrativos", 275: "Tecnología de la Información", 
    276: "Cálculo Financiero", 278: "Macroeconomía y Política Económica", 279: "Administración Financiera", 
    283: "Macroeconomía II", 284: "Análisis Matemático II", 286: "Microeconomía II", 288: "Matemática para Economistas", 
    290: "Microeconomía I", 291: "Microeconomía para Economistas", 351: "Sistemas Contables", 
    353: "Sistemas de Costos", 354: "Derecho del Trabajo y Seg. Social", 355: "Auditoría", 
    356: "Teoría y Técnica Impositiva I", 357: "Teoría y Técnica Impositiva II", 362: "Gestión y Costos (Contadores)", 
    451: "Estadística para Administradores", 452: "Sociología de la Organización", 453: "Admin. de la Producción", 
    455: "Régimen Tributario", 457: "Teoría de la Decisión", 458: "Planeamiento a Largo Plazo", 
    460: "Seminario de Integración", 462: "Derecho Empresarial", 463: "Gestión de Tecnologías Digitales", 
    464: "Gestión de Costos", 465: "Métodos Predictivos para la Gestión", 466: "Administración de Operaciones", 
    467: "Gestión del Talento", 468: "Administración Tributaria", 469: "Marketing", 470: "Ciencias de la Decisión", 
    471: "Planeamiento Estratégico", 472: "Dirección General", 473: "Práctica Profesional", 
    485: "Fintech, Pagos Digitales y Cripto", 488: "Estrategia", 489: "Liderazgo Organizacional", 
    520: "Ciencia de Datos para Econ. y Neg.", 523: "Economía y Derecho Corporativo", 540: "Análisis Estadístico", 
    541: "Estructura y Pol. Econ. Arg.", 542: "Matemática Aplicada I", 543: "Econometría I", 
    544: "Matemática Aplicada II", 545: "Epist. e Hist. del Pensamiento Econ.", 546: "Econometría II", 
    547: "Estructura Económica Argentina", 548: "Dinero, Crédito y Bancos", 549: "Economía Financiera", 
    552: "Dinero, Crédito y Bancos", 554: "Crecimiento Económico", 555: "Organización Industrial", 
    556: "Finanzas Públicas", 558: "Economía Internacional", 559: "Desarrollo Económico", 
    561: "Cuentas Nacionales", 562: "Seminario de Integración y Aplicación", 563: "Economía de la Innovación", 
    601: "Matemática Financiera y Actuarial", 602: "Análisis Estadístico II", 603: "Dcho. Financiero y Seguros", 
    655: "Tecnología de las Comunicaciones", 657: "Sistemas de Datos", 658: "Metodología de Sist. de Información", 
    661: "Lógica Simbólica", 662: "Seguridad, Informática y Auditoría", 663: "Sistemas de Datos", 
    701: "Analítica de Datos", 717: "Modelos y Proyecciones Actuariales", 728: "Práctica Profesional del Actuario", 
    740: "Redes Informáticas", 746: "Computación Científica Actuarial", 751: "Estadística Actuarial", 
    752: "Análisis Numérico", 753: "Biometría Actuarial", 754: "Teoría Actuarial de Seguros Personales", 
    755: "Teoría Actuarial de Seguros Patrimoniales", 756: "Teoría Actuarial de Fondos de Jubilación", 
    757: "Teoría del Equilibrio Actuarial", 758: "Bases Act. Inversiones y Finanzas", 759: "Seminario de Integración", 
    763: "Teoría de los Juegos", 791: "Ética de las Ocupaciones", 795: "Conducción de Equipos", 
    1275: "Intro. a la Tecnol. de la Información", 1330: "Contabilidad Social y Ambiental", 
    1352: "Contabilidad Financiera", 1358: "Taller de Actuación Judicial", 1359: "Derecho Económico", 
    1360: "Derecho Crediticio y Bursátil", 1361: "Taller de Práctica Prof. en Org.", 1374: "Contab. Gubernamental", 
    1601: "Ingeniería de Software", 1603: "Derecho Informático I", 1604: "Derecho Informático II", 
    1652: "Teoría de Lenguajes y Algoritmos", 1653: "Tecnol. de los Computadores", 
    1654: "Construcción de Aplicaciones", 1660: "Actuación Profesional del Lic. en Sistemas", 
    1711: "Gestión de la Inteligencia Artificial", 1799: "Gestión de los Recursos Informáticos",
    9998: "Optativa I", 9999: "Optativa II"
}

# --- 2. ÁRBOLES DE CORRELATIVIDADES (Plan Actualizado) ---
# Estructura: Código: [Correlativas]
CORRELATIVAS = {
    247: [242], 248: [241], 249: [246], 250: [242], 251: [244], 274: [252], 
    276: [248], 278: [250], 279: [276], 272: [241, 245], 262: [250], 283: [262], 
    286: [250, 272], 351: [247], 353: [247], 355: [1352], 356: [251, 1352], 
    362: [353], 462: [251], 463: [245], 464: [247], 465: [248], 466: [463], 
    467: [276], 468: [278], 469: [467], 470: [465], 471: [279], 472: [467, 470], 
    540: [241], 542: [241, 245], 543: [540, 544], 544: [542], 548: [279, 602], 
    556: [291], 601: [540, 542], 602: [540, 542], 658: [1601], 663: [661], 
    751: [544, 602], 753: [601, 751, 752], 754: [753], 755: [601, 751], 
    1352: [351, 353], 1358: [355, 1360], 1361: [473], 1601: [1275], 1654: [1652], 
    1660: [740, 1654], 1799: [658, 662]
}

# --- 3. LISTAS DE MATERIAS POR CARRERA ---
PLANES_CARRERA = {
    "Actuario": [245, 241, 242, 246, 255, 256, 540, 542, 262, 274, 462, 602, 601, 751, 753, 544, 752, 291, 548, 279, 603, 746, 754, 755, 756, 757, 758, 717, 728, 9998, 9999],
    "Lic. en Sistemas": [241, 242, 245, 246, 252, 254, 248, 274, 250, 247, 249, 1275, 464, 278, 276, 279, 1653, 655, 740, 1652, 1654, 663, 662, 1660, 1601, 658, 1603, 1604, 1799, 9998, 9999],
    "Lic. en Administración": [245, 241, 242, 246, 252, 254, 248, 247, 250, 463, 274, 462, 276, 464, 278, 467, 466, 465, 468, 279, 469, 470, 471, 473, 472, 489, 9998, 9999],
    "Contador Público": [245, 241, 242, 246, 244, 243, 248, 252, 250, 247, 249, 251, 275, 278, 276, 274, 351, 353, 1359, 279, 1352, 362, 273, 1330, 355, 1374, 354, 1358, 356, 357, 1360, 1361, 9998],
    "Lic. en Economía": [245, 241, 242, 246, 255, 256, 540, 542, 262, 291, 541, 544, 547, 556, 549, 283, 548, 543, 545, 555, 554, 286, 558, 546, 559]
}

# --- 4. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_soft_v1")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "", "rank": 500.0, "car": "Contador Público", "aprob": [], "sedes": ["Córdoba"]}

# --- 5. SIDEBAR (PERFIL LIMPIO) ---
with st.sidebar:
    st.title("🌱 Perfil")
    u_reg = st.text_input("N° Registro", value=saved["reg"])
    u_rank = st.number_input("Ranking", value=float(saved["rank"]))
    u_car = st.selectbox("Carrera", list(PLANES_CARRERA.keys()), index=list(PLANES_CARRERA.keys()).index(saved["car"]))
    u_sedes = st.multiselect("Sedes", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.subheader("✅ Mi Progreso")
    plan_codes = PLANES_CARRERA[u_car]
    aprobadas = []
    
    # Buscador suave
    filtro = st.text_input("Buscar materia para marcar...")
    
    for cod in plan_codes:
        nombre = DB_MATERIAS.get(cod, f"Materia {cod}")
        if filtro.lower() in nombre.lower():
            # Verificación de correlatividades
            reqs = CORRELATIVAS.get(cod, [])
            faltan = [r for r in reqs if r not in aprobadas]
            bloqueada = len(faltan) > 0 and cod not in saved["aprob"]
            
            label = f"{nombre} ({cod})"
            if st.checkbox(label, value=(cod in saved["aprob"]), key=f"sidebar_{cod}", disabled=bloqueada):
                aprobadas.append(cod)
            if bloqueada:
                st.caption(f"🔒 Bloqueada por: {faltan}")

    if st.button("💾 GUARDAR"):
        data = {"reg": u_reg, "rank": u_rank, "car": u_car, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_soft_v1", json.dumps(data))
        st.success("Guardado.")

# --- 6. CUERPO PRINCIPAL ---
st.title(f"Planificador {u_car}")

tab1, tab2 = st.tabs(["🧩 Armar Cuatrimestre", "📋 Mi Carrera"])

with tab1:
    st.write("Elegí las materias que te gustaría cursar este cuatrimestre:")
    
    # Solo mostrar materias habilitadas (aprobó las correlativas y no la cursó ya)
    habilitadas = {c: DB_MATERIAS[c] for c in plan_codes if c not in aprobadas and all(r in aprobadas for r in CORRELATIVAS.get(c, []))}
    
    elegidas = st.multiselect("Materias disponibles:", options=list(habilitadas.keys()), format_func=lambda x: f"{habilitadas[x]} ({x})")
    
    st.write("Disponibilidad de Horarios:")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True)]

    if elegidas:
        # Oferta simulada con datos de tus fotos
        oferta_fce = [
            {"id": 466, "doc": "Scampini", "h": "07-09", "s": "Córdoba", "corte": 173.1},
            {"id": 355, "doc": "Gallego Tinto", "h": "07-09", "s": "Córdoba", "corte": 186.9},
            {"id": 276, "doc": "Sciaccaluga", "h": "07-09", "s": "Córdoba", "corte": 154.8},
            {"id": 751, "doc": "Landro", "h": "09-11", "s": "Córdoba", "corte": 181.6},
            {"id": 278, "doc": "Gesualdo", "h": "09-11", "s": "Córdoba", "corte": 131.4},
            {"id": 351, "doc": "Pahlen", "h": "09-11", "s": "Córdoba", "corte": 130.9},
            {"id": 543, "doc": "Calicchio", "h": "19-21", "s": "Córdoba", "corte": 185.0},
        ]
        
        filtrada = [o for o in oferta_fce if o["id"] in elegidas and o["s"] in u_sedes and o["h"] in u_bloques]
        
        if filtrada:
            st.subheader("Sugerencia de Cursada")
            for c in filtrada:
                diff = u_rank - c["corte"]
                color = "#059669" if diff > 20 else "#d97706" if diff > -20 else "#dc2626"
                st.markdown(f"""
                    <div class="materia-card">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight: 600;">{DB_MATERIAS[c['id']]}</span>
                            <span style="color: {color}; font-weight: bold;">● Probabilidad {('Alta' if diff > 20 else 'Media' if diff > -20 else 'Baja')}</span>
                        </div>
                        <div style="color: #6b7280; font-size: 0.9em; margin-top: 5px;">
                            Docente: {c['doc']} | Sede: {c['s']} | Horario: {c['h']} hs
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay cátedras cargadas que coincidan con tus filtros actuales.")

with tab2:
    st.subheader("Hoja de Ruta")
    # Generar tabla limpia de materias
    df_plan = []
    for c in plan_codes:
        status = "✅ Aprobada" if c in aprobadas else "🟢 Habilitada" if all(r in aprobadas for r in CORRELATIVAS.get(c, [])) else "🔒 Bloqueada"
        df_plan.append({"Código": c, "Materia": DB_MATERIAS.get(c, "N/A"), "Estado": status})
    st.dataframe(df_plan, use_container_width=True, hide_index=True)
