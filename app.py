import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ESTÉTICA NEUTRA (PALETA STONE/SLATE) ---
st.set_page_config(page_title="Inscripción Economía UBA", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8FAFC; color: #334155; }
    .stApp { background-color: #F8FAFC; }
    
    /* Contenedores Estéticos */
    .materia-card { 
        background: white; padding: 1.5rem; border-radius: 12px; 
        border: 1px solid #E2E8F0; margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .opcion-header { 
        background-color: #1E293B; color: white; padding: 10px 18px; 
        border-radius: 8px; margin: 25px 0 15px 0; font-weight: 500;
    }
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.7em; font-weight: 700; text-transform: uppercase; }
    .badge-p { background-color: #F1F5F9; color: #475569; border: 1px solid #CBD5E0; } /* Presencial */
    .badge-v { background-color: #334155; color: #F8FAFC; } /* Virtual */
    
    /* Sidebar */
    .css-1d391kg { background-color: white !important; border-right: 1px solid #E2E8F0; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. PLAN DE ESTUDIOS ECONOMÍA 2026 ---
PLAN_ECON = {
    "Primer Tramo": {
        241: "Análisis Matemático I", 242: "Economía", 245: "Álgebra", 
        246: "Hist. Econ. y Soc. Gral.", 255: "Análisis Contable", 256: "Inst. de Gob. y Econ. Pol."
    },
    "Ciclo Profesional": {
        540: ["Análisis Estadístico", [241]], 542: ["Matemática Aplicada I", [241, 245]],
        262: ["Macroeconomía I", [242]], 291: ["Microeconomía p/ Economistas", [542]],
        541: ["Historia de la Econ. y Pol. Arg.", [246]], 544: ["Matemática Aplicada II", [542]],
        556: ["Finanzas Públicas", [291]], 549: ["Economía Financiera", [262, 291]],
        283: ["Macroeconomía II", [262, 544]], 543: ["Econometría I", [540, 544]],
        545: ["Epistemología e Hist. Pensamiento", [262]], 555: ["Organización Industrial", [286]],
        554: ["Crecimiento Económico", [283, 291]], 286: ["Microeconomía II", [291, 544]],
        558: ["Economía Internacional", [262, 286]], 546: ["Econometría II", [543]],
        559: ["Desarrollo Económico", [262, 291, 543]],
        547: ["Estructura y Pol. Econ. Arg.", [262, 541, 543, 556]],
        562: ["Seminario de Integración", [543, 558]]
    },
    "Optativas / Electivas": {
        520: ["Ciencia de Datos", [543]], 521: ["Econ. Austriaca", [242]], 522: ["Econ. Sraffiana", [262]],
        523: ["Econ. y Derecho Corp.", [256]], 527: ["Big Data & ML", [543]], 563: ["Econ. de Innovación", [242]],
        734: ["Sist. Econ. Comparados", [242]], 745: ["Econ. de la Energía", [262]], 767: ["Econ. Marxista", [242]],
        1721: ["Econ. del Comportamiento", [291]]
    }
}

# --- 2. OFERTA ACADÉMICA REAL (PROCESADA DEL PDF 2026) ---
# [Cod, Docente, Horario, Sede, Ranking_Corte, Modalidad (P/V)]
# Ranking_Corte aproximado según tus tablas de imágenes
OFERTA_REAL = [
    [262, "PASTOR J.", "07-09", "Córdoba", 144.0, "P"], [262, "KRYSA A.", "09-11", "Córdoba", 140.0, "P"],
    [262, "DI LALLA", "11-13", "Córdoba", 135.0, "P"], [262, "ZACK (AVEL)", "09-11", "Avellaneda", 118.0, "P"],
    [283, "ELOSEGUI", "17-19", "Córdoba", 170.0, "P"], [283, "RAPETTI", "07-09", "Córdoba", 165.0, "P"],
    [286, "AROMI", "09-11", "Córdoba", 156.5, "P"], [286, "OJEDA", "17-19", "Córdoba", 166.0, "P"],
    [291, "APELLA", "17-19", "Córdoba", 148.4, "P"], [291, "PETRECOLLA", "09-11", "Córdoba", 145.0, "P"],
    [291, "JACK PABLO", "09-11", "Virtual", 145.0, "V"],
    [540, "BIANCO (AVEL)", "09-11", "Avellaneda", 147.2, "P"], [540, "CAVIEZEL", "07-09", "Córdoba", 150.0, "P"],
    [540, "BIANCO (VIRT)", "17-19", "Virtual", 150.0, "V"],
    [541, "BELINI", "09-11", "Paternal", 141.0, "P"], [541, "ROUGIER", "17-19", "Córdoba", 145.0, "P"],
    [541, "BELINI (VIRT)", "19-21", "Virtual", 140.0, "V"],
    [542, "BIANCO", "07-09", "Córdoba", 130.0, "P"], [542, "GARCIA FRONTI", "19-21", "Paternal", 135.0, "P"],
    [542, "BIANCO (VIRT)", "13-15", "Virtual", 125.0, "V"],
    [543, "GONZALEZ M.", "07-09", "Córdoba", 167.0, "P"], [543, "MONTES ROJAS", "09-11", "Córdoba", 185.0, "P"],
    [543, "GONZALEZ (V)", "07-09", "Virtual", 161.0, "V"],
    [544, "TARULLO", "09-11", "Córdoba", 137.0, "P"], [544, "ZORZOLI", "15-17", "Córdoba", 130.0, "P"],
    [548, "KATZ", "09-11", "Córdoba", 177.4, "P"], [549, "GOMEZ J.", "19-21", "Córdoba", 160.0, "P"],
    [556, "CURCIO", "09-11", "Córdoba", 175.7, "P"], [547, "MAURIZIO", "09-11", "Córdoba", 153.5, "P"],
    [563, "ARZA (VIRT)", "09-11", "Virtual", 86.7, "V"]
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_vfinal_zen")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "900000", "rank": 500.0, "aprob": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("👤 Mi Perfil")
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

    with st.expander("2. Ciclo Profesional"):
        for cod, info in PLAN_ECON["Ciclo Profesional"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            # Caso especial Estructura: depende de las 4 que mencionaste
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"s_{cod}", disabled=bloq): aprobadas.append(cod)
            if bloq: st.caption(f"🔒 Bloqueada. Falta: {faltan if cbc_ok else 'Terminar CBC'}")

    with st.expander("3. Optativas"):
        for cod, info in PLAN_ECON["Optativas / Electivas"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"o_{cod}", disabled=bloq): aprobadas.append(cod)

    if st.button("💾 GUARDAR DATOS"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_vfinal_zen", json.dumps(data))
        st.success("Guardado.")

# --- 5. LÓGICA DE FILTRADO DINÁMICO (SÓLO LO QUE PODÉS CURSAR) ---
hab_dict = {}
todas_mats = {**PLAN_ECON["Primer Tramo"], 
              **{k: v[0] for k, v in PLAN_ECON["Ciclo Profesional"].items()},
              **{k: v[0] for k, v in PLAN_ECON["Optativas / Electivas"].items()}}

for cod, nom in todas_mats.items():
    if cod not in aprobadas:
        # Requisitos
        reqs = []
        if cod in PLAN_ECON["Ciclo Profesional"]: reqs = PLAN_ECON["Ciclo Profesional"][cod][1]
        elif cod in PLAN_ECON["Optativas / Electivas"]: reqs = PLAN_ECON["Optativas / Electivas"][cod][1]
        
        # Validar si puede cursar
        cumple_reqs = True
        for r in reqs:
            if r not in aprobadas: cumple_reqs = False
        
        # El profesional requiere el 1er tramo completo (excepto las del 1er tramo faltantes)
        if cod > 256 and not cbc_ok: cumple_reqs = False
            
        if cumple_reqs:
            hab_dict[cod] = nom

# --- 6. PANTALLA PRINCIPAL ---
st.title("Planificador Lic. en Economía - UBA")

tab1, tab2 = st.tabs(["📝 Selección", "📋 Sugerencias de Cursada"])

with tab1:
    st.header("Materias para este cuatrimestre")
    elegidas = st.multiselect("Buscá entre tus materias habilitadas (máx 4):", 
                              options=list(hab_dict.keys()), 
                              format_func=lambda x: f"{hab_dict[x]} ({x})",
                              max_selections=4)
    
    st.divider()
    st.subheader("Bloques Horarios que tenés libres")
    bloques = ["07:00-09:00", "09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00", "19:00-21:00", "21:00-23:00"]
    cols_h = st.columns(4)
    u_bloques = []
    for i, b in enumerate(bloques):
        if cols_h[i % 4].checkbox(b, value=True, key=f"t_{b}"):
            u_bloques.append(b[:5]) # Guardamos solo el inicio (ej: 07-09)

with tab2:
    if elegidas:
        # Filtrar oferta real por lo elegido, sedes y horas
        oferta_f = [o for o in OFERTA_REAL if o[0] in elegidas and o[3] in u_sedes and any(b in o[2] for b in u_bloques)]
        
        # Agrupar cátedras por materia
        grupos = []
        for mid in elegidas:
            match = [o for o in oferta_f if o[0] == mid]
            if match: grupos.append(match)

        if len(grupos) == len(elegidas):
            combos = list(product(*grupos))
            validos = []
            
            for combo in combos:
                # 1. Sin choques de horario
                if len(set(x[2] for x in combo)) != len(combo): continue
                # 2. Regla 3 Presenciales + 1 Virtual max
                virts = len([x for x in combo if x[5] == "V"])
                if virts <= 1: validos.append(combo)
            
            if validos:
                # Ordenar por probabilidad
                validos.sort(key=lambda c: sum(1 for m in c if u_rank > m[4]), reverse=True)

                for i, combo in enumerate(validos[:2]):
                    st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1} DE ARMADO</div>", unsafe_allow_html=True)
                    cols = st.columns(len(combo))
                    for idx, c in enumerate(combo):
                        badge = "badge-v" if c[5] == "V" else "badge-p"
                        diff = u_rank - c[4]
                        color = "#059669" if diff > 15 else "#D97706" if diff > -10 else "#DC2626"
                        
                        cols[idx].markdown(f"""
                            <div class="materia-card">
                                <span class="badge {badge}">{('Virtual' if c[5]=='V' else 'Presencial')}</span><br><br>
                                <b>{hab_dict[c[0]]}</b><br>
                                <small>{c[1]}</small><br><br>
                                <small>📍 {c[3]}</small><br>
                                <small>⏰ {c[2]} hs</small>
                                <hr style="border:0.5px solid #F1F5F9; margin: 12px 0;">
                                <div style="color:{color}; font-weight:700; font-size:0.75em; text-align:center;">PROBABILIDAD: {('ALTA' if diff > 15 else 'MEDIA' if diff > -10 else 'BAJA')}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No hay combinaciones que respeten la regla 3 Presenciales + 1 Virtual sin choque de horario.")
        else:
            st.error("No encontramos cátedras para todas las materias seleccionadas en tus sedes/horarios actuales.")
    else:
        st.info("Regresá a 'Elegir Materias' para comenzar.")
