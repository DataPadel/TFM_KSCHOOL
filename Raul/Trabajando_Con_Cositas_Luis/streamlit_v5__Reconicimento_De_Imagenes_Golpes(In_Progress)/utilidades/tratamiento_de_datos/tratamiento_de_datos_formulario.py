import os
import pandas as pd
import streamlit as st
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from utilidades.utilidades import ponderaciones_lesion, ponderaciones_nivel

# Variables globales
df_transformado = None
mapeos_generados = None
df_scored_lesion = None
df_scored_nivel = None
df_scaled_formularios = None

#LABEL ENCODING(FORMULARIO CSV)

def procesar_datos_formulario_csv():
    """
    Procesa un archivo CSV aplicando LabelEncoder a columnas categóricas.

    Modifica:
        df_transformado (global): DataFrame transformado con LabelEncoder.
        mapeos_generados (global): Diccionario de mapeos originales -> codificados.
    """
    global df_transformado, mapeos_generados

    # Ruta del archivo CSV
    csv_file_path = 'formulario_combinaciones.csv'
    try:
        # Obtener la ruta completa del archivo CSV
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, '../../formulario_combinaciones.csv')
        print("Ruta completa:", csv_file_path)
        print("¿Archivo encontrado?:", os.path.exists(csv_file_path))

        # Leer el archivo CSV
        df = pd.read_csv(csv_file_path)
        df_label = df.copy()

        # Definir las columnas categóricas a transformar
        columnas_categoricas = [
            'Cuantas horas juega a la semana', 'Indique su peso', 'Indique su sexo',
            'Indique su altura', 'Rango de precio dispuesto a pagar', 'Indique su lado de juego',
            'Indique su nivel de juego', 'Tipo de juego', 'Que tipo de balance te gusta',
            'Has tenido alguna de las siguientes lesiones previamente lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros',
            'Con que frecuencia', 'Hace cuanto'
        ]

        # Inicializar el diccionario para almacenar los mapeos
        mapeos_generados = {}
        labelencoder = LabelEncoder()

        # Aplicar LabelEncoder a cada columna categórica
        for columna in columnas_categoricas:
            if columna in df_label.columns:
                # Aplicar LabelEncoder y almacenar el mapeo
                df_label[columna] = labelencoder.fit_transform(df_label[columna].astype(str))
                mapeos_generados[columna] = dict(zip(range(len(labelencoder.classes_)), labelencoder.classes_))

        # Guardar el DataFrame transformado en la variable global
        df_transformado = df_label
        print("Label encoding aplicado correctamente.")

        # Crear un diccionario adicional para mapear valores codificados a originales
        mapeos_invertidos = {}
        for columna in columnas_categoricas:
            if columna in df.columns:
                categorias_originales = df[columna].astype(str)  # Asegurarse de que sean cadenas
                categorias_codificadas = df_label[columna]
                mapeo_invertido = dict(zip(categorias_codificadas, categorias_originales))
                mapeos_invertidos[columna] = mapeo_invertido

                # Mostrar el mapeo invertido por consola
                print(f"Columna: {columna}")
                print(mapeo_invertido)

    except FileNotFoundError:
        print(f"Error: El archivo '{csv_file_path}' no se encontró.")
    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")



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
    Calcula los scores totales y escalados, guarda el resultado en un archivo CSV,
    y devuelve el último registro procesado.

    Args:
        output_file (str): Nombre del archivo CSV donde se guardará el resultado.

    Returns:
        dict: Diccionario con los valores del último registro procesado (Score_Lesion y Score_Nivel).
    """
    global df_scored_lesion, df_scored_nivel

    # Validar que los DataFrames existen y son válidos
    if df_scored_lesion is None or df_scored_nivel is None:
        raise ValueError("Los DataFrames proporcionados son inválidos o no están definidos.")

    # Definir las fórmulas específicas para cada DataFrame
    formulas = {
        'df_scored_lesion': lambda df: 1 - df.sum(axis=1),
        'df_scored_nivel': lambda df: df.sum(axis=1)
    }

    # Procesar cada DataFrame con su fórmula correspondiente
    for df_name, df, score_formula in [
        ('df_scored_lesion', df_scored_lesion, formulas['df_scored_lesion']),
        ('df_scored_nivel', df_scored_nivel, formulas['df_scored_nivel'])
    ]:
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError(f"El DataFrame '{df_name}' está vacío o no es válido.")

        # Convertir todas las columnas a tipo float, ignorando errores
        try:
            df[:] = df.apply(pd.to_numeric, errors='coerce')  # Convertir todo a numérico
            df.fillna(0, inplace=True)  # Reemplazar NaN con 0
        except Exception as e:
            raise ValueError(f"Error al convertir las columnas a numéricas en '{df_name}': {e}")

        # Calcular el score total usando la fórmula específica
        try:
            df['Score'] = score_formula(df)
        except Exception as e:
            raise ValueError(f"Error al calcular la columna 'Score' en '{df_name}': {e}")

        # Validar que la columna 'Score' no tiene valores nulos
        if df['Score'].isnull().any():
            raise ValueError(f"La columna 'Score' en '{df_name}' contiene valores nulos.")

    # Escalar los scores
    scaler = MinMaxScaler(feature_range=(0, 1))
    try:
        df_scored_lesion['Score_Escalar'] = scaler.fit_transform(df_scored_lesion[['Score']])
        df_scored_nivel['Score_Escalar'] = scaler.fit_transform(df_scored_nivel[['Score']])
    except Exception as e:
        raise ValueError(f"Error al escalar los scores: {e}")

    # Crear un nuevo DataFrame para guardar
    try:
        df_scaled_formularios = pd.DataFrame({
            'Score_Lesion': df_scored_lesion['Score_Escalar'],
            'Score_Nivel': df_scored_nivel['Score_Escalar']
        })
    except KeyError as e:
        raise KeyError(f"Error al crear el DataFrame final: {e}")

    # Guardar en archivo CSV
    try:
        df_scaled_formularios.to_csv(output_file, index=False)
        print(f"Archivo '{output_file}' guardado correctamente.")
    except Exception as e:
        raise IOError(f"Error al guardar el archivo: {e}")

    # Devolver el último registro procesado
    ultimo_registro = {
        'Score_Lesion': df_scored_lesion.iloc[-1]['Score_Escalar'],
        'Score_Nivel': df_scored_nivel.iloc[-1]['Score_Escalar']
    }
    
    print("Primeros resultados de df_scored_lesion : Score y Score_Escalar")
    print(df_scored_lesion[['Score', 'Score_Escalar']].head())
    print("Primeros resultados de df_scored_nivel : Score y Score_Escalar")
    print(df_scored_nivel[['Score', 'Score_Escalar']].head())
    print("ultimo_registro ",ultimo_registro)

    return ultimo_registro


def regresion_a_la_media_formulario():
    """
    Aplica una regresión a la media a las columnas 'Score_Escalar' de los DataFrames globales
    df_scored_nivel y df_scored_lesion según las siguientes reglas:
    - Valores >= 0.8 y <= 1: Se convierten en 0.8.
    - Valores >= 0.7 y < 0.8: Se reducen un 40%.
    - Valores >= 0.6 y < 0.7: Se reducen un 20%.
    - Valores >= 0.0 y <= 0.2: Se convierten en 0.2.
    - Valores > 0.2 y <= 0.3: Se reducen un 40%.
    - Valores > 0.3 y <= 0.4: Se reducen un 20%.

    Otros valores permanecen iguales.
    """
    global df_scored_nivel, df_scored_lesion, df_scaled_formularios

    def ajustar_valor(valor):
        # Reglas superiores
        if 0.9 <= valor <= 1:
            return 0.9
        elif 0.7 <= valor < 0.9:
            return valor * 0.8
        elif 0.6 <= valor < 0.7:
            return valor * 0.9

        # Reglas inferiores
        elif 0.0 <= valor <= 0.1:
            return 0.1
        elif 0.1 < valor <= 0.3:
            return valor * 1.2
        elif 0.3 < valor <= 0.4:
            return valor * 1.1

        # Otros valores permanecen iguales
        else:
            return valor

    # Aplicar la función de ajuste a las columnas 'Score_Escalar'
    df_scored_nivel['Score_Escalar_Ajustado'] = df_scored_nivel['Score_Escalar'].apply(ajustar_valor)
    df_scored_lesion['Score_Escalar_Ajustado'] = df_scored_lesion['Score_Escalar'].apply(ajustar_valor)

    # Crear el DataFrame final con los valores ajustados
    df_scaled_formularios = pd.DataFrame({
        'Score_Lesion': df_scored_lesion['Score_Escalar_Ajustado'],
        'Score_Nivel': df_scored_nivel['Score_Escalar_Ajustado']
    })

   # Leer el archivo formulario_combinaciones.csv
    try:
        df = pd.read_csv('formulario_combinaciones.csv')
    except FileNotFoundError:
        raise FileNotFoundError("Regresion A La Media Formulario (Funcion). El archivo 'formulario_combinaciones.csv' no se encuentra en el directorio actual.")

    # Asignar directamente los valores ajustados a las columnas finales requeridas
    try:
        df['Score_Escalar_Lesion'] = df_scored_lesion['Score_Escalar_Ajustado'].values
        df['Score_Escalar_Nivel'] = df_scored_nivel['Score_Escalar_Ajustado'].values
    except ValueError as e:
        raise ValueError(f"Error al asignar valores ajustados: {e}")

    # Guardar el resultado en un nuevo archivo CSV
    output_file = 'df_scaled_formularios_3.0.csv'
    try:
        df.to_csv(output_file, index=False)
        print(f"Regresion A La Media Formulario(Funcion). Archivo guardado correctamente como '{output_file}'.")
    except Exception as e:
        raise IOError(f"Regresion A La Media Formulario(Funcion). Error al guardar el archivo '{output_file}': {e}")

      # Guardar el DataFrame ajustado en session_state
    st.session_state["df_scaled_formularios"] = df_scaled_formularios
    return df_scaled_formularios









