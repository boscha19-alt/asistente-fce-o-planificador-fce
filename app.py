import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ESTÉTICA NEUTRA ---
st.set_page_config(page_title="Planificador Economía UBA", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FAFAFA; color: #444; }
    .stApp { background-color: #FAFAFA; }
    
    /* Contenedores Neutros */
    .materia-card { 
        background: white; padding: 1.5rem; border-radius: 12px; 
        border: 1px solid #E5E7EB; margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    /* Botones y Checkboxes */
    .stCheckbox { font-size: 0.9em; }
    .stButton>button { 
        border-radius: 8px; border: 1px solid #D1D5DB; 
        background-color: white; color: #374151; font-weight: 500;
    }
    
    /* Badges */
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.75em; font-weight: 600; text-transform: uppercase; }
    .badge-presencial { background-color: #F3F4F6; color: #374151; }
    .badge-virtual { background-color: #EEF2FF; color: #4338CA; }
    .badge-prob { background-color: #ECFDF5; color: #065F46; }
    
    h1, h2, h3 { color: #111827; letter-spacing: -0.02em; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS LIC. EN ECONOMÍA (Plan Actualizado) ---
DB_ECON = {
    # Primer Tramo
    241: ["Análisis Matemático I", []], 242: ["Economía", []], 245: ["Álgebra", []], 
    246: ["Hist. Econ. y Soc. Gral.", []], 255: ["Análisis Contable", []], 
    256: ["Inst. de Gob. y Econ. Pol.", []],
    
    # Ciclo Profesional Obligatorio
    540: ["Análisis Estadístico", [241]], 542: ["Matemática Aplicada I", [241, 245]],
    262: ["Macroeconomía I", [242]], 291: ["Microeconomía p/ Economistas", [542]],
    541: ["Estructura y Pol. Econ. Arg.", [262]], 544: ["Matemática Aplicada II", [542]],
    547: ["Estructura Económica Arg.", [246, 262]], 556: ["Finanzas Públicas", [291]],
    549: ["Economía Financiera", [291]], 283: ["Macroeconomía II", [262, 544]],
    548: ["Dinero, Crédito y Bancos", [283]], 543: ["Econometría I", [540, 544]],
    545: ["Epistemología Económica", [244]], 555: ["Organización Industrial", [286]],
    554: ["Crecimiento Económico", [283]], 286: ["Microeconomía II", [291]],
    558: ["Economía Internacional", [286, 283]], 546: ["Econometría II", [543]],
    559: ["Desarrollo Económico", [554, 558]], 562: ["Seminario de Integración", [543, 558]],

    # Orientadas / Optativas Frecuentes
    763: ["Teoría de los Juegos", [291]],
    563: ["Economía de la Innovación", [242]],
    520: ["Ciencia de Datos", [543]],
    523: ["Econ. y Derecho Corp.", [251]],
    457: ["Teoría de la Decisión", [540]],
    1711: ["Gestión Inteligencia Art.", [245]]
}

# --- 2. OFERTA REAL (Basada en tus PDFs) ---
# [Código, Docente, Horario, Sede, Ranking Corte, Modalidad (P/V)]
OFERTA_ECON = [
    [262, "WAINER", "07-09", "Córdoba", 144.6, "Presencial"],
    [262, "AGOSTINELLI", "11-13", "Córdoba", 137.2, "Presencial"],
    [291, "FAJFAR", "17-19", "Córdoba", 148.4, "Presencial"],
    [291, "JACK PABLO", "09-11", "Córdoba", 145.0, "Virtual"],
    [540, "BIANCO", "07-09", "Paternal", 147.2, "Presencial"],
    [540, "ZAIA", "19-21", "Córdoba", 150.0, "Presencial"],
    [544, "GARCIA FRONTI", "09-11", "Córdoba", 137.0, "Presencial"],
    [544, "FAJFAR", "17-19", "Virtual", 128.1, "Virtual"],
    [286, "AROMI", "09-11", "Córdoba", 156.5, "Presencial"],
    [286, "OJEDA", "19-21", "Paternal", 166.0, "Presencial"],
    [543, "CALICCHIO", "19-21", "Córdoba", 185.0, "Presencial"],
    [543, "VITALE", "07-09", "Córdoba", 161.8, "Virtual"],
    [554, "COREMBERG", "11-13", "Córdoba", 180.6, "Presencial"],
    [548, "KATZ", "07-09", "Córdoba", 177.4, "Presencial"],
    [556, "SIRLIN", "17-19", "Córdoba", 175.7, "Presencial"]
]

# --- 3. LÓGICA DE PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v1")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "", "rank": 500.0, "aprob": [], "sedes": ["Córdoba"]}

with st.sidebar:
    st.title("👤 Mi Perfil")
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.subheader("✅ Materias Aprobadas")
    filtro = st.text_input("Filtrar materias...")
    aprobadas = []
    for cod, info in DB_ECON.items():
        if filtro.lower() in info[0].lower():
            # Bloqueo por correlativas
            faltan = [r for r in info[1] if r not in aprobadas]
            bloqueada = len(faltan) > 0 and cod not in saved["aprob"]
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved["aprob"]), key=f"s_{cod}", disabled=bloqueada):
                aprobadas.append(cod)

    if st.button("💾 GUARDAR PROGRESO"):
        data = {"reg": "", "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_v1", json.dumps(data))
        st.success("Progreso guardado.")

# --- 4. PANTALLA PRINCIPAL ---
st.title("🎓 Lic. en Economía - Plan 2023")

tab1, tab2 = st.tabs(["📝 Selección de Materias", "📋 Sugerencia de Inscripción"])

with tab1:
    st.header("Materias para este cuatrimestre")
    st.write("Seleccioná las materias que te gustaría cursar (máximo 4):")
    
    hab = {c: DB_ECON[c][0] for c in DB_ECON if c not in aprobadas and all(r in aprobadas for r in DB_ECON[c][1])}
    
    elegidas = st.multiselect("Materias habilitadas:", options=list(hab.keys()), 
                              format_func=lambda x: f"{hab[x]} ({x})", max_selections=4)
    
    st.divider()
    st.subheader("Tus Horarios Libres")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True)]

with tab2:
    if elegidas:
        # Filtrar oferta por sedes y horarios
        oferta_f = [o for o in OFERTA_ECON if o[0] in elegidas and o[3] in u_sedes and o[2] in u_bloques]
        
        # Agrupar por materia
        grupos = []
        for mid in elegidas:
            c_m = [o for o in oferta_f if o[0] == mid]
            if c_m: grupos.append(c_m)

        if len(grupos) == len(elegidas):
            combos = list(product(*grupos))
            validos = []
            
            for combo in combos:
                # 1. No superposición
                if len(set(x[2] for x in combo)) != len(combo): continue
                # 2. Máximo 1 virtual
                virtuales = len([x for x in combo if x[5] == "Virtual"])
                if virtuales > 1: continue
                # 3. Máximo 3 presenciales (implícito por el total de 4)
                validos.append(combo)
            
            if validos:
                st.info(f"Se generaron **{len(validos)}** combinaciones válidas.")
                # Ordenar por probabilidad (ranking)
                validos.sort(key=lambda x: sum(y[4] for x in combo for y in x), reverse=True)

                for i, combo in enumerate(validos[:2]): # Mostrar solo 2 opciones (1era y 2da)
                    st.subheader(f"OPCIÓN {i+1}")
                    cols = st.columns(len(combo))
                    for idx, c in enumerate(combo):
                        mode_badge = "badge-virtual" if c[5] == "Virtual" else "badge-presencial"
                        diff = u_rank - c[4]
                        color_prob = "#059669" if diff > 20 else "#D97706" if diff > -20 else "#DC2626"
                        
                        cols[idx].markdown(f"""
                            <div class="materia-card">
                                <span class="badge {mode_badge}">{c[5]}</span><br>
                                <div style="margin-top:10px; font-weight:600; font-size:1.1em;">{DB_ECON[c[0]][0]}</div>
                                <div style="color:#6B7280; font-size:0.9em; margin-bottom:15px;">{c[1]}</div>
                                <div style="font-size:0.85em;">📍 {c[3]}</div>
                                <div style="font-size:0.85em;">⏰ {c[2]} hs</div>
                                <hr style="border:0.5px solid #F3F4F6">
                                <div style="color:{color_prob}; font-weight:700; font-size:0.8em;">PROBABILIDAD: {('ALTA' if diff > 20 else 'MEDIA' if diff > -20 else 'BAJA')}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("No hay combinaciones que respeten la regla: Máximo 3 Presenciales + 1 Virtual/Distancia sin choque de horario.")
        else:
            st.warning("No hay oferta disponible para todas las materias seleccionadas en tus sedes/horarios.")
    else:
        st.info("Regresá a la pestaña de Selección para elegir tus materias de este cuatrimestre.")
