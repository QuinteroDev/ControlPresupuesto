import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime

with st.expander("Opciones avanzadas: Gestión de archivos y categorías"):
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
mes_seleccionado = st.sidebar.selectbox("Gastos Mes", 
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

# Sección para gestionar CRUD de categorías
st.header("Gestionar categorías")

# Formulario para agregar nuevas categorías
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

# Sección para editar y eliminar categorías existentes
categoria_a_editar = st.selectbox("Selecciona una categoría para editar o eliminar", categorias)

nuevo_nombre_categoria = st.text_input("Editar nombre de la categoría", value=categoria_a_editar)
if st.button("Guardar cambios en categoría"):
    if nuevo_nombre_categoria and nuevo_nombre_categoria not in categorias:
        categorias[categorias.index(categoria_a_editar)] = nuevo_nombre_categoria
        guardar_categorias(archivo_categorias, categorias)
        st.success(f"La categoría '{categoria_a_editar}' ha sido renombrada a '{nuevo_nombre_categoria}' correctamente.")
    elif nuevo_nombre_categoria in categorias:
        st.warning(f"El nombre '{nuevo_nombre_categoria}' ya existe.")
    else:
        st.warning("El nombre de la categoría no puede estar vacío.")

# Botón para eliminar la categoría
if st.button("Eliminar categoría"):
    if categoria_a_editar in categorias:
        categorias.remove(categoria_a_editar)
        guardar_categorias(archivo_categorias, categorias)
        st.success(f"La categoría '{categoria_a_editar}' ha sido eliminada correctamente.")
    else:
        st.warning(f"No se pudo eliminar la categoría '{categoria_a_editar}'.")



# Funciones para guardar y cargar los eventos en un archivo JSON
def cargar_eventos(nombre_archivo):
    if os.path.exists(nombre_archivo):
        try:
            with open(nombre_archivo, 'r') as archivo:
                data = archivo.read()
                if data.strip():  # Verifica si el archivo no está vacío
                    return pd.read_json(nombre_archivo)
                else:
                    return pd.DataFrame(columns=["Fecha", "Hora", "Quien", "Concepto", "Todo_el_dia"])
        except ValueError:  # Atrapa cualquier error de lectura de JSON
            return pd.DataFrame(columns=["Fecha", "Hora", "Quien", "Concepto", "Todo_el_dia"])
    else:
        return pd.DataFrame(columns=["Fecha", "Hora", "Quien", "Concepto", "Todo_el_dia"])

# Funciones para guardar y cargar los eventos en un archivo JSON
def cargar_eventos(nombre_archivo):
    if os.path.exists(nombre_archivo):
        try:
            with open(nombre_archivo, 'r') as archivo:
                data = archivo.read()
                if data.strip():  # Verifica si el archivo no está vacío
                    return pd.read_json(nombre_archivo)
                else:
                    return pd.DataFrame(columns=["Fecha", "Hora", "Quien", "Concepto", "Todo_el_dia"])
        except ValueError:  # Atrapa cualquier error de lectura de JSON
            return pd.DataFrame(columns=["Fecha", "Hora", "Quien", "Concepto", "Todo_el_dia"])
    else:
        return pd.DataFrame(columns=["Fecha", "Hora", "Quien", "Concepto", "Todo_el_dia"])

def guardar_eventos(nombre_archivo, eventos):
    with open(nombre_archivo, 'w') as archivo:
        archivo.write(eventos.to_json(orient='records', date_format='iso'))

# Nombre del archivo JSON para los eventos
nombre_archivo_eventos = "eventos.json"

# Cargar eventos desde el archivo JSON
df_eventos = cargar_eventos(nombre_archivo_eventos)

# Título de la aplicación
st.title("❤️ Gestión de Eventos")

# Sección para añadir eventos
st.header("Añadir nuevos eventos")

# Formulario para agregar eventos
with st.form("Añadir evento"):
    rango_fechas = st.date_input("Selecciona el rango de fechas", value=(date.today(), date.today()), help="Selecciona una fecha de inicio y una fecha de finalización")
    todo_el_dia = st.checkbox("¿Todo el día?")
    
    if not todo_el_dia:
        hora_evento = st.time_input("Hora del evento", value=datetime.now().time())
    else:
        hora_evento = None

    quien_evento = st.selectbox("¿Quién lo hace?", ["Juntos", "Quintero", "Andreea"])
    concepto_evento = st.text_input("Concepto del evento")
    
    # Botón de submit
    submit_evento = st.form_submit_button("Añadir evento")

# Añadir el nuevo evento al DataFrame
if submit_evento and concepto_evento:
    fecha_inicio, fecha_fin = rango_fechas
    rango_dias = pd.date_range(fecha_inicio, fecha_fin).tolist()
    
    for fecha in rango_dias:
        nuevo_evento = pd.DataFrame({
            "Fecha": [str(fecha.date())],
            "Hora": [str(hora_evento) if hora_evento else "Todo el día"],
            "Quien": [quien_evento],
            "Concepto": [concepto_evento],
            "Todo_el_dia": [todo_el_dia]
        })
        
        df_eventos = pd.concat([df_eventos, nuevo_evento], ignore_index=True)
    
    guardar_eventos(nombre_archivo_eventos, df_eventos)
    st.success(f"Evento '{concepto_evento}' añadido correctamente para los días {fecha_inicio} a {fecha_fin}.")

# Mostrar calendario de eventos
st.header("Calendario de eventos")

# Filtrar eventos por el mes seleccionado
mes_actual = datetime.now().month
ano_actual = datetime.now().year

# Mostrar eventos del mes actual por defecto
mes_seleccionado = st.sidebar.selectbox("Eventos Mes", [f"{mes_actual}/{ano_actual}"] + [f"{mes}/{ano_actual}" for mes in range(mes_actual + 1, 13)])

# Convertir la selección de mes en formato datetime
mes, ano = map(int, mes_seleccionado.split('/'))

# Filtrar eventos por mes y año seleccionados
df_eventos_mes = df_eventos[
    (pd.to_datetime(df_eventos["Fecha"]).dt.month == mes) &
    (pd.to_datetime(df_eventos["Fecha"]).dt.year == ano)
]

# Ordenar los eventos por fecha
df_eventos_mes = df_eventos_mes.sort_values(by="Fecha")

# Mostrar los eventos del mes seleccionado, día por día si están en un rango
if not df_eventos_mes.empty:
    for index, evento in df_eventos_mes.iterrows():
        fecha_evento = pd.to_datetime(evento["Fecha"])
        concepto_evento = evento["Concepto"]
        quien_evento = evento["Quien"]
        hora_evento = evento["Hora"]

        # Limpiar cualquier valor nulo en hora_evento
        if pd.isna(hora_evento) or hora_evento == "Todo el día":
            hora_evento_str = "Todo el día"
        else:
            hora_evento_str = pd.to_datetime(hora_evento).strftime('%H:%M')  # Formato HH:MM sin segundos

        # Mostrar el evento en cada día con botones de edición y eliminación
        st.write(f"📅 {fecha_evento.strftime('%Y-%m-%d')} - {hora_evento_str} - {quien_evento} - {concepto_evento}")

        # Botones eliminar

        if st.button("Eliminar", key=f"delete_{index}"):
            df_eventos = df_eventos.drop(index).reset_index(drop=True)
            guardar_eventos(nombre_archivo_eventos, df_eventos)
            st.success("Evento eliminado correctamente.")
else:
    st.write("No hay eventos para este mes.")