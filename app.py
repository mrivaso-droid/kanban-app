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

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

df = st.session_state.df

# =========================
# SIDEBAR
# =========================
st.sidebar.title("👤 Usuario")
usuario = st.sidebar.text_input("Tu nombre")

ver_todos = st.sidebar.checkbox("Ver todos", True)

# =========================
# FORMULARIO NUEVO
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
    if nombre.strip() != "":
        nueva_fila = {
            "Nombre": nombre,
            "Fecha": str(fecha),
            "Monto": monto,
            "Encargado": encargado,
            "Estado": estado
        }

        # 🚫 evitar duplicados
        if not ((df["Nombre"] == nombre) & (df["Fecha"] == str(fecha))).any():
            st.session_state.df = pd.concat(
                [df, pd.DataFrame([nueva_fila])],
                ignore_index=True
            )
            guardar_datos(st.session_state.df)
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Proyecto duplicado")

# =========================
# EDITAR
# =========================
if st.session_state.edit_index is not None:
    i = st.session_state.edit_index
    st.subheader("✏️ Editar tarea")

    nombre_edit = st.text_input("Nombre", st.session_state.df.at[i, "Nombre"])
    fecha_edit = st.text_input("Fecha", st.session_state.df.at[i, "Fecha"])
    monto_edit = st.number_input("Monto", value=int(st.session_state.df.at[i, "Monto"]))
    encargado_edit = st.text_input("Encargado", st.session_state.df.at[i, "Encargado"])
    estado_edit = st.selectbox(
        "Estado",
        ["No iniciado", "En progreso", "Completado", "Cerrado-Pagado"],
        index=["No iniciado", "En progreso", "Completado", "Cerrado-Pagado"].index(
            st.session_state.df.at[i, "Estado"]
        )
    )

    if st.button("Guardar cambios"):
        st.session_state.df.at[i, "Nombre"] = nombre_edit
        st.session_state.df.at[i, "Fecha"] = fecha_edit
        st.session_state.df.at[i, "Monto"] = monto_edit
        st.session_state.df.at[i, "Encargado"] = encargado_edit
        st.session_state.df.at[i, "Estado"] = estado_edit

        guardar_datos(st.session_state.df)
        st.session_state.edit_index = None
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
            fila_real = idx

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
                # ⬅ mover izquierda
                if estado != "No iniciado":
                    if st.button("⬅", key=f"left_{idx}"):
                        nuevo_estado = estados[estados.index(estado)-1]
                        st.session_state.df.at[fila_real, "Estado"] = nuevo_estado
                        guardar_datos(st.session_state.df)
                        st.rerun()

                # ➡ mover derecha
                if estado != "Cerrado-Pagado":
                    if st.button("➡", key=f"right_{idx}"):
                        nuevo_estado = estados[estados.index(estado)+1]
                        st.session_state.df.at[fila_real, "Estado"] = nuevo_estado
                        guardar_datos(st.session_state.df)
                        st.rerun()

                # ✏️ editar
                if st.button("✏️", key=f"edit_{idx}"):
                    st.session_state.edit_index = fila_real

                # 🗑 eliminar
                if st.button("🗑", key=f"delete_{idx}"):
                    st.session_state.df = st.session_state.df.drop(fila_real).reset_index(drop=True)
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