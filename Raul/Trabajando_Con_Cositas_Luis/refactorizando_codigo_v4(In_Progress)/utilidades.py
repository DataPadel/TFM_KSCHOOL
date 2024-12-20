from sklearn.neighbors import NearestNeighbors


#DESCARGA, CONVERSION Y GENERACION DE ARCHIVOS S3

def descargar_generar_archivo_palas_s3():
    """
    Descarga múltiples archivos JSON desde un bucket de Amazon S3, los convierte en DataFrames de pandas
    y los guarda como archivos CSV en el sistema local. Verifica e instala automáticamente las
    librerías necesarias si no están instaladas.

    :return: None
    """
    import importlib.util
    import subprocess
    import sys

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
        # Importar las librerías necesarias después de asegurarse de que están instaladas
        from dotenv import load_dotenv
        import os
        import json
        import pandas as pd
        import boto3

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
    "Balance": {0: "No data", 1: "Bajo", 2: "Medio", 3: "Alto"},
    "Dureza": {0: "No data", 1: "Blanda", 2: "Media", 3: "Dura"},
    "Nivel de Juego": {0: "No Data", 1: "Iniciacion", 2: "Intermedio", 3: "Avanzado"},
    "Forma": {0: "No Data", 1: "Redonda", 2: "Lágrima", 3: "Diamante"},
    "Tipo de Juego": {0: "No Data", 1: "Control", 2: "Polivalente", 3: "Potencia"}
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
    "opciones_balance": {"Medio": 0, "Alto": 0.5},
    "opciones_horas_semana":{"Menos de 3,5 horas": 0, "Mas de 3.5 horas": 0.5},
    "opciones_rango_precio": {"Menos de 100": 0, "Entre 100 y 200": 0, "Mas de 200": 0},
    "opciones_rango_juego": {"Drive": 0, "Reves": 0.5},
    "opciones_lesiones_antiguas":{"Lumbares": 0.5,"Epicondilitis": 0.15,"Gemelos o fascitis": 0.5,"Cervicales": 0.25,"Hombros": 0.5,"Ninguna": 0},
    "opciones_frecuencia_lesion": {"Siempre que juego defensivamente": 0.5,"Siempre que juego ofensivamente": 0.5,"Casi siempre que juego intensamente": 0.25,"Rara vez cuando juego": 0.15},
    "opciones_cuanto_lesion": {"Menos de 3 meses": 0.5,"Entre 3 y 6 meses": 0.25,"Mas de 6 meses": 0.15}
}

#Diccionario para la division de las Palas por precio (Aplicable division al clickar checkbox)
PRECIO_MAXIMO_MAP= {"Menos de 100": 100,"Entre 100 y 200 ": 200,"Mas de 200 ": float('inf')}

#----------------------------------------------------------------------------------------------------------------------------------------------------

#ALGORITMO KNN

# Encontrar vecinos más cercanos con KNN considerando el precio si está seleccionado
def encontrar_vecinos_mas_cercanos_knn(df_palas, x_random, y_random, z_random, considerar_precio, precio_maximo):
    knn_features = ['score_lesion', 'score_nivel', 'Score_Escalar']
    
    if considerar_precio:
        knn_features.append('Precio')
        df_palas = df_palas[df_palas['Precio'] <= precio_maximo]
    
    knn = NearestNeighbors(n_neighbors=3)
    knn.fit(df_palas[knn_features])
    
    reference_point = [[x_random, y_random, z_random] + ([precio_maximo] if considerar_precio else [])]
    
    distances, indices = knn.kneighbors(reference_point)
    
    palas_recomendadas = df_palas.iloc[indices[0]]
    
    # Mapear valores numéricos a etiquetas descriptivas
    palas_recomendadas["Nivel de Juego"] = palas_recomendadas["Nivel de Juego"].map(LABEL_MAPPING["Nivel de Juego"])
    palas_recomendadas["Tipo de Juego"] = palas_recomendadas["Tipo de Juego"].map(LABEL_MAPPING["Tipo de Juego"])
    palas_recomendadas["Balance"] = palas_recomendadas["Balance"].map(LABEL_MAPPING["Balance"])
    
    return palas_recomendadas[['Palas', 'Nivel de Juego', 'Tipo de Juego', 'Balance', 'Precio']]


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


