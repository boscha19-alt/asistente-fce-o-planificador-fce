import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json
from itertools import product

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="FCE UBA - Planificador Integral", layout="wide")
cookie_manager = stx.CookieManager()

# --- 1. BASE DE DATOS INTEGRAL DE PLANES DE ESTUDIO ---
# Estructura: Código: ["Nombre", [Correlativas]]

PLANES = {
    "Contador Público": {
        # Primer Tramo
        241: ["Análisis Matemático I", []], 242: ["Economía", []], 243: ["Sociología", []],
        244: ["Metodología de las Cs. Soc.", []], 245: ["Álgebra", []], 246: ["Hist. Econ. y Soc. Gral.", []],
        # Segundo Tramo
        247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 249: ["Hist. Econ. y Soc. Arg.", [246]],
        250: ["Microeconomía I", [242]], 251: ["Inst. de Derecho Público", [244]], 252: ["Administración General", [243]],
        # Ciclo Profesional
        276: ["Cálculo Financiero", [248]], 351: ["Sistemas Contables", [247]], 353: ["Sistemas de Costos", [247]],
        274: ["Sistemas Administrativos", [252]], 278: ["Micro y Política Econ.", [250]], 1359: ["Derecho Económico", [251]],
        275: ["Tecnol. de la Información", [252]], 279: ["Administración Financiera", [276]], 1352: ["Contabilidad Financiera", [351]],
        362: ["Gestión y Costos", [353]], 273: ["Inst. de Derecho Privado", [1359]], 355: ["Auditoría", [1352]],
        1330: ["Contab. Social y Ambiental", [1352]], 1374: ["Contab. Gubernamental", [1352]], 354: ["Dcho. Trabajo y Seg. Soc.", [273]],
        356: ["Teoría y Tec. Imp. I", [1352]], 357: ["Teoría y Tec. Imp. II", [356]], 1360: ["Dcho. Crediticio y Bursátil", [273]],
        1358: ["Taller Actuación Judicial", [355, 357]], 1361: ["Taller de Práctica Prof.", [355, 357, 1360]]
    },
    "Lic. en Administración": {
        241: ["Análisis I", []], 242: ["Economía", []], 243: ["Sociología", []], 244: ["Metodología", []], 245: ["Álgebra", []], 246: ["Hist. Gral.", []],
        247: ["Teoría Contable", [242]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]], 252: ["Admin. General", [243]],
        463: ["Gestión de Tec. Digitales", [245]], 274: ["Sistemas Administrativos", [252]], 462: ["Derecho Empresarial", [251]],
        276: ["Cálculo Financiero", [248]], 464: ["Gestión de Costos", [247]], 278: ["Macro y Pol. Econ.", [250]],
        467: ["Gestión del Talento", [252]], 466: ["Admin. de Operaciones", [463]], 465: ["Métodos Predictivos", [276, 464]],
        468: ["Admin. Tributaria", [464, 278]], 279: ["Admin. Financiera", [276]], 469: ["Marketing", [467]],
        470: ["Ciencias de la Decisión", [465]], 471: ["Planeamiento Estratégico", [279, 469]], 472: ["Dirección General", [471]],
        473: ["Práctica Profesional", [471]], 489: ["Liderazgo Organizacional", [467]]
    },
    "Lic. en Economía": {
        241: ["Análisis I", []], 242: ["Economía", []], 243: ["Sociología", []], 244: ["Metodología", []], 245: ["Álgebra", []], 246: ["Hist. Gral.", []],
        272: ["Análisis II", [241, 245]], 248: ["Estadística I", [241]], 250: ["Microeconomía I", [242]], 262: ["Macroeconomía I", [250]],
        288: ["Matemática p/ Economistas", [272]], 286: ["Microeconomía II", [250, 272]], 283: ["Macroeconomía II", [262]],
        543: ["Econometría", [248, 283]], 556: ["Finanzas Públicas", [262]], 548: ["Dinero y Bancos", [262]],
        547: ["Estructura Econ. Arg.", [249, 262]], 554: ["Crecimiento Económico", [283]], 558: ["Econ. Internacional", [286, 283]],
        562: ["Seminario de Integración", [543]]
    },
    "Lic. en Sistemas de Información": {
        241: ["Análisis I", []], 242: ["Economía", []], 243: ["Sociología", []], 244: ["Metodología", []], 245: ["Álgebra", []], 246: ["Hist. Gral.", []],
        1275: ["Intro Tecnol. Inf.", [245]], 248: ["Estadística I", [241]], 274: ["Sistemas Admin.", [252]],
        1601: ["Ingeniería de Software", [1275]], 1653: ["Tecnol. de Computadores", [1275]], 658: ["Metodol. Sistemas Inf.", [1601]],
        655: ["Tecn. Comunicaciones", [1653]], 740: ["Redes Informáticas", [655]], 663: ["Sistemas de Datos", [658]],
        662: ["Seguridad Informática", [663]], 1799: ["Gestión de Recursos IT", [658]], 1660: ["Actuación Prof. Sistemas", [662]]
    },
    "Actuario (Admin)": {
        241: ["Análisis I", []], 245: ["Álgebra", []], 248: ["Estadística I", [241]], 276: ["Cálculo Financiero", [248]],
        277: ["Estadística II", [248]], 601: ["Matemática Financiera", [276]], 751: ["Estadística Actuarial", [277]],
        753: ["Biometría Actuarial", [751]], 754: ["Seguros Personales", [601, 753]], 755: ["Seguros Patrimoniales", [601, 751]],
        756: ["Fondos de Jubilaciones", [753]], 757: ["Equilibrio Actuarial", [755, 756]], 758: ["B.Act. Inversiones", [757]]
    },
    "Actuario (Econ)": {
        241: ["Análisis I", []], 245: ["Álgebra", []], 272: ["Análisis II", [241, 245]], 248: ["Estadística I", [241]],
        277: ["Estadística II", [248]], 601: ["Matemática Financiera", [276]], 751: ["Estadística Actuarial", [277]],
        753: ["Biometría Actuarial", [751]], 746: ["Computación Actuarial", [751]]
    }
}

# --- 2. BASE DE DATOS DE OFERTA CON CORTES REALES (Extraídos de tus imágenes) ---
OFERTA_REAL = [
    [466, "Scampini", "07-09", "Córdoba", 173.1, 898636],
    [466, "Lorena Sanchez", "19-21", "Córdoba", 170.8, 897297],
    [279, "Frechero", "21-23", "Córdoba", 167.1, 904593],
    [355, "Gallego Tinto", "07-09", "Córdoba", 186.9, 908546],
    [276, "Sciaccaluga", "07-09", "Córdoba", 154.8, 904388],
    [276, "Tasat", "09-11", "Córdoba", 179.6, 864043],
    [751, "Landro", "09-11", "Córdoba", 181.6, 901495],
    [278, "Gesualdo", "09-11", "Córdoba", 131.4, 915420],
    [489, "Indelicato", "17-19", "Córdoba", 136.2, 918158],
    [274, "Canals", "09-11", "Córdoba", 118.4, 917868],
    [351, "Pahlen", "09-11", "Córdoba", 130.9, 915679],
    [548, "Katz Sebastian", "07-09", "Córdoba", 196.5, 899452],
    [1374, "Cowes Luis", "11-13", "Córdoba", 175.5, 903738],
    [543, "Calicchio Nicolas", "19-21", "Córdoba", 185.0, 897120],
    [1660, "Duarte Ivan", "17-19", "Córdoba", 228.8, 898972],
    [471, "Corti Marcelo", "17-19", "Avellaneda", 211.8, 881045]
]

# --- 3. LÓGICA DE PERSISTENCIA ---
cookies = cookie_manager.get_all()
saved_data = cookies.get("fce_v6_pro")
if saved_data:
    try: saved_data = json.loads(saved_data)
    except: saved_data = None
if not saved_data:
    saved_data = {"registro": "", "ranking": 500.0, "carrera": "Contador Público", "aprobadas": [], "sedes": ["Córdoba"]}

# --- 4. INTERFAZ ---
st.title("⚖️ Planificador FCE UBA - Versión Ciclo Completo")

with st.sidebar:
    st.header("👤 Mi Perfil")
    u_reg = st.text_input("N° Registro:", value=saved_data["registro"])
    u_rank = st.number_input("Mi Ranking Actual:", value=float(saved_data["ranking"]))
    u_carrera = st.selectbox("Carrera:", list(PLANES.keys()), index=list(PLANES.keys()).index(saved_data["carrera"]))
    u_sedes = st.multiselect("Sedes:", ["Córdoba", "Paternal", "Pilar", "San Isidro", "Avellaneda", "Virtual"], default=saved_data["sedes"])
    
    st.subheader("✅ Materias Aprobadas")
    # Dividimos por tramos para que sea legible
    aprobadas = []
    plan_actual = PLANES[u_carrera]
    
    # 1er Tramo (Códigos 241-246)
    with st.expander("Primer Tramo (CBC/Ciclo Gral.)"):
        for cod in sorted([c for c in plan_actual.keys() if c <= 246]):
            if st.checkbox(f"{plan_actual[cod][0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"c_{cod}"):
                aprobadas.append(cod)
    
    # Resto de la carrera
    cbc_ok = all(c in aprobadas for c in plan_actual.keys() if c <= 246)
    with st.expander("Ciclo Profesional / Especialización", expanded=cbc_ok):
        for cod in sorted([c for c in plan_actual.keys() if c > 246]):
            faltan = [c for c in plan_actual[cod][1] if c not in aprobadas]
            disabled = not cbc_ok or len(faltan) > 0
            if st.checkbox(f"{plan_actual[cod][0]} ({cod})", value=(cod in saved_data["aprobadas"]), key=f"s_{cod}", disabled=disabled and cod not in saved_data["aprobadas"]):
                aprobadas.append(cod)
            if disabled and cod not in saved_data["aprobadas"]:
                st.caption(f"🔒 Falta: {faltan if cbc_ok else 'Terminar 1er Tramo'}")

    if st.button("💾 GUARDAR PROGRESO"):
        data = {"registro": u_reg, "ranking": u_rank, "carrera": u_carrera, "aprobadas": aprobadas, "sedes": u_sedes}
        cookie_manager.set("fce_v6_pro", json.dumps(data))
        st.success("Guardado en navegador.")

# --- 5. CUERPO PRINCIPAL ---
tab1, tab2 = st.tabs(["🧩 Armador de Horarios", "📊 Estado Académico"])

with tab1:
    mats_hab = {cod: info[0] for cod, info in plan_actual.items() 
                if cod not in aprobadas and (cod <= 246 or (cbc_ok and all(c in aprobadas for c in info[1])))}
    
    st.header("1. Elegí qué querés cursar este cuatrimestre")
    elegidas = st.multiselect("Materias Habilitadas:", options=list(mats_hab.keys()), format_func=lambda x: f"{mats_hab[x]} ({x})")
    
    st.header("2. Bloques Horarios")
    bloques = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
    cols_h = st.columns(8)
    u_bloques = [b for i, b in enumerate(bloques) if cols_h[i].checkbox(b, value=True, key=f"t_{b}")]

    if elegidas:
        st.header("3. Combinaciones sin superposición")
        # Filtrar oferta real
        oferta_f = [o for o in OFERTA_REAL if o[0] in elegidas and o[3] in u_sedes and o[2] in u_bloques]
        
        cursos_por_m = []
        for m_id in elegidas:
            c_m = [o for o in oferta_f if o[0] == m_id]
            if c_m: cursos_por_m.append(c_m)

        if len(cursos_por_m) == len(elegidas):
            combos = list(product(*cursos_por_m))
            validos = []
            for combo in combos:
                # Detección de colisión (mismo bloque horario)
                ocupado = set()
                choque = False
                for c in combo:
                    if c[2] in ocupado: choque = True; break
                    ocupado.add(c[2])
                if not choque: validos.append(combo)

            if validos:
                for i, combo in enumerate(validos[:3]):
                    with st.expander(f"OPCIÓN DE CURSADA {i+1}", expanded=(i==0)):
                        cols = st.columns(len(combo))
                        for idx, c in enumerate(combo):
                            # Semáforo de ranking basado en imágenes
                            diff = u_rank - c[4]
                            color = "green" if diff > 30 else "orange" if diff > -20 else "red"
                            cols[idx].markdown(f"""
                            <div style="background:white; padding:15px; border-radius:10px; border-top: 5px solid {color}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1)">
                                <small>Cód: {c[0]}</small><br><b>{plan_actual[c[0]][0]}</b><br>
                                Docente: {c[1]}<br>
                                ⏰ {c[2]} hs | 📍 {c[3]}<br>
                                <hr>
                                Probabilidad: <b style="color:{color}">{('Alta' if color=='green' else 'Media' if color=='orange' else 'Baja')}</b><br>
                                <small>Corte: {c[4]} | Reg: {c[5]}</small>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.error("Esas materias se pisan en el horario. Probá habilitando otros bloques o sedes.")
        else:
            st.warning("No hay oferta cargada para todas las materias elegidas con tus filtros actuales.")

with tab2:
    st.header(f"Seguimiento: {u_carrera}")
    data_plan = []
    for cod, info in plan_actual.items():
        status = "✅ Aprobada" if cod in aprobadas else "🟢 Habilitada" if (cod <= 246 or (cbc_ok and all(c in aprobadas for c in info[1]))) else "🔒 Bloqueada"
        data_plan.append({"Código": cod, "Materia": info[0], "Correlativas": info[1], "Estado": status})
    st.dataframe(pd.DataFrame(data_plan), use_container_width=True)
