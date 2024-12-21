import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from utilidades.utilidades import ponderaciones_lesion, ponderaciones_nivel

# Variables globales
df_transformado = None
mapeos_generados = None
df_scored_lesion = None
df_scored_nivel = None

#LABEL ENCODING(FORMULARIO CSV)

def procesar_datos_formulario_csv():
    """
    Procesa un archivo CSV aplicando LabelEncoder a columnas categóricas.

    Modifica:
        df_transformado (global): DataFrame transformado con LabelEncoder.
        mapeos_generados (global): Diccionario de mapeos originales -> codificados.
    """
    global df_transformado, mapeos_generados

    csv_file_path = 'formulario_combinaciones.csv'
    try:
        df = pd.read_csv(csv_file_path)
        df_label = df.copy()

        columnas_categoricas = [
            'Cuantas horas juega a la semana', 'Indique su peso', 'Indique su sexo',
            'Indique su altura', 'Rango de precio dispuesto a pagar', 'Indique su lado de juego',
            'Indique su nivel de juego', 'Tipo de juego', 'Que tipo de balance te gusta',
            'Has tenido alguna de las siguientes lesiones previamente lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros',
            'Con que frecuencia', 'Hace cuanto'
        ]

        mapeos_generados = {}
        labelencoder = LabelEncoder()

        for columna in columnas_categoricas:
            if columna in df_label.columns:
                df_label[columna] = labelencoder.fit_transform(df_label[columna].astype(str))
                mapeos_generados[columna] = dict(zip(range(len(labelencoder.classes_)), labelencoder.classes_))

        df_transformado = df_label
        print("Label encoding aplicado correctamente.")

    except FileNotFoundError:
        print(f"Error: El archivo '{csv_file_path}' no se encontró.")
        df_transformado, mapeos_generados = None, None




def crear_dataframes_con_scores():
    """
    Crea dos DataFrames con scores personalizados para lesiones y nivel.

    Modifica:
        df_scored_lesion (global): DataFrame con scores de lesiones.
        df_scored_nivel (global): DataFrame con scores de nivel.
    """
    global df_transformado, df_scored_lesion, df_scored_nivel

    if df_transformado is None or df_transformado.empty:
        raise ValueError("El DataFrame transformado está vacío o no definido.")

    df_scored_lesion = df_transformado.copy()
    df_scored_nivel = df_transformado.copy()

    for columna, ponderacion in ponderaciones_lesion.items():
        if columna in df_scored_lesion.columns:
            df_scored_lesion[columna] = df_scored_lesion[columna].map(ponderacion)

    for columna, ponderacion in ponderaciones_nivel.items():
        if columna in df_scored_nivel.columns:
            df_scored_nivel[columna] = df_scored_nivel[columna].map(ponderacion)

    print("DataFrames con scores generados correctamente.")



def procesar_scores_y_guardar(output_file='df_scaled_formularios.csv'):
    """
    Calcula los scores totales y escalados, y guarda el resultado en un archivo CSV.

    Args:
        output_file (str): Nombre del archivo CSV donde se guardará el resultado.

    Modifica:
        Guarda un archivo CSV con los resultados escalados.
    """
    global df_scored_lesion, df_scored_nivel

    if df_scored_lesion is None or df_scored_nivel is None:
        raise ValueError("Los DataFrames proporcionados son inválidos.")

    for df in [df_scored_lesion, df_scored_nivel]:
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("Uno o más DataFrames están vacíos o no son válidos.")
        
        # Calcular el score total
        df['Score'] = df.sum(axis=1)

    # Escalar los scores
    scaler = MinMaxScaler(feature_range=(0, 1))
    df_scored_lesion['Score_Escalar'] = scaler.fit_transform(df_scored_lesion[['Score']])
    df_scored_nivel['Score_Escalar'] = scaler.fit_transform(df_scored_nivel[['Score']])

    # Crear un nuevo DataFrame para guardar
    df_scaled_formularios = pd.DataFrame({
        'Score_Lesion': df_scored_lesion['Score_Escalar'],
        'Score_Nivel': df_scored_nivel['Score_Escalar']
    })

    # Guardar en archivo CSV
    try:
        df_scaled_formularios.to_csv(output_file, index=False)
        print(f"Archivo '{output_file}' guardado correctamente.")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")





