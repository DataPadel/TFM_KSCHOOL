import os
import pandas as pd
import streamlit as st
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from utilidades.utilidades import ponderaciones_lesion, ponderaciones_nivel

if "df_transformado" not in st.session_state:
    st.session_state["df_transformado"] = None

if "mapeos_generados" not in st.session_state:
    st.session_state["mapeos_generados"] = None

if "df_scored_lesion" not in st.session_state:
    st.session_state["df_scored_lesion"] = None

if "df_scored_nivel" not in st.session_state:
    st.session_state["df_scored_nivel"] = None

if "df_scaled_formularios" not in st.session_state:
    st.session_state["df_scaled_formularios"] = None

#--------------------------------------------------------------

#LABEL ENCODING(FORMULARIO CSV)
def procesar_datos_formulario_csv():
    """
    Procesa un archivo CSV aplicando LabelEncoder a columnas categóricas.

    Modifica:
        - st.session_state["df_transformado"]: DataFrame transformado con LabelEncoder.
        - st.session_state["mapeos_generados"]: Diccionario de mapeos originales -> codificados.
    """
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

        # Guardar el DataFrame transformado y los mapeos en session_state
        st.session_state["df_transformado"] = df_label
        st.session_state["mapeos_generados"] = mapeos_generados

        print("Df_transformado", st.session_state["df_transformado"].head())
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

#--------------------------------------------------------------

def crear_dataframes_con_scores():
    """
    Crea dos DataFrames con scores personalizados para lesiones y nivel.

    Modifica:
        - st.session_state["df_scored_lesion"]: DataFrame con scores de lesiones.
        - st.session_state["df_scored_nivel"]: DataFrame con scores de nivel.
    """
    # Acceder al DataFrame transformado desde session_state
    df_transformado = st.session_state.get("df_transformado")

    if df_transformado is None or df_transformado.empty:
        raise ValueError("El DataFrame transformado está vacío o no definido.")

    # Crear copias del DataFrame transformado
    df_scored_lesion = df_transformado.copy()
    df_scored_nivel = df_transformado.copy()

    # Aplicar ponderaciones para lesiones
    for columna, ponderacion in ponderaciones_lesion.items():
        if columna in df_scored_lesion.columns:
            df_scored_lesion[columna] = df_scored_lesion[columna].map(ponderacion).fillna(0)

    # Aplicar ponderaciones para nivel
    for columna, ponderacion in ponderaciones_nivel.items():
        if columna in df_scored_nivel.columns:
            df_scored_nivel[columna] = df_scored_nivel[columna].map(ponderacion).fillna(0)

    # Calcular la columna 'Score' como la suma de todas las columnas
    df_scored_lesion['Score'] = df_scored_lesion.sum(axis=1)
    df_scored_nivel['Score'] = df_scored_nivel.sum(axis=1)

    # Guardar los DataFrames en session_state
    st.session_state["df_scored_lesion"] = df_scored_lesion
    
    st.session_state["df_scored_nivel"] = df_scored_nivel

    print("DataFrames con scores generados correctamente.")


#--------------------------------------------------------------

def procesar_scores_y_guardar(output_file='df_scaled_formularios.csv'):
    """
    Calcula los scores totales y escalados, guarda el resultado en un archivo CSV,
    y devuelve el último registro procesado.
    """
    # Acceder a los DataFrames desde session_state
    df_scored_lesion = st.session_state.get("df_scored_lesion")
    
    df_scored_nivel = st.session_state.get("df_scored_nivel")

    if df_scored_lesion is None or df_scored_nivel is None:
        raise ValueError("Los DataFrames proporcionados son inválidos o no están definidos.")

    # Escalar los scores y crear un nuevo DataFrame
    scaler = MinMaxScaler(feature_range=(0, 1))
    try:
        st.session_state["df_scored_lesion"]['Score_Escalar'] = scaler.fit_transform(df_scored_lesion[['Score']])
        
        st.session_state["df_scored_nivel"]['Score_Escalar'] = scaler.fit_transform(df_scored_nivel[['Score']])
        
        st.session_state["df_scaled_formularios"] = pd.DataFrame({
            'Score_Lesion': st.session_state["df_scored_lesion"]['Score_Escalar'],
            'Score_Nivel': st.session_state["df_scored_nivel"]['Score_Escalar']
        })
        
        # Guardar en archivo CSV
        output_path = os.path.join(os.getcwd(), output_file)
        st.session_state["df_scaled_formularios"].to_csv(output_path, index=False)
        print(f"Archivo '{output_path}' guardado correctamente.")
    
    except Exception as e:
        raise IOError(f"Error al guardar el archivo '{output_file}': {e}")

    return {
        'Score_Lesion': st.session_state["df_scaled_formularios"]['Score_Lesion'].iloc[-1],
        'Score_Nivel': st.session_state["df_scaled_formularios"]['Score_Nivel'].iloc[-1]
    }


#--------------------------------------------------------------

def regresion_a_la_media_formulario():
    """
    Aplica una regresión a la media a las columnas 'Score_Escalar' de los DataFrames almacenados en session_state:
    - 'df_scored_nivel'
    - 'df_scored_lesion'

    Las reglas son:
    - Valores >= 0.9 y <= 1: Se convierten en 0.9.
    - Valores >= 0.7 y < 0.9: Se reducen un 20%.
    - Valores >= 0.6 y < 0.7: Se reducen un 10%.
    - Valores >= 0.0 y <= 0.1: Se convierten en 0.1.
    - Valores > 0.1 y <= 0.3: Se aumentan un 20%.
    - Valores > 0.3 y <= 0.4: Se aumentan un 10%.

    Otros valores permanecen iguales.

    Returns:
        pd.DataFrame: DataFrame con los valores ajustados.
    """
    # Acceder a los DataFrames desde session_state
    df_scored_nivel = st.session_state.get("df_scored_nivel")
    df_scored_lesion = st.session_state.get("df_scored_lesion")

    # Validar que los DataFrames existen y son válidos
    if df_scored_nivel is None or df_scored_lesion is None:
        raise ValueError("Los DataFrames proporcionados son inválidos o no están definidos.")

    # Definir la función de ajuste
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










