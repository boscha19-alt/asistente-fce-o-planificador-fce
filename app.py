import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="Planificador Economía UBA", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F5F5F4; color: #444; }
    .stApp { background-color: #F5F5F4; }
    .materia-card { 
        background: white; padding: 20px; border-radius: 12px; 
        border: 1px solid #E7E5E4; margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .opcion-header { 
        background-color: #292524; color: white; padding: 10px 20px; 
        border-radius: 8px; margin-top: 20px; font-weight: 500;
    }
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.7em; font-weight: 700; text-transform: uppercase; }
    .badge-p { background-color: #E7E5E4; color: #444; } /* Presencial */
    .badge-v { background-color: #D6D3D1; color: #1C1917; } /* Virtual */
    </style>
    """, unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS COMPLETA ECONOMÍA ---
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
    "Optativas": {
        763: ["Teoría de los Juegos", [291]], 563: ["Economía de la Innovación", [242]],
        520: ["Ciencia de Datos", [543]], 523: ["Econ. y Derecho Corp.", [251]],
        457: ["Teoría de la Decisión", [540]], 561: ["Cuentas Nacionales", [262]]
    }
}

# --- 2. OFERTA REAL (PROCESADA DE TUS FOTOS) ---
# [Código, Docente, Horario, Sede, Ranking Corte, Registro Corte, Modalidad]
OFERTA_REAL = [
    [262, "WAINER", "07-09", "Córdoba", 144.6, 906762, "P"],
    [262, "AGOSTINELLI", "11-13", "Córdoba", 137.2, 910774, "P"],
    [291, "FAJFAR", "17-19", "Córdoba", 148.4, 907217, "P"],
    [291, "JACK PABLO", "09-11", "Córdoba", 145.0, 909051, "V"],
    [540, "BIANCO", "07-09", "Paternal", 147.2, 909450, "P"],
    [540, "ZAIA", "19-21", "Córdoba", 150.0, 911693, "P"],
    [544, "GARCIA FRONTI", "09-11", "Córdoba", 137.0, 912535, "P"],
    [544, "FAJFAR", "17-19", "Virtual", 128.1, 913540, "V"],
    [286, "AROMI", "09-11", "Córdoba", 156.5, 909143, "P"],
    [286, "OJEDA", "19-21", "Paternal", 166.0, 901554, "P"],
    [543, "CALICCHIO", "19-21", "Córdoba", 185.0, 897120, "P"],
    [543, "VITALE", "07-09", "Córdoba", 161.8, 907635, "V"],
    [554, "COREMBERG", "11-13", "Córdoba", 180.6, 896347, "P"],
    [548, "KATZ", "07-09", "Córdoba", 177.4, 904971, "P"],
    [556, "SIRLIN", "17-19", "Córdoba", 175.7, 909007, "P"],
    [541, "HIST. ECON. ARG.", "11-13", "Córdoba", 141.0, 910000, "P"]
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved = cookies.get("fce_econ_vfinal")
if saved:
    try: saved = json.loads(saved)
    except: saved = None
if not saved:
    saved = {"reg": "900000", "rank": 500.0, "aprob": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("👤 Mi Perfil")
    u_reg = st.text_input("N° Registro:", value=saved["reg"])
    u_rank = st.number_input("Mi Ranking:", value=float(saved["rank"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Virtual"], default=saved["sedes"])
    
    st.divider()
    st.subheader("✅ Materias Aprobadas")
    aprobadas = []
    
    # TR0: Primer Tramo
    with st.expander("Primer Tramo (CBC/FCE)", expanded=True):
        for cod, nom in PLAN_ECON["Primer Tramo"].items():
            if st.checkbox(nom, value=(cod in saved["aprob"]), key=f"p_{cod}"):
                aprobadas.append(cod)
    
    # TR1: Ciclo Profesional
    with st.expander("Ciclo Profesional"):
        for cod, info in PLAN_ECON["Ciclo Profesional"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = len(faltan) > 0 and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"s_{cod}", disabled=bloq):
                aprobadas.append(cod)
    
    # TR2: Optativas
    with st.expander("Optativas / Orientadas"):
        for cod, info in PLAN_ECON["Optativas"].items():
            faltan = [r for r in info[1] if r not in aprobadas]
            bloq = len(faltan) > 0 and cod not in saved["aprob"]
            if st.checkbox(info[0], value=(cod in saved["aprob"]), key=f"o_{cod}", disabled=bloq):
                aprobadas.append(cod)

    if st.button("💾 GUARDAR DATOS"):
        data = {"reg": u_reg, "rank": u_rank, "aprob": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_econ_vfinal", json.dumps(data))
        st.success("Guardado.")

# --- 5. CUERPO PRINCIPAL ---
st.title("🧩 Planificador Lic. en Economía")

tab1, tab2 = st.tabs(["📝 Selección", "📋 Sugerencias de Cursada"])

with tab1:
    st.header("Materias para este cuatrimestre")
    # Consolidar todas las materias en un solo diccionario para búsqueda
    total_mats = {**PLAN_ECON["Primer Tramo"], **{k:v[0] for k,v in PLAN_ECON["Ciclo Profesional"].items()}, **{k:v[0] for k,v in PLAN_ECON["Optativas"].items()}}
    
    # Solo habilitadas
    hab = {c: total_mats[c] for c in total_mats if c not in aprobadas}
    # Filtro de correlatividades real
    hab_list = []
    for c in hab:
        reqs = []
        if c in PLAN_ECON["Ciclo Profesional"]: reqs = PLAN_ECON["Ciclo Profesional"][c][1]
        elif c in PLAN_ECON["Optativas"]: reqs = PLAN_ECON["Optativas"][c][1]
        
        if all(r in aprobadas for r in reqs):
            hab_list.append(c)

    elegidas = st.multiselect("Materias habilitadas (Máximo 4):", options=hab_list, format_func=lambda x: f"{total_mats[x]} ({x})", max_selections=4)
    
    st.divider()
    st.subheader("Bloques Horarios Disponibles")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True)]

with tab2:
    if elegidas:
        oferta_f = [o for o in OFERTA_REAL if o[0] in elegidas and o[3] in u_sedes and o[2] in u_bloques]
        
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
                # 2. Regla 3+1 (3 Presenciales max, 1 Virtual max)
                virts = len([x for x in combo if x[6] == "V"])
                pres = len([x for x in combo if x[6] == "P"])
                if virts <= 1 and pres <= 3:
                    validos.append(combo)
            
            if validos:
                # Ordenar por Ranking y Registro
                def scoring(c):
                    score = 0
                    for m in c:
                        # Si tu ranking es mayor, score alto. Si es igual, comparamos registro.
                        if u_rank > m[4]: score += 100
                        elif u_rank == m[4] and int(u_reg) < m[5]: score += 50
                    return score
                
                validos.sort(key=scoring, reverse=True)

                for i, combo in enumerate(validos[:2]):
                    st.markdown(f"<div class='opcion-header'>OPCIÓN {i+1} DE CURSADA</div>", unsafe_allow_html=True)
                    cols = st.columns(len(combo))
                    for idx, c in enumerate(combo):
                        mode = "VIRTUAL" if c[6] == "V" else "PRESENCIAL"
                        badge_class = "badge-v" if c[6] == "V" else "badge-p"
                        
                        # Lógica de probabilidad real (Ranking + Registro)
                        if u_rank > c[4]: prob = "ALTA"
                        elif u_rank == c[4] and int(u_reg) <= c[5]: prob = "ALTA (Por Registro)"
                        elif u_rank > c[4] - 10: prob = "MEDIA"
                        else: prob = "BAJA"
                        
                        cols[idx].markdown(f"""
                            <div class="materia-card">
                                <span class="badge {badge_class}">{mode}</span><br><br>
                                <b>{total_mats[c[0]]}</b><br>
                                <small>{c[1]}</small><br><br>
                                <small>📍 {c[3]}</small><br>
                                <small>⏰ {c[2]} hs</small>
                                <hr style="border:0.5px solid #eee">
                                <small style="color:#059669; font-weight:700">PROB: {prob}</small>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No hay combinaciones que respeten la regla 3+1 (Max 3 presenciales + 1 virtual) con tus filtros de sede/horario.")
        else:
            st.error("Faltan cátedras para alguna de las materias elegidas en tus sedes/horarios seleccionados.")
    else:
        st.info("Elegí materias en la pestaña anterior para generar las opciones.")
