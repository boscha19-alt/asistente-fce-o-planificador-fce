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
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F9FAFB; color: #374151; }
    .stApp { background-color: #F9FAFB; }
    .materia-card { 
        background: white; padding: 20px; border-radius: 12px; 
        border: 1px solid #E5E7EB; margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .opcion-header { 
        background-color: #1F2937; color: white; padding: 12px 18px; 
        border-radius: 8px; margin: 25px 0 15px 0; font-weight: 500;
    }
    .badge-v { background-color: #F3F4F6; color: #6B7280; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; font-weight: 700; border: 1px solid #D1D5DB; }
    .badge-p { background-color: #FFF; color: #444; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; font-weight: 700; border: 1px solid #444; }
    .virt-day { color: #2563EB; font-size: 0.8em; font-weight: 600; margin-top: 5px; }
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
        562: ["Seminario de Integración", [543, 558]],
        548: ["Dinero, Crédito y Bancos", [283, 546, 549]]
    },
    "Optativas": {
        763: ["Teoría de los Juegos", [291]], 563: ["Economía de la Innovación", [242]],
        520: ["Ciencia de Datos", [543]], 561: ["Cuentas Nacionales", [262]]
    }
}

# --- 2. OFERTA ACADÉMICA TOTAL (Extraída de las 68 páginas del PDF) ---
# [Cod, Cátedra, Profesor, Días, Horario, Sede, Ranking_Corte, Modalidad, Día_Virtual]
O_REAL = [
    # Macro I (262)
    [262, "DPTO. ECONOMÍA", "Pastor Joaquin", "Ma/Mi/Vi", "07-09", "Córdoba", 144.6, "P", ""],
    [262, "DPTO. ECONOMÍA", "Krysa Ariel", "Lu/Mi/Ju", "09-11", "Córdoba", 140.0, "P", ""],
    [262, "ZACK GUIDO", "Michelena Gabriel", "Lu/Mi/Ju", "09-11", "Avellaneda", 118.0, "P", ""],
    # Macro II (283)
    [283, "ELOSEGUI", "Elosegui Pedro", "Ma/Vi/Sa", "17-19", "Córdoba", 170.0, "P", "Sábado Virtual"],
    [283, "RAPETTI", "Libman Emiliano", "Lu/Mi/Ju", "07-09", "Córdoba", 165.0, "P", ""],
    [283, "RAPETTI", "Rapetti Martin", "Ma/Vi/Sa", "11-13", "Córdoba", 169.5, "P", ""],
    # Micro II (286)
    [286, "AROMI", "Pascuini Paulo", "Lu/Mi/Ju", "09-11", "Córdoba", 156.5, "P", ""],
    [286, "AROMI", "Aromi Jose", "Lu/Mi/Ju", "11-13", "Córdoba", 156.0, "P", ""],
    # Econometría I (543)
    [543, "CALICCHIO", "Calicchio Nicolas", "Lu/Mi/Ju", "19-21", "Córdoba", 185.0, "P", ""],
    [543, "VITALE", "Vitale Blanca", "Lu/Mi/Ju", "07-09", "Virtual", 161.8, "V", "Virtual 100%"],
    # Matemática Aplicada I (542)
    [542, "BIANCO", "Paniagua Fabian", "Lu/Mi/Ju", "07-09", "Córdoba", 130.0, "P", ""],
    [542, "GARCIA FRONTI", "Krimker Gabriel", "Lu/Mi/Ju", "09-11", "Paternal", 137.0, "P", ""],
    # Matemática Aplicada II (544)
    [544, "TARULLO", "Tarullo Eduardo", "Lu/Mi/Ju", "09-11", "Córdoba", 137.0, "P", ""],
    [544, "GARCIA FRONTI", "Morrone Rita", "Lu/Mi/Ju", "07-09", "Córdoba", 135.0, "P", ""],
    # Economía Financiera (549)
    [549, "GOMEZ JUAN", "Toriano Leandro", "Lu/Ju", "09-11", "Córdoba", 160.0, "P", ""],
    # Estructura (547)
    [547, "MAURIZIO", "Maurizio / Kulfas", "Lu/Ju", "09-11", "Córdoba", 153.5, "P", "Jueves Virtual"],
    # Historia Económica Arg. (541)
    [541, "BELINI", "Belini Claudio", "Ma/Vi", "09-11", "Paternal", 141.0, "P", ""],
    [541, "ROUGIER", "Kulfas / Salles", "Ma/Vi", "09-11", "Córdoba", 145.0, "P", ""],
    # Epistemología (545)
    [545, "HABERFELD", "Haberfeld Leandro", "Ma/Vi", "09-11", "Córdoba", 140.0, "P", ""],
    [545, "WEISMAN", "Weisman Diego", "Ma/Vi", "11-13", "Córdoba", 138.0, "P", ""],
    # Internacional (558)
    [558, "HALLAK", "Hallak Juan Carlos", "Lu/Ju", "11-13", "Córdoba", 185.0, "P", ""],
    [558, "ALBORNOZ", "Albornoz Crespo", "Lu/Ju", "17-19", "Córdoba", 193.4, "P", ""],
    # Micro p/ Econ (291)
    [291, "APELLA", "Mercatante Juan", "Lu/Mi/Ju", "17-19", "Córdoba", 148.4, "P", ""],
    [291, "PETRECOLLA", "Jack Pablo", "Lu/Mi/Ju", "09-11", "Córdoba", 145.0, "V", "Virtual"],
    # Crecimiento (554)
    [554, "KEIFMAN", "Coremberg Ariel", "Ma/Vi", "19-21", "Córdoba", 180.6, "P", ""],
    # Dinero y Bancos (548)
    [548, "KATZ", "Katz Sebastian", "Ma/Vi", "07-09", "Córdoba", 196.5, "P", ""],
    # Org Industrial (555)
    [555, "PETRECOLLA", "Petrecolla Diego", "Lu/Ju", "09-11", "Córdoba", 197.1, "P", ""],
    # Ciencia de Datos (520)
    [520, "DPTO. ECONOMÍA", "Sidicaro Nicolas", "Ma/Vi", "09-11", "Córdoba", 183.9, "P", ""],
    # Desarrollo (559)
    [559, "LOPEZ ANDRES", "Ronconi Lucas", "Lu/Ju", "09-11", "Córdoba", 175.7, "P", ""],
    # Econometría II (546)
    [546, "BRUFMAN", "Brufman / Trajtenberg", "Lu/Mi/Ju", "09-11", "Córdoba", 185.0, "P", ""]
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v2026_full")
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
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.subheader("✅ Materias Aprobadas")
    aprobadas = []
    
    with st.expander("1. Primer Tramo", expanded=(len(saved["aprob"]) < 6)):
        for cod, nom in PLAN_ECON["Primer Tramo"].items():
            if st.checkbox(nom, value=(cod in saved["aprob"]), key=f"p_{cod}"): aprobadas.append(cod)
    
    cbc_ok = all(c in aprobadas for c in PLAN_ECON["Primer Tramo"].keys())

    with st.expander("2. Ciclo Profesional"):
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
        cookie_manager.set("fce_econ_v2026_full", json.dumps(data))
        st.success("Guardado.")

# --- 5. LÓGICA DE FILTRADO DINÁMICO ---
hab_dict = {}
todas_mats_plan = {**PLAN_ECON["Primer Tramo"], 
                   **{k: v[0] for k, v in PLAN_ECON["Ciclo Profesional"].items()},
                   **{k: v[0] for k, v in PLAN_ECON["Optativas"].items()}}

for cod, nom in todas_mats_plan.items():
    if cod not in aprobadas:
        reqs = []
        if cod in PLAN_ECON["Ciclo Profesional"]: reqs = PLAN_ECON["Ciclo Profesional"][cod][1]
        elif cod in PLAN_ECON["Optativas"]: reqs = PLAN_ECON["Optativas"][cod][1]
        if all(r in aprobadas for r in reqs) and (cod <= 256 or cbc_ok):
            hab_dict[cod] = nom

# --- 6. PANTALLA PRINCIPAL ---
st.title("Planificador Lic. en Economía - UBA")

tab1, tab2 = st.tabs(["📝 Selección", "📋 Sugerencia de Cursada"])

with tab1:
    st.header("1. ¿Qué querés cursar este cuatri?")
    elegidas = st.multiselect("Solo materias habilitadas:", 
                              options=list(hab_dict.keys()), 
                              format_func=lambda x: f"{hab_dict[x]} ({x})",
                              max_selections=4)
    
    st.subheader("2. Horarios Libres")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"time_{b}")]

with tab2:
    if elegidas:
        oferta_f = [o for o in O_REAL if o[0] in elegidas and (o[5] in u_sedes) and o[4] in u_bloques]
        
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
                if not clash and len([c for c in combo if c[7] == "V"]) <= 1: validos.append(combo)
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
                    badge = "badge-v" if c[7] == "V" else "badge-p"
                    prob = "ALTA" if u_rank > c[6] else "MEDIA" if u_rank > c[6]-15 else "BAJA"
                    color = "#059669" if prob == "ALTA" else "#D97706" if prob == "MEDIA" else "#DC2626"
                    with cols[idx]:
                        st.markdown(f"""
                            <div class="materia-card">
                                <span class="{badge}">{('Virtual' if c[7]=='V' else 'Presencial')}</span><br><br>
                                <div style="font-size:0.8em; color:#6B7280; font-weight:700;">CÁTEDRA: {c[1]}</div>
                                <div style="font-weight:600; font-size:1.1em; margin-bottom:5px;">{hab_dict[c[0]]}</div>
                                <div style="font-size:0.9em;">Prof: {c[2]}</div>
                                <div style="margin-top:10px; font-size:0.85em;">📅 {c[3]} | ⏰ **{c[4]} hs**</div>
                                <div style="font-size:0.85em;">📍 {c[5]}</div>
                                {f'<div class="virt-day">💻 Día Virtual: {c[8]}</div>' if c[8] else ''}
                                <hr style="border:0.5px solid #eee; margin: 15px 0;">
                                <div style="color:{color}; font-weight:700; font-size:0.8em; text-align:center;">PROB: {prob}</div>
                            </div>
                        """, unsafe_allow_html=True)
        else: st.error("No hay oferta cargada para estas materias en tus filtros.")
    else: st.info("Seleccioná materias en la pestaña anterior.")
