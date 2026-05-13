import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Planificador FCE UBA", layout="wide")

# Inicializar el administrador de almacenamiento local
@st.cache_resource
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# --- DATA DE MATERIAS (Resumida para el ejemplo) ---
primer_tramo = {241: "Análisis I", 242: "Economía", 243: "Sociología", 244: "Metodología", 245: "Álgebra", 246: "Hist. Gral."}
materias_master = {
    "Contador Público": {248: "Estadística I", 247: "Teoría Contable", 351: "Sistemas Contables", 355: "Auditoría", 356: "Impuestos I", 274: "Sistemas Admin."},
    "Lic. en Administración": {248: "Estadística I", 252: "Admin Gral", 274: "Sistemas Admin", 471: "Plan. Estratégico", 469: "Marketing"},
    "Lic. en Sistemas": {1275: "Intro IT", 1601: "Ing. Software", 662: "Seguridad", 663: "Sist. Datos"},
    "Lic. en Economía": {272: "Análisis II", 262: "Macro I", 543: "Econometría", 286: "Micro II"},
    "Actuario": {276: "Cálculo Fin.", 277: "Estadística II", 601: "Mat. Actuarial", 751: "Est. Actuarial"}
}

# --- LÓGICA DE CARGA DE DATOS ---
# Intentamos recuperar los datos guardados en la compu del alumno
saved_data = cookie_manager.get(cookie="fce_user_data")
if saved_data:
    if isinstance(saved_data, str):
        saved_data = json.loads(saved_data)
else:
    saved_data = {"registro": "", "ranking": 500, "carrera": "Contador Público", "aprobadas": []}

# --- INTERFAZ ---
st.title("🛡️ Planificador FCE UBA (Privado)")
st.caption("Tus datos se guardan solo en tu navegador. Nadie más puede ver tu registro ni tu ranking.")

# SIDEBAR
with st.sidebar:
    st.header("👤 Mi Perfil")
    user_reg = st.text_input("N° de Registro:", value=saved_data["registro"])
    user_rank = st.number_input("Mi Ranking:", value=int(saved_data["ranking"]))
    user_carrera = st.selectbox("Mi Carrera:", list(materias_master.keys()), index=list(materias_master.keys()).index(saved_data["carrera"]))
    
    st.markdown("---")
    st.subheader("✅ Materias Aprobadas")
    
    mats_actuales = {**primer_tramo, **materias_master[user_carrera]}
    aprobadas_ids = []
    
    for cod, nom in mats_actuales.items():
        # Verificamos si ya estaba aprobada en la "memoria"
        is_aprobada = cod in saved_data["aprobadas"]
        if st.checkbox(f"{nom} ({cod})", value=is_aprobada):
            aprobadas_ids.append(cod)

    st.markdown("---")
    if st.button("💾 GUARDAR EN MI PC"):
        data_to_save = {
            "registro": user_reg,
            "ranking": user_rank,
            "carrera": user_carrera,
            "aprobadas": aprobadas_ids
        }
        cookie_manager.set("fce_user_data", json.dumps(data_to_save))
        st.success("¡Datos guardados localmente!")

# --- BLOQUES HORARIOS (Lo que pediste anteriormente) ---
st.header("🕒 Mi Disponibilidad Horaria")
st.write("Seleccioná los bloques en los que PODÉS cursar:")
bloques_posibles = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
cols = st.columns(4)
bloques_libres = []
for i, b in enumerate(bloques_posibles):
    with cols[i % 4]:
        if st.checkbox(f"Bloque {b}", value=True):
            bloques_libres.append(b)

# --- RESULTADOS (Habilitadas y Oferta) ---
st.divider()
col_mats, col_oferta = st.columns([1, 2])

# Lógica simplificada de habilitadas
primer_tramo_ok = all(c in aprobadas_ids for c in primer_tramo.keys())

with col_mats:
    st.subheader("📚 Materias Habilitadas")
    habilitadas = []
    if not primer_tramo_ok:
        st.warning("Pendientes del 1er Tramo:")
        for cod, nom in primer_tramo.items():
            if cod not in aprobadas_ids:
                st.write(f"• {nom}")
                habilitadas.append(cod)
    else:
        for cod, nom in materias_master[user_carrera].items():
            if cod not in aprobadas_ids:
                st.write(f"• {nom}")
                habilitadas.append(cod)

with col_oferta:
    st.subheader("🏢 Oferta Sugerida")
    # Simulamos oferta para las materias habilitadas
    oferta_ejemplo = [
        {"id": 252, "materia": "Admin Gral", "curso": "Cátedra A", "horario": "07-09", "sede": "Cordoba"},
        {"id": 252, "materia": "Admin Gral", "curso": "Cátedra B", "horario": "19-21", "sede": "Paternal"},
        {"id": 274, "materia": "Sistemas Admin", "curso": "Cátedra C", "horario": "17-19", "sede": "Cordoba"},
        {"id": 1601, "materia": "Ing. Software", "curso": "Cátedra D", "horario": "09-11", "sede": "Virtual"},
    ]
    
    filtrados = [o for o in oferta_ejemplo if o["id"] in habilitadas and o["horario"] in bloques_libres]
    
    if filtrados:
        st.table(pd.DataFrame(filtrados)[['materia', 'curso', 'horario', 'sede']])
    else:
        st.info("No hay cursos que coincidan con tus bloques horarios seleccionados.")
