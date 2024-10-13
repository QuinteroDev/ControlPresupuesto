import streamlit as st
import pandas as pd
import json
import os
from datetime import date

# Funciones para guardar y cargar los datos en un archivo JSON
def cargar_datos(nombre_archivo):
    if os.path.exists(nombre_archivo):
        try:
            with open(nombre_archivo, 'r') as archivo:
                data = archivo.read()
                if data.strip():  # Verifica si el archivo no está vacío
                    return pd.read_json(nombre_archivo)
                else:
                    return pd.DataFrame(columns=["Mes", "Concepto", "Cantidad", "Pagado", "Categoría", "Fecha"])
        except ValueError:  # Atrapa cualquier error de lectura de JSON
            return pd.DataFrame(columns=["Mes", "Concepto", "Cantidad", "Pagado", "Categoría", "Fecha"])
    else:
        return pd.DataFrame(columns=["Mes", "Concepto", "Cantidad", "Pagado", "Categoría", "Fecha"])

def guardar_datos(nombre_archivo, datos):
    with open(nombre_archivo, 'w') as archivo:
        archivo.write(datos.to_json(orient='records', date_format='iso'))

# Funciones para gestionar categorías
def cargar_categorias(nombre_archivo):
    if os.path.exists(nombre_archivo):
        try:
            with open(nombre_archivo, 'r') as archivo:
                return json.load(archivo)
        except ValueError:
            return ["Casa", "Deporte", "Alimentación / Hogar", "Salir Fuera"]  # Categorías por defecto
    else:
        return ["Casa", "Deporte", "Alimentación / Hogar", "Salir Fuera"]

def guardar_categorias(nombre_archivo, categorias):
    with open(nombre_archivo, 'w') as archivo:
        json.dump(categorias, archivo)

# Archivo para las categorías
archivo_categorias = "categorias.json"
categorias = cargar_categorias(archivo_categorias)

nombre_archivo = "gastos_fijos.json"

# Cargar datos desde el archivo JSON
df = cargar_datos(nombre_archivo)

# Validar si existe la columna 'Mes' y 'Categoría', si no, agregarla
if 'Mes' not in df.columns:
    df['Mes'] = None  # Inicializar la columna 'Mes' si no existe
if 'Categoría' not in df.columns:
    df['Categoría'] = None  # Inicializar la columna 'Categoría' si no existe

# Título de la aplicación
st.title("❤️ Gestión de Gastos Fijos Mensuales")

# Selección de mes en la barra lateral
mes_seleccionado = st.sidebar.selectbox("Selecciona el mes", 
                                        ["Octubre 2024", "Noviembre 2024", "Diciembre 2024"])

# Filtrar los datos por mes
df_mes = df[df["Mes"] == mes_seleccionado]

if df_mes.empty:
    st.session_state.gastos = pd.DataFrame(columns=["Mes", "Concepto", "Cantidad", "Pagado", "Categoría", "Fecha"])
else:
    st.session_state.gastos = df_mes

# Mostrar la tabla de gastos como un checklist editable (organizado por categorías)
st.header(f"Gastos fijos de {mes_seleccionado}")

# Iterar sobre cada categoría
for categoria in categorias:
    with st.expander(f"{categoria}"):  # Crea un desplegable por categoría
        gastos_categoria = st.session_state.gastos[st.session_state.gastos["Categoría"] == categoria]
        
        if gastos_categoria.empty:
            st.write("No hay gastos en esta categoría.")
        else:
            # Mostrar los gastos en la categoría con checkbox
            for index, row in gastos_categoria.iterrows():
                pagado_checkbox = st.checkbox(f"{row['Concepto']} - {int(row['Cantidad'])} € - {row['Fecha']}", 
                                              value=row['Pagado'], key=f"{mes_seleccionado}_{categoria}_{index}")
                st.session_state.gastos.at[index, "Pagado"] = pagado_checkbox

                # Botón para editar cada gasto
                if f"edit_mode_{index}" not in st.session_state:
                    st.session_state[f"edit_mode_{index}"] = False  # Estado de edición para cada gasto

                if st.session_state[f"edit_mode_{index}"]:
                    nuevo_concepto = st.text_input("Editar concepto", row["Concepto"], key=f"new_concepto_{index}")
                    nueva_cantidad = st.number_input("Editar cantidad (€)", min_value=0, step=1, value=int(row["Cantidad"]), key=f"new_cantidad_{index}")
                    nueva_fecha = st.date_input("Editar fecha", pd.to_datetime(row["Fecha"]).date(), key=f"new_fecha_{index}")
                    if st.button("Guardar cambios", key=f"save_button_{index}"):
                        st.session_state.gastos.at[index, "Concepto"] = nuevo_concepto
                        st.session_state.gastos.at[index, "Cantidad"] = nueva_cantidad
                        st.session_state.gastos.at[index, "Fecha"] = str(nueva_fecha)
                        st.session_state[f"edit_mode_{index}"] = False
                        st.success("Gasto actualizado correctamente")

                else:
                    if st.button("Editar", key=f"edit_button_{index}"):
                        st.session_state[f"edit_mode_{index}"] = True

                # Botón para eliminar un gasto
                if st.button("Eliminar", key=f"delete_{mes_seleccionado}_{index}"):
                    st.session_state.gastos = st.session_state.gastos.drop(index).reset_index(drop=True)
                    st.success("Gasto eliminado correctamente")

# Calcular el total de gastos, lo pagado y lo pendiente
total_gastos = st.session_state.gastos["Cantidad"].sum()
pagado_total = st.session_state.gastos[st.session_state.gastos["Pagado"] == True]["Cantidad"].sum()
por_pagar_total = st.session_state.gastos[st.session_state.gastos["Pagado"] == False]["Cantidad"].sum()

# Mostrar el balance
st.subheader(f"Balance de {mes_seleccionado}")
st.write(f"Total de gastos: {int(total_gastos)} €")
st.write(f"Total pagado: {int(pagado_total)} €")
st.write(f"Por pagar: {int(por_pagar_total)} €")


# Formulario para agregar nuevos gastos (FORMULARIO ABAJO)
st.header("Añadir nuevos gastos")
with st.form("Añadir gasto"):
    concepto = st.text_input("Concepto del gasto")
    cantidad = st.number_input("Cantidad (€)", min_value=0, step=1)  # Solo números enteros
    categoria = st.selectbox("Categoría", categorias)
    fecha = st.date_input("Fecha", value=date.today())
    pagado = st.checkbox("¿Está pagado?")
    submit = st.form_submit_button("Añadir gasto")

# Añadir nuevo gasto al DataFrame
if submit and concepto:
    nuevo_gasto = pd.DataFrame({"Mes": [mes_seleccionado], "Concepto": [concepto], "Cantidad": [cantidad], "Pagado": [pagado], "Categoría": [categoria], "Fecha": [str(fecha)]})
    st.session_state.gastos = pd.concat([st.session_state.gastos, nuevo_gasto], ignore_index=True)
    st.success("Gasto añadido correctamente")

# Guardar los datos actualizados en el archivo JSON
df = pd.concat([df[df["Mes"] != mes_seleccionado], st.session_state.gastos], ignore_index=True)
guardar_datos(nombre_archivo, df)

# Formulario para agregar nuevas categorías
st.header("Agregar nueva categoría")
nueva_categoria = st.text_input("Nombre de la nueva categoría")

if st.button("Añadir nueva categoría"):
    if nueva_categoria and nueva_categoria not in categorias:
        categorias.append(nueva_categoria)
        guardar_categorias(archivo_categorias, categorias)
        st.success(f"Nueva categoría '{nueva_categoria}' añadida correctamente.")
    elif nueva_categoria in categorias:
        st.warning(f"La categoría '{nueva_categoria}' ya existe.")
    else:
        st.warning("El nombre de la categoría no puede estar vacío.")
