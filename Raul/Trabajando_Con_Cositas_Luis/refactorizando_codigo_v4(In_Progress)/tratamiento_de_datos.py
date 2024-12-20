import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler

from utilidades import ponderaciones_lesion, ponderaciones_nivel

#LABEL ENCODING(FORMULARIO CSV)

def procesar_datos_formulario_csv():
    """
    Método para leer el archivo 'formulario_combinaciones.json.csv', aplicar LabelEncoder
    a las columnas categóricas y generar un diccionario con los mapeos originales -> codificados.

    Retorna:
        tuple: (DataFrame transformado, diccionario de mapeos) o (None, None) si ocurre un error.
    """
    # Ruta fija del archivo CSV
    csv_file_path = 'formulario_combinaciones.json.csv'

    try:
        # Leer el archivo CSV y convertirlo en un DataFrame
        df = pd.read_csv(csv_file_path)
        
        # Crear una copia del DataFrame original
        df_label = df.copy()

        # Lista de columnas categóricas
        columnas_categoricas = [
            'Cuantas horas juega a la semana',
            'Indique su peso',
            'Indique su sexo',
            'Indique su altura',
            'Rango de precio dispuesto a pagar',
            'Indique su lado de juego',
            'Indique su nivel de juego',
            'Tipo de juego',
            'Que tipo de balance te gusta',
            'Has tenido alguna de las siguientes lesiones previamente lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros',
            'Con que frecuencia',
            'Hace cuanto'
        ]

        # Diccionario para guardar los mapeos (original -> codificado)
        mapeos = {}

        # Aplicar LabelEncoder a cada columna categórica y generar los mapeos
        labelencoder = LabelEncoder()
        for columna in columnas_categoricas:
            if columna in df_label.columns:  # Verificar si la columna existe en el DataFrame
                # Aplicar LabelEncoder
                df_label[columna] = labelencoder.fit_transform(df_label[columna].astype(str))  # Convertir a string para evitar errores
                
                # Crear el mapeo original -> codificado
                categorias_originales = labelencoder.classes_  # Obtiene las categorías originales ordenadas
                categorias_codificadas = range(len(categorias_originales))  # Rango de valores codificados
                mapeo = dict(zip(categorias_codificadas, categorias_originales))
                
                # Guardar el mapeo en el diccionario
                mapeos[columna] = mapeo

        print("Label encoding aplicado correctamente a las columnas categóricas.")
        
        return df_label, mapeos

    except FileNotFoundError:
        print("Error: El archivo no se encontró.")
        return None, None

# Ejecutar el método
df_transformado,mapeos_generados=procesar_datos_formulario_csv()


def crear_dataframes_con_scores():
    """
    Crea dos nuevos DataFrames a partir de un DataFrame transformado y sus mapeos:
    - Uno con scores personalizados para las lesiones.
    - Otro con scores personalizados para el nivel de juego.

    Returns:
        tuple: (DataFrame con scores de lesiones, DataFrame con scores de nivel de juego)
    """
    # Crear copias del DataFrame original
    df_scored_lesion = df_transformado.copy()
    df_scored_nivel = df_transformado.copy()

    # Reemplazar las categorías por sus scores personalizados en las columnas de lesiones
    for columna, mapeos_generados in ponderaciones_lesion.items():
        if columna in df_scored_lesion.columns:  # Verificar si la columna existe
            df_scored_lesion[columna] = df_scored_lesion[columna].map(mapeos_generados)

    # Reemplazar las categorías por sus scores personalizados en las columnas de nivel
    for columna, mapeos_generados in ponderaciones_nivel.items():
        if columna in df_scored_nivel.columns:  # Verificar si la columna existe
            df_scored_nivel[columna] = df_scored_nivel[columna].map(mapeos_generados)

    print("Generados df_scored_lesion y df_scored_nivel")
    return df_scored_lesion, df_scored_nivel

df_scored_lesion,df_scored_nivel=crear_dataframes_con_scores()

def procesar_scores_y_guardar(output_file='df_scaled_formularios.csv'):
    """
    Calcula los scores totales, los escala, crea un nuevo DataFrame con los resultados
    y guarda el DataFrame final en un archivo CSV.

    Args:
        df_scored_lesion (DataFrame): DataFrame con las columnas ponderadas de lesiones.
        df_scored_nivel (DataFrame): DataFrame con las columnas ponderadas de nivel.
        output_file (str): Nombre del archivo CSV donde se guardará el resultado.

    Returns:
        DataFrame: DataFrame con los scores escalados de lesiones y nivel.
    """
    # Calcular el score total sumando las columnas ponderadas
    df_scored_lesion['Score'] = df_scored_lesion.sum(axis=1)
    df_scored_nivel['Score'] = df_scored_nivel.sum(axis=1)

    # Crear el escalador
    scaler = MinMaxScaler(feature_range=(0, 1))

    # Ajustar y transformar la columna Score
    df_scored_lesion['Score_Escalar'] = scaler.fit_transform(df_scored_lesion[['Score']])
    df_scored_nivel['Score_Escalar'] = scaler.fit_transform(df_scored_nivel[['Score']])

    # Crear un nuevo DataFrame con los scores escalados
    df_scaled_formularios = pd.DataFrame({
        'Score_Lesion': df_scored_lesion['Score_Escalar'],
        'Score_Nivel': df_scored_nivel['Score_Escalar']
    })

    # Guardar el nuevo DataFrame en un archivo CSV
    df_scaled_formularios.to_csv(output_file, index=False)

    # Confirmar que el archivo se ha guardado
    print(f"Archivo '{output_file}' guardado correctamente.")

    return df_scaled_formularios




