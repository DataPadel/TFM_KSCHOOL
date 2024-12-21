import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from utilidades.utilidades import LABEL_MAPPING,PESO_LESION,PESO_NIVEL,SCORE_LESION,SCORE_NIVEL

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from utilidades.utilidades import LABEL_MAPPING, PESO_LESION, PESO_NIVEL, SCORE_LESION, SCORE_NIVEL

# Variables globales para mantener el estado entre funciones
df = None
df_labelizado = None
df_scaled = None

# Registro global para controlar mensajes únicos
mensajes_mostrados = set()

def mostrar_mensaje(mensaje):
    """Muestra un mensaje solo si no ha sido mostrado antes."""
    if mensaje not in mensajes_mostrados:
        print(mensaje)
        mensajes_mostrados.add(mensaje)


def lectura_tratamiento_datos_palas():

    """Lee un archivo CSV, realiza el tratamiento de las columnas y guarda el DataFrame en una variable global."""
    global df  
    try:
        ruta_csv = r'C:\repositorio\TFM_KSCHOOL\Raul\Trabajando_Con_Cositas_Luis\refactorizando_codigo_v4(In_Progress)\palas_procesadas.csv'
        df = pd.read_csv(ruta_csv)

        # Eliminación de columnas con excesiva aparición de "No Data"
        df = df.drop(['Producto', 'Acabado'], axis=1)

        # Tratamiento de columnas específicas
        df['Precio'] = df['Precio'].apply(lambda x: float(x.replace('€', '').replace(',', '.').strip()))
        df['Balance'] = df['Balance'].apply(
            lambda x: x if x in ['medio', 'alto', 'bajo'] else 
            'medio' if 'principiante' in x or 'intermedio' in x else 
            'alto' if 'avanzado' in x or 'competición' in x else 'No data'
        )
        df['Nucleo'] = df['Nucleo'].apply(
            lambda x: x if x in ['soft eva', 'medium eva', 'hard eva', 'foam'] else 
            'soft eva' if any(sub in x for sub in ['ultrasoft eva', 'black eva, soft eva', 'supersoft eva']) else 
            'foam' if 'eva, polietileno' in x else 
            'hard eva' if 'black eva hr9' in x else 
            'medium eva' if any(sub in x for sub in ['black eva hr3', 'eva', 'multieva']) else 'No data'
        )
        df['Cara'] = df['Cara'].apply(
            lambda x: x if x in ['fibra de carbono', 'fibra de vidrio'] else 
            'mix' if any(sub in x for sub in ['carbono 12k, fibra de vidrio', 
                                              'fibra de vidrio, carbono 15k', 
                                              'carbono, fibra de vidrio']) else 'No data'
        )
        df['Dureza'] = df['Dureza'].apply(
            lambda x: x if x in ['media', 'blanda', 'dura'] else 
            'dura' if 'dura, media'in x else 
            'blanda' if 'media, blanda' in x else 'No data'
        )
        mostrar_mensaje("Carga de Palas/Tratamiento Datos Palas Realizado Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al leer o procesar el archivo CSV: {e}")

@st.cache_data
def labelizar_columnas():

    """Labeliza las columnas del DataFrame según un mapeo especificado."""
    global df, df_labelizado  
    try:
        if df is None:
            raise ValueError("El DataFrame no ha sido inicializado.")
        
        # Crear una copia para evitar modificar el original
        df_labelizado = df.copy()

        # Aplicar mapeo a las columnas según LABEL_MAPPING
        for columna in df_labelizado.columns:
            if columna in LABEL_MAPPING:
                if "No data" not in LABEL_MAPPING[columna]:
                    LABEL_MAPPING[columna]["No data"] = 0
                df_labelizado[columna] = df_labelizado[columna].map(LABEL_MAPPING[columna])
                mostrar_mensaje("Labelizacion de Columnas de Palas Realizada Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al labelizar las columnas: {e}")

@st.cache_data
def calcular_scores():

    """Calcula los scores de lesión y nivel para cada fila."""
    global df_labelizado  # Usar la variable global para mantener el estado
    try:
        if df_labelizado is None:
            raise ValueError("El DataFrame labelizado no ha sido inicializado.")
        
        # Inicializar columnas de score en 0
        df_labelizado["score_lesion"] = 0
        df_labelizado["score_nivel"] = 0

        # Calcular scores basados en los mapeos y pesos
        for columna in df_labelizado.columns:
            if columna in PESO_LESION:
                df_labelizado["score_lesion"] += (
                    df_labelizado[columna].map(SCORE_LESION.get(columna, {})) * PESO_LESION[columna]
                )
            if columna in PESO_NIVEL:
                df_labelizado["score_nivel"] += (
                    df_labelizado[columna].map(SCORE_NIVEL.get(columna, {})) * PESO_NIVEL[columna]
                )
                mostrar_mensaje("Calculo de Scores y de Nivel Realizado Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al calcular los scores: {e}")

def escalar_columnas():
    """Escala las columnas seleccionadas usando MinMaxScaler."""
    global df_labelizado, df_scaled  
    try:
        if df_labelizado is None:
            raise ValueError("El DataFrame labelizado no ha sido inicializado.")
        
        scaler = MinMaxScaler()
        
        # Escalar columnas específicas
        columnas_a_escalar = ["score_lesion", "score_nivel"]
        df_scaled = df_labelizado.copy()
        df_scaled[columnas_a_escalar] = scaler.fit_transform(df_scaled[columnas_a_escalar])
        mostrar_mensaje("Columnas Escaladas Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al escalar las columnas: {e}")

def generar_graficos():
    """Genera gráficos basados en los datos escalados."""
    global df_scaled  
    try:
        if df_scaled is None:
            raise ValueError("df_scaled no ha sido inicializado.")
        
        # Histograma para score_lesion y score_nivel
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        sns.histplot(df_scaled['score_lesion'], kde=True, color='blue', bins=20)
        plt.title('Histograma de Score de Lesión')
        
        plt.subplot(1, 2, 2)
        sns.histplot(df_scaled['score_nivel'], kde=True, color='green', bins=20)
        plt.title('Histograma de Score de Nivel')

        plt.tight_layout()
        plt.show()

        mostrar_mensaje("Los graficos han sido generados correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al generar gráficos: {e}")
