import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Kanban Proyectos", layout="wide")

# =========================
# CONEXIÓN SUPABASE
# =========================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# FUNCIONES
# =========================
def cargar_datos():
    response = supabase.table("kanban").select("*").execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        df.columns = df.columns.str.lower()
        return df
    else:
        return pd.DataFrame(columns=["id","nombre","fecha","monto","encargado","estado"])

def agregar_dato(data):
    supabase.table("kanban").insert(data).execute()

def actualizar_estado(id, nuevo_estado):
    supabase.table("kanban").update({"estado": nuevo_estado}).eq("id", id).execute()

def eliminar_dato(id):
    supabase.table("kanban").delete().eq("id", id).execute()

def editar_dato(id, data):
    supabase.table("kanban").update(data).eq("id", id).execute()

# =========================
# CARGAR DATOS
# =========================
df = cargar_datos()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("👤 Usuario")
usuario = st.sidebar.text_input("Tu nombre")

st.sidebar.markdown("---")
st.sidebar.header("➕ Nueva tarea")

nombre = st.sidebar.text_input("Nombre")
fecha = st.sidebar.date_input("Fecha")
monto = st.sidebar.number_input("Monto", min_value=0)
encargado = st.sidebar.text_input("Encargado", value=usuario)
estado = st.sidebar.selectbox("Estado", [
    "No iniciado", "En progreso", "Completado", "Cerrado-Pagado"
])

if st.sidebar.button("Agregar"):
    if nombre:
        agregar_dato({
            "nombre": nombre,
            "fecha": str(fecha),
            "monto": monto,
            "encargado": encargado,
            "estado": estado
        })
        st.rerun()

# =========================
# EDITAR
# =========================
if "edit_id" in st.session_state:
    st.subheader("✏️ Editar tarea")

    row = df[df["id"] == st.session_state.edit_id].iloc[0]

    nombre_e = st.text_input("Nombre", row["nombre"])
    monto_e = st.number_input("Monto", value=int(row["monto"]))
    encargado_e = st.text_input("Encargado", row["encargado"])
    estado_e = st.selectbox(
        "Estado",
        ["No iniciado", "En progreso", "Completado", "Cerrado-Pagado"],
        index=["No iniciado", "En progreso", "Completado", "Cerrado-Pagado"].index(row["estado"])
    )

    if st.button("Guardar cambios"):
        editar_dato(st.session_state.edit_id, {
            "nombre": nombre_e,
            "monto": monto_e,
            "encargado": encargado_e,
            "estado": estado_e
        })
        del st.session_state.edit_id
        st.rerun()

# =========================
# TABLERO
# =========================
st.title("📊 Kanban de Proyectos")

estados = ["No iniciado", "En progreso", "Completado", "Cerrado-Pagado"]
colores = ["#ff4b4b", "#4CAF50", "#2196F3", "#000000"]

cols = st.columns(4)

for estado, col, color in zip(estados, cols, colores):
    with col:
        st.markdown(f"## {estado}")

        subset = df[df["estado"] == estado]

        # 🔥 Totales por columna
        total_monto = subset["monto"].sum()
        cantidad = len(subset)

        total_formateado = f"${int(total_monto):,}".replace(",", ".")

        st.markdown(f"""
        <div style='background-color:#f0f0f0;
        padding:8px;border-radius:8px;margin-bottom:10px'>
        <b>Total:</b> {total_formateado}<br>
        <b>Proyectos:</b> {cantidad}
        </div>
        """, unsafe_allow_html=True)

        for _, row in subset.iterrows():
            col_a, col_b = st.columns([4,1])

            with col_a:
                monto_formateado = f"${int(row['monto']):,}".replace(",", ".")

                st.markdown(
                    f"""
                    <div style='background-color:{color};
                    padding:10px;border-radius:10px;
                    color:white;margin-bottom:10px'>
                    <b>{row['nombre']}</b><br>
                    📅 {row['fecha']}<br>
                    💰 {monto_formateado}<br>
                    👤 {row['encargado']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_b:
                if estado != "No iniciado":
                    if st.button("⬅", key=f"L{row['id']}"):
                        actualizar_estado(row["id"], estados[estados.index(estado)-1])
                        st.rerun()

                if estado != "Cerrado-Pagado":
                    if st.button("➡", key=f"R{row['id']}"):
                        actualizar_estado(row["id"], estados[estados.index(estado)+1])
                        st.rerun()

                if st.button("✏️", key=f"E{row['id']}"):
                    st.session_state.edit_id = row["id"]

                if st.button("🗑", key=f"D{row['id']}"):
                    eliminar_dato(row["id"])
                    st.rerun()

# =========================
# RESUMEN
# =========================
st.markdown("---")
st.subheader("📌 Resumen")

if not df.empty:
    resumen = df.groupby("estado").agg({
        "nombre": "count",
        "monto": "sum"
    }).rename(columns={
        "nombre": "Cantidad",
        "monto": "Total $"
    })

    # 🔥 Formato miles + $
    resumen["Total $"] = resumen["Total $"].apply(
        lambda x: f"${int(x):,}".replace(",", ".")
    )

    st.dataframe(resumen, use_container_width=True)
else:
    st.info("No hay datos aún")