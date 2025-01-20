import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

def diagrama_palas_palas_recomendadas(palas_recomendadas):
    """
    Genera un diagrama basado en las palas recomendadas con una leyenda para identificar los colores.

    Args:
        palas_recomendadas (DataFrame): DataFrame con las palas recomendadas.
    """

    if palas_recomendadas.empty:
        st.warning("No hay datos para generar el diagrama.")
        return

    # Crear una lista de colores basada en la posición de los registros
    colores = ['lightgreen'] * min(3, len(palas_recomendadas))  # Los tres primeros en verde claro
    colores += ['yellow'] * max(0, len(palas_recomendadas) - 3)  # Los dos últimos en amarillo

    # Crear un gráfico ajustado con un tamaño más proporcionado
    fig, ax = plt.subplots(figsize=(12, 8))  # Ajustar el tamaño de la figura
    ax.bar(
        palas_recomendadas['nombre'],
        palas_recomendadas['Precio'],
        color=colores[:len(palas_recomendadas)],  # Aplicar colores según la longitud de los datos
        width=0.6  # Ajustar el ancho de las barras
    )
    ax.set_title("Precios de las Palas Recomendadas", fontsize=16)
    ax.set_xlabel("Palas", fontsize=14)
    ax.set_ylabel("Precio (€)", fontsize=14)

    # Rotar las etiquetas del eje X y alinearlas a la derecha
    plt.xticks(rotation=30, ha='right', fontsize=12)

    # Añadir una leyenda personalizada
    handles = [
        plt.Line2D([0], [0], color='lightgreen', lw=4, label='Palas Recomendadas'),
        plt.Line2D([0], [0], color='yellow', lw=4, label='Palas que Quizá te Gusten')
    ]
    ax.legend(handles=handles, loc='upper right', fontsize=12)

    # Ajustar los márgenes automáticamente
    plt.tight_layout()

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)



def grafica_recomendaciones_knn(df_palas, x_random, y_random):
    """
    Genera un gráfico de dispersión 2D basado en los datos de palas y un punto adicional.

    Args:
        df_palas (DataFrame): DataFrame con los datos de las palas.
        x_random (float): Coordenada X del punto adicional.
        y_random (float): Coordenada Y del punto adicional.
    """
    if df_palas.empty:
        st.warning("No hay datos para generar la gráfica.")
        return

    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 6))

    # Definir los valores de cada eje para el DataFrame principal (df_palas)
    x = df_palas['score_lesion_ajustado']
    y = df_palas['score_nivel_ajustado']

    # Crear el gráfico de dispersión 2D para df_palas
    ax.scatter(x, y, color='blue', label='Datos de Palas')

    # Crear los puntos adicionales
    ax.scatter([x_random], [y_random], color='red', s=100, label='Formulario')

    # Calcular los límites con buffer
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    buffer = 0.01  # Cambia este valor para ajustar el tamaño del margen

    # Ajustar límites de los ejes con el buffer
    ax.set_xlim(x_min - buffer, x_max + buffer)
    ax.set_ylim(y_min - buffer, y_max + buffer)

    # Añadir etiquetas a los ejes
    ax.set_xlabel('Score de Lesión (Escalado)')
    ax.set_ylabel('Score de Nivel (Escalado)')

    # Título del gráfico
    ax.set_title('Gráfico 2D de Score de Lesión, Score de Nivel y Formulario')

    # Añadir leyenda para diferenciar los conjuntos de puntos
    ax.legend()

    # Configurar las particiones de Y para solo mostrar en 0.45, 0.55, 0.65
    ax.set_yticks([0.45, 0.55, 0.65])  # Solo las marcas deseadas en Y
    ax.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    
    
def diagrama_palas_palas_recomendadas_grafica(palas_definitivas):
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
    if not palas_definitivas.empty:
        sns.scatterplot(
            x=palas_definitivas['score_lesion_ajustado'], 
            y=palas_definitivas['score_nivel_ajustado'], 
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



def mostrar_imagen_palas(palas_recomendadas):
    """
    Muestra las palas recomendadas donde las imágenes se pueden abrir y cerrar dentro de la misma página,
    con un diseño estilizado.
    """
    # Crear una copia del DataFrame para evitar modificar el original
    df_mostrar = palas_recomendadas.copy()

    # Generar HTML con estilo para la tabla y funcionalidad para mostrar/cerrar imágenes
    html_content = """
    <style>
        .image-container {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1000;
            background-color: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 10px;
        }
        .image-container img {
            border: 5px solid #C2D6A6; /* Verde pastel */
            border-radius: 10px; /* Bordes redondeados */
            max-width: 100%; /* Ajustar al tamaño máximo */
            height: auto; /* Mantener proporción */
            box-shadow: none !important; /* Eliminar cualquier sombra negra */
            outline: none !important; /* Eliminar cualquier contorno adicional */
            background-color: transparent; /* Asegurar fondo transparente */
        }
        .image-container .close-button {
            position: absolute;
            top: 10px;
            right: 10px;
            color: white;
            background-color: red;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            font-size: 20px;
            cursor: pointer;
        }
        .styled-table {
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 18px;
            font-family: 'sans-serif';
            width: 100%;
            background-color: #F5F5F5; /* Fondo blanco suave */
            color: #333333; /* Texto oscuro */
            border-radius: 10px; /* Bordes redondeados */
            overflow: hidden;
        }
        .styled-table thead tr {
            background-color: #C2D6A6; /* Verde pastel */
            color: #333333; /* Texto oscuro */
            text-align: left;
        }
        .styled-table th, .styled-table td {
            padding: 12px 15px;
            border: 1px solid #C2D6A6; /* Bordes verdes pastel */
        }
        .styled-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }
        .styled-table tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }
        .styled-table tbody tr:last-of-type {
            border-bottom: 2px solid #2D471D; /* Verde oscuro */
        }
    </style>
    <script>
        function showImage(url) {
            const container = document.getElementById('image-container');
            const img = document.getElementById('popup-image');
            img.src = url;
            container.style.display = 'block';
        }
        function closeImage() {
            const container = document.getElementById('image-container');
            container.style.display = 'none';
        }
    </script>
    <div id="image-container" class="image-container">
        <button class="close-button" onclick="closeImage()">×</button>
        <img id="popup-image" src="" alt="Imagen de la pala">
    </div>
    <table class="styled-table">
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Score Lesión Ajustado</th>
                <th>Score Nivel Ajustado</th>
                <th>Precio</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in df_mostrar.iterrows():
        html_content += f"""
        <tr class="table-row" onclick="showImage('{row['imagen_url']}')">
            <td>{row['nombre']}</td>
            <td>{row['score_lesion_ajustado']}</td>
            <td>{row['score_nivel_ajustado']}</td>
            <td>{row['Precio']} €</td>
        </tr>
        """

    html_content += """
        </tbody>
    </table>
    """

    # Renderizar el HTML usando components.html
    components.html(html_content, height=600, scrolling=True)