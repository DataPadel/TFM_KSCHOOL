import pandas as pd
import streamlit as st

from utilidades.app.utilidadaes_app import obtener_dataframe_actualizado,cargar_dataframes
from utilidades.utilidades import encontrar_vecinos_mas_cercanos_knn_2d,obtener_palas_por_cuadrante
from utilidades.graficos.graficos_recomendador_de_pala import diagrama_palas_palas_recomendadas,diagrama_palas_palas_recomendadas_grafica,grafica_recomendaciones_knn,mostrar_imagen_palas

def recomendador_de_palas():
    
    st.title("Recomendador de Palas")

    try:
        # Obtener el DataFrame actualizado desde el estado global
        df_form = obtener_dataframe_actualizado()
        _, df_palas = cargar_dataframes()
        print("------------------------------------------------------------------------------------------------------------")
        print("Este es el dataframe de palas que llega al recomendador de palas")
        print(df_palas.head())
        print(df_palas['Precio'].tolist())

        # Renombrar columnas del DataFrame formulario
        df_form = renombrar_columnas(df_form)

        # Slider para seleccionar índice del registro en el formulario
        index = st.slider("Índice del Registro Formulario", min_value=0, max_value=len(df_form) - 1, step=1)

        # Validar índice seleccionado
        if index < 0 or index >= len(df_form):
            st.error("El índice seleccionado está fuera de rango.")
            return

        """
        # Crear nueva columna 'Score_Escalar_Lesion_Nivel' basada en la intersección geométrica
        df_form['Score_Escalar_Lesion_Nivel'] = (
            (df_form['Score_Escalar_Lesion']**2 + df_form['Score_Escalar_Nivel']**2)**0.5
        )
        """

        # Mostrar detalles del registro seleccionado en forma tabular
        st.subheader("Detalles del Registro Seleccionado")
        detalles_registro_df = mostrar_detalles_registro_tabular(df_form, index)
        st.dataframe(detalles_registro_df)

        # Obtener el valor de "Rango de precio dispuesto a pagar" del registro seleccionado
        rango_precio_seleccionado = detalles_registro_df.loc[
            detalles_registro_df["Característica"] == "Rango de precio dispuesto a pagar", 
            "Valor"
        ].values[0].strip()  # Eliminar espacios adicionales

        # Depuración: Imprimir el rango seleccionado
        print(f"Rango de precio seleccionado: '{rango_precio_seleccionado}'")

        # Determinar los rangos seleccionados automáticamente según el valor del formulario
        rangos_seleccionados = []
        if rango_precio_seleccionado == "Menos de 100":
            rangos_seleccionados.append((0, 100))
        elif rango_precio_seleccionado == "Entre 100 y 200":
            rangos_seleccionados.append((100, 200))
        elif rango_precio_seleccionado == "Mas de 200":
            rangos_seleccionados.append((200, float('inf')))

        if not rangos_seleccionados:
            st.warning("Por favor, selecciona al menos un rango de precios.")
            return

        # Obtener valores específicos del registro seleccionado
        x_random = df_form.iloc[index]['Score_Escalar_Lesion']
        y_random = df_form.iloc[index]['Score_Escalar_Nivel']

        # Iterar sobre los rangos seleccionados y generar recomendaciones por cada rango
        for rango in rangos_seleccionados:
            
            precio_maximo = rango[1]  # Máximo del rango actual
            try:

                    st.subheader(f"Grafico Palas Recomendadas")
                    
                    #PALAS RECOMENDADAS KNN
                    recomendaciones_knn = encontrar_vecinos_mas_cercanos_knn_2d(df_palas, x_random, y_random, considerar_precio=False, precio_maximo=precio_maximo)
                    
                    grafica_recomendaciones_knn(df_palas,x_random,y_random)
                    
                    #PALAS RECOMENDADAS REJILLA
                    palas_recomendadas_rejilla = obtener_palas_por_cuadrante(df_palas, x_random, y_random,recomendaciones_knn)
                    
                    if len(palas_recomendadas_rejilla) < 2:
                        dos_palas_recomendadas_rejilla = palas_recomendadas_rejilla
    
                    else:
                        dos_palas_recomendadas_rejilla = palas_recomendadas_rejilla.sample(n=2, replace=False)

                    # PALAS RECOMENDADAS = PALAS RECOMENDADAS POR KNN (recomendaciones_knn) + PALAS ALEATORIAS SUGERIDAS POR REJILLA (dos_palas_recomendadas_rejilla)
                    
                    palas_definitivas = pd.concat([recomendaciones_knn, dos_palas_recomendadas_rejilla], ignore_index=True)

                    st.subheader(f"Tabla con Palas Recomendadas y Palas Que Quiza Te Gusten")
                    
                    # METODO PARA MOSTRAR LA IMAGEN DE LAS PALAS
                    mostrar_imagen_palas(palas_definitivas)
                    
                    # DIAGRAMA CON TODAS LAS PALAS = PALAS KNN + PALAS SUGERIDAS POR REJILLA
                    diagrama_palas_palas_recomendadas(palas_definitivas)
                    
                    #DIAGRAMA DE DISPERSION CON LA UBICACION DE TODAS LAS PALAS = PALAS KNN + PALAS SUGERIDAS POR REJILLA
                    diagrama_palas_palas_recomendadas_grafica(palas_definitivas)

            except ValueError as knn_error:
                if "No hay suficientes palas" in str(knn_error):
                    st.warning(f"No hay suficientes palas disponibles en el rango {rango[0]} - {rango[1]} Euros.")
                else:
                    raise knn_error

    except Exception as e:
       st.error(f"Recomendador de Palas .Error al generar el gráfico o procesar los datos: {str(e)}")

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

# Mostrar detalles del registro seleccionado en forma tabular
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
    columnas_no_deseadas = [
        "Score_Escalar_Lesion", "Score_Escalar_Nivel",
        "Score_Escalar_Ajustado_Lesion", "Score_Escalar_Ajustado_Nivel"
    ]

    # Filtrar las columnas no deseadas y eliminar duplicados
    selected_row = df_form.drop(columns=columnas_no_deseadas, errors='ignore').iloc[index]

    # Filtrar valores None o NaN
    selected_row = selected_row.dropna()

    # Crear el DataFrame de detalles
    return pd.DataFrame({
        "Característica": selected_row.index,
        "Valor": selected_row.values
    })



    
    