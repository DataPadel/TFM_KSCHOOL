import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st

def graficas_formularios():
    st.title("Gráficas de Formularios")

    try:
        grafico_dispersion_formularios()
    except Exception as e:
        st.error(f"Gráficas de Formularios. Error al generar el gráfico o procesar los datos: {str(e)}")


def grafico_dispersion_formularios():
    """Genera un gráfico de dispersión estilizado con eje invertido y colores en tonos verdes."""
    try:
        # Verificar si df_scaled_formularios está disponible en st.session_state
        if "df_scaled_formularios" not in st.session_state or st.session_state["df_scaled_formularios"] is None:
            raise ValueError("El DataFrame 'df_scaled_formularios' no está inicializado. Completa el preprocesamiento primero.")

        # Extraer el DataFrame desde session_state
        df_scaled_formularios = st.session_state["df_scaled_formularios"]

        # Seleccionar 200 filas aleatorias
        random_rows = df_scaled_formularios.sample(200)

        # Crear categorías para la leyenda basada en Score_Lesion
        bins = [0, 0.33, 0.66, 1.0]
        labels = ['Bajo', 'Medio', 'Alto']
        random_rows['lesion_categoria'] = pd.cut(random_rows['Score_Lesion'], bins=bins, labels=labels)

        # Crear el gráfico de dispersión con Plotly
        fig = px.scatter(
            random_rows,
            x='Score_Lesion',
            y='Score_Nivel',
            color='lesion_categoria',  # Categorías como colores
            title='Diagrama de Dispersión: Score de Lesión vs Score de Nivel',
            labels={
                'Score_Lesion': 'Score de Lesión',
                'Score_Nivel': 'Score de Nivel'
            },
            template='plotly_white',
            color_discrete_map={
                'Bajo': '#8FCB9B',  # Verde claro
                'Medio': '#4CAF50',  # Verde medio
                'Alto': '#2E7D32'   # Verde oscuro
            }
        )

        # Invertir los ejes X e Y para que el gráfico vaya desde la parte inferior derecha a la superior izquierda
        fig.update_layout(
            xaxis=dict(autorange='reversed'),
            yaxis=dict(autorange=True),
            title_font=dict(size=20, family='Arial', color='black'),
            xaxis_title_font=dict(size=16),
            yaxis_title_font=dict(size=16),
            legend_title="Categoría de Lesión",
            margin=dict(l=40, r=40, t=60, b=40)
        )

        # Ajustar diseño de los puntos
        fig.update_traces(
            marker=dict(
                size=10,  # Tamaño de los puntos
                line=dict(
                    width=2,  # Grosor del contorno
                    color='black'  # Color del contorno
                )
            )
        )

        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig, use_container_width=True)

    except ValueError as e:
        st.error(f"Gráfico de Dispersión Formularios. Error al generar el gráfico o procesar los datos: {e}")




