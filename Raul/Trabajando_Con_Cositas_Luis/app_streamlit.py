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

# Función para el formulario
def formulario():

    #Titulo del Formulario
    st.title("Formulario")
    
    #Opciones de las distintos desplegables de los input
    opciones_peso = ["Entre 51 y 70 Kg","Entre 71 y 90 Kg","Más de 91 Kg"]
    opciones_altura = ["Entre 1,51 y 1,70 metros","Entre 1,71 y 1,80 metros","Mas de 1,80 metros"]
    opciones_nivel_de_juego = ["Iniciacion", "Intermedio", "Avanzado"]
    opciones_tipo_de_juego = ["Ofensivo","Defensivo"]
    opciones_balance = ["Medio","Alto"]
    opciones_horas_semana = ["Menos de 3,5 horas","Mas de 3.5 horas"]
    opciones_rango_precio = ["Menos de 100","Entre 100 y 200","Mas de 200"]
    opciones_rango_juego = ["Drive","Reves"]
    opciones_lesiones_antiguas = ["Lumbares","Epicondilitis","Gemelos o fascitis","Cervicales","Hombros","Ninguna"]
    opciones_frecuencia_lesion = ["Siempre que juego defensivamente","Siempre que juego ofensivamente","Casi siempre que juego intensamente","Rara vez cuando juego"]
    opciones_cuanto_lesion = ["Menos de 3 meses","Entre 3 y 6 meses","Mas de 6 meses"]

    # Preguntas relativas a la persona
    peso = st.selectbox("Indica tu peso (kg)", opciones_peso)
    altura = st.selectbox("Indica tu altura (cm)",opciones_altura)
    rango_precios =  st.selectbox("¿Cuando dinero estas dispuesto a pagar por una pala?", opciones_rango_precio)
    horas_semana = st.selectbox("¿Cuántas horas juega a la semana?", opciones_horas_semana)
    

    #Preguntas relativas al nivel de padel y caracteristicas relacionadas con este
    nivel_de_juego = st.selectbox("¿Cual es tu Nivel de juego ?", opciones_nivel_de_juego)
    tipo_de_juego = st.selectbox("¿Que tipo de Juego te gusta?", opciones_tipo_de_juego)
    tipo_de_balance = st.selectbox("¿Que tipo de Balance te gusta?", opciones_balance)
    lado_de_juego = st.selectbox("Indique su lado de juego", opciones_rango_juego)

    #Preguntas relacionadas con las posibles lesiones de padel en el pasado
    lesiones_antiguas = st.selectbox("¿Has tenido alguna de las siguientes lesiones previamente:  lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros?", opciones_lesiones_antiguas)
    frecuencia_lesion = st.selectbox("¿Cuando sueles caer lesionado?",opciones_frecuencia_lesion)
    cuanto_lesion = st.selectbox("¿Cuanto tiempo paso desde tu ultima lesion?",opciones_cuanto_lesion)

   

    
    if st.button("Enviar"):
        st.success(f"Datos enviados:\nHoras a la semana: {horas_semana}, Peso: {peso}, Altura: {altura}")

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