import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
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
    colores += ['yellow'] * max(0, len(palas_recomendadas) - 3)  # Los restantes en amarillo

    # Crear el gráfico de barras con Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=palas_recomendadas['Palas'],
        y=palas_recomendadas['Precio'],
        marker_color=colores[:len(palas_recomendadas)],  # Aplicar colores según la longitud de los datos
        text=palas_recomendadas['Precio'],  # Mostrar los precios como texto
        textposition='outside'  # Mostrar texto fuera de las barras
    ))

    # Configurar diseño del gráfico
    fig.update_layout(
        title="Precios de las Palas Recomendadas",
        title_font_size=20,
        xaxis_title="Palas",
        yaxis_title="Precio (€)",
        xaxis=dict(tickangle=-45),  # Rotar etiquetas del eje X
        font=dict(family="Arial", size=14),
        legend=dict(title="Leyenda", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=50),  # Márgenes ajustados
        height=600  # Altura del gráfico
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)



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

    
    
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def diagrama_palas_palas_recomendadas_grafica(palas_definitivas):
    """
    Genera un diagrama de dispersión para score_lesion y score_nivel,
    marcando las palas recomendadas en diferentes colores según su orden,
    con bordes personalizados y nombres visibles.
    """
    # Verificar si el DataFrame df_scaled está disponible en session_state
    if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
        raise ValueError("El DataFrame 'df_scaled' no está inicializado.")

    df_scaled = st.session_state["df_scaled"]

    # Crear el gráfico base con todas las palas
    fig = px.scatter(
        df_scaled,
        x='score_lesion',
        y='score_nivel',
        color_discrete_sequence=['blue'],  # Color azul para todas las palas
        labels={'score_lesion': 'Score de Lesión', 'score_nivel': 'Score de Nivel'},
        title='Diagrama de Dispersión: Lesión vs Nivel'
    )

    # Añadir las palas recomendadas (primeras 3) al gráfico
    if not palas_definitivas.empty:
        fig.add_trace(go.Scatter(
            x=palas_definitivas['score_lesion_ajustado'][:3],
            y=palas_definitivas['score_nivel_ajustado'][:3],
            mode='markers',
            marker=dict(size=12, color='lightgreen', line=dict(width=2, color='black')),
            name='Palas Recomendadas'
        ))

        # Añadir las siguientes palas recomendadas (4ta y 5ta) al gráfico
        if len(palas_definitivas) > 3:
            fig.add_trace(go.Scatter(
                x=palas_definitivas['score_lesion_ajustado'][3:5],
                y=palas_definitivas['score_nivel_ajustado'][3:5],
                mode='markers',
                marker=dict(size=12, color='yellow', line=dict(width=2, color='black')),
                name='Palas Que Quizá Te Gusten'
            ))

    # Configurar el diseño del gráfico
    fig.update_layout(
        xaxis=dict(range=[0, 1], title="Score de Lesión"),
        yaxis=dict(range=[0, 1], title="Score de Nivel"),
        legend=dict(title="Leyenda", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=50),  # Márgenes ajustados
        height=600  # Altura del gráfico
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)


def mostrar_palas_en_tarjetas(palas_recomendadas):
    """
    Muestra las palas recomendadas en un diseño de tarjetas estilizadas.
    """
    # Crear una copia del DataFrame para evitar modificar el original
    df_mostrar = palas_recomendadas.copy()

    # Generar HTML con estilo para las tarjetas
    html_content = """
    <style>
        .card-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }
        .card {
            background-color: #f9f9f9;
            border: 2px solid #C2D6A6; /* Verde pastel */
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            width: 300px;
            padding: 15px;
            text-align: center;
            font-family: Arial, sans-serif;
        }
        .card img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
        }
        .card h3 {
            color: #333333;
            font-size: 18px;
            margin-bottom: 10px;
        }
        .card p {
            color: #666666;
            font-size: 14px;
            margin: 5px 0;
        }
        .card .highlight {
            color: #C2D6A6; /* Verde pastel */
            font-weight: bold;
        }
    </style>
    <div class="card-container">
    """

    # Generar una tarjeta por cada pala recomendada
    for _, row in df_mostrar.iterrows():
        html_content += f"""
        <div class="card">
            <img src="{row['Imagen URL']}" alt="{row['Palas']}">
            <h3>{row['Palas']}</h3>
            <p><span class="highlight">Nivel de Juego:</span> {row['Nivel de Juego']}</p>
            <p><span class="highlight">Tipo de Juego:</span> {row['Tipo de Juego']}</p>
            <p><span class="highlight">Balance:</span> {row['Balance']}</p>
            <p><span class="highlight">Dureza:</span> {row['Dureza']}</p>
            <p><span class="highlight">Cara:</span> {row['Cara']}</p>
            <p><span class="highlight">Score Nivel Pala:</span> {round(row['score_nivel_ajustado'], 2)}</p>
            <p><span class="highlight">Score Lesión Pala:</span> {round(row['score_lesion_ajustado'], 2)}</p>
        </div>
        """

    html_content += "</div>"

    # Renderizar el HTML usando components.html
    components.html(html_content, height=800, scrolling=True)
    
def mostrar_tabla_caracteristicas(df):
    """
    Muestra una tabla estilizada y responsiva utilizando HTML y CSS.

    Args:
        df (DataFrame): DataFrame con las características a mostrar.
    """
    # Generar el contenido HTML con estilo
    html_table = """
    <style>
        .table-container {
            max-width: 800px; /* Ancho máximo */
            margin: 20px auto; /* Centrado horizontal */
            overflow-x: auto; /* Habilitar desplazamiento horizontal si es necesario */
            font-family: Arial, sans-serif;
        }
        .responsive-table {
            width: 100%; /* Tabla ocupa todo el ancho del contenedor */
            border-collapse: collapse;
            font-size: 16px; /* Tamaño de fuente ajustado */
        }
        .responsive-table thead tr {
            background-color: #C2D6A6; /* Verde pastel */
            color: #333333;
        }
        .responsive-table th, .responsive-table td {
            border: 1px solid #dddddd;
            padding: 12px 15px; /* Espaciado interno */
            text-align: left; /* Alineación del texto */
        }
        .responsive-table tbody tr:nth-of-type(even) {
            background-color: #f9f9f9; /* Fondo alternado */
        }
        .responsive-table tbody tr:hover {
            background-color: #D5E8D4; /* Fondo verde claro al pasar el cursor */
        }
    </style>
    <div class="table-container">
        <table class="responsive-table">
            <thead>
                <tr>
                    <th>Característica</th>
                    <th>Valor</th>
                </tr>
            </thead>
            <tbody>
    """

    # Agregar filas al HTML dinámicamente
    for _, row in df.iterrows():
        html_table += f"""
        <tr>
            <td>{row['Característica']}</td>
            <td>{row['Valor']}</td>
        </tr>
        """

    html_table += """
            </tbody>
        </table>
    </div>
    """

    # Renderizar la tabla en Streamlit usando components.html
    components.html(html_table, height=400, scrolling=True)







