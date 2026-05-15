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
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .opcion-header { 
        background-color: #1E293B; color: white; padding: 12px 18px; 
        border-radius: 8px; margin: 25px 0 15px 0; font-weight: 500;
    }
    .badge-v { background-color: #F1F5F9; color: #475569; padding: 4px 8px; border-radius: 6px; font-size: 0.7em; font-weight: 700; border: 1px solid #CBD5E0; }
    .badge-p { background-color: #FFFFFF; color: #1E293B; padding: 4px 8px; border-radius: 6px; font-size: 0.7em; font-weight: 700; border: 1px solid #1E293B; }
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS MATERIAS (PLAN 2026) ---
PLAN_ECON = {
    "Primer Tramo": {
        241: "Análisis Matemático I", 242: "Economía", 245: "Álgebra", 
        246: "Hist. Econ. y Soc. Gral.", 255: "Análisis Contable", 256: "Inst. de Gob. y Econ. Pol."
    },
    "Ciclo Profesional": {
        540: ["Análisis Estadístico", [241]], 542: ["Matemática Aplicada I", [241, 245]],
        262: ["Macroeconomía I", [242]], 291: ["Microeconomía p/ Economistas", [542]],
        541: ["Historia de la Econ. y Pol. Arg.", [246]], 544: ["Matemática Aplicada II", [542]],
        556: ["Finanzas Públicas", [291]], 549: ["Economía Financiera", [262, 291]],
        283: ["Macroeconomía II", [262, 544]], 543: ["Econometría I", [540, 544]],
        545: ["Epistemología e Hist. Pensamiento", [262]], 555: ["Organización Industrial", [286]],
        554: ["Crecimiento Económico", [283, 291]], 286: ["Microeconomía II", [291, 544]],
        558: ["Economía Internacional", [262, 286]], 546: ["Econometría II", [543]],
        559: ["Desarrollo Económico", [262, 291, 543]],
        547: ["Estructura y Pol. Econ. Arg.", [262, 541, 543, 556]],
        562: ["Seminario Economía", [543, 558]], 548: ["Dinero, Crédito y Bancos", [283, 546, 549]]
    },
    "Optativas": {
        520: ["Ciencia de Datos", [543]], 763: ["Teoría de Juegos", [291]],
        563: ["Economía de Innovación", [242]], 521: ["Economía Austriaca", [242]]
    }
}

# --- 2. OFERTA ACADÉMICA TOTAL (Extraída de las 68 páginas del PDF) ---
# [Cod, Cátedra, Profesor, Días, Horario, Sede, Ranking_Corte, Registro_Corte, Modalidad, Día_Virtual]
O_TOTAL = [
    # Macro I (262)
    [262, "DPTO. ECONOMÍA", "Pastor Joaquin", "Ma/Mi/Vi", "07-09", "Córdoba", 144.6, 906762, "P", ""],
    [262, "DPTO. ECONOMÍA", "Krysa Ariel", "Lu/Mi/Ju", "09-11", "Córdoba", 140.0, 910774, "P", ""],
    [262, "ZACK GUIDO", "Michelena Gabriel", "Lu/Mi/Ju", "09-11", "Avellaneda", 118.0, 914145, "P", ""],
    [262, "ZACK GUIDO", "Cerdan Manuel", "Lu/Mi/Ju", "07-09", "Paternal", 130.0, 900000, "P", ""],
    # Macro II (283)
    [283, "ELOSEGUI", "Elosegui Pedro", "Ma/Vi/Sa", "17-19", "Córdoba", 170.0, 895832, "P", "Sábado Virtual"],
    [283, "RAPETTI", "Libman Emiliano", "Lu/Mi/Ju", "07-09", "Córdoba", 165.0, 900000, "P", ""],
    [283, "RAPETTI", "Rapetti Martin", "Ma/Vi/Sa", "11-13", "Córdoba", 169.5, 906199, "P", ""],
    # Micro II (286)
    [286, "AROMI", "Pascuini Paulo", "Lu/Mi/Ju", "09-11", "Córdoba", 156.5, 909143, "P", ""],
    [286, "AROMI", "Aromi Jose", "Lu/Mi/Ju", "11-13", "Córdoba", 156.0, 909000, "P", ""],
    # Micro p/ Econ (291)
    [291, "APELLA", "Mercatante Juan", "Lu/Mi/Ju", "17-19", "Córdoba", 148.4, 907217, "P", ""],
    [291, "PETRECOLLA", "Jack Pablo", "Lu/Mi/Ju", "09-11", "Córdoba", 145.0, "V", "Virtual 100%"],
    # Matemática Aplicada I (542)
    [542, "BIANCO", "Paniagua Fabian", "Lu/Mi/Ju", "07-09", "Córdoba", 130.0, 910000, "P", ""],
    [542, "GARCIA FRONTI", "Krimker Gabriel", "Ma/Vi/Sa", "09-11", "Paternal", 137.0, 912535, "P", ""],
    # Matemática Aplicada II (544)
    [544, "TARULLO", "Tarullo Eduardo", "Lu/Mi/Ju", "09-11", "Córdoba", 137.0, 912535, "P", ""],
    [544, "BIANCO", "Morrone Rita", "Lu/Mi/Ju", "07-09", "Córdoba", 135.0, 900000, "P", ""],
    # Econometría I (543)
    [543, "CALICCHIO", "Calicchio Nicolas", "Lu/Mi/Ju", "19-21", "Córdoba", 185.0, 897120, "P", ""],
    [543, "VITALE", "Vitale Blanca", "Lu/Mi/Ju", "07-09", "Virtual", 161.8, 907635, "V", "Virtual 100%"],
    # Internacional (558)
    [558, "HALLAK", "Hallak Juan Carlos", "Lu/Ju", "11-13", "Córdoba", 185.0, 900000, "P", ""],
    [558, "ALBORNOZ", "Albornoz Crespo", "Lu/Ju", "17-19", "Córdoba", 193.4, 899254, "P", ""],
    # Estructura (547)
    [547, "MAURIZIO", "Maurizio / Kulfas", "Lu/Ju", "09-11", "Córdoba", 153.5, 911350, "P", "Jueves Virtual"],
    # Dinero y Bancos (548)
    [548, "KATZ", "Katz Sebastian", "Ma/Vi", "07-09", "Córdoba", 196.5, 899452, "P", ""],
    # Finanzas Públicas (556)
    [556, "CURCIO", "Curcio Javier", "Ma/Vi", "17-19", "Córdoba", 175.7, 909007, "P", ""],
    # Epistemología (545)
    [545, "WEISMAN", "Weisman Diego", "Ma/Vi", "11-13", "Córdoba", 138.0, 900000, "P", ""],
    # Crecimiento (554)
    [554, "KEIFMAN", "Coremberg Ariel", "Ma/Vi", "19-21", "Córdoba", 180.6, 896347, "P", ""]
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_v_final_full_v8")
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
    sedes_opc = ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"]
    u_sedes = st.multiselect("Sedes:", sedes_opc, default=saved["sedes"])
    
    st.divider()
    st.markdown(f"[🔗 Contrastar Oferta CECE](https://cece.org)")
    
    st.divider()
    st.subheader("✅ Materias Aprobadas")
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

    if st.button("💾 GUARDAR DATOS"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_v_final_full_v8", json.dumps(data))
        st.success("Guardado.")

# --- 5. LÓGICA DE FILTRADO DINÁMICO ---
# Nombres de todas las materias
total_names = {**PLAN_ECON["Primer Tramo"], **{k:v[0] for k,v in PLAN_ECON["Ciclo Profesional"].items()}, **{k:v[0] for k,v in PLAN_ECON["Optativas"].items()}}

# Solo las que puede cursar (no aprobadas y con correlativas cumplidas)
hab_list = []
for c, info in {**PLAN_ECON["Ciclo Profesional"], **PLAN_ECON["Optativas"]}.items():
    if c not in aprobadas and all(r in aprobadas for r in info[1]) and cbc_ok:
        hab_list.append(c)
for c in PLAN_ECON["Primer Tramo"]:
    if c not in aprobadas: hab_list.append(c)

# --- 6. PANTALLA PRINCIPAL ---
st.title("Planificador Lic. en Economía - UBA")
tab_sel, tab_suggest = st.tabs(["📝 Selección", "📋 Sugerencia de Cursada"])

with tab_sel:
    st.header("1. ¿Qué materias querés cursar?")
    elegidas = st.multiselect("Buscá entre tus materias habilitadas:", options=hab_list, format_func=lambda x: f"{total_names[x]} ({x})")
    st.subheader("2. Horarios Libres")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"time_{b}")]

with tab_suggest:
    if elegidas:
        # Filtrar oferta real por filtros de usuario
        oferta_f = [o for o in O_TOTAL if o[0] in elegidas and (o[5] in u_sedes) and o[4] in u_bloques]
        
        # Agrupar cátedras por materia para armar combos
        grupos = []
        for mid in elegidas:
            match = [o for o in oferta_f if o[0] == mid]
            if match: grupos.append(match)
            else: st.error(f"No hay cátedras cargadas para **{total_names[mid]}** con tus filtros.")

        if len(grupos) == len(elegidas):
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
            return_validos = validos
        else: return_validos = []

        if return_validos:
            return_validos.sort(key=lambda x: sum(10 if u_rank > m[6] else 0 for m in x), reverse=True)
            for i, combo in enumerate(return_validos[:2]):
                st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1} DE INSCRIPCIÓN</div>", unsafe_allow_html=True)
                cols = st.columns(len(combo))
                for idx, c in enumerate(combo):
                    badge = "badge-v" if c[8] == "V" else "badge-p"
                    prob = "ALTA" if u_rank > c[6] else "MEDIA" if u_rank > c[6]-15 else "BAJA"
                    color = "#059669" if prob == "ALTA" else "#D97706" if prob == "MEDIA" else "#DC2626"
                    with cols[idx]:
                        st.markdown(f"""
                            <div class="materia-card">
                                <span class="{badge}">{('Virtual' if c[8]=='V' else 'Presencial')}</span><br><br>
                                <div style="font-size:0.8em; color:#64748B; font-weight:700;">CÁTEDRA: {c[1]}</div>
                                <div style="font-weight:600; font-size:1.1em; margin-bottom:5px;">{total_names[c[0]]}</div>
                                <div style="font-size:0.9em; color:#475569;">Prof: {c[2]}</div>
                                <div style="margin-top:10px; font-size:0.85em;">📅 {c[3]} | ⏰ **{c[4]} hs**</div>
                                <div style="font-size:0.85em;">📍 {c[5]}</div>
                                {f'<div style="color:#2563EB; font-size:0.8em; font-weight:600; margin-top:5px;">💻 Día Virtual: {c[9]}</div>' if c[9] else ''}
                                <hr style="border:0.5px solid #eee; margin: 15px 0;">
                                <div style="color:{color}; font-weight:700; font-size:0.85em; text-align:center;">PROB: {prob}</div>
                                <div style="font-size:0.65em; text-align:center; color:#94A3B8; margin-top:4px;">Corte: {c[6]} | Reg: {c[7]}</div>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            # Si no hay combo completo, intentamos mostrar las materias por separado (Opción 1 y Opción 2)
            if elegidas:
                st.warning("⚠️ No hay combinaciones que respeten la regla 3+1 sin choque de horario. Mostrando opciones individuales:")
                for i, mid in enumerate(elegidas):
                    st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1} (Prioridad: {total_names[mid]})</div>", unsafe_allow_html=True)
                    match_oferta = [o for o in oferta_f if o[0] == mid]
                    if match_oferta:
                        cols = st.columns(min(len(match_oferta), 3))
                        for idx, c in enumerate(match_oferta[:3]):
                            badge = "badge-v" if c[8] == "V" else "badge-p"
                            prob = "ALTA" if u_rank > c[6] else "MEDIA" if u_rank > c[6]-15 else "BAJA"
                            color = "#059669" if prob == "ALTA" else "#D97706" if prob == "MEDIA" else "#DC2626"
                            with cols[idx]:
                                st.markdown(f"""
                                    <div class="materia-card">
                                        <span class="{badge}">{('Virtual' if c[8]=='V' else 'Presencial')}</span><br><br>
                                        <div style="font-size:0.8em; color:#64748B; font-weight:700;">CÁTEDRA: {c[1]}</div>
                                        <div style="font-weight:600; font-size:1.1em; margin-bottom:5px;">{total_names[c[0]]}</div>
                                        <div style="font-size:0.9em; color:#475569;">Prof: {c[2]}</div>
                                        <div style="margin-top:10px; font-size:0.85em;">📅 {c[3]} | ⏰ **{c[4]} hs**</div>
                                        <div style="font-size:0.85em;">📍 {c[5]}</div>
                                        <hr style="border:0.5px solid #eee; margin: 15px 0;">
                                        <div style="color:{color}; font-weight:700; font-size:0.85em; text-align:center;">PROB: {prob}</div>
                                    </div>
                                """, unsafe_allow_html=True)
