import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Gestión de Gastos Fijos Mensuales")

# Selección de mes en la barra lateral (solo octubre, noviembre y diciembre 2024)
mes_seleccionado = st.sidebar.selectbox("Selecciona el mes", 
                                        ["Octubre 2024", "Noviembre 2024", "Diciembre 2024"])

# Estado inicial para almacenar los gastos en la sesión
if 'gastos' not in st.session_state:
    st.session_state.gastos = {}

# Si no hay datos del mes seleccionado, inicializar el mes
if mes_seleccionado not in st.session_state.gastos:
    st.session_state.gastos[mes_seleccionado] = pd.DataFrame(columns=["Concepto", "Cantidad", "Pagado"])

# Mostrar la tabla de gastos como un checklist editable (CHECKLIST ARRIBA)
st.header(f"Gastos fijos de {mes_seleccionado}")

df = st.session_state.gastos[mes_seleccionado]

# Iterar sobre cada gasto
for index, row in df.iterrows():
    col1, col2, col3 = st.columns([6, 1, 1])

    # Mostrar checkbox para "Pagado" y actualizar el estado
    with col1:
        pagado_checkbox = st.checkbox(f"{row['Concepto']} - {int(row['Cantidad'])} €", 
                                      value=row['Pagado'], key=f"{mes_seleccionado}_{index}")
        st.session_state.gastos[mes_seleccionado].at[index, "Pagado"] = pagado_checkbox

    # Botón para editar un gasto
    with col2:
        if f"edit_mode_{index}" not in st.session_state:
            st.session_state[f"edit_mode_{index}"] = False  # Estado de edición para cada gasto

        if st.session_state[f"edit_mode_{index}"]:
            nuevo_concepto = st.text_input("Editar concepto", row["Concepto"], key=f"new_concepto_{index}")
            nueva_cantidad = st.number_input("Editar cantidad (€)", min_value=0, step=1, value=int(row["Cantidad"]), key=f"new_cantidad_{index}")
            if st.button("Guardar cambios", key=f"save_button_{index}"):
                st.session_state.gastos[mes_seleccionado].at[index, "Concepto"] = nuevo_concepto
                st.session_state.gastos[mes_seleccionado].at[index, "Cantidad"] = nueva_cantidad
                st.session_state[f"edit_mode_{index}"] = False
                st.success("Gasto actualizado correctamente")
        else:
            if st.button("Edit", key=f"edit_button_{index}"):
                st.session_state[f"edit_mode_{index}"] = True

    # Botón para eliminar un gasto
    with col3:
        if st.button("Delete", key=f"delete_{mes_seleccionado}_{index}"):
            st.session_state.gastos[mes_seleccionado] = st.session_state.gastos[mes_seleccionado].drop(index).reset_index(drop=True)
            st.success("Gasto eliminado correctamente")

# Mostrar el balance
pagado_total = st.session_state.gastos[mes_seleccionado][st.session_state.gastos[mes_seleccionado]["Pagado"] == True]["Cantidad"].sum()
por_pagar_total = st.session_state.gastos[mes_seleccionado][st.session_state.gastos[mes_seleccionado]["Pagado"] == False]["Cantidad"].sum()

st.subheader(f"Balance de {mes_seleccionado}")
st.write(f"Total pagado: {int(pagado_total)} €")
st.write(f"Por pagar: {int(por_pagar_total)} €")

# Formulario para agregar nuevos gastos (FORMULARIO ABAJO)
st.header("Añadir nuevos gastos")
with st.form("Añadir gasto"):
    concepto = st.text_input("Concepto del gasto")
    cantidad = st.number_input("Cantidad (€)", min_value=0, step=1)  # Solo números enteros
    pagado = st.checkbox("¿Está pagado?")
    submit = st.form_submit_button("Añadir gasto")

# Añadir nuevo gasto al DataFrame
if submit and concepto:
    nuevo_gasto = pd.DataFrame({"Concepto": [concepto], "Cantidad": [cantidad], "Pagado": [pagado]})
    st.session_state.gastos[mes_seleccionado] = pd.concat([df, nuevo_gasto], ignore_index=True)
    st.success("Gasto añadido correctamente")

