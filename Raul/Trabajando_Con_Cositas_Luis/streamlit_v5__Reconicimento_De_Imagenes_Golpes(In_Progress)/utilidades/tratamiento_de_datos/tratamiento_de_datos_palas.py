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

def ejecutar_una_vez(func, estado_key):
    """
    Ejecuta una función solo si no ha sido ejecutada previamente en la sesión.

    Args:
        func (callable): La función a ejecutar.
        estado_key (str): Clave en st.session_state para rastrear si la función ya fue ejecutada.
    """
    if not st.session_state.get(estado_key, False):
        func()
        st.session_state[estado_key] = True
    else:
        print(f"La función '{func.__name__}' ya fue ejecutada previamente.")

def lectura_tratamiento_datos_palas():
    """
    Lee un archivo CSV, realiza el tratamiento de las columnas y guarda el DataFrame en session_state.
    """
    try:
        # Verificar si ya existe "df" en session_state
        if "df" not in st.session_state or st.session_state["df"] is None:
            # Ruta del archivo CSV
            ruta_csv = r'C:\repositorio\TFM_KSCHOOL\Raul\Trabajando_Con_Cositas_Luis\streamlit_v5__Reconicimento_De_Imagenes_Golpes(In_Progress)\PNpalas_DF_3.csv'
            
            # Leer el archivo CSV
            df = pd.read_csv(ruta_csv)

            # Eliminación de columnas no necesarias
            columnas_a_eliminar = ['producto', 'acabado']
            df = df.drop(columnas_a_eliminar, axis=1)

            # Transformaciones de columnas
            df['Precio'] = df['precio'].apply(limpiar_precio)
            df['Balance'] = df['balance'].apply(tratar_balance)
            df['Nucleo'] = df['núcleo'].apply(tratar_nucleo)
            df['Cara'] = df['cara'].apply(tratar_cara)
            df['Dureza'] = df['dureza'].apply(tratar_dureza)
            df['Nivel de Juego'] = df['nivel de juego'].apply(tratar_nivel_juego)
            df['Tipo de Juego'] = df['tipo de juego'].apply(tratar_tipo_juego)
            df['Jugador'] = df['jugador'].apply(tratar_jugador)

            # Guardar el DataFrame procesado en session_state
            st.session_state["df"] = df

            mostrar_mensaje("Carga de Palas/Tratamiento Datos Palas Realizado Correctamente")
        else:
            print("El DataFrame ya estaba inicializado en session_state.")
    except Exception as e:
        raise RuntimeError(f"Error al leer o procesar el archivo CSV: {e}")


def limpiar_precio(precio):
    """Convierte el precio a formato float eliminando símbolos y caracteres innecesarios."""
    try:
        if isinstance(precio, float):  # Si ya es float, devolver directamente
            return precio
        if precio is None:  # Manejar valores nulos
            return None
        precio = str(precio)  # Convertir a cadena si no lo es
        return float(precio.replace('€', '').replace(',', '.').strip())
    except (ValueError, AttributeError):
        return None  # Devolver None si no se puede procesar

def tratar_balance(balance):
    """Transforma los valores de la columna Balance según las reglas especificadas."""
    if balance is None:  # Manejar valores nulos
        return 'No data'
    if balance in ['medio', 'alto', 'bajo']:
        return balance
    if isinstance(balance, str):  # Verificar que sea cadena antes de buscar palabras clave
        if 'principiante' in balance or 'intermedio' in balance:
            return 'medio'
        if 'avanzado' in balance or 'competición' in balance:
            return 'alto'
    return 'No data'

def tratar_nucleo(nucleo):
    """Transforma los valores de la columna Núcleo según las reglas especificadas."""
    if nucleo is None:  # Manejar valores nulos
        return 'No data'
    if nucleo in ['soft eva', 'medium eva', 'hard eva', 'foam']:
        return nucleo
    if isinstance(nucleo, str):  # Verificar que sea cadena antes de buscar palabras clave
        if any(sub in nucleo for sub in ['ultrasoft eva', 'black eva, soft eva', 'supersoft eva']):
            return 'soft eva'
        if 'eva, polietileno' in nucleo:
            return 'foam'
        if 'black eva hr9' in nucleo:
            return 'hard eva'
        if any(sub in nucleo for sub in ['black eva hr3', 'eva', 'multieva']):
            return 'medium eva'
    return 'No data'

def tratar_cara(cara):
    """Transforma los valores de la columna Cara según las reglas especificadas."""
    if cara is None:  # Manejar valores nulos
        return 'No data'
    if cara in ['fibra de carbono', 'fibra de vidrio']:
        return cara
    if isinstance(cara, str):  # Verificar que sea cadena antes de buscar palabras clave
        if any(sub in cara for sub in ['carbono 12k, fibra de vidrio',
                                       'fibra de vidrio, carbono 15k',
                                       'carbono, fibra de vidrio']):
            return 'mix'
    return 'No data'

def tratar_dureza(dureza):
    """Transforma los valores de la columna Dureza según las reglas especificadas."""
    if dureza is None:  # Manejar valores nulos
        return 'No data'
    if dureza in ['media', 'blanda', 'dura']:
        return dureza
    if isinstance(dureza, str):  # Verificar que sea cadena antes de buscar palabras clave
        if 'dura, media' in dureza:
            return 'dura'
        if 'media, blanda' in dureza:
            return 'blanda'
    return 'No data'

def tratar_nivel_juego(nivel):
    """Transforma los valores de la columna Nivel de Juego según las reglas especificadas."""
    if nivel is None:  # Manejar valores nulos
        return None
    if nivel == 'No data':
        return nivel
    if isinstance(nivel, str):  # Verificar que sea cadena antes de buscar palabras clave
        if 'profesional' in nivel:
            return 'pro'
        if any(sub in nivel for sub in ['avanzado / competición',
                                        'avanzado / competición, profesional',
                                        'principiante / intermedio, profesional']):
            return 'avanzado'
        if 'principiante / intermedio' in nivel:
            return 'principiante'
    return None

def tratar_tipo_juego(tipo):
    """Transforma los valores de la columna Tipo de Juego según las reglas especificadas."""
    if tipo is None:  # Manejar valores nulos
        return 'No data'
    if tipo in ['control', 'polivalente', 'potencia']:
        return tipo
    if isinstance(tipo, str):  # Verificar que sea cadena antes de buscar palabras clave
        if 'control, potencia' in tipo:
            return 'polivalente'
    return 'No data'

def tratar_jugador(jugador):
    """Transforma los valores de la columna Jugador según las reglas especificadas."""
    if jugador is None:  # Manejar valores nulos
        return 'No data'
    if jugador in ['hombre', 'mujer', 'junior']:
        return jugador
    if isinstance(jugador, str):  # Verificar que sea cadena antes de buscar palabras clave
        if 'hombre, mujer' in jugador:
            return 'mixta'
    return 'No data'


def mostrar_mensaje(mensaje):
    """Muestra un mensaje en consola."""
    print(mensaje)
    
def ejecutar_una_vez(func, estado_key):
    """
    Ejecuta una función solo si no ha sido ejecutada previamente en la sesión.

    Args:
        func (callable): La función a ejecutar.
        estado_key (str): Clave en st.session_state para rastrear si la función ya fue ejecutada.
    """
    if not st.session_state.get(estado_key, False):
        func()
        st.session_state[estado_key] = True
    else:
        print(f"La función '{func.__name__}' ya fue ejecutada previamente.")
   
def labelizar_columnas():
    """Labeliza las columnas del DataFrame según un mapeo especificado."""
    try:
        # Validar si "df" está disponible en session_state
        if "df" not in st.session_state or st.session_state["df"] is None:
            raise ValueError("El DataFrame no ha sido inicializado en session_state.")

        # Crear una copia para evitar modificar el original
        df_labelizado = st.session_state["df"].copy()
        

        for columna in df_labelizado.columns:
            if columna in LABEL_MAPPING:
                if "No data" not in LABEL_MAPPING[columna]:
                    LABEL_MAPPING[columna]["No data"] = 0

                # Aplicar el mapeo y manejar valores faltantes (NaN)
                df_labelizado[columna] = df_labelizado[columna].map(
                    LABEL_MAPPING[columna]
                ).fillna(0)

        # Guardar el DataFrame procesado en session_state
        st.session_state["df_labelizado"] = df_labelizado
        

        mostrar_mensaje("Labelización de Columnas de Palas Realizada Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al labelizar las columnas: {e}")

def calcular_scores():
    """Calcula los scores de lesión y nivel para cada fila."""
    try:
        if "df_labelizado" not in st.session_state or st.session_state["df_labelizado"] is None:
            raise ValueError("Calcular Scores (Funcion) . El DataFrame labelizado no ha sido inicializado.")

        df_labelizado = st.session_state["df_labelizado"]

        df_labelizado["score_lesion"] = 0
        df_labelizado["score_nivel"] = 0

        for columna in df_labelizado.columns:
            if columna in PESO_LESION:
                df_labelizado["score_lesion"] += (
                    df_labelizado[columna].map(SCORE_LESION.get(columna, {})) * PESO_LESION[columna]
                )
            if columna in PESO_NIVEL:
                df_labelizado["score_nivel"] += (
                    df_labelizado[columna].map(SCORE_NIVEL.get(columna, {})) * PESO_NIVEL[columna]
                )

        df_labelizado.fillna(0, inplace=True)
        st.session_state["df_labelizado"] = df_labelizado

        mostrar_mensaje("Cálculo de Scores y de Nivel Realizado Correctamente")

    except Exception as e:
        raise RuntimeError(f"Error al calcular los scores: {e}")

def escalar_columnas():
    """Escala las columnas seleccionadas usando MinMaxScaler."""
    try:
        if "df_labelizado" not in st.session_state or st.session_state["df_labelizado"] is None:
            raise ValueError("Escalar Columnas (Funcion). El DataFrame labelizado no ha sido inicializado.")

        scaler = MinMaxScaler()
        columnas_a_escalar = ["score_lesion", "score_nivel"]

        df_scaled = st.session_state["df_labelizado"].copy()
        df_scaled[columnas_a_escalar] = scaler.fit_transform(df_scaled[columnas_a_escalar])

        st.session_state["df_scaled"] = df_scaled
        
        print("df_scaled" , df_scaled)

        mostrar_mensaje("Columnas Escaladas Correctamente")

    except Exception as e:
        raise RuntimeError(f"Error al escalar las columnas: {e}")
    
    

def regresion_a_la_media_palas():
    """Aplica una regresión a la media a las columnas específicas."""
    try:
        if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
            raise ValueError("Regresion A La Media Palas (Funcion) .El DataFrame 'df_scaled' no ha sido inicializado.")

        df_scaled = st.session_state["df_scaled"]

        def ajustar_valor(valor, es_score_nivel):
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

        df_scaled['score_lesion_ajustado'] = df_scaled['score_lesion'].apply(lambda x: ajustar_valor(x, es_score_nivel=False))
        df_scaled['score_nivel_ajustado'] = df_scaled['score_nivel'].apply(lambda x: ajustar_valor(x, es_score_nivel=True))
        
        nombre_archivo = 'df_scaled_palas_3.0.csv'
        df_scaled.to_csv(nombre_archivo, index=False)
        
        st.session_state["df_scaled"] = df_scaled

    except Exception as e:
        raise RuntimeError(f"Error al aplicar la regresión a la media: {e}")




