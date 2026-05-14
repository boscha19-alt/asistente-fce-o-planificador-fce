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
        background: white; padding: 20px; border-radius: 12px; 
        border: 1px solid #E2E8F0; margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .opcion-header { 
        background-color: #1E293B; color: white; padding: 12px 18px; 
        border-radius: 8px; margin: 25px 0 15px 0; font-weight: 500;
    }
    .badge-v { background-color: #F1F5F9; color: #475569; padding: 4px 8px; border-radius: 6px; font-size: 0.7em; font-weight: 700; }
    .badge-p { background-color: #F8FAFC; color: #64748B; padding: 4px 8px; border-radius: 6px; font-size: 0.7em; font-weight: 700; border: 1px solid #E2E8F0; }
    .virt-day { color: #2563EB; font-size: 0.8em; font-weight: 600; margin-top: 5px; }
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
        563: ["Innovación", [242]], 763: ["Teoría Juegos", [291]], 1721: ["Econ. Comportamiento", [291]]
    }
}

# --- 2. OFERTA ACADÉMICA COMPLETA (PROCESADA DE TU PDF) ---
# [Cod, Cátedra, Profesor, Días, Horario, Sede, Ranking_Corte, Modalidad, Día_Virtual]
OFERTA_TOTAL = [
    # Macro I (262)
    [262, "DPTO. ECONOMÍA", "Pastor Joaquin", "Ma/Mi/Vi", "07-09", "Córdoba", 144.6, "P", ""],
    [262, "DPTO. ECONOMÍA", "Krysa Ariel", "Lu/Mi/Ju", "09-11", "Córdoba", 140.0, "P", ""],
    [262, "ZACK GUIDO", "Michelena Gabriel", "Lu/Mi/Ju", "09-11", "Avellaneda", 118.0, "P", ""],
    [262, "ZACK GUIDO", "Cerdan Manuel", "Lu/Mi/Ju", "07-09", "Paternal", 130.0, "P", ""],
    [262, "ZACK GUIDO", "Favata Federico", "Lu/Ju", "11-13", "San Isidro", 132.7, "P", "Lunes presencial 09-13"],
    # Macro II (283)
    [283, "ELOSEGUI", "Elosegui Pedro", "Ma/Vi/Sa", "17-19", "Córdoba", 170.0, "P", "Sábado virtual (11-13)"],
    [283, "RAPETTI", "Libman Emiliano", "Lu/Mi/Ju", "07-09", "Córdoba", 165.0, "P", ""],
    [283, "RAPETTI", "Rapetti Martin", "Ma/Vi/Sa", "11-13", "Córdoba", 169.5, "P", ""],
    [283, "RAPETTI", "Zack Guido", "Lu/Mi/Ju", "17-19", "Córdoba", 164.3, "P", ""],
    [283, "RAPETTI", "Pierri Damian", "Lu/Mi/Ju", "19-21", "Córdoba", 158.4, "P", ""],
    # Micro II (286)
    [286, "AROMI", "Pascuini Paulo", "Lu/Mi/Ju", "09-11", "Córdoba", 156.5, "P", ""],
    [286, "AROMI", "Aromi Jose", "Lu/Mi/Ju", "11-13", "Córdoba", 156.0, "P", ""],
    [286, "AROMI", "Ojeda Maria", "Lu/Mi/Ju", "17-19", "Córdoba", 166.0, "P", ""],
    [286, "AROMI", "Acosta Jorge", "Lu/Mi/Ju", "17-19", "Córdoba", 166.7, "P", ""],
    [286, "FERRARO", "Rigoni Camila", "Ma/Vi/Sa", "09-11", "Córdoba", 160.0, "P", "Sábado virtual (11-13)"],
    # Micro p/ Econ (291)
    [291, "APELLA", "Mercatante Juan", "Lu/Mi/Ju", "17-19", "Córdoba", 148.4, "P", ""],
    [291, "APELLA", "Scheimberg Seb.", "Ma/Vi/Sa", "17-19", "Córdoba", 148.5, "P", "Sábado virtual (09-11)"],
    [291, "APELLA", "Apella Ignacio", "Lu/Mi/Ju", "19-21", "Córdoba", 140.0, "P", ""],
    [291, "PETRECOLLA", "Petrecolla Diego", "Lu/Mi/Ju", "09-11", "Córdoba", 145.0, "P", ""],
    [291, "PETRECOLLA", "Jack Pablo", "Lu/Mi/Ju", "09-11", "Córdoba", 145.0, "V", "Comisión Virtual"],
    [291, "PETRECOLLA", "Fajfar Pablo", "Lu/Mi/Ju", "11-13", "Córdoba", 148.0, "P", ""],
    # Análisis Estadístico (540)
    [540, "BIANCO", "Larra Matias", "Lu/Mi/Ju", "09-11", "Avellaneda", 147.2, "P", ""],
    [540, "BIANCO", "Salaberry Natalia", "Ma/Mi/Vi", "09-11", "Córdoba", 150.0, "P", ""],
    [540, "BIANCO", "Serebrisky Juan", "Ma/Mi/Vi", "09-11", "Paternal", 145.0, "P", ""],
    [540, "BIANCO", "Comisión 99", "Miércoles", "17-19", "Virtual", 147.0, "V", "Virtual 100%"],
    # Hist Econ Arg (541)
    [541, "BELINI", "Belini Claudio", "Ma/Vi", "09-11", "Paternal", 141.0, "P", ""],
    [541, "BELINI", "Dethiou Cecilia", "Ma/Vi", "07-09", "San Isidro", 130.0, "P", ""],
    [541, "ROUGIER", "Caravaca Jimena", "Ma/Vi", "09-11", "Avellaneda", 140.0, "P", ""],
    [541, "ROUGIER", "Kulfas / Salles", "Ma/Vi", "09-11", "Córdoba", 145.0, "P", ""],
    # Matemática Aplicada II (544)
    [544, "BIANCO", "Tarullo Eduardo", "Lu/Mi/Ju", "09-11", "Córdoba", 137.0, "P", ""],
    [544, "GARCIA FRONTI", "Morrone Rita", "Lu/Mi/Ju", "07-09", "Córdoba", 135.0, "P", ""],
    [544, "ZORZOLI", "Fajfar Pablo", "Lu/Mi/Ju", "07-09", "Córdoba", 128.1, "P", ""],
    # Epistemología (545)
    [545, "HABERFELD", "Haberfeld Leandro", "Ma/Vi", "09-11", "Córdoba", 140.0, "P", ""],
    [545, "HABERFELD", "Arana Mariano", "Lu/Ju", "17-19", "Córdoba", 135.0, "P", ""],
    [545, "WEISMAN", "Weisman Diego", "Ma/Vi", "11-13", "Córdoba", 138.0, "P", ""],
    [545, "WEISMAN", "Calderon Manuel", "Lu/Ju", "19-21", "Córdoba", 134.5, "P", ""],
    # Econometría II (546)
    [546, "BRUFMAN", "Brufman / Trajtenberg", "Lu/Mi/Ju", "09-11", "Córdoba", 185.0, "P", ""],
    [546, "GONZALEZ MIRTA", "Gonzalez Mirta", "Lu/Mi/Ju", "09-11", "Córdoba", 175.0, "P", ""],
    [546, "MONTES ROJAS", "Corfield Kevin", "Lu/Mi/Ju", "11-13", "Córdoba", 170.0, "P", ""],
    # Estructura (547)
    [547, "MAURIZIO", "Maurizio / Kulfas", "Lu/Ju", "09-11", "Córdoba", 153.5, "P", "Jueves Virtual"],
    # Dinero y Bancos (548)
    [548, "KATZ", "Katz Sebastian", "Ma/Vi", "09-11", "Córdoba", 177.4, "P", ""],
    [548, "LORENZO", "Lorenzo Guido", "Ma/Vi", "17-19", "Córdoba", 188.9, "P", ""],
    # Desarrollo Económico (559)
    [559, "LOPEZ ANDRES", "Ronconi Lucas", "Lu/Ju", "09-11", "Córdoba", 175.7, "P", ""],
    [559, "LOPEZ ANDRES", "Lopez Andres", "Lu/Ju", "19-21", "Córdoba", 168.0, "P", ""],
    # Internacional (558)
    [558, "HALLAK", "Hallak Juan Carlos", "Lu/Ju", "11-13", "Córdoba", 185.0, "P", ""],
    [558, "ALBORNOZ", "Albornoz Crespo", "Lu/Ju", "17-19", "Córdoba", 193.4, "P", ""],
    # Finanzas Públicas (556)
    [556, "CURCIO", "Curcio Javier", "Ma/Vi", "17-19", "Córdoba", 175.7, "P", ""],
    # Optativas
    [520, "MASTELLI", "Mastelli Franco", "Lu/Ju", "19-21", "Córdoba", 221.9, "P", ""],
    [763, "FAJFAR", "Fajfar Pablo", "Ma/Vi", "09-11", "Virtual", 170.5, "V", "Virtual"],
    [563, "ARZA", "Arza Valeria", "Lunes", "09-11", "Virtual", 86.7, "V", "Virtual"]
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v_final_full_all")
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
    with st.expander("2. Ciclo Profesional", expanded=cbc_ok):
        for cod, info in PLAN_ECON["Ciclo Profesional"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"s_{cod}", disabled=bloq): aprobadas.append(cod)
            if bloq: st.caption(f"🔒 Falta: {faltan if cbc_ok else 'CBC'}")
    with st.expander("3. Optativas"):
        for cod, info in PLAN_ECON["Optativas"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"o_{cod}", disabled=bloq): aprobadas.append(cod)

    if st.button("💾 GUARDAR"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_v_final_full_all", json.dumps(data))
        st.success("¡Datos guardados!")

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
        oferta_f = [o for o in OFERTA_TOTAL if o[0] in elegidas and (o[5] in u_sedes or o[5] == "Virtual") and o[4] in u_bloques]
        
        def find_valid_combos(target_subjects):
            grupos = []
            for mid in target_subjects:
                match = [o for o in oferta_f if o[0] == mid]
                if match: grupos.append(match)
            if len(grupos) < len(target_subjects): return []
            combos = list(product(*grupos))
            validos = []
            for combo in combos:
                occupied = set()
                clash = False
                for c in combo:
                    days = c[3].split("/")
                    for d in days:
                        slot = (d.strip(), c[4])
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
            validos.sort(key=lambda x: sum(10 if u_rank > m[6] else 0 for m in x), reverse=True)
            for i, combo in enumerate(validos[:2]):
                st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1}</div>", unsafe_allow_html=True)
                cols = st.columns(len(combo))
                for idx, c in enumerate(combo):
                    badge = "badge-v" if c[7] == "V" else "badge-p"
                    prob = "ALTA" if u_rank > c[6] else "MEDIA" if u_rank > c[6]-15 else "BAJA"
                    color = "#059669" if prob == "ALTA" else "#D97706" if prob == "MEDIA" else "#DC2626"
                    with cols[idx]:
                        st.markdown(f"""
                            <div class="materia-card">
                                <span class="{badge}">{('Virtual' if c[7]=='V' else 'Presencial')}</span><br><br>
                                <div style="font-size:0.8em; color:#64748B; font-weight:700;">CÁTEDRA: {c[1]}</div>
                                <div style="font-weight:600; font-size:1.1em; margin-bottom:5px;">{total_mats_names[c[0]]}</div>
                                <div style="font-size:0.9em; color:#475569;">Prof: {c[2]}</div>
                                <div style="margin-top:10px; font-size:0.85em;">📅 {c[3]} | ⏰ {c[2]} hs</div>
                                <div style="font-size:0.85em;">📍 {c[5]}</div>
                                {f'<div class="virt-day">💻 Día Virtual: {c[8]}</div>' if c[8] else ''}
                                <hr style="border:0.5px solid #eee">
                                <div style="color:{color}; font-weight:700; font-size:0.8em; text-align:center;">PROB: {prob}</div>
                            </div>
                        """, unsafe_allow_html=True)
        else: st.error("No hay oferta cargada para estas materias.")
    else: st.info("Seleccioná materias en la pestaña anterior.")
