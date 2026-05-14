import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="Planificador Economía 2026", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FAFAFA; color: #444; }
    .stApp { background-color: #FAFAFA; }
    .materia-card { 
        background: white; padding: 20px; border-radius: 10px; 
        border: 1px solid #E5E7EB; margin-bottom: 12px;
    }
    .opcion-header { 
        background-color: #444; color: white; padding: 8px 15px; 
        border-radius: 6px; margin: 20px 0; font-weight: 500;
    }
    .badge-v { background-color: #F3F4F6; color: #6B7280; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; font-weight: 700; border: 1px solid #D1D5DB; }
    .badge-p { background-color: #FFF; color: #444; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; font-weight: 700; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS FIEL AL PLAN CECE 2026 (Foto enviada) ---
PLAN_ECON = {
    "Primer Tramo": {
        245: ["Álgebra", []], 
        241: ["Análisis Matemático I", []], 
        242: ["Economía", []], 
        246: ["Historia Econ. y Soc. Gral.", []], 
        255: ["Análisis Contable", []], 
        256: ["Inst. de Gob. y Econ. Pol.", []]
    },
    "Segundo Tramo / Profesional": {
        540: ["Análisis Estadístico", ["1er Tramo"]],
        542: ["Matemática Aplicada I", ["1er Tramo"]],
        262: ["Macroeconomía I", ["1er Tramo"]],
        291: ["Microeconomía p/ Economistas", [542]],
        541: ["Historia de la Econ. y Pol. Econ. Arg.", ["1er Tramo"]],
        544: ["Matemática Aplicada II", [542]],
        547: ["Estructura y Pol. Econ. Arg.", [262, 541, 543, 556]],
        556: ["Finanzas Públicas", [291]],
        549: ["Economía Financiera", [262, 291]],
        283: ["Macroeconomía II", [262, 544]],
        548: ["Dinero, Crédito y Bancos", [283, 546, 549]],
        543: ["Econometría I", [540, 544]],
        545: ["Epistemología e Hist. del Pens. Econ.", [262]],
        555: ["Organización Industrial", [286]],
        554: ["Crecimiento Económico", [283, 291]],
        286: ["Microeconomía II", [291, 544]],
        558: ["Economía Internacional", [262, 286]],
        546: ["Econometría II", [543]],
        559: ["Desarrollo Económico", [262, 291, 543]],
        562: ["Seminario Economía", [543, 558]]
    },
    "Optativas Orientadas": {
        763: ["Teoría de los Juegos", [291]],
        563: ["Economía de la Innovación", [242]],
        520: ["Ciencia de Datos", [543]],
        523: ["Econ. y Derecho Corp.", [251]]
    }
}

# --- 2. OFERTA REAL (Ajustada para Lic. Economía) ---
OFERTA_REAL = [
    [262, "WAINER VALERIA", "07-09", "Córdoba", 144.6, 906762, "Presencial"],
    [262, "AGOSTINELLI", "11-13", "Córdoba", 137.2, 910774, "Presencial"],
    [291, "FAJFAR PABLO", "17-19", "Córdoba", 148.4, 907217, "Presencial"],
    [291, "JACK PABLO", "09-11", "San Isidro", 145.0, 909051, "Virtual"],
    [540, "BIANCO MARIA", "07-09", "Paternal", 147.2, 909450, "Presencial"],
    [540, "ZAIA ALEJANDRA", "19-21", "Córdoba", 150.0, 911693, "Presencial"],
    [544, "GARCIA FRONTI", "09-11", "Córdoba", 137.0, 912535, "Presencial"],
    [544, "FAJFAR PABLO", "17-19", "Virtual", 128.1, 913540, "Virtual"],
    [286, "AROMI JOSE", "09-11", "Córdoba", 156.5, 909143, "Presencial"],
    [543, "CALICCHIO NIC.", "19-21", "Córdoba", 185.0, 897120, "Presencial"],
    [543, "VITALE BLANCA", "07-09", "Virtual", 161.8, 907635, "Virtual"],
    [548, "KATZ SEB.", "07-09", "Córdoba", 177.4, 904971, "Presencial"],
    [556, "SIRLIN PABLO", "17-19", "Córdoba", 175.7, 909007, "Presencial"],
    [541, "HIST. ECON. ARG", "11-13", "Córdoba", 141.0, 910000, "Presencial"]
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v2026")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "910000", "rank": 500.0, "aprob": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("👤 Mi Perfil")
    u_reg = st.text_input("N° Registro:", value=saved["reg"])
    u_rank = st.number_input("Ranking:", value=float(saved["rank"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.subheader("✅ Materias Aprobadas")
    aprobadas = []
    
    # 1. Primer Tramo
    with st.expander("Primer Tramo (CBC)", expanded=True):
        for cod, info in PLAN_ECON["Primer Tramo"].items():
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved["aprob"]), key=f"p_{cod}"):
                aprobadas.append(cod)
    
    cbc_full = all(c in aprobadas for c in PLAN_ECON["Primer Tramo"].keys())

    # 2. Ciclo Profesional
    with st.expander("Ciclo Profesional", expanded=cbc_full):
        for cod, info in PLAN_ECON["Segundo Tramo / Profesional"].items():
            # Check correlativas
            faltan = []
            for r in info[1]:
                if r == "1er Tramo":
                    if not cbc_full: faltan.append("1er Tramo")
                elif r not in aprobadas:
                    faltan.append(str(r))
            
            dis = len(faltan) > 0 and cod not in saved["aprob"]
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved["aprob"]), key=f"s_{cod}", disabled=dis):
                aprobadas.append(cod)
            if dis: st.caption(f"🔒 Bloqueada. Falta: {', '.join(faltan)}")

    # 3. Optativas
    with st.expander("Optativas"):
        for cod, info in PLAN_ECON["Optativas Orientadas"].items():
            faltan = [str(r) for r in info[1] if r not in aprobadas]
            dis = len(faltan) > 0 and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"o_{cod}", disabled=dis):
                aprobadas.append(cod)

    if st.button("💾 GUARDAR"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_v2026", json.dumps(data))
        st.success("Guardado.")

# --- 5. LÓGICA DE FILTRADO PARA EL CURSADO ---
# Solo habilitadas = No aprobadas Y requisitos cumplidos
habilitadas_dict = {}
for cat in PLAN_ECON:
    for cod, info in PLAN_ECON[cat].items():
        if cod not in aprobadas:
            # Check reqs
            if cat == "Primer Tramo":
                habilitadas_dict[cod] = info[0]
            else:
                reqs_ok = True
                for r in info[1]:
                    if r == "1er Tramo":
                        if not cbc_full: reqs_ok = False
                    elif r not in aprobadas:
                        reqs_ok = False
                if reqs_ok:
                    habilitadas_dict[cod] = info[0]

# --- 6. PANTALLA PRINCIPAL ---
st.title("Planificador Lic. en Economía")

tab_selec, tab_suggest = st.tabs(["📝 Elegir Materias", "📊 Sugerencia de Inscripción"])

with tab_selec:
    st.header("Seleccioná qué querés cursar este cuatrimestre")
    st.write("Solo aparecen materias que podés cursar según tus aprobadas:")
    
    elegidas = st.multiselect("Materias habilitadas:", options=list(habilitadas_dict.keys()), 
                              format_func=lambda x: f"{habilitadas_dict[x]} ({x})", max_selections=4)
    
    st.divider()
    st.subheader("Bloques Horarios Disponibles")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"time_{b}")]

with tab_suggest:
    if elegidas:
        # Filtrar oferta real
        oferta_f = [o for o in OFERTA_REAL if o[0] in elegidas and o[3] in u_sedes and o[2] in u_bloques]
        
        # Agrupar por materia
        grupos = []
        for mid in elegidas:
            c_m = [o for o in oferta_f if o[0] == mid]
            if c_m: grupos.append(c_m)

        if len(grupos) == len(elegidas):
            # Producto cartesiano de todas las cátedras posibles
            combos = list(product(*grupos))
            validos = []
            
            for combo in combos:
                # 1. No choque horario
                if len(set(x[2] for x in combo)) != len(combo): continue
                # 2. Máximo 1 virtual
                virts = len([x for x in combo if x[6] == "Virtual"])
                if virts > 1: continue
                validos.append(combo)
            
            if validos:
                # Puntaje para ordenar por probabilidad (Ranking + Registro)
                def get_score(c):
                    pts = 0
                    for m in c:
                        if u_rank > m[4]: pts += 10
                        if int(u_reg) <= m[5]: pts += 5
                    return pts
                
                validos.sort(key=get_score, reverse=True)

                for i, combo in enumerate(validos[:2]): # Mostrar máximo 2 opciones
                    st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1} DE INSCRIPCIÓN</div>", unsafe_allow_html=True)
                    cols = st.columns(len(combo))
                    for idx, c in enumerate(combo):
                        badge = "badge-v" if c[6] == "Virtual" else "badge-p"
                        # Lógica de probabilidad
                        if u_rank > c[4]: prob, color = "ALTA", "#059669"
                        elif u_rank == c[4] and int(u_reg) <= c[5]: prob, color = "ALTA (Reg)", "#059669"
                        elif u_rank > c[4] - 10: prob, color = "MEDIA", "#D97706"
                        else: prob, color = "BAJA", "#DC2626"
                        
                        cols[idx].markdown(f"""
                            <div class="materia-card">
                                <span class="{badge}">{c[6].upper()}</span><br><br>
                                <b>{habilitadas_dict[c[0]]}</b><br>
                                <small>{c[1]}</small><br><br>
                                <small>📍 {c[3]}</small><br>
                                <small>⏰ {c[2]} hs</small>
                                <hr style="border:0.5px solid #F1F5F9; margin: 12px 0;">
                                <div style="color:{color}; font-weight:700; font-size:0.8em; text-align:center;">PROB: {prob}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No hay combinaciones que respeten la regla 3+1 (Max 3 presenciales + 1 virtual) sin choque de horario.")
        else:
            st.error("No hay cátedras cargadas para alguna de las materias elegidas con tus filtros actuales.")
    else:
        st.info("Regresá a la pestaña de Selección y elegí al menos 1 materia.")
