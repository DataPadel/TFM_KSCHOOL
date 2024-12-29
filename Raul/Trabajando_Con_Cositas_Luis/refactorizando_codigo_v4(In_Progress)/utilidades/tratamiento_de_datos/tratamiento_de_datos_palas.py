import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from utilidades.utilidades import LABEL_MAPPING, PESO_LESION, PESO_NIVEL, SCORE_LESION, SCORE_NIVEL

# Inicializar session_state para almacenar los DataFrames
if "df" not in st.session_state:
    st.session_state["df"] = None
if "df_labelizado" not in st.session_state:
    st.session_state["df_labelizado"] = None
if "df_scaled" not in st.session_state:
    st.session_state["df_scaled"] = None

# Registro global para controlar mensajes únicos
mensajes_mostrados = set()

def mostrar_mensaje(mensaje):
    """Muestra un mensaje solo si no ha sido mostrado antes."""
    if mensaje not in mensajes_mostrados:
        print(mensaje)
        mensajes_mostrados.add(mensaje)

def lectura_tratamiento_datos_palas():
    """
    Lee un archivo CSV, realiza el tratamiento de las columnas y guarda el DataFrame en una variable global.
    """
    global df
    try:
        # Ruta del archivo CSV
        ruta_csv = r'C:\repositorio\TFM_KSCHOOL\Raul\Trabajando_Con_Cositas_Luis\refactorizando_codigo_v4(In_Progress)\PNpalas_DF_2_procesado.csv'
        df = pd.read_csv(ruta_csv)

        # Eliminación de columnas no necesarias
        columnas_a_eliminar = ['Producto', 'Acabado']
        df = df.drop(columnas_a_eliminar, axis=1)

        # Transformaciones de columnas
        df['Precio'] = df['Precio'].apply(limpiar_precio)
        df['Balance'] = df['Balance'].apply(tratar_balance)
        df['Nucleo'] = df['Nucleo'].apply(tratar_nucleo)
        df['Cara'] = df['Cara'].apply(tratar_cara)
        df['Dureza'] = df['Dureza'].apply(tratar_dureza)
        df['Nivel de Juego'] = df['Nivel de Juego'].apply(tratar_nivel_juego)
        df['Tipo de Juego'] = df['Tipo de Juego'].apply(tratar_tipo_juego)
        df['Jugador'] = df['Jugador'].apply(tratar_jugador)

        # Guardar en session_state
        st.session_state["df"] = df
        
        mostrar_mensaje("Carga de Palas/Tratamiento Datos Palas Realizado Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al leer o procesar el archivo CSV: {e}")

# Funciones auxiliares para transformar columnas
def limpiar_precio(precio):
    """Convierte el precio a formato float eliminando símbolos y caracteres innecesarios."""
    return float(precio.replace('€', '').replace(',', '.').strip())

def tratar_balance(balance):
    """Transforma los valores de la columna Balance según las reglas especificadas."""
    if balance in ['medio', 'alto', 'bajo']:
        return balance
    elif 'principiante' in balance or 'intermedio' in balance:
        return 'medio'
    elif 'avanzado' in balance or 'competición' in balance:
        return 'alto'
    else:
        return 'No data'

def tratar_nucleo(nucleo):
    """Transforma los valores de la columna Núcleo según las reglas especificadas."""
    if nucleo in ['soft eva', 'medium eva', 'hard eva', 'foam']:
        return nucleo
    elif any(sub in nucleo for sub in ['ultrasoft eva', 'black eva, soft eva', 'supersoft eva']):
        return 'soft eva'
    elif 'eva, polietileno' in nucleo:
        return 'foam'
    elif 'black eva hr9' in nucleo:
        return 'hard eva'
    elif any(sub in nucleo for sub in ['black eva hr3', 'eva', 'multieva']):
        return 'medium eva'
    else:
        return 'No data'

def tratar_cara(cara):
    """Transforma los valores de la columna Cara según las reglas especificadas."""
    if cara in ['fibra de carbono', 'fibra de vidrio']:
        return cara
    elif any(sub in cara for sub in ['carbono 12k, fibra de vidrio', 
                                     'fibra de vidrio, carbono 15k',
                                     'carbono, fibra de vidrio']):
        return 'mix'
    else:
        return 'No data'

def tratar_dureza(dureza):
    """Transforma los valores de la columna Dureza según las reglas especificadas."""
    if dureza in ['media', 'blanda', 'dura']:
        return dureza
    elif 'dura, media' in dureza:
        return 'dura'
    elif 'media, blanda' in dureza:
        return 'blanda'
    else:
        return 'No data'

def tratar_nivel_juego(nivel):
    """Transforma los valores de la columna Nivel de Juego según las reglas especificadas."""
    if nivel == 'No data':
        return nivel
    elif 'profesional' in nivel:
        return 'pro'
    elif any(sub in nivel for sub in ['avanzado / competición', 
                                      'avanzado / competición, profesional',
                                      'principiante / intermedio, profesional']):
        return 'avanzado'
    elif 'principiante / intermedio' in nivel:
        return 'principiante'
    else:
        return None

def tratar_tipo_juego(tipo):
    """Transforma los valores de la columna Tipo de Juego según las reglas especificadas."""
    if tipo in ['control', 'polivalente', 'potencia']:
        return tipo
    elif 'control, potencia' in tipo:
        return 'polivalente'
    else:
        return 'No data'

def tratar_jugador(jugador):
    """Transforma los valores de la columna Jugador según las reglas especificadas."""
    if jugador in ['hombre', 'mujer', 'junior']:
        return jugador
    elif 'hombre, mujer' in jugador:
        return 'mixta'
    else:
        return 'No data'

def mostrar_mensaje(mensaje):
    """Muestra un mensaje en consola."""
    print(mensaje)


def labelizar_columnas():

    """Labeliza las columnas del DataFrame según un mapeo especificado."""
    try:
        
        if st.session_state["df"] is None:
            raise ValueError("El DataFrame no ha sido inicializado.")

        # Crear una copia para evitar modificar el original
        df_labelizado = st.session_state["df"].copy()

        # Aplicar mapeo a las columnas según LABEL_MAPPING
        for columna in df_labelizado.columns:
            if columna in LABEL_MAPPING:
                if "No data" not in LABEL_MAPPING[columna]:
                    LABEL_MAPPING[columna]["No data"] = 0
                df_labelizado[columna] = df_labelizado[columna].map(LABEL_MAPPING[columna])
                # Guardar en session_state
                st.session_state["df_labelizado"] = df_labelizado
                mostrar_mensaje("Labelizacion de Columnas de Palas Realizada Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al labelizar las columnas: {e}")

def calcular_scores():

    """Calcula los scores de lesión y nivel para cada fila."""
    try:
        if st.session_state["df_labelizado"] is None:
            raise ValueError("El DataFrame labelizado no ha sido inicializado.")

        # Obtener el DataFrame desde session_state
        df_labelizado = st.session_state["df_labelizado"]
        
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
                # Guardar en session_state
                st.session_state["df_labelizado"] = df_labelizado
                mostrar_mensaje("Calculo de Scores y de Nivel Realizado Correctamente")
        print("Mostrar el dataframe labelizado en palas",df_labelizado)
    except Exception as e:
        raise RuntimeError(f"Error al calcular los scores: {e}")

def escalar_columnas():
    """Escala las columnas seleccionadas usando MinMaxScaler."""
    try:
        if st.session_state["df_labelizado"] is None:
            raise ValueError("El DataFrame labelizado no ha sido inicializado.")

        scaler = MinMaxScaler()
        
        # Escalar columnas específicas
        columnas_a_escalar = ["score_lesion", "score_nivel"]
        
        # Crear una copia escalada del DataFrame
        df_scaled = st.session_state["df_labelizado"].copy()
        
        # Aplicar escalado
        df_scaled[columnas_a_escalar] = scaler.fit_transform(df_scaled[columnas_a_escalar])

        # Guardar en session_state
        st.session_state["df_scaled"] = df_scaled

        mostrar_mensaje("Columnas Escaladas Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al escalar las columnas: {e}")


def regresion_a_la_media_palas():
    """
    Aplica una regresión a la media a las columnas específicas del DataFrame almacenado en `st.session_state["df_scaled"]`.
    Guarda los resultados en un archivo CSV y actualiza el DataFrame en `st.session_state`.
    """
    try:
        # Verificar que el DataFrame escalado esté inicializado en session_state
        if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
            raise ValueError("El DataFrame 'df_scaled' no ha sido inicializado. Asegúrate de completar el preprocesamiento primero.")

        # Obtener el DataFrame desde session_state
        df_scaled = st.session_state["df_scaled"]

        # Definir la función de ajuste
        def ajustar_valor(valor, es_score_nivel):
            """
            Ajusta un valor según las reglas de regresión a la media.
            
            Parámetros:
            - valor: valor numérico a ajustar.
            - es_score_nivel: booleano que indica si se aplican las reglas específicas para `score_nivel`.
            
            Retorna:
            - Valor ajustado.
            """
            if es_score_nivel:
                if 0.0 <= valor <= 0.2:
                    return 0.2
                elif 0.2 < valor <= 0.3:
                    return valor * 1.3
                elif 0.3 < valor <= 0.4:
                    return valor * 1.1
                else:
                    return valor
            else:
                if 0.9 <= valor <= 1:
                    return 0.9
                elif 0.7 <= valor < 0.9:
                    return valor * 0.8
                elif 0.6 <= valor < 0.7:
                    return valor * 0.9
                elif 0.0 <= valor <= 0.2:
                    return 0.2
                elif 0.2 < valor <= 0.3:
                    return valor * 1.3
                elif 0.3 < valor <= 0.4:
                    return valor * 1.1
                else:
                    return valor

        # Aplicar ajustes a las columnas correspondientes
        df_scaled['score_lesion_ajustado'] = df_scaled['score_lesion'].apply(lambda x: ajustar_valor(x, es_score_nivel=False))
        df_scaled['score_nivel_ajustado'] = df_scaled['score_nivel'].apply(lambda x: ajustar_valor(x, es_score_nivel=True))

        # Guardar los resultados en un archivo CSV
        nombre_archivo = 'df_scaled_palas_3.0.csv'
        df_scaled.to_csv(nombre_archivo, index=False)
        print(f"Archivo guardado como '{nombre_archivo}'")

        # Actualizar el DataFrame ajustado en session_state
        st.session_state["df_scaled"] = df_scaled

        print("Este es el dataframe de palas escalado y ajustado:", df_scaled)

    except Exception as e:
        raise RuntimeError(f"Error al aplicar la regresión a la media: {e}")


