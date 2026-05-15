import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import combinations, product

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="Inscripción Economía UBA 2026", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F9FAFB; color: #374151; }
    .stApp { background-color: #F9FAFB; }
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

# --- 1. BASE DE DATOS DE MATERIAS (PLAN 2026 - SEGÚN TUS FOTOS) ---
PLAN_ECON = {
    "Primer Tramo": {
        241: "Análisis Matemático I", 242: "Economía", 245: "Álgebra", 
        246: "Hist. Econ. y Soc. Gral.", 255: "Análisis Contable", 256: "Inst. de Gob. y Econ. Pol."
    },
    "Ciclo Profesional": {
        262: ["Macroeconomía I", [242]], 283: ["Macroeconomía II", [262, 544]],
        286: ["Microeconomía II", [291, 544]], 291: ["Micro p/ Economistas", [542]],
        540: ["Análisis Estadístico", [241]], 541: ["Hist. Econ. y Pol. Arg.", [246]],
        542: ["Matemática Aplicada I", [241, 245]], 543: ["Econometría I", [540, 544]],
        544: ["Matemática Aplicada II", [542]], 545: ["Epistemología", [262]],
        546: ["Econometría II", [543]], 547: ["Estructura y Pol. Econ.", [262, 541, 543, 556]],
        548: ["Dinero, Crédito y Bancos", [283, 546, 549]], 549: ["Economía Financiera", [262, 291]],
        554: ["Crecimiento Económico", [283, 291]], 555: ["Org. Industrial", [286]],
        556: ["Finanzas Públicas", [291]], 558: ["Economía Internacional", [262, 286]],
        559: ["Desarrollo Económico", [262, 291, 543]], 562: ["Seminario Economía", [543, 558]]
    },
    "Optativas": {
        520: ["Ciencia de Datos", [543]], 521: ["Economía Austriaca", [242]],
        523: ["Econ. y Derecho Corp.", [256]], 527: ["Big Data & ML", [543]],
        563: ["Economía de Innovación", [242]], 763: ["Teoría de Juegos", [291]],
        1721: ["Economía del Comportamiento", [291]], 1725: ["Admin. Tributaria", [256]]
    }
}

# --- 2. OFERTA ACADÉMICA CALIFICADA (CONSOLIDADA DE LAS 5 PÁGINAS DEL PDF) ---
# [Cod, Cátedra/Titular, Profesor, Días, Horario, Sede, Ranking_Corte, Registro_Corte, Modalidad (P/V), Día_Virtual]
O_TOTAL = [
    # Macroeconomía I (262)
    [262, "DPTO. ECONOMÍA", "Pastor Joaquin", "Ma/Mi/Vi", "07:00-09:00", "Córdoba", 144.6, 906762, "P", ""],
    [262, "DPTO. ECONOMÍA", "Krysa Ariel", "Lu/Mi/Ju", "09:00-11:00", "Córdoba", 140.0, 910774, "P", ""],
    [262, "DPTO. ECONOMÍA", "Di Lalla Daniela", "Lu/Mi/Ju", "11:00-13:00", "Córdoba", 137.0, 910000, "P", ""],
    [262, "ZACK GUIDO", "Michelena Gabriel", "Lu/Mi/Ju", "09:00-11:00", "Avellaneda", 118.0, 914145, "P", ""],
    [262, "ZACK GUIDO", "Cerdan Manuel", "Lu/Mi/Ju", "07:00-09:00", "Paternal", 130.0, 900000, "P", ""],
    [262, "ZACK GUIDO", "Favata Federico", "Lu/Ju", "11:00-13:00", "San Isidro", 132.7, 913239, "P", "Lunes Presencial 09-13"],

    # Macroeconomía II (283)
    [283, "ELOSEGUI", "Elosegui Pedro Luis", "Ma/Vi/Sa", "17:00-19:00", "Córdoba", 170.0, 895832, "P", "Sábado Virtual"],
    [283, "RAPETTI", "Libman Emiliano", "Lu/Mi/Ju", "07:00-09:00", "Córdoba", 165.0, 900000, "P", ""],
    [283, "RAPETTI", "Rapetti Martin", "Ma/Vi/Sa", "11:00-13:00", "Córdoba", 169.5, 906199, "P", ""],
    [283, "RAPETTI", "Zack Guido", "Lu/Mi/Ju", "17:00-19:00", "Córdoba", 164.3, 903382, "P", ""],

    # Microeconomía II (286)
    [286, "AROMI", "Pascuini Paulo", "Lu/Mi/Ju", "09:00-11:00", "Córdoba", 156.5, 909143, "P", ""],
    [286, "AROMI", "Aromi Jose Daniel", "Lu/Mi/Ju", "11:00-13:00", "Córdoba", 156.0, 909000, "P", ""],
    [286, "AROMI", "Ojeda Maria Laura", "Lu/Mi/Ju", "17:00-19:00", "Córdoba", 166.0, 901554, "P", ""],
    [286, "FERRARO", "Rigoni Camila", "Ma/Vi/Sa", "09:00-11:00", "Córdoba", 160.0, "P", "Sábado Virtual"],

    # Micro p/ Economistas (291)
    [291, "APELLA", "Mercatante Juan", "Lu/Mi/Ju", "17:00-19:00", "Córdoba", 148.4, 907217, "P", ""],
    [291, "APELLA", "Scheimberg Seb.", "Ma/Vi/Sa", "17:00-19:00", "Córdoba", 148.5, 907000, "P", "Sábado Virtual"],
    [291, "PETRECOLLA", "Petrecolla Diego", "Lu/Mi/Ju", "09:00-11:00", "Córdoba", 145.0, 910000, "P", ""],
    [291, "PETRECOLLA", "Jack Pablo", "Lu/Mi/Ju", "09:00-11:00", "Córdoba", 145.0, 909051, "V", "Virtual 100%"],

    # Análisis Estadístico (540)
    [540, "BIANCO", "Larra Matias", "Lu/Mi/Ju", "09:00-11:00", "Avellaneda", 147.2, 909450, "P", ""],
    [540, "BIANCO", "Salaberry Natalia", "Ma/Mi/Vi", "09:00-11:00", "Córdoba", 150.0, 911693, "P", ""],
    [540, "BIANCO", "Comisión 99", "Miércoles", "17:00-19:00", "Virtual", 147.0, 900000, "V", "Virtual"],

    # Historia Económica Arg (541)
    [541, "BELINI", "Belini Claudio", "Ma/Vi", "09:00-11:00", "Paternal", 141.0, 910000, "P", ""],
    [541, "ROUGIER", "Kulfas / Salles", "Ma/Vi", "09:00-11:00", "Córdoba", 145.0, 900000, "P", ""],

    # Matemática Aplicada I (542)
    [542, "BIANCO", "Paniagua Fabian", "Lu/Mi/Ju", "07:00-09:00", "Córdoba", 130.0, 910000, "P", ""],
    [542, "GARCIA FRONTI", "Krimker Gabriel", "Ma/Vi/Sa", "09:00-11:00", "Paternal", 137.0, 912535, "P", ""],

    # Matemática Aplicada II (544)
    [544, "BIANCO", "Tarullo Eduardo", "Lu/Mi/Ju", "09:00-11:00", "Córdoba", 137.0, 912535, "P", ""],
    [544, "ZORZOLI", "Fajfar Pablo", "Lu/Mi/Ju", "07:00-09:00", "Córdoba", 128.1, 913540, "P", ""],

    # Econometría I (543)
    [543, "GONZALEZ MIRTA", "Calicchio Nicolas", "Lu/Mi/Ju", "07:00-09:00", "Córdoba", 167.0, 902303, "P", ""],
    [543, "VITALE BLANCA", "Vitale Blanca", "Lu/Mi/Ju", "07:00-09:00", "Virtual", 161.8, 907635, "V", "Virtual"],

    # Epistemología (545)
    [545, "HABERFELD", "Haberfeld Leandro", "Ma/Vi", "09:00-11:00", "Córdoba", 140.0, 900000, "P", ""],
    [545, "WEISMAN", "Weisman Diego", "Ma/Vi", "11:00-13:00", "Córdoba", 138.0, 900000, "P", ""],

    # Econometría II (546)
    [546, "BRUFMAN", "Brufman / Trajtenberg", "Lu/Mi/Ju", "09:00-11:00", "Córdoba", 185.0, 897120, "P", ""],

    # Estructura (547)
    [547, "MAURIZIO", "Maurizio / Kulfas", "Lu/Ju", "09:00-11:00", "Córdoba", 153.5, 911350, "P", "Jueves Virtual"],

    # Dinero y Bancos (548)
    [548, "KATZ", "Katz Sebastian", "Ma/Vi", "07:00-09:00", "Córdoba", 196.5, 899452, "P", ""],
    [548, "LORENZO", "Lorenzo Guido", "Ma/Vi", "17:00-19:00", "Córdoba", 188.9, 894998, "P", ""],

    # Crecimiento (554)
    [554, "KEIFMAN", "Coremberg Ariel", "Ma/Vi", "19:00-21:00", "Córdoba", 180.6, 896347, "P", ""],

    # Finanzas Públicas (556)
    [556, "CURCIO", "Curcio Javier", "Ma/Vi", "17:00-19:00", "Córdoba", 175.7, 909007, "P", ""],

    # Economía Internacional (558)
    [558, "HALLAK", "Hallak Juan Carlos", "Lu/Ju", "11:00-13:00", "Córdoba", 185.0, 900000, "P", ""],
    [558, "ALBORNOZ", "Albornoz Crespo", "Lu/Ju", "17:00-19:00", "Córdoba", 193.4, 899254, "P", ""],

    # Desarrollo Económico (559)
    [559, "LOPEZ ANDRES", "Ronconi Lucas", "Lu/Ju", "09:00-11:00", "Córdoba", 175.7, 909000, "P", ""],
    
    # Optativas frecuentes
    [520, "DPTO. ECONOMÍA", "Sidicaro Nicolas", "Ma/Vi", "09:00-11:00", "Córdoba", 183.9, 905528, "P", ""]
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v_final_full_2026")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "910000", "rank": 180.0, "aprob": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("👤 Mi Perfil")
    u_reg = st.text_input("N° Registro:", value=saved["reg"])
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    sedes_opc = ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"]
    u_sedes = st.multiselect("Sedes Disponibles:", sedes_opc, default=saved["sedes"])
    
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
    with st.expander("3. Optativas"):
        for cod, info in PLAN_ECON["Optativas"].items():
            faltan = [str(r) for r in info[1] if r not in aprobadas]
            bloq = (len(faltan) > 0 or not cbc_ok) and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"o_{cod}", disabled=bloq): aprobadas.append(cod)

    if st.button("💾 GUARDAR DATOS"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_v_final_full_2026", json.dumps(data))
        st.success("Guardado.")

# --- 5. LÓGICA DE FILTRADO DROPDOWN DINÁMICO ---
total_names = {**PLAN_ECON["Primer Tramo"], **{k:v[0] for k,v in PLAN_ECON["Ciclo Profesional"].items()}, **{k:v[0] for k,v in PLAN_ECON["Optativas"].items()}}
hab_list = [c for c, info in {**PLAN_ECON["Ciclo Profesional"], **PLAN_ECON["Optativas"]}.items() if c not in aprobadas and all(r in aprobadas for r in info[1]) and cbc_ok]
for c in PLAN_ECON["Primer Tramo"]:
    if c not in aprobadas: hab_list.append(c)

# --- 6. PANTALLA PRINCIPAL ---
st.title("Planificador Lic. en Economía - UBA")
tab_sel, tab_suggest = st.tabs(["📝 Selección de Materias", "📋 Sugerencia de Inscripción"])

with tab_sel:
    st.header("1. ¿Qué materias querés cursar?")
    elegidas = st.multiselect("Buscá entre tus materias habilitadas:", options=hab_list, format_func=lambda x: f"{total_names[x]} ({x})")
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
                    if u_rank > c[6] + 10: prob, color = "ALTA", "#059669"
                    elif u_rank > c[6] - 10:
                        if int(u_reg) <= c[7]: prob, color = "MEDIA (Reg)", "#D97706"
                        else: prob, color = "BAJA (Rank)", "#DC2626"
                    else: prob, color = "BAJA", "#DC2626"
                    
                    with cols[idx]:
                        st.markdown(f"""
                            <div class="materia-card">
                                <span class="{badge}">{('Virtual' if c[8]=='V' else 'Presencial')}</span><br><br>
                                <div style="font-size:0.8em; color:#64748B; font-weight:700;">CÁTEDRA: {c[1]}</div>
                                <div style="font-weight:600; font-size:1.1em; margin-bottom:5px;">{total_names[c[0]]}</div>
                                <div style="font-size:0.9em; color:#475569;">Prof: {c[2]}</div>
                                <div style="margin-top:10px; font-size:0.85em;">📅 {c[3]} | ⏰ **{c[4]} hs**</div>
                                <div style="font-size:0.85em;">📍 {c[5]}</div>
                                {f'<div style="color:#2563EB; font-size:0.8em; font-weight:600; margin-top:5px;">💻 {c[9]}</div>' if c[9] else ''}
                                <hr style="border:0.5px solid #eee; margin: 15px 0;">
                                <div style="color:{color}; font-weight:700; font-size:0.85em; text-align:center;">PROB: {prob}</div>
                                <div style="font-size:0.65em; text-align:center; color:#94A3B8; margin-top:4px;">Corte: {c[6]} | Reg: {c[7]}</div>
                            </div>
                        """, unsafe_allow_html=True)
        else: st.error("No hay oferta cargada para estas materias en tus filtros.")
    else: st.info("Seleccioná materias en la pestaña anterior para generar las sugerencias.")
