import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ESTÉTICA ZEN (NEUTRA) ---
st.set_page_config(page_title="Inscripción Economía UBA", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F9FAFB; color: #374151; }
    .stApp { background-color: #F9FAFB; }
    .materia-card { 
        background: white; padding: 18px; border-radius: 12px; 
        border: 1px solid #E5E7EB; margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .opcion-header { 
        background-color: #1F2937; color: white; padding: 12px 18px; 
        border-radius: 8px; margin: 25px 0 15px 0; font-weight: 500;
    }
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.7em; font-weight: 700; text-transform: uppercase; margin-right: 5px;}
    .badge-p { background-color: #F3F4F6; color: #374151; border: 1px solid #D1D5DB; } 
    .badge-v { background-color: #E5E7EB; color: #111827; border: 1px solid #9CA3AF; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. PLAN DE ESTUDIOS ECONOMÍA 2026 (FIEL A TU FOTO) ---
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
        520: ["Ciencia de Datos", [543]], 521: ["Economía Austriaca", [242]],
        763: ["Teoría de los Juegos", [291]], 563: ["Economía de la Innovación", [242]]
    }
}

# --- 2. OFERTA REAL MASIVA (DATOS EXTRAÍDOS DE TU PDF Y RANKINGS) ---
# [Cod, Docente, Horario, Sede, Ranking Corte, Registro Corte, Modalidad (P=Presencial, V=Virtual)]
OFERTA_BASE = [
    # Macro I (262)
    [262, "PASTOR JOAQUIN", "07-09", "Córdoba", 144.6, 906762, "P"],
    [262, "KRYSA ARIEL", "09-11", "Córdoba", 137.2, 910774, "P"],
    [262, "DI LALLA DANIELA", "11-13", "Córdoba", 140.0, 910000, "P"],
    [262, "ZACK GUIDO", "09-11", "Avellaneda", 118.0, 914145, "P"],
    # Macro II (283)
    [283, "ELOSEGUI PEDRO", "17-19", "Córdoba", 170.0, 895832, "P"],
    [283, "LIBMAN EMILIANO", "07-09", "Córdoba", 165.0, 900000, "P"],
    # Micro II (286)
    [286, "AROMI JOSE", "09-11", "Córdoba", 156.5, 909143, "P"],
    [286, "OJEDA MARIA", "17-19", "Córdoba", 166.0, 901554, "P"],
    # Micro para Economistas (291)
    [291, "MERCATANTE JUAN", "17-19", "Córdoba", 148.4, 907217, "P"],
    [291, "JACK PABLO", "09-11", "Córdoba", 145.0, 909051, "V"],
    # Análisis Estadístico (540)
    [540, "LARRA MATIAS", "09-11", "Avellaneda", 147.2, 909450, "P"],
    [540, "ZAIA ALEJANDRA", "19-21", "Córdoba", 150.0, 911693, "P"],
    # Hist Econ Arg (541)
    [541, "BELINI CLAUDIO", "09-11", "Paternal", 141.0, 910000, "P"],
    [541, "ROUGIER MARCELO", "09-11", "Córdoba", 145.0, 900000, "P"],
    # Matemática Aplicada I (542)
    [542, "PANIAGUA FABIAN", "07-09", "Córdoba", 130.0, 910000, "P"],
    # Econometría I (543)
    [543, "CALICCHIO NICOLAS", "19-21", "Córdoba", 185.0, 897120, "P"],
    [543, "VITALE BLANCA", "07-09", "Virtual", 161.8, 907635, "V"],
    # Matemática Aplicada II (544)
    [544, "TARULLO EDUARDO", "09-11", "Córdoba", 137.0, 912535, "P"],
    # Dinero y Bancos (548)
    [548, "KATZ SEBASTIAN", "07-09", "Córdoba", 177.4, 904971, "P"],
    # Finanzas Públicas (556)
    [556, "SIRLIN PABLO", "17-19", "Córdoba", 175.7, 909007, "P"],
    # Crecimiento Económico (554)
    [554, "COREMBERG ARIEL", "11-13", "Córdoba", 180.6, 896347, "P"],
    # Estructura (547)
    [547, "MAURIZIO ROXANA", "09-11", "Córdoba", 153.5, 911350, "P"],
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_final_v1")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "910000", "rank": 500.0, "aprob": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. SIDEBAR (PERFIL Y MATERIAS APROBADAS) ---
with st.sidebar:
    st.title("👤 Mi Perfil")
    u_reg = st.text_input("N° Registro:", value=saved["reg"])
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved["sedes"])
    
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
            # Caso especial Estructura: depende de las 4 que mencionaste
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
        cookie_manager.set("fce_econ_final_v1", json.dumps(data))
        st.success("Guardado.")

# --- 5. LÓGICA DE FILTRADO PARA EL CURSADO (DROPDOWN DINÁMICO) ---
habilitadas_dict = {}
todas_mats_plan = {**PLAN_ECON["Primer Tramo"], 
                   **{k: v[0] for k, v in PLAN_ECON["Ciclo Profesional"].items()},
                   **{k: v[0] for k, v in PLAN_ECON["Optativas"].items()}}

for cod, nom in todas_mats_plan.items():
    if cod not in aprobadas:
        reqs = []
        if cod in PLAN_ECON["Ciclo Profesional"]: reqs = PLAN_ECON["Ciclo Profesional"][cod][1]
        elif cod in PLAN_ECON["Optativas"]: reqs = PLAN_ECON["Optativas"][cod][1]
        
        if all(r in aprobadas for r in reqs):
            habilitadas_dict[cod] = nom

# --- 6. PANTALLA PRINCIPAL ---
st.title("Planificador Lic. en Economía - UBA")

tab1, tab2 = st.tabs(["📝 Selección de Materias", "📋 Sugerencia de Inscripción"])

with tab1:
    st.header("1. Elegí qué querés cursar este cuatrimestre")
    st.caption("Solo verás materias que podés cursar según tus correlativas aprobadas.")
    
    elegidas = st.multiselect("Materias disponibles:", 
                              options=list(habilitadas_dict.keys()), 
                              format_func=lambda x: f"{habilitadas_dict[x]} ({x})",
                              max_selections=4)
    
    st.divider()
    st.subheader("2. Tus Bloques Horarios Disponibles")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"time_{b}")]

with tab2:
    if elegidas:
        # Filtrar oferta real por sedes y horarios
        oferta_f = [o for o in OFERTA_BASE if o[0] in elegidas and o[3] in u_sedes and o[2] in u_bloques]
        
        # Agrupar cátedras por materia
        grupos_materia = []
        encontradas_ids = []
        for mid in elegidas:
            match = [o for o in oferta_f if o[0] == mid]
            if match:
                grupos_materia.append(match)
                encontradas_ids.append(mid)
            else:
                st.error(f"No hay cátedras para **{habilitadas_dict[mid]}** en las sedes/horarios seleccionados.")

        if len(grupos_materia) == len(elegidas):
            combos = list(product(*grupos_materia))
            validos = []
            
            for combo in combos:
                # 1. No choque horario
                if len(set(c[2] for c in combo)) != len(combo): continue
                # 2. Regla 3+1 (Max 1 Virtual)
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

                for i, combo in enumerate(validos[:2]): # Opción 1 y 2
                    st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1} DE CURSADA</div>", unsafe_allow_html=True)
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
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No hay combinaciones que respeten la regla 3+1 (Max 1 Virtual) sin choque de horario.")
    else:
        st.info("Regresá a la pestaña Selección para elegir tus materias.")
