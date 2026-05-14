import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ESTÉTICA NEUTRA ---
st.set_page_config(page_title="Economía UBA 2026", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F9FAFB; color: #374151; }
    .stApp { background-color: #F9FAFB; }
    
    /* Estilo de Tarjetas */
    .materia-card { 
        background: white; padding: 20px; border-radius: 12px; 
        border: 1px solid #E5E7EB; margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .opcion-header { 
        background-color: #1F2937; color: white; padding: 10px 15px; 
        border-radius: 8px; margin: 25px 0 15px 0; font-weight: 500; letter-spacing: 0.5px;
    }
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.7em; font-weight: 700; }
    .badge-p { background-color: #F3F4F6; color: #374151; border: 1px solid #D1D5DB; } 
    .badge-v { background-color: #E5E7EB; color: #111827; border: 1px solid #9CA3AF; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS MATERIAS (PLAN CECE 2026 ACTUALIZADO) ---
PLAN_ECON = {
    "Primer Tramo": {
        245: "Álgebra", 241: "Análisis Matemático I", 242: "Economía", 
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
        561: ["Cuentas Nacionales", [262]],
        288: ["Matemática para Economistas", [272]]
    }
}

# --- 2. OFERTA REAL (DATOS EXTRAÍDOS DE TUS FOTOS DE RANKING) ---
# [Cod, Docente, Horario, Sede, Ranking Corte, Registro Corte, Modalidad]
OFERTA_BASE = [
    [262, "WAINER VALERIA", "07-09", "Córdoba", 144.6, 906762, "P"],
    [262, "AGOSTINELLI", "11-13", "Córdoba", 137.2, 910774, "P"],
    [291, "FAJFAR PABLO", "17-19", "Córdoba", 148.4, 907217, "P"],
    [291, "JACK PABLO", "09-11", "Virtual", 145.0, 909051, "V"],
    [540, "BIANCO MARIA", "07-09", "Paternal", 147.2, 909450, "P"],
    [540, "ZAIA ALEJANDRA", "19-21", "Córdoba", 150.0, 911693, "P"],
    [544, "GARCIA FRONTI", "09-11", "Córdoba", 137.0, 912535, "P"],
    [544, "FAJFAR PABLO", "17-19", "Virtual", 128.1, 913540, "V"],
    [286, "AROMI JOSE", "09-11", "Córdoba", 156.5, 909143, "P"],
    [543, "CALICCHIO NIC.", "19-21", "Córdoba", 185.0, 897120, "P"],
    [543, "VITALE BLANCA", "07-09", "Virtual", 161.8, 907635, "V"],
    [554, "COREMBERG ARIEL", "11-13", "Córdoba", 180.6, 896347, "P"],
    [548, "KATZ SEB.", "07-09", "Córdoba", 177.4, 904971, "P"],
    [556, "SIRLIN PABLO", "17-19", "Córdoba", 175.7, 909007, "P"],
    [541, "HIST. ECON. ARG", "11-13", "Córdoba", 141.0, 910000, "P"],
    [547, "ESTRUCTURA", "19-21", "Córdoba", 153.5, 911350, "P"]
]

# --- 3. LÓGICA DE PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v2026_fixed")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "910000", "rank": 500.0, "aprob": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("👤 Mi Perfil")
    u_reg = st.text_input("N° Registro:", value=saved["reg"])
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.subheader("✅ Materias Aprobadas")
    aprobadas = []
    
    # 1. Primer Tramo
    with st.expander("Primer Tramo (CBC/FCE)", expanded=True):
        for cod, nom in PLAN_ECON["Primer Tramo"].items():
            if st.checkbox(nom, value=(cod in saved["aprob"]), key=f"p_{cod}"):
                aprobadas.append(cod)
    
    # 2. Ciclo Profesional
    with st.expander("Ciclo Profesional"):
        for cod, info in PLAN_ECON["Ciclo Profesional"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = len(faltan) > 0 and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"s_{cod}", disabled=bloq):
                aprobadas.append(cod)
            if bloq: st.caption(f"🔒 Falta: {faltan}")

    # 3. Optativas
    with st.expander("Optativas"):
        for cod, info in PLAN_ECON["Optativas"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = len(faltan) > 0 and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"o_{cod}", disabled=bloq):
                aprobadas.append(cod)

    if st.button("💾 GUARDAR DATOS"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_v2026_fixed", json.dumps(data))
        st.success("Progreso guardado.")

# --- 5. FILTRADO DINÁMICO DE HABILITADAS (PEDIDO 1) ---
habilitadas_dict = {}
todas_mats_plan = {**PLAN_ECON["Primer Tramo"], 
                   **{k: v[0] for k, v in PLAN_ECON["Ciclo Profesional"].items()},
                   **{k: v[0] for k, v in PLAN_ECON["Optativas"].items()}}

for cod, nom in todas_mats_plan.items():
    if cod not in aprobadas:
        # Definir requisitos
        reqs = []
        if cod in PLAN_ECON["Ciclo Profesional"]: reqs = PLAN_ECON["Ciclo Profesional"][cod][1]
        elif cod in PLAN_ECON["Optativas"]: reqs = PLAN_ECON["Optativas"][cod][1]
        
        # Verificar si cumple correlativas
        if all(r in aprobadas for r in reqs):
            habilitadas_dict[cod] = nom

# --- 6. CUERPO PRINCIPAL ---
st.title("Planificador Lic. en Economía")

tab1, tab2 = st.tabs(["📝 Selección", "📋 Sugerencia de Inscripción"])

with tab1:
    st.header("Materias habilitadas para cursar")
    st.caption("Solo aparecen las materias que podés hacer según lo que aprobaste.")
    
    elegidas = st.multiselect("Seleccioná hasta 4 materias:", 
                              options=list(habilitadas_dict.keys()), 
                              format_func=lambda x: f"{habilitadas_dict[x]} ({x})",
                              max_selections=4)
    
    st.divider()
    st.subheader("Bloques Horarios Disponibles")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"time_{b}")]

with tab2:
    if elegidas:
        # Filtrar la oferta real
        oferta_f = [o for o in OFERTA_BASE if o[0] in elegidas and o[3] in u_sedes and o[2] in u_bloques]
        
        # Agrupar cátedras por materia seleccionada
        grupos_materia = []
        for mid in elegidas:
            match = [o for o in oferta_f if o[0] == mid]
            if match: grupos_materia.append(match)
        
        if len(grupos_materia) == len(elegidas):
            # Generar combinaciones de cátedras
            posibles_combos = list(product(*grupos_materia))
            validos = []
            
            for combo in posibles_combos:
                # 1. No choque de bloque horario
                if len(set(c[2] for c in combo)) != len(combo): continue
                # 2. Lógica 3+1 (Max 1 Virtual)
                virts = len([c for c in combo if c[6] == "V"])
                if virts > 1: continue
                validos.append(combo)
            
            if validos:
                # Ordenar por Ranking y Registro
                def get_score(comb):
                    s = 0
                    for m in comb:
                        if u_rank > m[4]: s += 100
                        if int(u_reg) <= m[5]: s += 50
                    return s
                
                validos.sort(key=get_score, reverse=True)

                for i, combo in enumerate(validos[:2]): # Mostrar Opción 1 y Opción 2
                    st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1} DE INSCRIPCIÓN</div>", unsafe_allow_html=True)
                    cols = st.columns(len(combo))
                    for idx, c in enumerate(combo):
                        mode = "VIRTUAL" if c[6] == "V" else "PRESENCIAL"
                        badge_c = "badge-v" if c[6] == "V" else "badge-p"
                        
                        # Probabilidad real
                        if u_rank > c[4]: prob, color = "ALTA", "#059669"
                        elif u_rank == c[4] and int(u_reg) <= c[5]: prob, color = "ALTA (Reg)", "#059669"
                        elif u_rank > c[4] - 15: prob, color = "MEDIA", "#D97706"
                        else: prob, color = "BAJA", "#DC2626"
                        
                        cols[idx].markdown(f"""
                            <div class="materia-card">
                                <span class="badge {badge_c}">{mode}</span><br><br>
                                <div style="font-weight:600; font-size:1.05em;">{habilitadas_dict[c[0]]}</div>
                                <div style="color:#6B7280; font-size:0.85em; margin-bottom:12px;">{c[1]}</div>
                                <div style="font-size:0.8em;">📍 {c[3]} | ⏰ {c[2]} hs</div>
                                <hr style="border:0.5px solid #F3F4F6; margin: 12px 0;">
                                <div style="color:{color}; font-weight:700; font-size:0.75em; text-align:center;">PROB: {prob}</div>
                                <div style="font-size:0.65em; color:#9CA3AF; text-align:center;">Corte: {c[4]}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No hay combinaciones que respeten la regla 3+1 (Max 1 Virtual) sin choque de horario.")
        else:
            st.error("Lo sentimos, no hay cátedras cargadas para alguna de las materias elegidas que coincidan con tus horarios/sedes.")
    else:
        st.info("Elegí al menos una materia en la pestaña Selección.")
