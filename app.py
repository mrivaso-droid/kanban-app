import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Kanban Proyectos", layout="wide")

# =========================
# ARCHIVO LOCAL
# =========================
FILE = "data.csv"

def cargar_datos():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    else:
        return pd.DataFrame(columns=["Nombre", "Fecha", "Monto", "Encargado", "Estado"])

def guardar_datos(df):
    df.to_csv(FILE, index=False)

# =========================
# INICIALIZAR
# =========================
if "df" not in st.session_state:
    st.session_state.df = cargar_datos()

df = st.session_state.df

# =========================
# SIDEBAR
# =========================
st.sidebar.title("👤 Usuario")
usuario = st.sidebar.text_input("Tu nombre")

ver_todos = st.sidebar.checkbox("Ver todos", True)

# =========================
# FORMULARIO
# =========================
st.sidebar.markdown("---")
st.sidebar.header("➕ Nueva tarea")

nombre = st.sidebar.text_input("Nombre del proyecto")
fecha = st.sidebar.date_input("Fecha")
monto = st.sidebar.number_input("Monto ($)", min_value=0)
encargado = st.sidebar.text_input("Encargado", value=usuario)
estado = st.sidebar.selectbox("Estado", [
    "No iniciado", "En progreso", "Completado", "Cerrado-Pagado"
])

if st.sidebar.button("Agregar"):
    nueva_fila = {
        "Nombre": nombre,
        "Fecha": str(fecha),
        "Monto": monto,
        "Encargado": encargado,
        "Estado": estado
    }

    st.session_state.df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    guardar_datos(st.session_state.df)
    st.rerun()

# =========================
# FILTRO
# =========================
df = st.session_state.df

if not ver_todos and usuario:
    df = df[df["Encargado"] == usuario]

# =========================
# TABLERO
# =========================
st.title("📊 Kanban de Proyectos")

col1, col2, col3, col4 = st.columns(4)

estados = ["No iniciado", "En progreso", "Completado", "Cerrado-Pagado"]
colores = ["#ff4b4b", "#4CAF50", "#2196F3", "#000000"]
cols = [col1, col2, col3, col4]

for estado, col, color in zip(estados, cols, colores):
    with col:
        st.markdown(f"## {estado}")

        subset = df[df["Estado"] == estado]

        for idx, row in subset.iterrows():
            col_a, col_b = st.columns([4,1])

            with col_a:
                st.markdown(
                    f"""
                    <div style='background-color:{color};
                    padding:10px;border-radius:10px;
                    color:white;margin-bottom:10px'>
                    <b>{row['Nombre']}</b><br>
                    📅 {row['Fecha']}<br>
                    💰 ${row['Monto']}<br>
                    👤 {row['Encargado']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_b:
                if estado != "No iniciado":
                    if st.button("⬅", key=f"left_{idx}"):
                        nuevo_estado = estados[estados.index(estado)-1]
                        st.session_state.df.at[idx, "Estado"] = nuevo_estado
                        guardar_datos(st.session_state.df)
                        st.rerun()

                if estado != "Cerrado-Pagado":
                    if st.button("➡", key=f"right_{idx}"):
                        nuevo_estado = estados[estados.index(estado)+1]
                        st.session_state.df.at[idx, "Estado"] = nuevo_estado
                        guardar_datos(st.session_state.df)
                        st.rerun()

# =========================
# RESUMEN
# =========================
st.markdown("---")
st.subheader("📌 Resumen")

if not df.empty:
    resumen = df.groupby("Estado").agg({
        "Nombre": "count",
        "Monto": "sum"
    }).rename(columns={"Nombre": "Cantidad"})

    st.dataframe(resumen, use_container_width=True)
else:
    st.info("No hay datos aún")