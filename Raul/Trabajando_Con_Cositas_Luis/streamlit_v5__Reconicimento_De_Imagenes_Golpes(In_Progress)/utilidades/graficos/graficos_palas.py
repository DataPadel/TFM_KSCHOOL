import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
import streamlit as st
import numpy as np
import pandas as pd

def graficas_palas():
    st.title("Gráficas de Palas")
    try:
        grafico_histograma_score_lesion()
        grafico_histograma_score_nivel()
        diagrama_dispersion_palas()
        diagrama_3d_palas()
    except Exception as e:
        st.error(f"Error al generar las gráficas o procesar los datos: {str(e)}")


import plotly.figure_factory as ff
import streamlit as st

def grafico_histograma_score_lesion():
    """Genera un histograma para score_lesion con contorno grueso y curva de densidad."""
    if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
        raise ValueError("El DataFrame 'df_scaled' no está inicializado. Completa el preprocesamiento primero.")

    df_scaled = st.session_state["df_scaled"]

    # Datos para el histograma
    hist_data = [df_scaled['score_lesion']]
    group_labels = ['Score de Lesión']

    # Crear histograma con curva de densidad
    fig = ff.create_distplot(
        hist_data, 
        group_labels, 
        bin_size=0.05,  # Tamaño de los bins
        show_hist=True, 
        show_curve=True
    )

    # Cambiar el color de las barras a lightgreen y ajustar el contorno
    fig.update_traces(
        marker=dict(
            color='green',  # Color de las barras
            line=dict(
                width=2,  # Grosor del contorno
                color='black'  # Color del contorno
            )
        )
    )

    fig.update_layout(
        title="Histograma de Score de Lesión con Curva de Densidad",
        xaxis_title="Score de Lesión",
        yaxis_title="Frecuencia",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_histograma_score_nivel():
    """Genera un histograma para score_nivel con contorno grueso y curva de densidad."""
    if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
        raise ValueError("El DataFrame 'df_scaled' no está inicializado. Completa el preprocesamiento primero.")

    df_scaled = st.session_state["df_scaled"]

    # Datos para el histograma
    hist_data = [df_scaled['score_nivel']]
    group_labels = ['Score de Nivel']

    # Crear histograma con curva de densidad
    fig = ff.create_distplot(
        hist_data, 
        group_labels, 
        bin_size=0.05,  # Tamaño de los bins
        show_hist=True, 
        show_curve=True
    )

    # Cambiar el color de las barras a lightgreen y ajustar el contorno
    fig.update_traces(
        marker=dict(
            color='green',  # Color de las barras
            line=dict(
                width=2,  # Grosor del contorno
                color='black'  # Color del contorno
            )
        )
    )

    fig.update_layout(
        title="Histograma de Score de Nivel con Curva de Densidad",
        xaxis_title="Score de Nivel",
        yaxis_title="Frecuencia",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


def diagrama_dispersion_palas():
    """Genera un diagrama de dispersión estilizado con jitter y agrupaciones."""
    if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
        raise ValueError("El DataFrame 'df_scaled' no está inicializado.")

    df_scaled = st.session_state["df_scaled"]

    # Aplicar jitter para separar los puntos ligeramente
    jitter_strength = 0.02  # Ajustar la fuerza del jitter
    np.random.seed(42)  # Para reproducibilidad
    df_scaled['score_lesion_jitter'] = df_scaled['score_lesion'] + np.random.uniform(-jitter_strength, jitter_strength, len(df_scaled))
    df_scaled['score_nivel_jitter'] = df_scaled['score_nivel'] + np.random.uniform(-jitter_strength, jitter_strength, len(df_scaled))

    # Crear categorías para la leyenda basada en score_lesion
    bins = [0, 0.33, 0.66, 1.0]
    labels = ['Bajo', 'Medio', 'Alto']
    df_scaled['lesion_categoria'] = pd.cut(df_scaled['score_lesion'], bins=bins, labels=labels)

    # Crear el diagrama de dispersión con jitter y categorías
    fig = px.scatter(
        df_scaled,
        x='score_lesion_jitter',
        y='score_nivel_jitter',
        color='lesion_categoria',  # Categorías como colores
        title='Diagrama de Dispersión: Score de Lesión vs Score de Nivel',
        labels={
            'score_lesion_jitter': 'Score de Lesión',
            'score_nivel_jitter': 'Score de Nivel'
        },
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Set2  # Paleta de colores agradable
    )

    # Ajustar diseño del gráfico
    fig.update_traces(
        marker=dict(
            size=10,  # Tamaño de los puntos
            line=dict(
                width=2,  # Grosor del contorno
                color='black'  # Color del contorno
            )
        )
    )

    fig.update_layout(
        title_font=dict(size=20, family='Arial', color='black'),
        xaxis=dict(
            title_font=dict(size=16),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title_font=dict(size=16),
            tickfont=dict(size=12)
        ),
        legend_title="Categoría de Lesión",
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)


def diagrama_3d_palas():
    """Genera un gráfico en 3D usando Plotly con una leyenda para la escala de colores."""
    if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
        raise ValueError("El DataFrame 'df_scaled' no está inicializado.")

    df_scaled = st.session_state["df_scaled"]

    # Crear gráfico 3D con Plotly
    fig = go.Figure(data=[go.Scatter3d(
        x=df_scaled['score_lesion'],  # Eje X: Score de Lesión
        y=df_scaled['score_nivel'],  # Eje Y: Score de Nivel
        z=df_scaled['Precio'],       # Eje Z: Precio
        mode='markers',
        marker=dict(
            size=8,                  # Tamaño de los puntos
            color=df_scaled['Precio'],  # Color basado en el precio
            colorscale='Viridis',    # Escala de colores
            opacity=0.8,             # Opacidad de los puntos
            colorbar=dict(
                title="Precio (€)",  # Título de la barra de colores
                titleside="top",     # Posición del título
                tickvals=[min(df_scaled['Precio']), max(df_scaled['Precio'])],  # Valores mínimos y máximos
                ticktext=["Bajo", "Alto"],  # Etiquetas descriptivas para los extremos
            )
        )
    )])

    # Configurar diseño del gráfico
    fig.update_layout(
        title="Gráfico 3D: Score de Lesión vs Nivel vs Precio",
        scene=dict(
            xaxis_title='Score de Lesión',
            yaxis_title='Score de Nivel',
            zaxis_title='Precio'
        ),
        template="plotly_white",
        width=900,   # Ancho más grande para mejor visualización
        height=800,  # Altura ajustada para mejor proporción
        margin=dict(l=20, r=20, t=40, b=20)  # Márgenes ajustados
    )

    st.plotly_chart(fig)

