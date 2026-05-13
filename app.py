import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Planificador FCE UBA PRO", layout="wide")
cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS DE MATERIAS ---
CBC = {
    241: ["Análisis I", []], 242: ["Economía", []], 243: ["Sociología", []],
    244: ["Metodología", []], 245: ["Álgebra", []], 246: ["Hist. Gral.", []]
}

PLANES = {
    "Contador Público": {
        247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]],
        252: ["Admin. General", [243]], 274: ["Sist. Administrativos", [252]], 276: ["Cálculo Financiero", [248]],
        351: ["Sistemas Contables", [247]], 355: ["Auditoría", [1352]]
    },
    "Lic. en Administración": {
        247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]],
        252: ["Admin. General", [243]], 274: ["Sist. Administrativos", [252]], 469: ["Marketing", [252]]
    },
    "Lic. en Sistemas": {
        1275: ["Intro IT", [245]], 248: ["Estadística I", [241]], 1601: ["Ing. Software", [1275]],
        662: ["Seguridad Inf.", [663]]
    },
    "Lic. en Economía": {
        272: ["Análisis II", [241, 245]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]],
        262: ["Macroeconomía I", [250]], 543: ["Econometría", [277, 283]]
    }
}

# --- 2. OFERTA ACADÉMICA (Con días específicos para detectar choques) ---
oferta = [
    {"id": 252, "m": "Admin Gral", "c": "Grondona", "dias": ["Lu", "Ju"], "h": "19-21", "s": "Paternal", "corte": 400},
    {"id": 252, "m": "Admin Gral", "c": "Moroni", "dias": ["Lu", "Ju"], "h": "07-09", "s": "Córdoba", "corte": 550},
    {"id": 274, "m": "Sist. Admin", "c": "Alcain", "dias": ["Ma", "Vi"], "h": "19-21", "s": "Córdoba", "corte": 600},
    {"id": 274, "m": "Sist. Admin", "c": "Gilli", "dias": ["Lu", "Ju"], "h": "09-11", "s": "Córdoba", "corte": 850},
    {"id": 248, "m": "Estadística I", "c": "Cantoni", "dias": ["Ma", "Vi"], "h": "19-21", "s": "San Isidro", "corte": 350},
    {"id": 248, "m": "Estadística I", "c": "Leepera", "dias": ["Lu", "Ju"], "h": "07-09", "s": "Córdoba", "corte": 450},
    {"id": 247, "m": "Teoría Cont.", "c": "Campo", "dias": ["Ma", "Vi"], "h": "07-09", "s": "Córdoba", "corte": 500},
    {"id": 247, "m": "Teoría Cont.", "c": "Bursesi", "dias": ["Lu", "Ju"], "h": "17-19", "s": "Avellaneda", "corte": 600},
    {"id": 1601, "m": "Ing. Software", "c": "Briano", "dias": ["Ma", "Vi"], "h": "09-11", "s": "Virtual", "corte": 450},
]

# --- 3. PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved_data = cookies.get("fce_v5_data")
if saved_data:
    try: saved_data = json.loads(saved_data)
    except: saved_data = None
if not saved_data:
    saved_data = {"registro": "", "ranking": 500, "carrera": "Contador Público", "aprobadas": [], "sedes": ["Córdoba", "Virtual"]}

# --- 4. INTERFAZ SIDEBAR ---
with st.sidebar:
    st.header("👤 Mi Perfil")
    user_reg = st.text_input("N° Registro:", value=saved_data["registro"])
    user_rank = st.number_input("Ranking:", value=int(saved_data["ranking"]))
    user_carrera = st.selectbox("Carrera:", list(PLANES.keys()), index=list(PLANES.keys()).index(saved_data["carrera"]))
    user_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved_data.get("sedes", ["Córdoba"]))
    
    st.subheader("✅ Materias Aprobadas")
    aprobadas = []
    with st.expander("Primer Tramo"):
        for cod, info in CBC.items():
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"c_{cod}"): aprobadas.append(cod)
    
    cbc_completo = all(c in aprobadas for c in CBC.keys())
    with st.expander("Profesional", expanded=cbc_completo):
        for cod, info in PLANES[user_carrera].items():
            faltan = [c for c in info[1] if c not in aprobadas]
            disabled = not cbc_completo or len(faltan) > 0
            if st.checkbox(f"{info[0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"s_{cod}", disabled=disabled and cod not in saved_data["aprobadas"]):
                aprobadas.append(cod)

    if st.button("💾 GUARDAR"):
        data = {"registro": user_reg, "ranking": user_rank, "carrera": user_carrera, "aprobadas": aprobadas, "sedes": user_sedes}
        cookie_manager.set("fce_v5_data", json.dumps(data))
        st.success("Guardado localmente.")

# --- 5. LÓGICA DE HABILITADAS ---
mats_habilitadas = {}
for cod, info in {**CBC, **PLANES[user_carrera]}.items():
    if cod not in aprobadas:
        if cod in CBC or (cbc_completo and all(c in aprobadas for c in info[1])):
            mats_habilitadas[cod] = info[0]

# --- 6. PANTALLA PRINCIPAL ---
st.title("🧩 Armador de Horarios FCE")

# PASO A: ELEGIR QUÉ CURSAR
st.header("1. Elegí las materias que querés cursar este cuatrimestre")
preferidas = st.multiselect("Seleccioná de tu lista de habilitadas:", 
                            options=list(mats_habilitadas.keys()), 
                            format_func=lambda x: f"{mats_habilitadas[x]} ({x})")

if preferidas:
    st.header("2. Combos de horarios posibles")
    
    # Obtener oferta para las elegidas
    oferta_filtrada = [o for o in oferta if o["id"] in preferidas and o["s"] in user_sedes]
    
    # Agrupar por materia
    cursos_por_materia = []
    for m_id in preferidas:
        cursos_m = [o for o in oferta_filtrada if o["id"] == m_id]
        if cursos_m:
            cursos_por_materia.append(cursos_m)

    if len(cursos_por_materia) < len(preferidas):
        st.warning("Algunas materias elegidas no tienen oferta disponible en tus sedes.")
    else:
        # Generar combinaciones (Cartesian Product)
        posibles_combos = list(product(*cursos_por_materia))
        
        validos = []
        for combo in posibles_combos:
            # Chequear superposición
            ocupado = set() # Guardará tuplas (dia, bloque)
            choque = False
            for curso in combo:
                for dia in curso["dias"]:
                    slot = (dia, curso["h"])
                    if slot in ocupado:
                        choque = True
                        break
                    ocupado.add(slot)
                if choque: break
            
            if not choque:
                validos.append(combo)

        if validos:
            st.write(f"Se encontraron **{len(validos)}** combinaciones sin superposición:")
            for i, combo in enumerate(validos[:5]): # Mostrar los primeros 5
                with st.expander(f"OPCIÓN {i+1}", expanded=(i==0)):
                    cols = st.columns(len(combo))
                    for j, curso in enumerate(combo):
                        diff = user_rank - curso["corte"]
                        color = "green" if diff > 100 else "orange" if diff > -50 else "red"
                        cols[j].markdown(f"""
                        <div style="background:#f0f2f6; padding:10px; border-radius:5px; border-left: 5px solid {color}">
                            <b>{curso['m']}</b><br>
                            {curso['c']}<br>
                            {'/'.join(curso['dias'])} {curso['h']}<br>
                            Sede: {curso['s']}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.error("No hay forma de combinar esas materias sin que se superpongan los horarios. Probá eligiendo otras cátedras o sedes.")
else:
    st.info("Seleccioná materias en la lista de arriba para empezar a armar tu cuatrimestre.")
