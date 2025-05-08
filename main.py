import streamlit as st
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    String,
    Float,
    Integer,
    MetaData,
    select,
    update,
    DateTime,
)
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Configuración de la base de datos SQLite
DATABASE_URL = "sqlite:///produccion_v2.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Definición de la tabla
produccion_table = Table(
    "produccion_datos_v2",
    metadata,
    Column("orden_produccion", String, primary_key=True),
    Column("dieta", String),
    Column("molienda", Float),
    Column("durabilidad", Float),
    Column("dureza", Integer),
    Column("temperatura", Integer),
    Column("hora_registro", DateTime),
    Column("peletizadora", String),
)

# Crear la tabla si no existe
metadata.create_all(engine)

st.title("⚙️ Formulario de Producción")

# Inicializar el estado para controlar el reseteo del formulario
if "formulario_enviado" not in st.session_state:
    st.session_state["formulario_enviado"] = False

# Resetear el formulario al inicio si se marcó como enviado en la iteración anterior
if st.session_state["formulario_enviado"]:
    st.session_state["orden_produccion"] = ""
    st.session_state["dieta"] = "🍎 Dieta 1"
    st.session_state["molienda"] = 0.6
    st.session_state["durabilidad"] = 0.6
    st.session_state["dureza"] = 2
    st.session_state["temperatura"] = 28
    st.session_state["peletizadora"] = "Pel 1"
    st.session_state["formulario_enviado"] = False

# Inicializar el estado de los campos del formulario si no existen
if "orden_produccion" not in st.session_state:
    st.session_state["orden_produccion"] = ""
if "dieta" not in st.session_state:
    st.session_state["dieta"] = "🍎 Dieta 1"
if "molienda" not in st.session_state:
    st.session_state["molienda"] = 0.6
if "durabilidad" not in st.session_state:
    st.session_state["durabilidad"] = 0.6
if "dureza" not in st.session_state:
    st.session_state["dureza"] = 2
if "temperatura" not in st.session_state:
    st.session_state["temperatura"] = 28
if "peletizadora" not in st.session_state:
    st.session_state["peletizadora"] = "Pel 1"

with st.form(key="produccion_formulario"):
    orden_produccion = st.text_input("🏭 Orden de Producción", key="orden_produccion")
    dieta = st.selectbox(
        "🍎 Dieta", ["🍎 Dieta 1", "🥦 Dieta 2", "🌾 Dieta 3"], key="dieta"
    )
    molienda = st.number_input(
        "⚙️ Molienda (0.6 - 1.0)",
        min_value=0.6,
        max_value=1.0,
        step=0.01,
        key="molienda",
    )
    durabilidad = st.number_input(
        "⏳ Durabilidad (0.6 - 1.0)",
        min_value=0.6,
        max_value=1.0,
        step=0.01,
        key="durabilidad",
    )
    dureza = st.number_input(
        "💪 Dureza (2 - 7)", min_value=2, max_value=7, step=1, key="dureza"
    )
    temperatura = st.number_input(
        "🌡️ Temperatura (°C, 28 - 50)",
        min_value=28,
        max_value=50,
        step=1,
        key="temperatura",
    )
    peletizadora = st.selectbox(
        " Pelletizadora", ["Pel 1", "Pel 2", "Pel 3"], key="peletizadora"
    )
    confirmar = st.checkbox("✅ Confirmo que deseo guardar los datos")
    submit_button = st.form_submit_button("💾 Guardar Registro")

if submit_button:
    errores = []
    if not confirmar:
        errores.append("Debes confirmar que deseas guardar los datos.")
    if not st.session_state.orden_produccion:
        errores.append("La **Orden de Producción** no puede estar vacía.")
    if not (0.6 <= st.session_state.molienda <= 1.0):
        errores.append("El valor de **Molienda** debe estar entre 0.6 y 1.0.")
    if not (0.6 <= st.session_state.durabilidad <= 1.0):
        errores.append("El valor de **Durabilidad** debe estar entre 0.6 y 1.0.")
    if not (2 <= st.session_state.dureza <= 7):
        errores.append("El valor de **Dureza** debe estar entre 2 y 7.")
    if not (28 <= st.session_state.temperatura <= 50):
        errores.append("El valor de **Temperatura** debe estar entre 28 y 50 °C.")

    if errores:
        for error in errores:
            st.error(f"⚠️ {error}")
    else:
        try:
            with engine.connect() as conn:
                select_stmt = select(produccion_table).where(
                    produccion_table.c.orden_produccion
                    == st.session_state.orden_produccion
                )
                result = conn.execute(select_stmt).fetchone()
                hora_actual = datetime.now()

                if result:
                    accion = st.radio(
                        f"La Orden de Producción '{st.session_state.orden_produccion}' ya existe. ¿Qué deseas hacer?",
                        [
                            "Corregir los datos existentes",
                            "Adicionar un nuevo registro (con la misma Orden de Producción)",
                        ],
                        index=0,
                    )

                    if accion == "Corregir los datos existentes":
                        if st.session_state.get("confirmar_correccion", False) is False:
                            st.info(
                                "¿Seguro que quieres corregir los datos? Presiona 'Guardar Registro' otra vez para confirmar."
                            )
                            st.session_state.confirmar_correccion = True
                        else:
                            update_stmt = (
                                update(produccion_table)
                                .where(
                                    produccion_table.c.orden_produccion
                                    == st.session_state.orden_produccion
                                )
                                .values(
                                    dieta=st.session_state.dieta,
                                    molienda=st.session_state.molienda,
                                    durabilidad=st.session_state.durabilidad,
                                    dureza=st.session_state.dureza,
                                    temperatura=st.session_state.temperatura,
                                    hora_registro=hora_actual,
                                    peletizadora=st.session_state.peletizadora,
                                )
                            )
                            conn.execute(update_stmt)
                            conn.commit()
                            st.success(
                                f"✅ Datos para la Orden de Producción '{st.session_state.orden_produccion}' corregidos exitosamente a las {hora_actual.strftime('%H:%M:%S')}."
                            )
                            st.session_state.confirmar_correccion = False
                            st.session_state["formulario_enviado"] = True
                            st.rerun()
                    elif (
                        accion
                        == "Adicionar un nuevo registro (con la misma Orden de Producción)"
                    ):
                        insert_stmt = produccion_table.insert().values(
                            orden_produccion=st.session_state.orden_produccion,
                            dieta=st.session_state.dieta,
                            molienda=st.session_state.molienda,
                            durabilidad=st.session_state.durabilidad,
                            dureza=st.session_state.dureza,
                            temperatura=st.session_state.temperatura,
                            hora_registro=hora_actual,
                            peletizadora=st.session_state.peletizadora,
                        )
                        conn.execute(insert_stmt)
                        conn.commit()
                        st.success(
                            f"✅ Nuevo registro para la Orden de Producción '{st.session_state.orden_produccion}' adicionado a las {hora_actual.strftime('%H:%M:%S')}."
                        )
                        st.session_state["formulario_enviado"] = True
                        st.rerun()
                        import subprocess

                        subprocess.run(["git", "add", "produccion_v2.db"])
                        subprocess.run(["git", "commit", "-m", f"add orden {orden_produccion}"])
                        subprocess.run(["git", "push"])


                else:
                    insert_stmt = produccion_table.insert().values(
                        orden_produccion=st.session_state.orden_produccion,
                        dieta=st.session_state.dieta,
                        molienda=st.session_state.molienda,
                        durabilidad=st.session_state.durabilidad,
                        dureza=st.session_state.dureza,
                        temperatura=st.session_state.temperatura,
                        hora_registro=hora_actual,
                        peletizadora=st.session_state.peletizadora,
                    )
                    conn.execute(insert_stmt)
                    conn.commit()
                    st.success(
                        f"✅ Datos para la Orden de Producción '{st.session_state.orden_produccion}' guardados exitosamente a las {hora_actual.strftime('%H:%M:%S')}."
                    )
                    st.session_state["formulario_enviado"] = True
                    st.rerun()

        except SQLAlchemyError as e:
            st.error(f"❌ Error al interactuar con la base de datos: {e}")
