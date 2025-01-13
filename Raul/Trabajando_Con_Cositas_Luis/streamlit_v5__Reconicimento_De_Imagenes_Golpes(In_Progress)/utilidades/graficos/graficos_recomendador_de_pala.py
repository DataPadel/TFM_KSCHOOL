import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def diagrama_palas_palas_recomendadas(palas_recomendadas):
    """
    Genera un diagrama basado en las palas recomendadas.

    Args:
        palas_recomendadas (DataFrame): DataFrame con las palas recomendadas.
    """

    if palas_recomendadas.empty:
        st.warning("No hay datos para generar el diagrama.")
        return

    # Crear un gráfico ajustado
    fig, ax = plt.subplots(figsize=(10, 6))  # Aumentar el tamaño de la figura
    ax.bar(
        palas_recomendadas['Palas'],
        palas_recomendadas['Precio'],
        color='skyblue'
    )
    ax.set_title("Precios de las Palas Recomendadas")
    ax.set_xlabel("Palas")
    ax.set_ylabel("Precio (€)")

    # Rotar las etiquetas del eje X y alinearlas a la derecha
    plt.xticks(rotation=45, ha='right')

    # Ajustar los márgenes automáticamente
    plt.tight_layout()

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)
    
    
def diagrama_palas_palas_recomendadas_grafica(palas_recomendadas):
    """
    Genera un diagrama de dispersión para score_lesion y score_nivel,
    marcando las palas recomendadas en rojo.
    """
    if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
        raise ValueError("El DataFrame 'df_scaled' no está inicializado.")

    df_scaled = st.session_state["df_scaled"]

    # Crear figura
    plt.figure(figsize=(10, 6))

    # Graficar todas las palas en azul
    sns.scatterplot(
        x=df_scaled['score_lesion'], 
        y=df_scaled['score_nivel'], 
        color='blue', 
        label='Todas las Palas'
    )

    # Filtrar las palas recomendadas para marcarlas en rojo
    if not palas_recomendadas.empty:
        sns.scatterplot(
            x=palas_recomendadas['score_lesion_ajustado'], 
            y=palas_recomendadas['score_nivel_ajustado'], 
            color='red', 
            label='Palas Recomendadas', 
            s=100  # Tamaño de los puntos
        )

    # Configurar título y etiquetas
    plt.title('Diagrama de Dispersión: Score de Lesión vs Score de Nivel')
    plt.xlabel('Score de Lesión')
    plt.ylabel('Score de Nivel')
    plt.legend()

    # Mostrar el gráfico en Streamlit
    st.pyplot(plt)

