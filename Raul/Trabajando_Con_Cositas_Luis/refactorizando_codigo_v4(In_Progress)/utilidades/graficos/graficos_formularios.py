import matplotlib.pyplot as plt
import streamlit as st

def grafico_dispersion_formularios():
    """Genera un gráfico de dispersión 2D basado en datos de df_scaled_formularios."""
    # Verificar si df_scaled_formularios está disponible en st.session_state
    if "df_scaled_formularios" not in st.session_state or st.session_state["df_scaled_formularios"] is None:
        raise ValueError("El DataFrame 'df_scaled_formularios' no está inicializado. Completa el preprocesamiento primero.")

    # Extraer el DataFrame desde session_state
    df_scaled_formularios = st.session_state["df_scaled_formularios"]

    # Seleccionar 200 filas aleatorias
    random_rows = df_scaled_formularios.sample(200)

    # Extraer las coordenadas X e Y
    x_random = random_rows['Score_Lesion']
    y_random = random_rows['Score_Nivel']

    # Crear figura
    fig = plt.figure(figsize=(10, 6))

    # Crear un gráfico de dispersión
    ax = fig.add_subplot(111)
    ax.scatter(x_random, y_random, c='b', alpha=0.7, edgecolor='k')

    # Etiquetas de los ejes
    ax.set_xlabel('Score Lesion')
    ax.set_ylabel('Score Nivel')

    # Título del gráfico
    ax.set_title('Gráfico de dispersión 2D de puntajes')

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)
