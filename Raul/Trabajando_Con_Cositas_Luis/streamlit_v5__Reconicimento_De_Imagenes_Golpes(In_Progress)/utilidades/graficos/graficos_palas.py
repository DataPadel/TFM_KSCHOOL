import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt


def graficas_palas():
    st.title("Graficas de Palas")
    try:
        grafico_histograma_palas()
        diagrama_dispersion_palas()
        diagrama_3d_palas()
    except Exception as e:
       st.error(f"Graficas de Palas. Error al generar el gráfico o procesar los datos: {str(e)}")

def grafico_histograma_palas():
    """Genera y muestra los histogramas de score_lesion y score_nivel."""
    if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
        raise ValueError("El DataFrame 'df_scaled' no está inicializado. Completa el preprocesamiento primero.")

    df_scaled = st.session_state["df_scaled"]

    # Verificar que las columnas necesarias existen en el DataFrame
    if 'score_lesion' not in df_scaled.columns or 'score_nivel' not in df_scaled.columns:
        raise ValueError("Grafico Histograma Palas (Funcion) . El DataFrame 'df_scaled' no contiene las columnas 'score_lesion' o 'score_nivel'.")

    plt.figure(figsize=(12, 6))

    # Histograma para score_lesion
    plt.subplot(1, 2, 1)
    sns.histplot(df_scaled['score_lesion'], kde=True, color='blue', bins=20)
    plt.title('Histograma de Score de Lesión')
    plt.xlabel('Score de Lesión')
    plt.ylabel('Frecuencia')

    # Histograma para score_nivel
    plt.subplot(1, 2, 2)
    sns.histplot(df_scaled['score_nivel'], kde=True, color='green', bins=20)
    plt.title('Histograma de Score de Nivel')
    plt.xlabel('Score de Nivel')
    plt.ylabel('Frecuencia')

    # Ajustar la disposición y mostrar en Streamlit
    plt.tight_layout()
    st.pyplot(plt)


def diagrama_dispersion_palas():
    """Genera un diagrama de dispersión para score_lesion y score_nivel."""
    if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
        raise ValueError("Diagrama de Dispersion De Palas (Funcion) .El DataFrame 'df_scaled' no está inicializado.")

    df_scaled = st.session_state["df_scaled"]

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=df_scaled['score_lesion'], y=df_scaled['score_nivel'], color='blue')

    plt.title('Diagrama de Dispersión: Score de Lesión vs Score de Nivel')
    plt.xlabel('Score de Lesión')
    plt.ylabel('Score de Nivel')

    st.pyplot(plt)


def diagrama_3d_palas():
    """Genera un gráfico en 3D para score_lesion, score_nivel y Precio."""
    if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
        raise ValueError("Diagrama 3D Palas(Funcion).El DataFrame 'df_scaled' no está inicializado.")

    df_scaled = st.session_state["df_scaled"]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    x = df_scaled['score_lesion']
    y = df_scaled['score_nivel']
    z = df_scaled['Precio']  # Cambia esta columna si es necesario

    ax.scatter(x, y, z, c='blue', marker='o')

    ax.set_xlabel('Score de Lesión')
    ax.set_ylabel('Score de Nivel')
    ax.set_zlabel('Precio')

    ax.set_title('Gráfico en 3D: Score de Lesión vs Score de Nivel vs Precio')
    
    st.pyplot(fig)



