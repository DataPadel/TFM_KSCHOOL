import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import streamlit as st
from streamlit_option_menu import option_menu

# Diccionario de mapeo para convertir valores numéricos a etiquetas descriptivas
LABEL_MAPPING = {
    "Balance": {0: "No data", 1: "bajo", 2: "medio", 3: "alto"},
    "Dureza": {0: "No data", 1: "blanda", 2: "media", 3: "dura"},
    "Nivel de Juego": {0: "No data", 1: "principiante", 2: "avanzado", 3: "pro"},
    "Forma": {0: "No data", 1: "redonda", 2: "lágrima", 3: "diamante"},
    "Tipo de Juego": {0: "No data", 1: "control", 2: "polivalente", 3: "potencia"}
}

# Función para cargar y validar los DataFrames
@st.cache_data
def cargar_dataframes():
    df_form = pd.read_json('dataframe_final_formulario.json', lines=True)
    df_palas = pd.read_csv('df_scaled_palas.csv')
    if 'Score_Escalar' not in df_form.columns:
        raise KeyError("La columna 'Score_Escalar' no existe en 'dataframe_final_formulario.json'.")
    return df_form, df_palas

# Sincronizar DataFrames
@st.cache_data
def sincronizar_dataframes(df_form, df_palas):
    min_rows = min(len(df_form), len(df_palas))
    df_form = df_form.iloc[:min_rows]
    df_palas = df_palas.iloc[:min_rows]
    df_palas['Score_Escalar'] = df_form['Score_Escalar'].values
    return df_form, df_palas

# Renombrar columnas del DataFrame df_form
def renombrar_columnas(df_form):
    column_mapping = {
        "Cuantas horas juegas a la semana": "Horas a la Semana",
        "Indique su peso": "Peso",
        "Indique su altura": "Altura",
        "Indique su Lado de Juego": "Lado de Juego",
        "Indique su nivel de juego": "Nivel de Juego",
        "Que tipo de balance te gusta": "Balance",
        "Has tenido alguna de las siguientes lesiones ...": "Lesiones Antiguas",
        "Con que frecuencia": "Frecuencia Lesion",
        "Hace cuanto": "Tiempo entre Lesiones"
    }
    df_form.rename(columns=column_mapping, inplace=True)
    return df_form.drop(columns=["Score", "Score_Escalar", "Rango de precio dispuesto a pagar"], errors='ignore')

# Mostrar detalles del registro seleccionado en forma tabular
def mostrar_detalles_registro_tabular(df_form, index):
    selected_row = df_form.iloc[index]
    return pd.DataFrame({"Característica": selected_row.index, "Valor": selected_row.values})

# Encontrar vecinos más cercanos con columnas específicas
def encontrar_vecinos_mas_cercanos(df_palas, x_random, y_random):
    reference_points = pd.DataFrame({
        'score_lesion': [x_random] * 3,
        'score_nivel': [y_random] * 3,
        'Balance': [1.0, 2.0, 3.0]
    })
    
    palas_data = df_palas[['Palas', 'Nivel de Juego', 'Tipo de Juego', 'Balance', 'Precio', 'Dureza', 'Forma']].copy()
    
    for columna in ['Nivel de Juego', 'Tipo de Juego', 'Balance', 'Dureza', 'Forma']:
        palas_data[columna] = palas_data[columna].map(LABEL_MAPPING[columna])

    knn = NearestNeighbors(n_neighbors=1)
    knn.fit(df_palas[['score_lesion', 'score_nivel', 'Balance']])
    
    resultados_tabular = []
    for _, point in reference_points.iterrows():
        distances, indices = knn.kneighbors([point])
        closest_point = palas_data.iloc[indices[0][0]].to_dict()
        closest_point['Punto'] = f"Punto {point['Balance']}"
        resultados_tabular.append(closest_point)
    
    return pd.DataFrame(resultados_tabular)

# Configuración de la página para ancho completo
st.set_page_config(page_title="Formulario", layout="wide")

# CSS personalizado para eliminar márgenes y ajustar espaciado

custom_css = """

<style>
/* Centrar todo el contenido y limitar su ancho al 80% */
[data-testid="stAppViewContainer"] {
    max-width: 80%; /* Ancho máximo del contenido */
    margin: 0 auto; /* Centrar horizontalmente */
    padding-top: 1rem; /* Espaciado superior */
    padding-bottom: 1rem; /* Espaciado inferior */
}

/* Ajustar márgenes entre columnas */
.css-1kyxreq {
    padding-left: 0rem;
    padding-right: 0rem;
}

/* Centrar el botón de enviar */
button[kind="primary"] {
    margin-top: 1rem;
    display: block;
    margin-left: auto;
    margin-right: auto;
}

/* Ajustar márgenes de los expanders */
[data-testid="stExpander"] {
    margin-top: 1rem;
    margin-bottom: 1rem;
}
</style>
"""

# Aplicar CSS personalizado
st.markdown(custom_css, unsafe_allow_html=True)

# Función para el formulario
def formulario():

    # Título del Formulario
    st.title("Formulario")
    
    # Opciones de los distintos desplegables de los inputs
    opciones_peso = {"Entre 51 y 70 Kg": 0, "Entre 71 y 90 Kg": 0, "Más de 91 Kg": 0.5}
    opciones_altura = {"Entre 1,51 y 1,70 metros": 0, "Entre 1,71 y 1,80 metros": 0, "Mas de 1,80 metros": 0.5}
    opciones_nivel_de_juego = {"Iniciacion": 0, "Intermedio": 1, "Avanzado": 2}
    opciones_tipo_de_juego = {"Ofensivo": 1, "Defensivo": 0}
    opciones_balance = {"Medio": 0, "Alto": 0.5}
    opciones_horas_semana = {"Menos de 3,5 horas": 0, "Mas de 3.5 horas": 0.5}
    opciones_rango_precio = {"Menos de 100": 0, "Entre 100 y 200": 0, "Mas de 200": 0}
    opciones_rango_juego = {"Drive": 0, "Reves": 0.5}
    opciones_lesiones_antiguas = {
        "Lumbares": 0.5,
        "Epicondilitis": 0.15,
        "Gemelos o fascitis": 0.5,
        "Cervicales": 0.25,
        "Hombros": 0.5,
        "Ninguna": 0
    }
    opciones_frecuencia_lesion = {
        "Siempre que juego defensivamente": 0.5,
        "Siempre que juego ofensivamente": 0.5,
        "Casi siempre que juego intensamente": 0.25,
        "Rara vez cuando juego": 0.15
    }
    opciones_cuanto_lesion = {
        "Menos de 3 meses": 0.5,
        "Entre 3 y 6 meses": 0.25,
        "Mas de 6 meses": 0.15
    }

    # Crear tres columnas para las preguntas del formulario
    col1, col2, col3 = st.columns(3)

    # Preguntas relativas a la persona (Columna izquierda)
    with col1:
        st.subheader("Datos Personales")
        peso = st.selectbox("Indica tu peso (kg)", opciones_peso)
        altura = st.selectbox("Indica tu altura (cm)", opciones_altura)
        rango_precios = st.selectbox("¿Cuánto dinero estás dispuesto a pagar por una pala?", opciones_rango_precio)
        horas_semana = st.selectbox("¿Cuántas horas juega a la semana?", opciones_horas_semana)

    # Preguntas relativas al nivel de pádel (Columna central)
    with col2:
        st.subheader("Nivel de Pádel")
        nivel_de_juego = st.selectbox("¿Cuál es tu Nivel de juego?", opciones_nivel_de_juego)
        tipo_de_juego = st.selectbox("¿Qué tipo de Juego te gusta?", opciones_tipo_de_juego)
        tipo_de_balance = st.selectbox("¿Qué tipo de Balance te gusta?", opciones_balance)
        lado_de_juego = st.selectbox("Indique su lado de juego", opciones_rango_juego)

    # Preguntas relacionadas con lesiones (Columna derecha)
    with col3:
        st.subheader("Lesiones")
        lesiones_antiguas = st.selectbox(
            "¿Has tenido alguna de las siguientes lesiones previamente: lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros?",
            opciones_lesiones_antiguas
        )
        frecuencia_lesion = st.selectbox("¿Cuándo sueles caer lesionado?", opciones_frecuencia_lesion)
        cuanto_lesion = st.selectbox("¿Cuánto tiempo pasó desde tu última lesión?", opciones_cuanto_lesion)

    # Botón Enviar debajo del formulario completo
    enviar_btn_clicked = st.button("Enviar")

    # Mostrar respuestas debajo del botón si se hace clic en Enviar
    if enviar_btn_clicked:
        st.subheader("Respuestas Enviadas")
        
        with st.expander("Respuestas Relativas Persona"):
            st.write(f"**Peso:** {peso}")
            st.write(f"**Altura:** {altura}")
            st.write(f"**Precio Dispuesto a Pagar:** {rango_precios}")
            st.write(f"**Horas a la Semana Jugadas:** {horas_semana}")

        with st.expander("Respuestas Relativas Nivel de Pádel"):
            st.write(f"**Nivel de Juego:** {nivel_de_juego}")
            st.write(f"**Tipo de Juego:** {tipo_de_juego}")
            st.write(f"**Balance:** {tipo_de_balance}")
            st.write(f"**Lado de Juego:** {lado_de_juego}")

        with st.expander("Respuestas Lesiones Antiguas"):
            st.write(f"**Lesiones Previas:** {lesiones_antiguas}")
            st.write(f"**Frecuencia de Lesión:** {frecuencia_lesion}")
            st.write(f"**Última Lesión:** {cuanto_lesion}")

# Función para el recomendador de pala
def recomendador_de_pala():
    st.title("Recomendador de Pala")
    
    try:
        # Cargar y sincronizar los DataFrames
        df_form, df_palas = cargar_dataframes()
        df_form, df_palas = sincronizar_dataframes(df_form, df_palas)
        df_form = renombrar_columnas(df_form)
        
        # Slider para seleccionar índice del registro
        index = st.slider("Índice del Registro", min_value=0, max_value=len(df_palas) - 1, step=1)
        
        # Seleccionar fila del DataFrame
        selected_row = df_palas.iloc[index]
        x_random, y_random, z_random = selected_row['score_lesion'], selected_row['score_nivel'], selected_row['Score_Escalar']
        
        # Crear gráfico interactivo (matplotlib)
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(df_palas['score_lesion'], df_palas['score_nivel'], df_palas['Score_Escalar'], color='blue', label='Datos Palas')
        ax.scatter(x_random, y_random, z_random, color='red', s=200, label='Pala Seleccionada')
        ax.set_xlabel('Lesión (%)')
        ax.set_ylabel('Nivel (%)')
        ax.set_zlabel('Formulario (%)')
        ax.legend()
        
        st.pyplot(fig)  # Mostrar gráfico interactivo
        
        # Encontrar vecinos más cercanos
        vecinos_df = encontrar_vecinos_mas_cercanos(df_palas, x_random, y_random)
        
        # Mostrar detalles del registro seleccionado en forma tabular
        detalles_registro_df = mostrar_detalles_registro_tabular(df_form, index)
        
        st.subheader("Detalles del Registro Seleccionado")
        st.dataframe(detalles_registro_df)
        
        st.subheader("Vecinos Más Cercanos")
        st.dataframe(vecinos_df)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Menú lateral moderno con streamlit-option-menu
with st.sidebar:
    opcion_seleccionada = option_menu(
        menu_title="Plai Padel Pro",
        options=["Formulario", "Recomendador de Pala"],
        icons=["pencil-fill", "bar-chart-fill"],
        menu_icon="cast",
        default_index=0,
    )

# Mostrar la opción seleccionada
if opcion_seleccionada == "Formulario":
    formulario()
elif opcion_seleccionada == "Recomendador de Pala":
    recomendador_de_pala()