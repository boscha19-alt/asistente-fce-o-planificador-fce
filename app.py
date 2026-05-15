import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import combinations, product

# --- CONFIGURACIÓN ESTÉTICA ZEN ---
st.set_page_config(page_title="Planificador Economía UBA", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8F9FA; color: #334155; }
    .stApp { background-color: #F8F9FA; }
    .materia-card { 
        background: white; padding: 22px; border-radius: 12px; 
        border: 1px solid #E5E7EB; margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .opcion-header { 
        background-color: #1F2937; color: white; padding: 12px 18px; 
        border-radius: 8px; margin: 25px 0 15px 0; font-weight: 500;
    }
    .badge-v { background-color: #F3F4F6; color: #6B7280; padding: 4px 10px; border-radius: 6px; font-size: 0.7em; font-weight: 700; border: 1px solid #D1D5DB; }
    .badge-p { background-color: #FFF; color: #444; padding: 4px 10px; border-radius: 6px; font-size: 0.7em; font-weight: 700; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS DE MATERIAS (PLAN 2026) ---
PLAN_ECON = {
    "Primer Tramo": {
        241: "Análisis Matemático I", 242: "Economía", 245: "Álgebra", 
        246: "Hist. Econ. y Soc. Gral.", 255: "Análisis Contable", 256: "Inst. de Gob. y Econ. Pol."
    },
    "Ciclo Profesional": {
        540: ["Análisis Estadístico", [241]], 542: ["Matemática Aplicada I", [241, 245]],
        262: ["Macroeconomía I", [242]], 290: ["Microeconomía I", [242]],
        291: ["Micro p/ Economistas", [542]], 541: ["Hist. Econ. Arg.", [246]], 
        544: ["Matemática Aplicada II", [542]], 556: ["Finanzas Públicas", [291]],
        549: ["Economía Financiera", [262, 291]], 283: ["Macroeconomía II", [262, 544]],
        543: ["Econometría I", [540, 544]], 545: ["Epistemología", [262]],
        555: ["Org. Industrial", [286]], 554: ["Crecimiento Económico", [283, 291]],
        286: ["Microeconomía II", [291, 544]], 558: ["Econ. Internacional", [262, 286]],
        546: ["Econometría II", [543]], 559: ["Desarrollo Económico", [262, 291, 543]],
        547: ["Estructura y Pol. Econ.", [262, 541, 543, 556]],
        562: ["Seminario Economía", [543, 558]], 548: ["Dinero, Crédito y Bancos", [283, 546, 549]]
    },
    "Optativas": {
        525: ["Tópicos de Economía Digital", [262]], 520: ["Ciencia de Datos", [543]], 
        763: ["Teoría de Juegos", [291]], 563: ["Economía de Innovación", [242]], 
        521: ["Economía Austriaca", [242]]
    }
}

# --- 2. BASE DE DATOS DE OFERTA COMPLETA (PROCESADA TOTAL) ---
# [Cod, Cátedra, Profesor, Días, Horario, Sede, Ranking, Registro, Modalidad, VirtualDay]
O_TOTAL = [
    # 525 - Tópicos Economía Digital
    [525, "DPTO. ECONOMÍA", "Coll Agustin Julian", "Ma / Vi", "17-19", "Córdoba", 140.0, 900000, "P", ""],
    
    # 262 - Macroeconomía I
    [262, "DPTO. ECONOMÍA", "Pastor Joaquin", "Ma / Mi / Vi", "07-09", "Córdoba", 144.6, 906762, "P", ""],
    [262, "DPTO. ECONOMÍA", "Krysa Ariel", "Lu / Mi / Ju", "09-11", "Córdoba", 140.0, 910774, "P", ""],
    [262, "ZACK GUIDO", "Michelena Gabriel", "Lu / Mi / Ju", "09-11", "Avellaneda", 118.0, 914145, "P", ""],
    
    # 283 - Macroeconomía II
    [283, "ELOSEGUI", "Elosegui Pedro", "Ma / Vi / Sa", "17-19", "Córdoba", 170.0, 895832, "P", "Sábado Virtual"],
    [283, "RAPETTI", "Libman Emiliano", "Lu / Mi / Ju", "07-09", "Córdoba", 165.0, 900000, "P", ""],
    [283, "RAPETTI", "Rapetti Martin", "Ma / Vi / Sa", "11-13", "Córdoba", 169.5, 906199, "P", ""],
    
    # 290 - Microeconomía I
    [290, "JACK PABLO", "Jack Pablo", "Lu / Mi / Ju", "09-11", "Córdoba", 148.6, 909051, "P", ""],
    [290, "FAJFAR PABLO", "Fajfar Pablo", "Lu / Mi / Ju", "09-11", "Córdoba", 134.0, 907217, "P", ""],
    
    # 286 - Microeconomía II
    [286, "AROMI", "Pascuini Paulo", "Lu / Mi / Ju", "09-11", "Córdoba", 156.5, 909143, "P", ""],
    [286, "AROMI", "Aromi Jose Daniel", "Lu / Mi / Ju", "11-13", "Córdoba", 156.0, 909000, "P", ""],
    
    # 291 - Micro p/ Economistas
    [291, "APELLA", "Mercatante Juan", "Lu / Mi / Ju", "17-19", "Córdoba", 148.4, 907217, "P", ""],
    [291, "PETRECOLLA", "Jack Pablo", "Lu / Mi / Ju", "09-11", "Córdoba", 145.0, 909051, "V", "Virtual 100%"],
    
    # 540 - Análisis Estadístico
    [540, "BIANCO", "Larra Matias", "Lu / Mi / Ju", "09-11", "Avellaneda", 147.2, 909450, "P", ""],
    [540, "BIANCO", "Salaberry Natalia", "Ma / Mi / Vi", "09-11", "Córdoba", 150.0, 911693, "P", ""],
    
    # 541 - Historia Económica Arg.
    [541, "BELINI", "Belini Claudio", "Ma / Vi", "09-11", "Paternal", 141.0, 910000, "P", ""],
    [541, "ROUGIER", "Kulfas / Salles", "Ma / Vi", "09-11", "Córdoba", 145.0, 900000, "P", ""],
    
    # 542 - Matemática Aplicada I
    [542, "BIANCO", "Paniagua Fabian", "Lu / Mi / Ju", "07-09", "Córdoba", 130.0, 910000, "P", ""],
    [542, "GARCIA FRONTI", "Krimker Gabriel", "Ma / Vi / Sa", "09-11", "Paternal", 137.0, 912535, "P", ""],
    
    # 544 - Matemática Aplicada II
    [544, "TARULLO", "Tarullo Eduardo", "Lu / Mi / Ju", "09-11", "Córdoba", 137.0, 912535, "P", ""],
    [544, "BIANCO", "Morrone Rita", "Lu / Mi / Ju", "07-09", "Córdoba", 135.0, 900000, "P", ""],
    
    # 543 - Econometría I
    [543, "CALICCHIO", "Calicchio Nicolas", "Lu / Mi / Ju", "19-21", "Córdoba", 185.0, 897120, "P", ""],
    [543, "VITALE", "Vitale Blanca", "Lu / Mi / Ju", "07-09", "Virtual", 161.8, 907635, "V", "Virtual 100%"],
    
    # 546 - Econometría II
    [546, "BRUFMAN", "Trajtenberg L.", "Lu / Mi / Ju", "09-11", "Córdoba", 185.0, 897120, "P", ""],
    
    # 547 - Estructura y Pol. Econ.
    [547, "MAURIZIO", "Maurizio / Kulfas", "Lu / Ju", "09-11", "Córdoba", 153.5, 911350, "P", "Jueves Virtual"],
    
    # 548 - Dinero, Crédito y Bancos
    [548, "KATZ", "Katz Sebastian", "Ma / Vi", "07-09", "Córdoba", 196.5, 899452, "P", ""],
    [548, "LORENZO", "Lorenzo Guido", "Ma / Vi", "17-19", "Córdoba", 188.9, 894998, "P", ""],
    
    # 554 - Crecimiento Económico
    [554, "KEIFMAN", "Coremberg Ariel", "Ma / Vi", "19-21", "Córdoba", 180.6, 896347, "P", ""],
    
    # 555 - Organización Industrial
    [555, "PETRECOLLA", "Petrecolla Diego", "Lu / Ju", "09-11", "Córdoba", 207.4, 899476, "P", ""],
    [555, "MACEIRA", "Maceira Daniel", "Ma / Vi", "09-11", "Córdoba", 173.1, 898636, "P", ""],
    
    # 556 - Finanzas Públicas
    [556, "CURCIO", "Curcio Javier", "Ma / Vi", "17-19", "Córdoba", 175.7, 909007, "P", ""],
    
    # 558 - Economía Internacional
    [558, "HALLAK", "Hallak Juan Carlos", "Lu / Ju", "11-13", "Córdoba", 185.0, 900000, "P", ""],
    [558, "ALBORNOZ", "Albornoz Crespo", "Lu / Ju", "17-19", "Córdoba", 193.4, 899254, "P", ""],
    
    # 559 - Desarrollo Económico
    [559, "LOPEZ ANDRES", "Ronconi Lucas", "Lu / Ju", "09-11", "Córdoba", 175.7, 909000, "P", ""],
    
    # 545 - Epistemología
    [545, "WEISMAN", "Weisman Diego", "Ma / Vi", "11-13", "Córdoba", 138.0, 900000, "P", ""],
    
    # 520 - Ciencia de Datos
    [520, "DPTO. ECONOMÍA", "Sidicaro Nicolas", "Ma / Vi", "09-11", "Córdoba", 183.9, 905528, "P", ""]
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_v_final_economy_v11")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "910000", "rank": 180.0, "aprob": [], "sedes": ["Córdoba", "Virtual", "Paternal"]}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("👤 Mi Perfil")
    u_reg = st.text_input("N° Registro:", value=saved["reg"])
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.markdown(f"[🔗 Contrastar Oferta CECE](https://cece.org)")
    
    st.divider()
    st.subheader("✅ Marcar Aprobadas")
    aprobadas = []
    
    with st.expander("1. Primer Tramo"):
        for cod, nom in PLAN_ECON["Primer Tramo"].items():
            if st.checkbox(nom, value=(cod in saved["aprob"]), key=f"p_{cod}"): aprobadas.append(cod)
    
    cbc_ok = all(c in aprobadas for c in PLAN_ECON["Primer Tramo"].keys())

    with st.expander("2. Ciclo Profesional", expanded=cbc_ok):
        for cod, info in PLAN_ECON["Ciclo Profesional"].items():
            faltan = [str(r) for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"s_{cod}", disabled=bloq): aprobadas.append(cod)
            if bloq: st.caption(f"🔒 Falta: {faltan if cbc_ok else 'CBC'}")

    with st.expander("3. Optativas"):
        for cod, info in PLAN_ECON["Optativas"].items():
            faltan = [str(r) for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"o_{cod}", disabled=bloq): aprobadas.append(cod)

    if st.button("💾 GUARDAR DATOS"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_v_final_economy_v11", json.dumps(data))
        st.success("Guardado.")

# --- 5. LÓGICA DE FILTRADO DINÁMICO ---
total_names = {**PLAN_ECON["Primer Tramo"], **{k:v[0] for k,v in PLAN_ECON["Ciclo Profesional"].items()}, **{k:v[0] for k,v in PLAN_ECON["Optativas"].items()}}
hab_list = [c for c, info in {**PLAN_ECON["Ciclo Profesional"], **PLAN_ECON["Optativas"]}.items() if c not in aprobadas and all(r in aprobadas for r in info[1]) and cbc_ok]
for c in PLAN_ECON["Primer Tramo"]:
    if c not in aprobadas: hab_list.append(c)

# --- 6. PANTALLA PRINCIPAL ---
st.title("Planificador Lic. en Economía - UBA")
tab_sel, tab_suggest = st.tabs(["📝 Selección de Materias", "📋 Sugerencia de Inscripción"])

with tab_sel:
    st.header("1. ¿Qué materias querés cursar?")
    elegidas = st.multiselect("Buscá materias habilitadas:", options=hab_list, format_func=lambda x: f"{total_names[x]} ({x})")
    st.subheader("2. Horarios Libres")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"time_{b}")]

with tab_suggest:
    if elegidas:
        oferta_f = [o for o in O_TOTAL if o[0] in elegidas and (o[5] in u_sedes) and o[4] in u_bloques]
        
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
                    for d in c[3].split("/"):
                        slot = (d.strip(), c[4])
                        if slot in occupied: clash = True; break
                        occupied.add(slot)
                    if clash: break
                if not clash and len([c for c in combo if c[8] == "V"]) <= 1: validos.append(combo)
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
                st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1} DE INSCRIPCIÓN</div>", unsafe_allow_html=True)
                cols = st.columns(len(combo))
                for idx, c in enumerate(combo):
                    badge = "badge-v" if c[8] == "V" else "badge-p"
                    diff = u_rank - c[6]
                    color = "#059669" if diff > 10 else "#D97706" if diff > -10 else "#DC2626"
                    prob = "ALTA" if diff > 10 else "MEDIA" if diff > -10 else "BAJA"
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="materia-card">
                            <span class="{badge}">{('Virtual' if c[8]=='V' else 'Presencial')}</span><br><br>
                            <div style="font-size:0.8em; color:#64748B; font-weight:700;">CÁTEDRA: {c[1]}</div>
                            <div style="font-weight:600; font-size:1.1em; margin-bottom:5px;">{total_names[c[0]]}</div>
                            <div style="font-size:0.9em; color:#475569;">Prof: {c[2]}</div>
                            <div style="margin-top:10px; font-size:0.85em;">📅 {c[3]} | ⏰ **{c[4]} hs**</div>
                            <div style="font-size:0.85em;">📍 {c[5]}</div>
                            <div style="color:#2563EB; font-size:0.8em; font-weight:600; margin-top:5px;">{('💻 ' + c[9]) if c[9] else ''}</div>
                            <hr style="border:0.5px solid #eee; margin: 15px 0;">
                            <div style="color:{color}; font-weight:700; font-size:0.85em; text-align:center;">PROB: {prob}</div>
                            <div style="font-size:0.65em; text-align:center; color:#94A3B8; margin-top:4px;">Corte: {c[6]} | Reg: {c[7]}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else: st.error("No hay oferta cargada para estas materias en tus filtros.")
