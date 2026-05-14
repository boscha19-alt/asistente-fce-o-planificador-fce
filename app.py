import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import combinations, product

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="Planificador Economía UBA", layout="wide")

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
    .opcion-header { 
        background-color: #1E293B; color: white; padding: 12px 18px; 
        border-radius: 8px; margin: 25px 0 15px 0; font-weight: 500;
    }
    .badge-v { background-color: #F1F5F9; color: #475569; padding: 4px 8px; border-radius: 6px; font-size: 0.7em; font-weight: 700; }
    .badge-p { background-color: #F8FAFC; color: #64748B; padding: 4px 8px; border-radius: 6px; font-size: 0.7em; font-weight: 700; border: 1px solid #E2E8F0; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS MATERIAS (PLAN 2026) ---
PLAN_ECON = {
    "Primer Tramo": {241: "Análisis I", 242: "Economía", 245: "Álgebra", 246: "Hist. Gral.", 255: "Análisis Cont.", 256: "Gobierno"},
    "Ciclo Profesional": {
        540: ["Estadística", [241]], 542: ["Mat. Aplicada I", [241, 245]], 262: ["Macroeconomía I", [242]],
        291: ["Micro p/ Econ.", [542]], 541: ["Hist. Econ. Arg.", [246]], 544: ["Mat. Aplicada II", [542]],
        556: ["Finanzas Públicas", [291]], 549: ["Econ. Financiera", [262, 291]], 283: ["Macroeconomía II", [262, 544]],
        543: ["Econometría I", [540, 544]], 545: ["Epistemología", [262]], 555: ["Org. Industrial", [286]],
        554: ["Crecimiento Econ.", [283, 291]], 286: ["Microeconomía II", [291, 544]], 558: ["Econ. Internacional", [262, 286]],
        546: ["Econometría II", [543]], 559: ["Desarrollo Econ.", [262, 291, 543]], 547: ["Estructura y Pol.", [262, 541, 543, 556]]
    },
    "Optativas": {763: ["Teoría Juegos", [291]], 520: ["Ciencia Datos", [543]]}
}

# --- 2. OFERTA REAL MASIVA ---
OFERTA_TOTAL = [
    [558, "HALLAK JUAN CARLOS", "09-11", "Córdoba", 193.4, 899254, "P"],
    [558, "SOLTZ HERNAN", "19-21", "Córdoba", 170.0, 910000, "P"],
    [547, "MAURIZIO ROXANA", "09-11", "Córdoba", 153.5, 911350, "P"],
    [547, "KULFAS MATIAS", "19-21", "Córdoba", 150.0, 910000, "P"],
    [262, "WAINER VALERIA", "07-09", "Córdoba", 144.6, 906762, "P"],
    [262, "AGOSTINELLI", "11-13", "Córdoba", 137.2, 910774, "P"],
    [291, "FAJFAR PABLO", "17-19", "Córdoba", 148.4, 907217, "P"],
    [291, "JACK PABLO", "09-11", "Virtual", 145.0, 909051, "V"],
    [540, "ZAIA ALEJANDRA", "19-21", "Córdoba", 150.0, 911693, "P"],
    [544, "GARCIA FRONTI", "09-11", "Córdoba", 137.0, 912535, "P"],
    [286, "AROMI JOSE", "09-11", "Córdoba", 156.5, 909143, "P"],
    [543, "CALICCHIO NICOLAS", "19-21", "Córdoba", 185.0, 897120, "P"],
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v_final_flex")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "910981", "rank": 180.0, "aprob": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("👤 Mi Perfil")
    u_reg = st.text_input("N° Registro:", value=saved["reg"])
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "San Isidro", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.subheader("✅ Materias Aprobadas")
    aprobadas = []
    with st.expander("1. Primer Tramo"):
        for cod, nom in PLAN_ECON["Primer Tramo"].items():
            if st.checkbox(nom, value=(cod in saved["aprob"]), key=f"p_{cod}"): aprobadas.append(cod)
    cbc_ok = all(c in aprobadas for c in PLAN_ECON["Primer Tramo"].keys())
    with st.expander("2. Ciclo Profesional"):
        for cod, info in PLAN_ECON["Ciclo Profesional"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"s_{cod}", disabled=bloq): aprobadas.append(cod)

    if st.button("💾 GUARDAR"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_v_final_flex", json.dumps(data))
        st.success("Guardado.")

# --- 5. LÓGICA DE FILTRADO ---
total_mats_names = {**PLAN_ECON["Primer Tramo"], **{k:v[0] for k,v in PLAN_ECON["Ciclo Profesional"].items()}, **{k:v[0] for k,v in PLAN_ECON["Optativas"].items()}}
hab_list = []
for c, info in {**PLAN_ECON["Ciclo Profesional"], **PLAN_ECON["Optativas"]}.items():
    if c not in aprobadas and all(r in aprobadas for r in info[1]) and cbc_ok:
        hab_list.append(c)

# --- 6. PANTALLA PRINCIPAL ---
st.title("Planificador Lic. en Economía - UBA")
tab_sel, tab_suggest = st.tabs(["📝 Selección", "📋 Sugerencia de Cursada"])

with tab_sel:
    st.header("1. ¿Qué querés cursar?")
    elegidas = st.multiselect("Materias habilitadas:", options=hab_list, format_func=lambda x: f"{total_mats_names[x]} ({x})")
    
    st.subheader("2. Horarios Libres")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"time_{b}")]

with tab_suggest:
    if elegidas:
        # Filtrar oferta inicial
        oferta_f = [o for o in OFERTA_TOTAL if o[0] in elegidas and o[3] in u_sedes and o[2] in u_bloques]
        
        def find_valid_combos(target_subjects):
            grupos = []
            for mid in target_subjects:
                match = [o for o in oferta_f if o[0] == mid]
                if match: grupos.append(match)
            if len(grupos) < len(target_subjects): return []
            
            combos = list(product(*grupos))
            validos = []
            for combo in combos:
                if len(set(c[2] for c in combo)) == len(combo): # No choque
                    if len([c for c in combo if c[6] == "V"]) <= 1: # Regla 3+1
                        validos.append(combo)
            return validos

        # Intentar con todas, si falla, intentar con subsets
        validos = find_valid_combos(elegidas)
        message = ""
        
        if not validos:
            message = "⚠️ Se detectaron choques de horarios entre todas las opciones. Mostrando alternativas separadas:"
            # Intentar subsets de 1 materia si son 2 elegidas
            subsets = []
            for i in range(len(elegidas)-1, 0, -1):
                for sub in combinations(elegidas, i):
                    res = find_valid_combos(sub)
                    if res: subsets.extend(res)
                if subsets: break
            validos = subsets

        if validos:
            if message: st.warning(message)
            # Ordenar por Ranking/Registro
            validos.sort(key=lambda x: sum(100 if u_rank > m[4] else 0 for m in x), reverse=True)
            
            for i, combo in enumerate(validos[:2]): # Top 2 opciones
                st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1}</div>", unsafe_allow_html=True)
                cols = st.columns(len(combo))
                for idx, c in enumerate(combo):
                    badge = "badge-v" if c[6] == "V" else "badge-p"
                    prob = "ALTA" if u_rank > c[4] else "MEDIA" if u_rank > c[4]-15 else "BAJA"
                    color = "#059669" if prob == "ALTA" else "#D97706" if prob == "MEDIA" else "#DC2626"
                    
                    cols[idx].markdown(f"""
                        <div class="materia-card">
                            <span class="badge {badge}">{('Virtual' if c[6]=='V' else 'Presencial')}</span><br><br>
                            <b>{total_mats_names[c[0]]}</b><br><small>{c[1]}</small><br><br>
                            <small>📍 {c[3]} | ⏰ {c[2]} hs</small><hr style="border:0.5px solid #eee">
                            <div style="color:{color}; font-weight:700; font-size:0.8em; text-align:center;">PROB: {prob}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("No se pudo encontrar ninguna oferta para las materias elegidas en tus sedes/bloques.")
    else:
        st.info("Seleccioná materias en la pestaña anterior.")
