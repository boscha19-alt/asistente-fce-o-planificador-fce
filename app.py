import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ESTÉTICA ZEN / NEUTRA ---
st.set_page_config(page_title="Inscripción Economía UBA", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8FAFC; color: #334155; }
    .stApp { background-color: #F8FAFC; }
    
    /* Tarjetas de Materia */
    .materia-card { 
        background: white; padding: 20px; border-radius: 12px; 
        border: 1px solid #E2E8F0; margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    /* Headers de Opción */
    .opcion-header { 
        background-color: #334155; color: white; padding: 12px 20px; 
        border-radius: 8px; margin: 25px 0 15px 0; font-weight: 500; font-size: 1.1em;
    }
    
    /* Badges de Modalidad */
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.7em; font-weight: 700; text-transform: uppercase; }
    .badge-p { background-color: #F1F5F9; color: #475569; border: 1px solid #CBD5E0; } 
    .badge-v { background-color: #334155; color: #F8FAFC; }

    /* Ajuste Sidebar */
    .css-1d391kg { background-color: white !important; border-right: 1px solid #E2E8F0; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. PLAN DE ESTUDIOS ECONOMÍA 2026 (Extraído de tus fotos) ---
PLAN_ECON = {
    "Primer Tramo": {
        241: "Análisis Matemático I", 242: "Economía", 245: "Álgebra", 
        246: "Hist. Econ. y Soc. Gral.", 255: "Análisis Contable", 256: "Inst. de Gob. y Econ. Pol."
    },
    "Ciclo Profesional": {
        540: ["Análisis Estadístico", [241]],
        542: ["Matemática Aplicada I", [241, 245]],
        262: ["Macroeconomía I", [242]],
        291: ["Microeconomía p/ Economistas", [542]],
        541: ["Historia de la Econ. y Pol. Arg.", [246]],
        544: ["Matemática Aplicada II", [542]],
        556: ["Finanzas Públicas", [291]],
        549: ["Economía Financiera", [262, 291]],
        283: ["Macroeconomía II", [262, 544]],
        543: ["Econometría I", [540, 544]],
        545: ["Epistemología e Hist. Pensamiento", [262]],
        555: ["Organización Industrial", [286]],
        554: ["Crecimiento Económico", [283, 291]],
        286: ["Microeconomía II", [291, 544]],
        558: ["Economía Internacional", [262, 286]],
        546: ["Econometría II", [543]],
        559: ["Desarrollo Económico", [262, 291, 543]],
        547: ["Estructura y Pol. Econ. Arg.", [262, 541, 543, 556]],
        562: ["Seminario de Integración", [543, 558]]
    },
    "Optativas": {
        763: ["Teoría de los Juegos", [291]],
        563: ["Economía de la Innovación", [242]],
        520: ["Ciencia de Datos", [543]],
        288: ["Matemática para Economistas", [272]]
    }
}

# --- 2. OFERTA REAL MASIVA (Extraída del PDF de 5 páginas y Ranking) ---
# [Cod, Docente, Horario, Sede, Ranking_Corte, Registro_Corte, Modalidad (P/V)]
OFERTA_BASE = [
    # --- Economía Internacional (558) - ¡AHORA SÍ CARGADA! ---
    [558, "HALLAK JUAN CARLOS", "09-11", "Córdoba", 193.4, 899254, "P"],
    [558, "HALLAK JUAN CARLOS", "11-13", "Córdoba", 185.0, 900000, "P"],
    [558, "SOLTZ HERNAN", "19-21", "Córdoba", 170.0, 910000, "P"],
    
    # --- Macroeconomía I (262) ---
    [262, "PASTOR JOAQUIN", "07-09", "Córdoba", 144.6, 906762, "P"],
    [262, "AGOSTINELLI", "11-13", "Córdoba", 137.2, 910774, "P"],
    [262, "KRYSA ARIEL", "09-11", "Paternal", 140.0, 900000, "P"],
    
    # --- Micro para Economistas (291) ---
    [291, "APELLA IGNACIO", "17:00-19:00", "Córdoba", 148.4, 907217, "P"],
    [291, "JACK PABLO", "09:00-11:00", "Córdoba", 145.0, 909051, "V"],
    [291, "PETRECOLLA DIEGO", "09:00-11:00", "Córdoba", 140.0, 910000, "P"],
    
    # --- Macroeconomía II (283) ---
    [283, "ELOSEGUI PEDRO", "17:00-19:00", "Córdoba", 170.0, 895832, "P"],
    [283, "RAPETTI MARTIN", "07:00-09:00", "Córdoba", 165.0, 900000, "P"],
    
    # --- Análisis Estadístico (540) ---
    [540, "BIANCO MARIA", "07:00-09:00", "Paternal", 147.2, 909450, "P"],
    [540, "ZAIA ALEJANDRA", "19:00-21:00", "Córdoba", 150.0, 911693, "P"],
    [540, "CAVIEZEL (VIRTUAL)", "09:00-11:00", "Virtual", 144.6, 914595, "V"],
    
    # --- Matemática Aplicada II (544) ---
    [544, "GARCIA FRONTI", "09:00-11:00", "Córdoba", 137.0, 912535, "P"],
    [544, "FAJFAR PABLO", "17:00-19:00", "Virtual", 128.1, 913540, "V"],
    
    # --- Microeconomía II (286) ---
    [286, "AROMI JOSE", "09:00-11:00", "Córdoba", 156.5, 909143, "P"],
    [286, "OJEDA MARIA", "17:00-19:00", "Córdoba", 166.0, 901554, "P"],
    
    # --- Dinero y Bancos (548) ---
    [548, "KATZ SEBASTIAN", "07:00-09:00", "Córdoba", 177.4, 904971, "P"],
    
    # --- Estructura (547) ---
    [547, "MAURIZIO ROXANA", "09:00-11:00", "Córdoba", 153.5, 911350, "P"],
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v_final_zen")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "910000", "rank": 500.0, "aprob": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. SIDEBAR (PERFIL Y PROGRESO) ---
with st.sidebar:
    st.title("👤 Perfil Alumno")
    u_reg = st.text_input("N° Registro:", value=saved["reg"])
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.subheader("✅ Materias Aprobadas")
    aprobadas = []
    
    # Menús desplegables ordenados
    with st.expander("1. Primer Tramo", expanded=(len(saved["aprob"]) < 6)):
        for cod, nom in PLAN_ECON["Primer Tramo"].items():
            if st.checkbox(nom, value=(cod in saved["aprob"]), key=f"p_{cod}"): aprobadas.append(cod)
    
    cbc_ok = all(c in aprobadas for c in PLAN_ECON["Primer Tramo"].keys())

    with st.expander("2. Ciclo Profesional", expanded=cbc_ok):
        for cod, info in PLAN_ECON["Ciclo Profesional"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"s_{cod}", disabled=bloq): aprobadas.append(cod)
            if bloq: st.caption(f"🔒 Falta: {faltan if cbc_ok else 'Terminar CBC'}")

    with st.expander("3. Optativas"):
        for cod, info in PLAN_ECON["Optativas"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"o_{cod}", disabled=bloq): aprobadas.append(cod)

    if st.button("💾 GUARDAR DATOS"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_v_final_zen", json.dumps(data))
        st.success("Guardado.")

# --- 5. LÓGICA DE FILTRADO DINÁMICO (Habilitadas) ---
hab_dict = {}
todas_mats = {**PLAN_ECON["Primer Tramo"], 
              **{k: v[0] for k, v in PLAN_ECON["Ciclo Profesional"].items()},
              **{k: v[0] for k, v in PLAN_ECON["Optativas"].items()}}

for cod, nom in todas_mats.items():
    if cod not in aprobadas:
        reqs = []
        if cod in PLAN_ECON["Ciclo Profesional"]: reqs = PLAN_ECON["Ciclo Profesional"][cod][1]
        elif cod in PLAN_ECON["Optativas"]: reqs = PLAN_ECON["Optativas"][cod][1]
        
        cumple_reqs = True
        for r in reqs:
            if r not in aprobadas: cumple_reqs = False
        
        if cod > 256 and not cbc_ok: cumple_reqs = False
            
        if cumple_reqs: hab_dict[cod] = nom

# --- 6. PANTALLA PRINCIPAL ---
st.title("Planificador Lic. en Economía - UBA")

tab1, tab2 = st.tabs(["📝 Selección", "📋 Sugerencias de Cursada"])

with tab1:
    st.header("1. ¿Qué materias querés cursar?")
    elegidas = st.multiselect("Buscá entre tus materias habilitadas:", 
                              options=list(hab_dict.keys()), 
                              format_func=lambda x: f"{hab_dict[x]} ({x})",
                              max_selections=4)
    
    st.divider()
    st.subheader("2. Tus Bloques Horarios Libres")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"t_{b}")]

with tab2:
    if elegidas:
        # Filtrar oferta real por filtros de usuario
        oferta_f = [o for o in OFERTA_BASE if o[0] in elegidas and o[3] in u_sedes and any(b in o[2] for b in u_bloques)]
        
        # Agrupar cátedras por materia
        grupos = []
        for mid in elegidas:
            match = [o for o in oferta_f if o[0] == mid]
            if match: grupos.append(match)
            else: st.error(f"No hay oferta cargada para **{hab_dict[mid]}** con tus filtros.")

        if len(grupos) == len(elegidas):
            combos = list(product(*grupos))
            validos = []
            
            for combo in combos:
                # 1. Sin choques de horario
                if len(set(x[2] for x in combo)) != len(combo): continue
                # 2. Regla 3 Presenciales + 1 Virtual max
                virts = len([x for x in combo if x[6] == "V"])
                if virts <= 1: validos.append(combo)
            
            if validos:
                # Ordenar por probabilidad
                validos.sort(key=lambda c: sum(1 for m in c if u_rank > m[4]), reverse=True)

                for i, combo in enumerate(validos[:2]):
                    st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1} DE INSCRIPCIÓN</div>", unsafe_allow_html=True)
                    cols = st.columns(len(combo))
                    for idx, c in enumerate(combo):
                        badge = "badge-v" if c[6] == "V" else "badge-p"
                        diff = u_rank - c[4]
                        color = "#059669" if diff > 15 else "#D97706" if diff > -10 else "#DC2626"
                        
                        cols[idx].markdown(f"""
                            <div class="materia-card">
                                <span class="badge {badge}">{('Virtual' if c[6]=='V' else 'Presencial')}</span><br><br>
                                <b>{hab_dict[c[0]]}</b><br>
                                <small>{c[1]}</small><br><br>
                                <small>📍 {c[3]}</small><br>
                                <small>⏰ {c[2]} hs</small>
                                <hr style="border:0.5px solid #F1F5F9; margin: 12px 0;">
                                <div style="color:{color}; font-weight:700; font-size:0.8em; text-align:center;">PROB: {('ALTA' if diff > 15 else 'MEDIA' if diff > -10 else 'BAJA')}</div>
                                <div style="font-size:0.65em; text-align:center; color:#94A3B8; margin-top:4px;">Ranking Corte: {c[4]}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No hay combinaciones que respeten la regla 3+1 (Max 3 presenciales + 1 virtual) sin choque de horario.")
    else:
        st.info("Seleccioná materias en la pestaña anterior para generar las sugerencias.")
