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
    
    # Verificar si 'Score_Escalar' existe, si no, calcularlo como placeholder (ejemplo)
    if 'Score_Escalar' not in df_form.columns:
        df_form['Score_Escalar'] = 0.5  # Placeholder o cálculo inicial
    
    if 'Score_Escalar' not in df_palas.columns:
        df_palas['Score_Escalar'] = df_palas['score_nivel'] * 0.5 + df_palas['score_lesion'] * 0.5
    
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
    return df_form
    #return df_form.drop(columns=["Score", "Score_Escalar", "Rango de precio dispuesto a pagar"], errors='ignore')

# Mostrar detalles del registro seleccionado en forma tabular
def mostrar_detalles_registro_tabular(df_form, index):
    selected_row = df_form.iloc[index]
    return pd.DataFrame({"Característica": selected_row.index, "Valor": selected_row.values})


# Encontrar vecinos más cercanos con KNN
def encontrar_vecinos_mas_cercanos_knn(df_palas, x_random, y_random, z_random):
    knn_features = df_palas[['score_lesion', 'score_nivel', 'Score_Escalar']]
    
    knn = NearestNeighbors(n_neighbors=3)
    knn.fit(knn_features)
    
    reference_point = [[x_random, y_random, z_random]]
    
    distances, indices = knn.kneighbors(reference_point)
    
    palas_recomendadas = df_palas.iloc[indices[0]]
    
    return palas_recomendadas[['Palas', 'Score_Escalar', 'score_nivel', 'score_lesion']]


# Función para analizar la relación entre Score y palas recomendadas
def analizar_relacion_score(df_palas):
    st.subheader("Relación entre Score y Palas Recomendadas")
    
    # Mapear los valores numéricos de "Tipo de Juego" a etiquetas descriptivas
    if "Tipo de Juego" in df_palas.columns:
        df_palas["Tipo de Juego Descriptivo"] = df_palas["Tipo de Juego"].map({
            0: "No data",
            1: "control",
            2: "polivalente",
            3: "potencia"
        })
    else:
        st.error("La columna 'Tipo de Juego' no existe en el DataFrame.")
        return
    
    # Verificar si hay datos en df_palas
    if df_palas.empty:
        st.error("El DataFrame 'df_palas' está vacío.")
        return
    
    # Crear checkboxes para seleccionar qué tipos de juego mostrar
    categorias_unicas = df_palas["Tipo de Juego Descriptivo"].unique()
    seleccionados = {categoria: st.checkbox(categoria, value=(categoria=="control")) for categoria in categorias_unicas}
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Iterar sobre las categorías descriptivas seleccionadas
    for tipo_juego, mostrar in seleccionados.items():
        if mostrar:
            subset = df_palas[df_palas["Tipo de Juego Descriptivo"] == tipo_juego]
            if not subset.empty:
                ax.scatter(subset["score_lesion"], subset["score_nivel"], label=tipo_juego)
    
    ax.set_xlabel("Lesión (%)")
    ax.set_ylabel("Nivel (%)")
    ax.legend(title="Tipo de Juego")
    
    st.pyplot(fig)


# Configuración de la página para ancho completo
st.set_page_config(page_title="Formulario", layout="wide")

# CSS personalizado para eliminar márgenes y ajustar espaciado

custom_css = """

<style>
/* Centrar todo el contenido y limitar su ancho al 80% */
[data-testid="stAppViewContainer"] {
    max-width: 70%; /* Ancho máximo del contenido */
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

    if enviar_btn_clicked:
        # Crear un nuevo registro con los datos del formulario
        nuevo_registro = {
            'Cuantas horas juega a la semana': horas_semana,
            'Indique su peso': peso,
            'Indique su altura': altura,
            'Rango de precio dispuesto a pagar': rango_precios,
            'Indique su lado de juego': lado_de_juego,
            'Indique su nivel de juego': nivel_de_juego,
            'Tipo de juego': tipo_de_juego,
            'Que tipo de balance te gusta': tipo_de_balance,
            'Has tenido alguna de las siguientes lesiones previamente lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros': lesiones_antiguas,
            'Con que frecuencia': frecuencia_lesion,
            'Hace cuanto': cuanto_lesion,
            'Score': None, # Placeholder for Score if needed later
            'Score_Escalar': None # Placeholder for Score_Escalar if needed later
        }

        # Cargar DataFrame existente y agregar el nuevo registro
        df_form , df_palas = cargar_dataframes()
        
        # Convertir el nuevo registro en un DataFrame y concatenarlo con el existente
        nuevo_df = pd.DataFrame([nuevo_registro])
        
        # Concatenar el nuevo registro al DataFrame existente
        df_form_actualizado = pd.concat([df_form, nuevo_df], ignore_index=True)

    """
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
            st.write(f"**Última Lesión:** {cuanto_lesion}") """

# Función para el recomendador de pala
def recomendador_de_pala():
    st.title("Recomendador de Pala")
    
    try:
        # Cargar los DataFrames
        df_form, df_palas = cargar_dataframes()
        
        # Renombrar columnas del DataFrame formulario
        df_form = renombrar_columnas(df_form)
        
        # Slider para seleccionar índice del registro en el formulario
        index = st.slider("Índice del Registro Formulario", min_value=0, max_value=len(df_form) - 1, step=1)
        
        # Mostrar detalles del registro seleccionado en forma tabular
        detalles_registro_df = mostrar_detalles_registro_tabular(df_form, index)
        
        st.subheader("Detalles del Registro Seleccionado")
        st.dataframe(detalles_registro_df)

        # Obtener valores del registro seleccionado en el formulario
        score_escalar = df_form.iloc[index]['Score_Escalar']
        
        # Crear gráfico interactivo (matplotlib)
        st.subheader("Gráfico Interactivo")
        
        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_subplot(111, projection='3d')
        
        ax.scatter(df_palas['score_lesion'], df_palas['score_nivel'], df_palas['Score_Escalar'], color='blue', label='Datos Palas')
        
        ax.scatter([df_palas['score_lesion'].mean()], [df_palas['score_nivel'].mean()], [score_escalar], color='red', s=200, label='Registro Seleccionado')
        
        ax.set_xlabel('Lesión (%)')
        ax.set_ylabel('Nivel (%)')
        ax.set_zlabel('Formulario (%)')
        ax.legend()
        
        st.pyplot(fig) 
        
        # Encontrar vecinos más cercanos con KNN (palas recomendadas)
        st.subheader("Palas Recomendadas")
        
        x_random = df_palas['score_lesion'].mean()
        y_random = df_palas['score_nivel'].mean()
        
        palas_recomendadas_df = encontrar_vecinos_mas_cercanos_knn(df_palas, x_random=x_random, y_random=y_random, z_random=score_escalar)
        
        st.dataframe(palas_recomendadas_df)

        # Analizar relación entre Score y Palas Recomendadas
        analizar_relacion_score(df_palas)
    
    except Exception as e:
        st.error(f"Error al generar el gráfico o procesar los datos: {str(e)}")


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