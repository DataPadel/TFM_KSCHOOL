import pandas as pd
import streamlit as st

from utilidades.utilidades import encontrar_vecinos_mas_cercanos_knn_2d,obtener_palas_por_cuadrante
from utilidades.graficos.graficos_recomendador_de_pala import diagrama_palas_palas_recomendadas,diagrama_palas_palas_recomendadas_grafica,mostrar_palas_en_tarjetas,mostrar_tabla_caracteristicas


LABEL_MAPPING = {"balance": {0: "No data", 1: "Bajo", 2: "Medio", 3: "Alto"},}


def recomendador_de_palas():
    """
    Función principal para recomendar palas de pádel basándose en datos del formulario y características del usuario.
    """
    st.title("Recomendador de Palas")

    try:
        # -----------------------------------------------
        # Cargar los DataFrames necesarios
        # -----------------------------------------------
        df_form, df_palas = cargar_datos()

        if df_form is None or df_palas is None:
            st.error("Error al cargar los datos. Verifica los archivos.")
            return

        # Renombrar columnas del formulario si es necesario
        df_form = renombrar_columnas(df_form)

        # -----------------------------------------------
        # Crear una lista de índices en orden inverso
        # -----------------------------------------------
        indices_inversos = list(range(len(df_form) - 1, -1, -1))  # Del último al primero

        # Usar select_slider con estilo predeterminado
        registro_index = st.select_slider(
            "Índice del Registro Formulario",
            options=indices_inversos,  # Mostrar los índices en orden inverso
            value=indices_inversos[0],  # Comienza con el índice más alto
            key="slider_registro_inverso",
        )

        # -----------------------------------------------
        # Mostrar detalles del registro seleccionado
        # -----------------------------------------------
        detalles_registro_df = mostrar_detalles_registro_tabular(df_form, registro_index)

        if detalles_registro_df.empty:
            st.error("No se encontraron datos en el registro seleccionado.")
            return

        mostrar_tabla_caracteristicas(detalles_registro_df)

        # -----------------------------------------------
        # Verificar y obtener el balance seleccionado
        # -----------------------------------------------
        try:
            balance_value = detalles_registro_df.loc[
                detalles_registro_df["Característica"].str.lower() == "balance", "Valor"
            ].values[0]

        except IndexError:
            st.error("La característica 'Balance' no está presente en los datos seleccionados.")
            return
        except Exception as e:
            st.error(f"Error inesperado al obtener el balance: {str(e)}")
            return

        balance_seleccionado_num = obtener_balance(balance_value)

        if balance_seleccionado_num is None:
            st.error(f"El balance seleccionado ('{balance_value}') no es válido.")
            return

        # -----------------------------------------------
        # Obtener las coordenadas del usuario
        # -----------------------------------------------
        try:
            x_random = df_form.iloc[registro_index]["Score_Escalar_Lesion"]
            y_random = df_form.iloc[registro_index]["Score_Escalar_Nivel"]

        except KeyError as e:
            st.error(f"Error al obtener las coordenadas del usuario: {str(e)}")
            return

        # -----------------------------------------------
        # Generar las recomendaciones de palas
        # -----------------------------------------------
        palas_definitivas = generar_recomendaciones(df_palas, x_random, y_random, balance_seleccionado_num)

        if palas_definitivas.empty:
            st.warning("No se encontraron palas recomendadas para los criterios seleccionados.")
            return

        # -----------------------------------------------
        # Mostrar resultados finales
        # -----------------------------------------------
        st.subheader("Palas Recomendadas")

        mostrar_palas_en_tarjetas(palas_definitivas)

        diagrama_palas_palas_recomendadas(palas_definitivas)

    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")



#------------------------------------------------------------------------------------------------------

# Renombrar columnas del DataFrame df_form
def renombrar_columnas(df_form):
    column_mapping = {
        "Cuantas horas juegas a la semana": "Horas a la Semana",
        "Indique su peso": "Peso",
        "Indique su sexo":"Sexo",
        "Indique su altura": "Altura",
        "Indique su Lado de Juego": "Lado de Juego",
        "Indique su nivel de juego": "Nivel de Juego",
        "Que tipo de balance te gusta": "Balance",
        "Has tenido alguna de las siguientes lesiones ...": "Lesiones Antiguas",
        "Con que frecuencia": "Frecuencia Lesion",
        "Hace cuanto": "Tiempo entre Lesiones"
    }
    df_form.rename(columns=column_mapping, inplace=True)
    return df_form
    #return df_form.drop(columns=["Score", "Score_Escalar", "Rango de precio dispuesto a pagar"], errors='ignore')
    
    
#-----------------------------------------------------------------------------------------------------------

def mostrar_detalles_registro_tabular(df_form, index):
    """
    Muestra los detalles de un registro en formato tabular, excluyendo columnas no deseadas.

    Args:
        df_form (pd.DataFrame): DataFrame que contiene los registros.
        index (int): Índice del registro a mostrar.

    Returns:
        pd.DataFrame: DataFrame con las características y valores del registro seleccionado.
    """

    # Identificar columnas no deseadas
    columnas_no_deseadas = ["Score_Escalar_Lesion", "Score_Escalar_Nivel"]

    # Validar que el índice esté dentro del rango
    if not (0 <= index < len(df_form)):
        st.error(f"El índice {index} está fuera del rango del DataFrame.")
        return pd.DataFrame()  # Retornar un DataFrame vacío

    try:
        # Filtrar las columnas no deseadas y seleccionar la fila por índice
        selected_row = df_form.drop(columns=columnas_no_deseadas, errors='ignore').iloc[index]

        # Filtrar valores None o NaN
        selected_row = selected_row.dropna()

        if selected_row.empty:
            st.error("Todos los valores en la fila seleccionada son nulos.")
            return pd.DataFrame()  # Retornar un DataFrame vacío

        # Crear el DataFrame de detalles
        detalles_registro_df = pd.DataFrame({
            "Característica": selected_row.index,
            "Valor": selected_row.values
        })

        return detalles_registro_df

    except Exception as e:
        st.error(f"Error al procesar el registro seleccionado: {str(e)}")
        return pd.DataFrame()  # Retornar un DataFrame vacío


#-----------------------------------------------------------------------------------------------------------

def mostrar_resultados(palas_definitivas):
    """
    Muestra los resultados finales al usuario.
    """
    st.subheader("Tabla con Palas Recomendadas y Palas Que Quizá Te Gusten")
    
    mostrar_imagen_palas(palas_definitivas)
    diagrama_palas_palas_recomendadas(palas_definitivas)
    diagrama_palas_palas_recomendadas_grafica(palas_definitivas)



def generar_recomendaciones(df_palas, x_random, y_random, balance_seleccionado_num):
    """
    Genera las recomendaciones de palas basándose en KNN y rejilla.
    """
    try:
        # Recomendaciones KNN
        recomendaciones_knn = encontrar_vecinos_mas_cercanos_knn_2d(
            df_palas, x_random, y_random, balance_seleccionado_num
        )

        if recomendaciones_knn.empty:
            st.warning(f"No se encontraron palas recomendadas para el balance seleccionado: {balance_seleccionado_num}.")
            return None

        # Recomendaciones por rejilla
        palas_recomendadas_rejilla = obtener_palas_por_cuadrante(df_palas, x_random, y_random, recomendaciones_knn)

        if len(palas_recomendadas_rejilla) < 2:
            dos_palas_recomendadas_rejilla = palas_recomendadas_rejilla
        else:
            dos_palas_recomendadas_rejilla = palas_recomendadas_rejilla.sample(n=2, replace=False)

        # Combinar recomendaciones finales (KNN + rejilla)
        palas_definitivas = pd.concat([recomendaciones_knn, dos_palas_recomendadas_rejilla], ignore_index=True)

        return palas_definitivas

    except ValueError as knn_error:
        if "No hay suficientes palas" in str(knn_error):
            st.warning(f"No hay suficientes palas disponibles para el balance seleccionado: {balance_seleccionado_num}.")
            return None
        else:
            raise knn_error


def obtener_balance(balance_texto):
    """
    Convierte el texto del balance a un valor numérico utilizando un mapeo predefinido.
    
    Args:
    - balance_texto (str): Texto que describe el balance (por ejemplo, 'Medio', 'Alto').
    
    Returns:
    - int o None: Valor numérico correspondiente al balance, o None si no es válido.
    """
    LABEL_MAPPING = {
        "bajo": 1,
        "medio": 2,
        "alto": 3
    }

    balance_texto = balance_texto.strip().lower()  # Normalizar texto
    return LABEL_MAPPING.get(balance_texto)  # Retorna el valor numérico o None si no es válido
    
def cargar_datos():
    """
    Carga los DataFrames necesarios para el recomendador.
    """
    try:
        df_form = pd.read_csv("df_scaled_formularios_3.0.csv")
        df_palas = pd.read_csv("df_scaled_palas_3.0.csv")

        if df_form.empty:
            st.error("El formulario no contiene registros.")
            return None, None

        if df_palas.empty:
            st.error("No se encontraron palas disponibles para recomendar.")
            return None, None

        return df_form, df_palas
    except FileNotFoundError as e:
        st.error(f"Archivo no encontrado: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None, None



    
    