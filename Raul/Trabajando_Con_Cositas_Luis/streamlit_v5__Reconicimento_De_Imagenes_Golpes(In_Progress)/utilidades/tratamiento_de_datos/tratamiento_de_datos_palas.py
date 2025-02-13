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


from utilidades.tratamiento_de_datos.utilidades_tratamiento_de_datos_palas import procesar_fila, mostrar_mensaje 
from utilidades.tratamiento_de_datos.utilidades_tratamiento_de_datos_palas import limpiar_precio, tratar_balance, tratar_nucleo, tratar_cara, tratar_dureza, tratar_forma, tratar_superficie, tratar_nivel_juego, tratar_tipo_juego, tratar_jugador


def lectura_tratamiento_datos_palas():
    """
    Realiza el tratamiento de las columnas del DataFrame almacenado en session_state como 'df_caracteristicas_palas'
    y guarda el resultado procesado en session_state como 'df'.
    """
    try:
        # Verificar si el DataFrame 'df_caracteristicas_palas' está disponible en session_state
        if "df_caracteristicas_palas" not in st.session_state or st.session_state["df_caracteristicas_palas"] is None:
            raise ValueError("El DataFrame 'df_caracteristicas_palas' no está definido en session_state.")

        # Obtener el DataFrame desde session_state
        df = st.session_state["df_caracteristicas_palas"]
        
        # Leer el archivo CSV nuevamente (opcional)
        df_csv = pd.read_csv("PNpalas_DF_3.csv")
        
         # Procesar cada fila de la columna 'data' para expandirla
        df_expandido = pd.DataFrame(df_csv['data'].apply(procesar_fila).tolist())
        
        # Eliminación de columnas no necesarias
        columnas_a_eliminar = ['Producto', 'Acabado', 'producto', 'acabado', 'colección jugadores', 'producto oficial', 'formato']
        if any(col in df_expandido.columns for col in columnas_a_eliminar):
            df_expandido = df_expandido.drop(columns=columnas_a_eliminar, errors='ignore')
        
        # ---------------------------------------------------------------------
        # renombrer columnas
        
        nuevos_nombres = {
            'nombre': 'Palas',
            'precio': 'Precio',
            'url': 'URL',
            'imagen_url': 'Imagen URL',
            'marca': 'Marca',
            'color': 'Color',
            'color 2': 'Color 2',
            'producto': 'Producto',
            'balance': 'Balance',
            'núcleo': 'Nucleo',
            'cara': 'Cara',
            'formato': 'Formato',
            'nivel de juego': 'Nivel de Juego',
            'forma': 'Forma',
            'superfície': 'Superficie',
            'tipo de juego': 'Tipo de Juego',
            'jugador': 'Jugador',
            'dureza': 'Dureza'
        }

        # Cambiar los nombres de las columnas
        df_expandido.rename(columns=nuevos_nombres, inplace=True)
        
        # ---------------------------------------------------------------------

        # Reemplazar None o NaN por 'No data' en todo el DataFrame
        df_expandido.fillna('No data', inplace=True)

        # ---------------------------------------------------------------------

        # Transformaciones de columnas
        if 'Precio' in df_expandido.columns:
            df_expandido['Precio'] = df_expandido['Precio'].apply(limpiar_precio)
        if 'Balance' in df_expandido.columns:
            df_expandido['Balance'] = df_expandido['Balance'].apply(tratar_balance)
        if 'Nucleo' in df_expandido.columns:
            df_expandido['Nucleo'] = df_expandido['Nucleo'].apply(tratar_nucleo)
        if 'Cara' in df_expandido.columns:
            df_expandido['Cara'] = df_expandido['Cara'].apply(tratar_cara)
        if 'Dureza' in df_expandido.columns:
            df_expandido['Dureza'] = df_expandido['Dureza'].apply(tratar_dureza)
        if 'Forma' in df_expandido.columns:
            df_expandido['Forma'] = df_expandido['Dureza'].apply(tratar_forma)
        if 'Superficie' in df_expandido.columns:
            df_expandido['Superficie'] = df_expandido['Superficie'].apply(tratar_superficie)
        if 'Nivel de Juego' in df_expandido.columns:
            df_expandido['Nivel de Juego'] = df_expandido['Nivel de Juego'].apply(tratar_nivel_juego)
        if 'Tipo de Juego' in df_expandido.columns:
            df_expandido['Tipo de Juego'] = df_expandido['Tipo de Juego'].apply(tratar_tipo_juego)
        if 'Jugador' in df_expandido.columns:
            df_expandido['Jugador'] = df_expandido['Jugador'].apply(tratar_jugador)

        # Guardar el DataFrame procesado en session_state
        st.session_state["df"] = df_expandido
        
        # Mostrar mensaje de éxito
        mostrar_mensaje("Carga de Palas/Tratamiento Datos Palas Realizado Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al leer o procesar el archivo CSV: {e}")



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
        print("df_labelizado",df_labelizado.head())
        

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
    """Aplica una regresión a la media a las columnas específicas y guarda el DataFrame procesado en session_state."""
    try:
        # Verificar si 'df_scaled' está inicializado en session_state
        if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
            raise ValueError("Regresion A La Media Palas (Funcion). El DataFrame 'df_scaled' no ha sido inicializado.")

        # Obtener el DataFrame desde session_state
        df_scaled = st.session_state["df_scaled"]

        # Definir la función para ajustar valores
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

        # Aplicar ajustes a las columnas relevantes
        df_scaled['score_lesion_ajustado'] = df_scaled['score_lesion'].apply(lambda x: ajustar_valor(x, es_score_nivel=False))
        df_scaled['score_nivel_ajustado'] = df_scaled['score_nivel'].apply(lambda x: ajustar_valor(x, es_score_nivel=True))

        # Guardar el DataFrame ajustado como archivo CSV
        nombre_archivo = 'df_scaled_palas_3.0.csv'
        df_scaled.to_csv(nombre_archivo, index=False)
        
        # Guardar el DataFrame ajustado en session_state como 'df_scaled_palas'
        st.session_state["df_scaled_palas"] = df_scaled
        print("Dataframe ajustado df_sacled_palas",st.session_state["df_scaled_palas"])

        print(f"Archivo '{nombre_archivo}' guardado correctamente.")
        print("DataFrame ajustado guardado en session_state como 'df_scaled_palas'.")

    except Exception as e:
        raise RuntimeError(f"Error al aplicar la regresión a la media: {e}")
