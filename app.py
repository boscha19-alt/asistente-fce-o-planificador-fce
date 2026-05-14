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
        540: ["Análisis Estadístico", [241]], 542: ["Mat. Aplicada I", [241, 245]], 262: ["Macroeconomía I", [242]],
        291: ["Micro p/ Econ.", [542]], 541: ["Hist. Econ. Arg.", [246]], 544: ["Mat. Aplicada II", [542]],
        556: ["Finanzas Públicas", [291]], 549: ["Econ. Financiera", [262, 291]], 283: ["Macroeconomía II", [262, 544]],
        543: ["Econometría I", [540, 544]], 545: ["Epistemología", [262]], 555: ["Org. Industrial", [286]],
        554: ["Crecimiento Econ.", [283, 291]], 286: ["Microeconomía II", [291, 544]], 558: ["Econ. Internacional", [262, 286]],
        546: ["Econometría II", [543]], 559: ["Desarrollo Econ.", [262, 291, 543]], 547: ["Estructura y Pol.", [262, 541, 543, 556]],
        562: ["Seminario Economía", [543, 558]]
    },
    "Optativas": {
        520: ["Ciencia Datos", [543]], 521: ["Econ. Austriaca", [242]], 523: ["Econ. y Dcho Corp.", [256]],
        563: ["Innovación", [242]], 763: ["Teoría Juegos", [291]]
    }
}

# --- 2. OFERTA ACADÉMICA TOTAL (68 PÁGINAS PROCESADAS) ---
# [Cod, Docente, Días, Horario, Sede, Ranking_Corte, Registro_Corte, Modalidad]
OFERTA_TOTAL = [
    # Macro I (262)
    [262, "PASTOR JOAQUIN", "Ma/Mi/Vi", "07-09", "Córdoba", 144.6, 906762, "P"],
    [262, "KRYSA ARIEL", "Lu/Mi/Ju", "09-11", "Córdoba", 140.0, 910774, "P"],
    [262, "DI LALLA", "Lu/Mi/Ju", "11-13", "Córdoba", 137.0, 910000, "P"],
    [262, "MICHELENA (ZACK)", "Lu/Mi/Ju", "09-11", "Avellaneda", 118.0, 914145, "P"],
    [262, "CERDAN (ZACK)", "Lu/Mi/Ju", "07-09", "Paternal", 130.0, 900000, "P"],
    [262, "FAVATA (ZACK)", "Lu/Ju", "11-13", "San Isidro", 132.7, 913239, "P"],
    # Macro II (283)
    [283, "ELOSEGUI PEDRO", "Ma/Vi/Sa", "17-19", "Córdoba", 170.0, 895832, "P"],
    [283, "LIBMAN EMILIANO", "Lu/Mi/Ju", "07-09", "Córdoba", 165.0, 900000, "P"],
    [283, "ZACK GUIDO", "Lu/Mi/Ju", "17-19", "Córdoba", 164.3, 903382, "P"],
    [283, "RAPETTI MARTIN", "Ma/Vi/Sa", "11-13", "Córdoba", 169.5, 906199, "P"],
    # Micro II (286)
    [286, "PAS CUINI", "Lu/Mi/Ju", "09-11", "Córdoba", 156.5, 909143, "P"],
    [286, "AROMI JOSE", "Lu/Mi/Ju", "11-13", "Córdoba", 156.0, 909000, "P"],
    [286, "OJEDA MARIA", "Lu/Mi/Ju", "17-19", "Córdoba", 166.0, 901554, "P"],
    [286, "ACOSTA JORGE", "Ma/Vi/Sa", "09-11", "Córdoba", 164.6, 903763, "P"],
    # Micro p/ Econ (291)
    [291, "MERCATANTE", "Lu/Mi/Ju", "17-19", "Córdoba", 148.4, 907217, "P"],
    [291, "JACK PABLO", "Lu/Mi/Ju", "09-11", "Córdoba", 145.0, 909051, "V"],
    [291, "FAJFAR PABLO", "Lu/Mi/Ju", "11-13", "Córdoba", 148.0, 907217, "P"],
    # Análisis Estadístico (540)
    [540, "LARRA MATIAS", "Lu/Mi/Ju", "09-11", "Avellaneda", 147.2, 909450, "P"],
    [540, "ZAIA ALEJANDRA", "Ma/Mi/Vi", "09-11", "Córdoba", 150.0, 911693, "P"],
    [540, "BIANCO MARIA", "Mi", "17-19", "Virtual", 147.0, 909450, "V"],
    # Matemática Aplicada I (542)
    [542, "PANIAGUA", "Lu/Mi/Ju", "07-09", "Córdoba", 130.0, 910000, "P"],
    [542, "GARCIA FRONTI", "Ma/Vi/Sa", "09-11", "Paternal", 137.0, 912535, "P"],
    # Econometría I (543)
    [543, "CALICCHIO", "Lu/Mi/Ju", "19-21", "Córdoba", 185.0, 897120, "P"],
    [543, "VITALE BLANCA", "Lu/Mi/Ju", "07-09", "Virtual", 161.8, 907635, "V"],
    [543, "FABRIS JULIO", "Lu/Mi/Ju", "09-11", "Córdoba", 163.2, 906746, "P"],
    # Internacional (558)
    [558, "HALLAK J.C.", "Lu/Ju", "09-11", "Córdoba", 193.4, 899254, "P"],
    [558, "HALLAK J.C.", "Lu/Ju", "11-13", "Córdoba", 185.0, 900000, "P"],
    [558, "SOLTZ HERNAN", "Lu/Ju", "19-21", "Córdoba", 170.0, 910000, "P"],
    # Estructura (547)
    [547, "MAURIZIO R.", "Lu/Ju", "09-11", "Córdoba", 153.5, 911350, "P"],
    [547, "KULFAS M.", "Ma/Vi", "11-13", "Córdoba", 150.0, 901996, "P"],
    # Dinero y Bancos (548)
    [548, "KATZ SEB.", "Ma/Vi", "09-11", "Córdoba", 177.4, 904971, "P"],
    [548, "LORENZO GUIDO", "Ma/Vi", "17-19", "Córdoba", 188.9, 894998, "P"],
    # Finanzas Públicas (556)
    [556, "SIRLIN PABLO", "Lu/Ju", "17-19", "Córdoba", 175.7, 909007, "P"],
    # Optativas
    [520, "MASTELLI (Data)", "Lu/Ju", "19-21", "Córdoba", 221.9, 877749, "P"],
    [763, "FAJFAR (Juegos)", "Ma/Vi", "09-11", "Virtual", 170.5, 911168, "V"],
    [563, "ARZA (Innov.)", "Lu", "09-11", "Virtual", 86.7, 920336, "V"]
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v_final_full")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "910981", "rank": 180.0, "aprob": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("👤 Perfil")
    u_reg = st.text_input("N° Registro:", value=saved["reg"])
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved["sedes"])
    
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
    with st.expander("3. Optativas"):
        for cod, info in PLAN_ECON["Optativas"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"o_{cod}", disabled=bloq): aprobadas.append(cod)

    if st.button("💾 GUARDAR"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_v_final_full", json.dumps(data))
        st.success("Guardado.")

# --- 5. LÓGICA DE FILTRADO ---
consolidated_names = {**PLAN_ECON["Primer Tramo"], **{k:v[0] for k,v in PLAN_ECON["Ciclo Profesional"].items()}, **{k:v[0] for k,v in PLAN_ECON["Optativas"].items()}}
hab_list = []
for c, info in {**PLAN_ECON["Ciclo Profesional"], **PLAN_ECON["Optativas"]}.items():
    if c not in aprobadas and all(r in aprobadas for r in info[1]) and cbc_ok:
        hab_list.append(c)

# --- 6. PANTALLA PRINCIPAL ---
st.title("Planificador Lic. en Economía - UBA")
tab_sel, tab_suggest = st.tabs(["📝 Selección", "📋 Sugerencia de Cursada"])

with tab_sel:
    st.header("1. ¿Qué querés cursar?")
    elegidas = st.multiselect("Materias habilitadas:", options=hab_list, format_func=lambda x: f"{consolidated_names[x]} ({x})")
    
    st.subheader("2. Horarios Libres")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"time_{b}")]

with tab_suggest:
    if elegidas:
        oferta_f = [o for o in OFERTA_TOTAL if o[0] in elegidas and o[4] in u_sedes and o[3] in u_bloques]
        
        def find_valid_combos(target_subjects):
            grupos = []
            for mid in target_subjects:
                match = [o for o in oferta_f if o[0] == mid]
                if match: grupos.append(match)
            if len(grupos) < len(target_subjects): return []
            combos = list(product(*grupos))
            validos = []
            for combo in combos:
                # No choque de bloque horario el mismo día
                occupied = set()
                clash = False
                for c in combo:
                    days = c[2].split("/")
                    for d in days:
                        slot = (d, c[3])
                        if slot in occupied: clash = True; break
                        occupied.add(slot)
                    if clash: break
                if not clash:
                    if len([c for c in combo if c[7] == "V"]) <= 1: validos.append(combo)
            return validos

        validos = find_valid_combos(elegidas)
        if not validos:
            for i in range(len(elegidas)-1, 0, -1):
                subsets = []
                for sub in combinations(elegidas, i):
                    res = find_valid_combos(sub)
                    if res: subsets.extend(res)
                if subsets: validos = subsets; break

        if validos:
            validos.sort(key=lambda x: sum(10 if u_rank > m[5] else 0 for m in x), reverse=True)
            for i, combo in enumerate(validos[:2]):
                st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1}</div>", unsafe_allow_html=True)
                cols = st.columns(len(combo))
                for idx, c in enumerate(combo):
                    badge = "badge-v" if c[7] == "V" else "badge-p"
                    prob = "ALTA" if u_rank > c[5] else "MEDIA" if u_rank > c[5]-15 else "BAJA"
                    color = "#059669" if prob == "ALTA" else "#D97706" if prob == "MEDIA" else "#DC2626"
                    cols[idx].markdown(f"""
                        <div class="materia-card">
                            <span class="{badge}">{('Virtual' if c[7]=='V' else 'Presencial')}</span><br><br>
                            <b>{consolidated_names[c[0]]}</b><br><small>{c[1]}</small><br><br>
                            <small>📅 {c[2]} | ⏰ {c[3]} hs</small><br>
                            <small>📍 {c[4]}</small><hr style="border:0.5px solid #eee">
                            <div style="color:{color}; font-weight:700; font-size:0.8em; text-align:center;">PROB: {prob}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else: st.error("No hay oferta cargada para estas materias.")
    else: st.info("Seleccioná materias en la pestaña anterior.")
