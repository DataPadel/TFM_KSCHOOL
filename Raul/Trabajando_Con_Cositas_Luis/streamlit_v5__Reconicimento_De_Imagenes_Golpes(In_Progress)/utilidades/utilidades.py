import sys
import subprocess
import streamlit as st
import importlib.util
import plotly.express as px
from sklearn.neighbors import NearestNeighbors
from sklearn.impute import SimpleImputer


#DESCARGA, CONVERSION Y GENERACION DE ARCHIVOS S3
@st.cache_data
def descargar_generar_archivo_palas_s3():
    """
    Descarga múltiples archivos JSON desde un bucket de Amazon S3, los convierte en DataFrames de pandas
    y los guarda como archivos CSV en el sistema local. Verifica e instala automáticamente las
    librerías necesarias si no están instaladas.

    :return: None
    """

    def check_library_installed(library_name):
        """
        Verifica si una librería está instalada.
        :param library_name: Nombre de la librería a verificar.
        :return: True si está instalada, False si no.
        """
        spec = importlib.util.find_spec(library_name)
        return spec is not None

    def install_library(library_name):
        """
        Instala una librería usando pip.
        :param library_name: Nombre de la librería a instalar.
        """
        subprocess.check_call([sys.executable, "-m", "pip", "install", library_name])

    # Verificar e instalar las librerías necesarias
    if not check_library_installed('dotenv'):
        install_library('python-dotenv')

    if not check_library_installed('boto3'):
        install_library('boto3')

    try:

        # Cargar las variables de entorno desde el archivo .env
        load_dotenv()

        # Obtener las credenciales de AWS desde las variables de entorno
        AWS_SERVER_PUBLIC_KEY = os.getenv('AWS_SERVER_PUBLIC_KEY')
        AWS_SERVER_SECRET_KEY = os.getenv('AWS_SERVER_SECRET_KEY')

        # Crear una sesión de boto3 con las credenciales de AWS
        session = boto3.Session(
            aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
            aws_secret_access_key=AWS_SERVER_SECRET_KEY,
        )

        # Obtener el recurso de S3
        s3 = session.resource('s3')

        # Especificar el bucket y los archivos que deseas leer
        bucket_name = 'proyectotfm'
        archivos_a_procesar = [
            {"key": "caracteristicas_palas_padel.json", "output": "caracteristicas_palas_padel.csv"},
            {"key": "formulario_combinaciones.json", "output": "formulario_combinaciones.csv"}
        ]

        for archivo in archivos_a_procesar:
            file_key = archivo["key"]
            output_file = archivo["output"]

            # Descargar el archivo desde S3
            obj = s3.Object(bucket_name=bucket_name, key=file_key)
            response = obj.get()
            data = response['Body'].read().decode('utf-8')

            # Cargar el contenido JSON en un diccionario de Python
            json_data = json.loads(data)

            # Convertir el diccionario a un DataFrame de pandas
            df = pd.DataFrame(json_data)

            # Guardar el DataFrame como un archivo CSV localmente
            df.to_csv(output_file, index=False)

            print(f"Archivo CSV creado exitosamente: {output_file}")

    except Exception as e:
        print(f"Error al procesar los archivos desde S3: {e}")


#DICCIONARIOS

# Diccionario de mapeo para convertir valores numéricos a etiquetas descriptivas

LABEL_MAPPING = {
    "Balance": {"No data": 0, "bajo": 1, "medio": 2, "alto": 3},
    "Nucleo": {"No data": 0, "foam": 1, "medium eva": 2, "hard eva": 3, "soft eva": 4},
    "Cara": {"No data": 0, "fibra de vidrio": 1, "mix": 2, "fibra de carbono": 3},
    "Dureza": {"No data": 0, "blanda": 1, "media": 2, "dura": 3},
    "Nivel de Juego": {"No data": 0, "principiante": 1, "avanzado": 2, "pro": 3},
    "Forma": {"No data": 0, "redonda": 1, "lágrima": 2, "diamante": 3},
    "Superficie": {"No data": 0, "lisa": 1, "rugosa": 2},
    "Tipo de Juego": {"No data": 0, "control": 1, "polivalente": 2, "potencia": 3},
}


LABEL_MAPPING_INVERTIDO = {
    "Balance": {0: "No data", 1: "bajo", 2: "medio", 3: "alto"},
    "Nucleo": {0: "No data", 1: "foam", 2: "medium eva", 3: "hard eva", 4: "soft eva"},
    "Cara": {0: "No data", 1: "fibra de vidrio", 2: "mix", 3: "fibra de carbono"},
    "Dureza": {0: "No data", 1: "blanda", 2: "media", 3: "dura"},
    "Nivel de Juego": {0: "No data", 1: "principiante", 2: "avanzado", 3: "pro"},
    "Forma": {0: "No data", 1: "redonda", 2: "lágrima", 3: "diamante"},
    "Superficie": {0: "No data", 1: "lisa", 2: "rugosa"},
    "Tipo de Juego": {0: "No data", 1: "control", 2: "polivalente", 3: "potencia"},
}


# Diccionario de mapeo para convertir valores numéricos a etiquetas descriptivas

LABEL_MAPPING_TIPO_DE_JUEGO = {0: "No Related", 1: "Control", 2: "Polivalente", 3: "Potencia"}

#Diccionario con las opciones y valores asociados de los selectbox  del formulario

OPCIONES_SELECTBOX_FORMULARIO = {
    "opciones_peso":{"Entre 51 y 70 Kg": 0, "Entre 71 y 90 Kg": 0, "Más de 91 Kg": 0.5},
    "opciones_altura": {"Entre 1,51 y 1,70 metros": 0, "Entre 1,71 y 1,80 metros": 0, "Mas de 1,80 metros": 0.5},
    "opciones_sexo": {"Mujer": 0, "Hombre":0},
    "opciones_nivel_de_juego":{"Iniciacion": 0, "Intermedio": 1, "Avanzado": 2},
    "opciones_tipo_de_juego": {"Ofensivo": 1, "Defensivo": 0},
    "opciones_tipo_de_balance": {"Medio": 0, "Alto": 0.5},
    "opciones_horas_semana":{"Menos de 3,5 horas": 0, "Mas de 3.5 horas": 0.5},
    "opciones_rango_precios": {"Menos de 100": 0, "Entre 100 y 200": 0, "Mas de 200": 0},
    "opciones_lado_de_juego": {"Drive": 0, "Reves": 0.5},
    "opciones_lesiones_antiguas":{"Lumbares": 0.5,"Epicondilitis": 0.15,"Gemelos o fascitis": 0.5,"Cervicales": 0.25,"Hombros": 0.5,"Ninguna": 0},
    "opciones_frecuencia_lesion": {"Siempre que juego defensivamente": 0.5,"Siempre que juego ofensivamente": 0.5,"Casi siempre que juego intensamente": 0.25,"Rara vez cuando juego": 0.15},
    "opciones_cuanto_lesion": {"Menos de 3 meses": 0.5,"Entre 3 y 6 meses": 0.25,"Mas de 6 meses": 0.15}
}

#Diccionario para la division de las Palas por precio (Aplicable division al clickar checkbox)
PRECIO_MAXIMO_MAP= {"Menos de 100": 100,"Entre 100 y 200 ": 200,"Mas de 200 ": float('inf')}

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#ALGORITMO KNN

def preprocesar_datos(df_palas, knn_features):
    """
    Preprocesa el dataframe imputando valores faltantes y asegurando compatibilidad de tipos.
    """
    # Manejar valores NaN imputando con la media
    imputer = SimpleImputer(strategy='mean')
    df_palas[knn_features] = imputer.fit_transform(df_palas[knn_features])
    return df_palas

def agregar_score_escalar(df_palas):
    """
    Calcula y agrega la columna 'Score_Escalar_Lesion_Nivel' al dataframe.
    """
    df_palas['Score_Escalar_Lesion_Nivel'] = (
        (df_palas['score_lesion_ajustado']**2 + df_palas['score_nivel_ajustado']**2)**0.5
    )
    return df_palas

def mapear_valores(palas_recomendadas, label_mapping):
    """
    Mapea valores numéricos a etiquetas descriptivas utilizando un diccionario de mapeo.
    """
    for col in label_mapping.keys():
        if col in palas_recomendadas.columns:
            palas_recomendadas[col] = palas_recomendadas[col].fillna(0).astype(int)
            palas_recomendadas[col] = palas_recomendadas[col].map(label_mapping[col])
    return palas_recomendadas

def ajustar_tipos(palas_recomendadas):
    """
    Asegura que todas las columnas tengan tipos de datos compatibles.
    """
    for col in palas_recomendadas.columns:
        if palas_recomendadas[col].dtype == 'object':
            palas_recomendadas[col] = palas_recomendadas[col].astype(str)
        elif palas_recomendadas[col].dtype == 'float64':
            palas_recomendadas[col] = palas_recomendadas[col].astype(float)
        elif palas_recomendadas[col].dtype == 'int64':
            palas_recomendadas[col] = palas_recomendadas[col].astype(int)
    return palas_recomendadas


def mapear_valores(df, label_mapping):
    """
    Mapea valores numéricos a etiquetas descriptivas según un diccionario de mapeo.

    Args:
        df (DataFrame): DataFrame con los datos a mapear.
        label_mapping (dict): Diccionario con el mapeo de valores.

    Returns:
        DataFrame: DataFrame con los valores mapeados.
    """
    for column, mapping in label_mapping.items():
        if column in df.columns:
            df[column] = df[column].map(mapping)
    return df

# Función para analizar la relación entre Score y palas recomendadas
def analizar_relacion_score(df_palas, palas_recomendadas):
    st.subheader("Pala Recomendada Evitar Lesión (Tipo de Juego)")

    # Depuración: Imprimir columnas disponibles
    print("Columnas disponibles en df_palas:", df_palas.columns)
    print("Primeras filas de df_palas:")
    print(df_palas.head())

    print("Columnas disponibles en palas_recomendadas:", palas_recomendadas.columns)
    print("Primeras filas de palas_recomendadas:")
    print(palas_recomendadas.head())

    # Validar columnas necesarias en df_palas
    required_columns = ['score_lesion_ajustado', 'score_nivel_ajustado', 'Tipo de Juego', 'Score_Escalar_Lesion_Nivel']
    for col in required_columns:
        if col not in df_palas.columns:
            raise ValueError(f"La columna '{col}' no está presente en el DataFrame df_palas.")

    # Asegurar que palas_recomendadas tenga las columnas necesarias
    if not palas_recomendadas.empty:
        if 'Score_Escalar_Lesion_Nivel' not in palas_recomendadas.columns:
            print("Copiando columnas faltantes desde df_palas a palas_recomendadas.")
            palas_recomendadas = palas_recomendadas.merge(
                df_palas[['Score_Escalar_Lesion_Nivel']],
                left_index=True,
                right_index=True,
                how='left'
            )

    # Mapear los valores numéricos de "Tipo de Juego" a etiquetas descriptivas
    if "Tipo de Juego" in df_palas.columns:
        df_palas["Tipo de Juego Descriptivo"] = df_palas["Tipo de Juego"].map(LABEL_MAPPING_TIPO_DE_JUEGO)
    else:
        st.error("La columna 'Tipo de Juego' no existe en el DataFrame.")
        return

    # Crear checkboxes para seleccionar qué tipos de juego mostrar
    categorias_unicas = df_palas["Tipo de Juego Descriptivo"].unique()
    
    col1, col2, col3, col4 = st.columns(len(categorias_unicas))
    seleccionados = {}
    
    for i, categoria in enumerate(categorias_unicas):
        with [col1, col2, col3, col4][i]:
            seleccionados[categoria] = st.checkbox(categoria, value=(categoria == "Polivalente"))
    
    categorias_seleccionadas = [categoria for categoria, mostrar in seleccionados.items() if mostrar]
    df_filtrado = df_palas[df_palas["Tipo de Juego Descriptivo"].isin(categorias_seleccionadas)]
    
    if df_filtrado.empty:
        st.warning("No hay datos para las categorías seleccionadas.")
        return

    print("Primeras filas del DataFrame filtrado:")
    print(df_filtrado.head())

    # Crear gráfico interactivo en 2D con plotly (scatter plot)
    fig = px.scatter(
        df_filtrado,
        x="score_lesion_ajustado",
        y="score_nivel_ajustado",
        color="Tipo de Juego Descriptivo",
        hover_data=["Palas", "Precio", "Balance"],
        title="Pala Recomendada Evitar Lesión (Tipo de Juego)"
    )
    
    # Filtrar las palas recomendadas por Score_Escalar_Lesion_Nivel
    if not palas_recomendadas.empty:
        threshold = st.slider("Umbral para Score_Escalar_Lesion_Nivel", min_value=0.0, max_value=1.0, value=0.5)
        recomendadas_filtradas = palas_recomendadas[palas_recomendadas['Score_Escalar_Lesion_Nivel'] >= threshold]

        # Añadir puntos rojos para las palas recomendadas filtradas
        fig.add_scatter(
            x=recomendadas_filtradas["score_lesion_ajustado"],
            y=recomendadas_filtradas["score_nivel_ajustado"],
            mode='markers',
            marker=dict(color='red', size=12, symbol='circle'),
            name='Palas Recomendadas'
        )
    
    # Ajustar diseño del gráfico
    fig.update_layout(
        xaxis_title="Lesión (%)",
        yaxis_title="Nivel (%)",
        margin=dict(l=40, r=40, t=40, b=40),  # Márgenes ajustados
        height=600  # Altura del gráfico
    )
    
    st.plotly_chart(fig)


def encontrar_vecinos_mas_cercanos_knn(df_palas, x_random, y_random, considerar_precio=False, precio_maximo=None):
    """
    Encuentra las 3 palas más cercanas según las características especificadas.

    Args:
        df_palas (DataFrame): DataFrame con los datos de las palas.
        x_random (float): Coordenada X del punto de referencia.
        y_random (float): Coordenada Y del punto de referencia.
        considerar_precio (bool): Si se debe considerar el precio en la búsqueda.
        precio_maximo (float): Precio máximo a considerar (si considerar_precio es True).

    Returns:
        DataFrame: DataFrame con las palas recomendadas.
    """
    try:
        # Calcular Score_Escalar_Lesion_Nivel para las palas
        df_palas['Score_Escalar_Lesion_Nivel'] = (
            (df_palas['score_lesion_ajustado']**2 + df_palas['score_nivel_ajustado']**2)**0.5
        )

        # Filtrar por precio si es necesario
        if considerar_precio and precio_maximo is not None:
            df_palas = df_palas[df_palas['Precio'] <= precio_maximo]

        # Verificar si hay suficientes datos para KNN
        if len(df_palas) < 3:
            raise ValueError("No hay suficientes palas para realizar la recomendación con KNN.")

        # Configurar y entrenar el modelo KNN
        knn_features = ['Score_Escalar_Lesion_Nivel']
        knn = NearestNeighbors(n_neighbors=3)
        knn.fit(df_palas[knn_features])

        # Crear el punto de referencia
        z_random = (x_random**2 + y_random**2)**0.5
        reference_point = [[z_random]]

        # Encontrar los vecinos más cercanos
        distances, indices = knn.kneighbors(reference_point)

        # Seleccionar las palas recomendadas
        palas_recomendadas = df_palas.iloc[indices[0]].copy(deep=True)

        return palas_recomendadas[['Palas', 'score_lesion_ajustado', 'score_nivel_ajustado', 'Score_Escalar_Lesion_Nivel', 'Precio']]

    except Exception as e:
        raise ValueError(f"Error en encontrar_vecinos_mas_cercanos_knn: {e}")



#Diccionario para la division de las Palas por precio (Aplicable division al clickar checkbox)
PRECIO_MAXIMO_MAP= {"Menos de 100": 100,"Entre 100 y 200 ": 200,"Mas de 200 ": float('inf')}

#PONDERACIONES

"""
Ponderaciones para Formulario(Ponderacion para lesion y para nivel )

A la hora de ponderar el formulario del usuario se hace una distincion para la eleccion de la pala teniendo en cuenta:
- Lesion : Hace referencia a la ponderacion de las respuestas del formulario del usuario que tienen relacion directa con un factor lesivo
- Nivel : Hace referencia a la ponderacion de las respuestas del formulario del usuario que tienen relacion directa con el nivel del usuario

"""

ponderaciones_lesion = {
    'Cuantas horas juega a la semana': {1: 0, 0: 0.5},
    'Indique su peso': {0: 0, 1: 0, 2: 0.5},
    'Indique su sexo': {0: 0, 1: 0.5},
    'Indique su altura': {0: 0, 1: 0, 2: 0.5},
    'Rango de precio dispuesto a pagar': {2: 0, 0: 0, 1: 0},
    'Indique su lado de juego': {0: 0, 1: 0.5},
    'Indique su nivel de juego': {1: 0, 2: 1, 0: 2},
    'Tipo de juego': {1: 0.5, 0: 0},
    'Que tipo de balance te gusta': {1: 0, 0: 0.5},
    'Has tenido alguna de las siguientes lesiones previamente lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros': {4: 0.5, 1: 1, 2: 0.5, 0: 1, 3: 1, 5: 0},
    'Con que frecuencia': {2: 0.5, 3: 0.5, 0: 0.25, 1: 0.15},
    'Hace cuanto': {2: 0.5, 0: 0.25, 1: 0.15}
}

ponderaciones_nivel = {
    'Cuantas horas juega a la semana': {1: 0, 0: 1},
    'Indique su peso': {0: 0, 1: 0, 2: 0},
    'Indique su sexo': {0: 0, 1: 0},
    'Indique su altura': {0: 0, 1: 0, 2: 0},
    'Rango de precio dispuesto a pagar': {2: 0, 0: 0, 1: 0},
    'Indique su lado de juego': {0: 0, 1: 0.5},
    'Indique su nivel de juego': {1: 0, 2: 1, 0: 2},
    'Tipo de juego': {1: 0.5, 0: 0},
    'Que tipo de balance te gusta': {1: 0, 0: 0.5},
    'Has tenido alguna de las siguientes lesiones previamente lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros': {4: 0, 1: 0, 2: 0, 0: 0, 3: 0, 5: 0},
    'Con que frecuencia': {2: 0, 3: 0, 0: 0, 1: 0},
    'Hace cuanto': {2: 0, 0: 0, 1: 0}
}



#Ponderaciones para Palas(Ponderacion para lesion y para nivel )

#PESOS(LESION Y NIVEL)

"""
Pesos de lesión para cada columna
peso_lesion (dict): Diccionario con los pesos de lesión para cada columna.

"""
PESO_LESION = {"Balance": 1.5,"Nucleo": 1.5,"Cara": 1.2,"Dureza": 1.5,"Nivel de Juego": 1,"Forma": 1,"Superficie": 1,"Tipo de Juego": 1.5}

"""
Pesos de nivel para cada columna
# peso_nivel (dict): Diccionario con los pesos de nivel para cada columna.

"""
PESO_NIVEL = {"Balance": 1.5,"Nucleo": 1.2,"Cara": 1.0,"Dureza": 1.2,"Nivel de Juego": 2.0,"Forma": 1.5,"Superficie": 1.2,"Tipo de Juego": 1.5}


#SCORES(LESION Y NIVEL)

"""
# Scores de lesión para cada variable en cada columna
#score_lesion (dict): Diccionario con los scores de lesión para cada variable de cada columna.
"""

SCORE_LESION = {
    "Balance": {0: 0, 1: 0 , 2: 0.25, 3: 0.5},
    "Nucleo": {0: 0, 1: 0, 2: 0.5, 3: 1, 4: 0.25},
    "Cara": {0: 0, 1: 0, 2: 0.25, 3: 0.5},
    "Dureza": {0: 0, 1: 0, 2: 0.5, 3: 0.75},
    "Nivel de Juego": {0: 0, 1: 0, 2: 0, 3: 0},
    "Forma": {0: 0, 1: 0, 2: 0.25, 3: 0.5},
    "Superficie": {0: 0, 1: 0, 2: 0},
    "Tipo de Juego": {0: 0, 1: 0, 2: 0.25, 3: 0.5},
}

"""
# Scores de nivel para cada variable en cada columna
# score_nivel (dict): Diccionario con los scores de nivel para cada variable de cada columna.
"""

SCORE_NIVEL = {
    "Balance": {0: 0, 1: 0 , 2: 0.25, 3: 0.5},
    "Nucleo": {0: 0, 1: 0, 2: 0, 3: 0 , 4: 0},
    "Cara": {0: 0, 1: 0, 2: 0, 3: 0},
    "Dureza": {0: 0, 1: 0, 2: 0.5, 3: 0.75},
    "Nivel de Juego": {0: 0, 1: 0, 2: 0.5, 3: 0.75},
    "Forma": {0: 0, 1: 0, 2: 0, 3: 0.25},
    "Superficie": {0: 0, 1: 0, 2: 0.25},
    "Tipo de Juego": {0: 0, 1: 0, 2: 0.10, 3: 0.30},
}

