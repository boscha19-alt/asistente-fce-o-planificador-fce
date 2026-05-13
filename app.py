import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Planificador FCE UBA", layout="wide")

# Inicializar el administrador de cookies de forma directa (sin cache)
cookie_manager = stx.CookieManager()

# --- DATA DE MATERIAS (Ciclo Profesional Completo) ---
primer_tramo = {241: "Análisis I", 242: "Economía", 243: "Sociología", 244: "Metodología", 245: "Álgebra", 246: "Hist. Gral."}
materias_master = {
    "Contador Público": {248: "Estadística I", 247: "Teoría Contable", 351: "Sistemas Contables", 355: "Auditoría", 356: "Impuestos I", 274: "Sistemas Admin.", 250: "Microeconomía I"},
    "Lic. en Administración": {248: "Estadística I", 252: "Admin Gral", 274: "Sistemas Admin", 471: "Plan. Estratégico", 469: "Marketing", 467: "Talento"},
    "Lic. en Sistemas": {1275: "Intro IT", 1601: "Ing. Software", 662: "Seguridad", 663: "Sist. Datos", 740: "Redes"},
    "Lic. en Economía": {272: "Análisis II", 262: "Macro I", 543: "Econometría", 286: "Micro II", 277: "Estadística II"}
}

# --- LÓGICA DE CARGA DE DATOS ---
# Leemos lo que hay guardado en el navegador
cookies = cookie_manager.get_all()
saved_data = cookies.get("fce_user_data")

if saved_data:
    try:
        if isinstance(saved_data, str):
            saved_data = json.loads(saved_data)
    except:
        saved_data = None

if not saved_data:
    saved_data = {"registro": "", "ranking": 500, "carrera": "Contador Público", "aprobadas": []}

# --- INTERFAZ ---
st.title("🛡️ Planificador FCE UBA (Privado)")
st.caption("Los datos se guardan solo en tu PC. Privacidad 100% garantizada.")

# SIDEBAR
with st.sidebar:
    st.header("👤 Mi Perfil")
    user_reg = st.text_input("N° de Registro:", value=saved_data["registro"])
    user_rank = st.number_input("Mi Ranking:", value=int(saved_data["ranking"]), step=1)
    
    # Asegurarnos de que la carrera guardada esté en la lista, si no, usar la primera
    default_carrera = saved_data["carrera"] if saved_data["carrera"] in materias_master else "Contador Público"
    user_carrera = st.selectbox("Mi Carrera:", list(materias_master.keys()), index=list(materias_master.keys()).index(default_carrera))
    
    st.markdown("---")
    st.subheader("✅ Materias Aprobadas")
    
    mats_actuales = {**primer_tramo, **materias_master[user_carrera]}
    aprobadas_ids = []
    
    # Generar checkboxes para cada materia
    for cod, nom in mats_actuales.items():
        is_aprobada = cod in saved_data["aprobadas"]
        if st.checkbox(f"{nom} ({cod})", value=is_aprobada, key=f"check_{cod}"):
            aprobadas_ids.append(cod)

    st.markdown("---")
    if st.button("💾 GUARDAR MI PROGRESO"):
        data_to_save = {
            "registro": user_reg,
            "ranking": user_rank,
            "carrera": user_carrera,
            "aprobadas": aprobadas_ids
        }
        cookie_manager.set("fce_user_data", json.dumps(data_to_save), key="save_button")
        st.success("¡Datos guardados!")
        st.balloons()

# --- CUERPO PRINCIPAL ---
st.header("🕒 Mi Disponibilidad de Horarios")
st.write("Marcá solo los bloques de 2hs en los que PODÉS cursar:")
bloques_posibles = ["07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
cols = st.columns(4)
bloques_libres = []
for i, b in enumerate(bloques_posibles):
    with cols[i % 4]:
        if st.checkbox(f"Bloque {b}", value=True, key=f"time_{b}"):
            bloques_libres.append(b)

st.divider()

# --- RESULTADOS ---
col_mats, col_oferta = st.columns([1, 2])

primer_tramo_ok = all(c in aprobadas_ids for c in primer_tramo.keys())

with col_mats:
    st.subheader("📚 Materias Habilitadas")
    habilitadas = []
    if not primer_tramo_ok:
        st.warning("Faltan del 1er Tramo:")
        for cod, nom in primer_tramo.items():
            if cod not in aprobadas_ids:
                st.write(f"• {nom} ({cod})")
                habilitadas.append(cod)
    else:
        for cod, nom in materias_master[user_carrera].items():
            if cod not in aprobadas_ids:
                st.write(f"• {nom} ({cod})")
                habilitadas.append(cod)

with col_oferta:
    st.subheader("🏢 Oferta Sugerida (Cursos)")
    # Datos de ejemplo basados en lo que pasaste antes
    oferta_ejemplo = [
        {"id": 252, "materia": "Admin Gral", "curso": "Grondona", "horario": "19-21", "sede": "Paternal", "corte": 400},
        {"id": 252, "materia": "Admin Gral", "curso": "Romero", "horario": "09-11", "sede": "Pilar", "corte": 200},
        {"id": 274, "materia": "Sistemas Admin", "curso": "Gilli", "horario": "09-11", "sede": "Cordoba", "corte": 800},
        {"id": 662, "materia": "Seguridad", "curso": "Gil Pablo", "horario": "19-21", "sede": "Cordoba", "corte": 650},
    ]
    
    filtrados = [o for o in oferta_ejemplo if o["id"] in habilitadas and o["horario"] in bloques_libres]
    
    if filtrados:
        df = pd.DataFrame(filtrados)
        # Lógica de probabilidad según ranking del usuario
        def get_prob(corte):
            diff = user_rank - corte
            if diff > 100: return "🟢 Alta"
            if diff >= -50: return "🟡 Media"
            return "🔴 Baja"
        
        df['Probabilidad'] = df['corte'].apply(get_prob)
        st.dataframe(df[['materia', 'curso', 'horario', 'sede', 'Probabilidad']], use_container_width=True)
    else:
        st.info("No hay cursos habilitados en los horarios/sedes elegidos.")
