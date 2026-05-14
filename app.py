import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import combinations, product

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="Inscripción Economía UBA", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8F9FA; color: #334155; }
    .stApp { background-color: #F8F9FA; }
    .materia-card { 
        background: white; padding: 18px; border-radius: 12px; 
        border: 1px solid #E2E8F0; margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .opcion-title { 
        color: #1E293B; font-size: 1.4em; font-weight: 600; 
        border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-top: 30px;
    }
    .badge-v { background-color: #F1F5F9; color: #475569; padding: 4px 8px; border-radius: 6px; font-size: 0.7em; font-weight: 700; }
    .badge-p { background-color: #F8FAFC; color: #64748B; padding: 4px 8px; border-radius: 6px; font-size: 0.7em; font-weight: 700; border: 1px solid #E2E8F0; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS MAESTRA ECONOMÍA (PLAN 2023/25) ---
PLAN_ECON = {
    "Primer Tramo": {
        241: "Análisis Matemático I", 242: "Economía", 245: "Álgebra", 
        246: "Hist. Econ. y Soc. Gral.", 255: "Análisis Contable", 256: "Inst. de Gob. y Econ. Pol."
    },
    "Ciclo Profesional": {
        540: ["Análisis Estadístico", [241]], 542: ["Matemática Aplicada I", [241, 245]],
        262: ["Macroeconomía I", [242]], 291: ["Microeconomía p/ Economistas", [542]],
        541: ["Estructura y Pol. Econ. Arg.", [262]], 544: ["Matemática Aplicada II", [542]],
        547: ["Estructura Económica Arg.", [246, 262]], 556: ["Finanzas Públicas", [291]],
        549: ["Economía Financiera", [291]], 283: ["Macroeconomía II", [262, 544]],
        548: ["Dinero, Crédito y Bancos", [283]], 543: ["Econometría I", [540, 544]],
        545: ["Epistemología Económica", [242]], 555: ["Organización Industrial", [286]],
        554: ["Crecimiento Económico", [283]], 286: ["Microeconomía II", [291]],
        558: ["Economía Internacional", [286, 283]], 546: ["Econometría II", [543]],
        559: ["Desarrollo Económico", [554, 558]], 562: ["Seminario de Integración", [543, 558]]
    },
    "Optativas/Orientadas": {
        763: ["Teoría de los Juegos", [291]], 563: ["Economía de la Innovación", [242]],
        520: ["Ciencia de Datos", [543]], 523: ["Econ. y Derecho Corp.", [251]],
        457: ["Teoría de la Decisión", [540]], 561: ["Cuentas Nacionales", [262]],
        288: ["Matemática para Economistas", [272]]
    }
}

# --- 2. OFERTA ACADÉMICA CARGADA DESDE TU PDF Y RANKINGS ---
# [Cod, Docente, Horario, Sede, Ranking_Corte, Registro_Corte, Modalidad (R=Regular, V=Virtual)]
OFERTA_TOTAL = [
    # Macro I (262)
    [262, "WAINER VALERIA", "07-09", "Córdoba", 144.6, 906762, "R"],
    [262, "AGOSTINELLI", "11-13", "Córdoba", 137.2, 910774, "R"],
    [262, "KRYSA ARIEL", "09-11", "Paternal", 140.0, 900000, "R"],
    # Micro p/ Economistas (291)
    [291, "FAJFAR PABLO", "17-19", "Córdoba", 148.4, 907217, "R"],
    [291, "JACK PABLO", "09-11", "Virtual", 145.0, 909051, "V"],
    # Análisis Estadístico (540)
    [540, "BIANCO MARIA", "07-09", "Paternal", 147.2, 909450, "R"],
    [540, "ZAIA ALEJANDRA", "19-21", "Córdoba", 150.0, 911693, "R"],
    [540, "LARRA MATIAS", "09-11", "Avellaneda", 140.0, 900000, "R"],
    # Matemática Aplicada II (544)
    [544, "GARCIA FRONTI", "09-11", "Córdoba", 137.0, 912535, "R"],
    [544, "FAJFAR PABLO", "17-19", "Virtual", 128.1, 913540, "V"],
    # Microeconomía II (286)
    [286, "AROMI JOSE", "09-11", "Córdoba", 156.5, 909143, "R"],
    [286, "OJEDA MARIA", "19-21", "Paternal", 166.0, 901554, "R"],
    [286, "ACOSTA JORGE", "07-09", "Virtual", 166.7, 900138, "V"],
    # Econometría I (543)
    [543, "CALICCHIO NICOLAS", "19-21", "Córdoba", 185.0, 897120, "R"],
    [543, "VITALE BLANCA", "07-09", "Córdoba", 161.8, 907635, "V"],
    [543, "FABRIS JULIO", "17-19", "Córdoba", 163.2, 906746, "R"],
    # Crecimiento Económico (554)
    [554, "COREMBERG ARIEL", "11-13", "Córdoba", 180.6, 896347, "R"],
    # Dinero y Bancos (548)
    [548, "KATZ SEBASTIAN", "07-09", "Córdoba", 177.4, 904971, "R"],
    [548, "LORENZO GUIDO", "19-21", "Córdoba", 188.9, 894998, "R"],
    # Finanzas Públicas (556)
    [556, "SIRLIN PABLO", "17-19", "Córdoba", 175.7, 909007, "R"],
    # Optativas
    [545, "WEISMAN DIEGO", "11-13", "Córdoba", 121.6, 917588, "R"],
    [763, "FAJFAR (Juegos)", "09-11", "Virtual", 170.5, 911168, "V"],
    [563, "ARZA VALERIA", "09-11", "Virtual", 86.7, 920336, "V"]
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v_final_full")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "900000", "rank": 500.0, "aprob": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. SIDEBAR ORDENADO ---
with st.sidebar:
    st.title("👤 Mi Perfil")
    u_reg = st.text_input("N° Registro:", value=saved["reg"])
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.subheader("✅ Materias Aprobadas")
    aprobadas = []
    
    with st.expander("1. Primer Tramo", expanded=(len(saved["aprob"]) < 6)):
        for cod, nom in PLAN_ECON["Primer Tramo"].items():
            if st.checkbox(nom, value=(cod in saved["aprob"]), key=f"p_{cod}"): aprobadas.append(cod)
    
    with st.expander("2. Ciclo Profesional"):
        for cod, info in PLAN_ECON["Ciclo Profesional"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or len(aprobadas) < 6) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"s_{cod}", disabled=bloq): aprobadas.append(cod)
            if bloq: st.caption(f"🔒 Bloqueada. Faltan: {faltan if len(aprobadas)>=6 else 'CBC'}")

    with st.expander("3. Optativas"):
        for cod, info in PLAN_ECON["Optativas/Orientadas"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or len(aprobadas) < 6) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"o_{cod}", disabled=bloq): aprobadas.append(cod)

    if st.button("💾 GUARDAR"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_v_final_full", json.dumps(data))
        st.success("Progreso guardado.")

# --- 5. CUERPO PRINCIPAL ---
st.title("⚖️ Planificador Economía UBA")

tab_sel, tab_suggest = st.tabs(["📝 Selección", "📋 Sugerencias de Cursada"])

with tab_sel:
    st.header("Materias para este cuatrimestre")
    total_mats_dict = {**PLAN_ECON["Primer Tramo"], **{k:v[0] for k,v in PLAN_ECON["Ciclo Profesional"].items()}, **{k:v[0] for k,v in PLAN_ECON["Optativas/Orientadas"].items()}}
    
    # Solo habilitadas
    hab_list = []
    for c, info in {**PLAN_ECON["Ciclo Profesional"], **PLAN_ECON["Optativas/Orientadas"]}.items():
        if c not in aprobadas and all(r in aprobadas for r in info[1]) and len(aprobadas) >= 6:
            hab_list.append(c)
    # Sumar tramo 1 faltante
    for c, nom in PLAN_ECON["Primer Tramo"].items():
        if c not in aprobadas: hab_list.append(c)

    elegidas = st.multiselect("Elegí hasta 4 materias:", options=hab_list, format_func=lambda x: f"{total_mats_dict[x]} ({x})", max_selections=4)
    
    st.divider()
    st.subheader("Bloques Horarios que podés cursar")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"time_{b}")]

with tab_suggest:
    if elegidas:
        oferta_f = [o for o in OFERTA_TOTAL if o[0] in elegidas and o[3] in u_sedes and o[2] in u_bloques]
        
        grupos = []
        for mid in elegidas:
            c_m = [o for o in oferta_f if o[0] == mid]
            if c_m: grupos.append(c_m)

        if len(grupos) == len(elegidas):
            combos = list(product(*grupos))
            validos = []
            
            for combo in combos:
                # 1. No choque horario
                if len(set(x[2] for x in combo)) != len(combo): continue
                # 2. Regla 3 Presenciales + 1 Virtual max
                virts = len([x for x in combo if x[6] == "V"])
                if virts > 1: continue
                validos.append(combo)
            
            if validos:
                # Ranking logic score
                def score(c):
                    s = 0
                    for m in c:
                        if u_rank > m[4]: s += 10
                        if int(u_reg) <= m[5]: s += 5
                    return s
                
                validos.sort(key=score, reverse=True)

                for i, combo in enumerate(validos[:2]): # Opción 1 y 2
                    st.markdown(f"<div class='opcion-title'>OPCIÓN {i+1}</div>", unsafe_allow_html=True)
                    cols = st.columns(len(combo))
                    for idx, c in enumerate(combo):
                        mode_label = "VIRTUAL" if c[6] == "V" else "PRESENCIAL"
                        badge_class = "badge-v" if c[6] == "V" else "badge-p"
                        
                        # Probabilidad
                        if u_rank > c[4] + 10: prob, color = "ALTA", "#059669"
                        elif u_rank > c[4] - 5: prob, color = "MEDIA", "#D97706"
                        else: prob, color = "BAJA", "#DC2626"
                        
                        cols[idx].markdown(f"""
                            <div class="materia-card">
                                <span class="{badge_class}">{mode_label}</span><br><br>
                                <div style="font-weight:600; font-size:1.1em; color:#1E293B;">{total_mats_dict[c[0]]}</div>
                                <div style="color:#64748B; font-size:0.9em; margin-bottom:12px;">{c[1]}</div>
                                <div style="font-size:0.85em;">📍 {c[3]} | ⏰ {c[2]} hs</div>
                                <hr style="border:0.5px solid #F1F5F9; margin: 12px 0;">
                                <div style="color:{color}; font-weight:700; font-size:0.8em; text-align:center;">{prob}</div>
                                <div style="font-size:0.7em; color:#94A3B8; text-align:center; margin-top:4px;">Corte: {c[4]} | Reg: {c[5]}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No hay combinaciones que respeten la regla 3 Presenciales + 1 Virtual sin choque de horario.")
        else:
            st.error("No hay cátedras cargadas para alguna de las materias elegidas en tus sedes o horarios.")
    else:
        st.info("Elegí las materias en la pestaña anterior para generar las sugerencias.")
