import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Estado Depósitos a Plazo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# ESTILOS GLOBALES
# =========================================================

st.markdown("""
<style>
    :root {
        --santander-red: #EC1C24;
    }

    .stApp {
        background-color: #ffffff;
    }

    h1 {
        color: #EC1C24 !important;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 2.2em;
    }

    h2 {
        border-bottom: 2px solid #EC1C24;
        padding-bottom: 6px;
    }

    .stMetric {
        border: 1px solid #eee;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }

    .stButton > button {
        background-color: #EC1C24 !important;
        color: white !important;
        border-radius: 6px;
    }

    .stButton > button:hover {
        background-color: #c9181f !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# PATH
# =========================================================

LOCAL_JSON_PATH = "data.json"

REQUIRED_COLUMNS = [
    "COUNTERPARTY",
    "TRADER",
    "CURRENCY",
    "ESTADO",
    "NOMINAL"
]

# =========================================================
# UTILIDAD IMAGEN
# =========================================================

def get_image_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

# =========================================================
# DATA
# =========================================================

def normalizar_columnas(df):
    df.columns = df.columns.astype(str).str.strip().str.upper()
    return df


@st.cache_data
def cargar_datos():
    try:
        if not os.path.exists(LOCAL_JSON_PATH):
            return None, None, "No existe data.json"

        df = pd.read_json(LOCAL_JSON_PATH)
        df = normalizar_columnas(df)

        faltantes = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if faltantes:
            return None, None, f"Faltan columnas: {faltantes}"

        fecha = datetime.fromtimestamp(
            os.path.getmtime(LOCAL_JSON_PATH)
        ).strftime("%d/%m/%Y %H:%M:%S")

        return df, fecha, None

    except Exception as e:
        return None, None, str(e)

# =========================================================
# LOAD
# =========================================================

df, fecha_actualizacion, error = cargar_datos()

if error:
    st.error(error)
    st.stop()

# =========================================================
# KPIs
# =========================================================

def count_estado(valor):
    return len(df[df["ESTADO"] == valor]) if "ESTADO" in df.columns else 0

total = len(df)
finalizados = count_estado("FINALIZADO")
pendientes = count_estado("PENDIENTE")
observados = count_estado("OBSERVADO")
sin_registro = count_estado("SIN REGISTRO")

# =========================================================
# HEADER
# =========================================================

st.markdown(f"""
# ESTADO DE DEPÓSITOS A PLAZO

Seguimiento operativo en tiempo real

🕐 Última actualización: *{fecha_actualizacion}*
""")

st.divider()

# =========================================================
# KPIs
# =========================================================

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("TOTAL", total)
c2.metric("FINALIZADOS", finalizados)
c3.metric("PENDIENTES", pendientes)
c4.metric("OBSERVADOS", observados)
c5.metric("SIN REGISTRO", sin_registro)

# =========================================================
# ALERTAS
# =========================================================

st.subheader("Alertas Operativas")

alertas = df[df["ESTADO"].isin(["OBSERVADO", "SIN REGISTRO"])]

if len(alertas) > 0:
    st.dataframe(alertas, use_container_width=True)
else:
    st.success("Sin alertas operativas")

# =========================================================
# FILTROS
# =========================================================

st.subheader("Filtros")

def opciones(col):
    if col in df.columns:
        return ["Todos"] + sorted(df[col].dropna().unique().tolist())
    return ["Todos"]

counterparty = st.selectbox("Counterparty", opciones("COUNTERPARTY"))
trader = st.selectbox("Trader", opciones("TRADER"))
estado = st.selectbox("Estado", opciones("ESTADO"))

filtrado = df.copy()

if counterparty != "Todos":
    filtrado = filtrado[filtrado["COUNTERPARTY"] == counterparty]

if trader != "Todos":
    filtrado = filtrado[filtrado["TRADER"] == trader]


if estado != "Todos":
    filtrado = filtrado[filtrado["ESTADO"] == estado]

# =========================================================
# RESULTADOS
# =========================================================

st.subheader("Resultados")
st.dataframe(filtrado, use_container_width=True, height=450)

# =========================================================
# TARJETA FINAL (MEJORADA Y ESTABLE)
# =========================================================

img_base64 = get_image_base64("SANTANDER.png")

st.divider()

st.markdown("## Frase Motivacional")

col1, col2 = st.columns([1, 4])

with col1:
    if img_base64:
        st.image("SANTANDER.png", width=150)
    else:
        st.warning("Imagen no encontrada")

with col2:
    st.markdown("""
### “La excelencia no es un destino, es un compromiso constante con la mejora continua.”

*— Jesus*
""")