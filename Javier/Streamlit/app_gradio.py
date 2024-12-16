import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import gradio as gr

# Diccionario de mapeo para convertir valores numéricos a etiquetas descriptivas
label_mapping = {
    "Balance": {0: "No data", 1: "bajo", 2: "medio", 3: "alto"},
    "Dureza": {0: "No data", 1: "blanda", 2: "media", 3: "dura"},
    "Nivel de Juego": {0: "No data", 1: "principiante", 2: "avanzado", 3: "pro"},
    "Forma": {0: "No data", 1: "redonda", 2: "lágrima", 3: "diamante"},
    "Tipo de Juego": {0: "No data", 1: "control", 2: "polivalente", 3: "potencia"}
}

# Función para cargar y validar los DataFrames
def cargar_dataframes():
    df_form = pd.read_json('dataframe_final_formulario.json', lines=True)
    df_palas = pd.read_csv('df_scaled_palas.csv')
    if 'Score_Escalar' not in df_form.columns:
        raise KeyError("La columna 'Score_Escalar' no existe en 'dataframe_final_formulario.json'.")
    return df_form, df_palas

# Sincronizar DataFrames
def sincronizar_dataframes(df_form, df_palas):
    if len(df_form) != len(df_palas):
        min_rows = min(len(df_form), len(df_palas))
        df_form = df_form.iloc[:min_rows]
        df_palas = df_palas.iloc[:min_rows]
    df_palas['Score_Escalar'] = df_form['Score_Escalar'].values
    return df_form, df_palas

# Renombrar columnas del DataFrame df_form
def renombrar_columnas(df_form):
    df_form.rename(columns={
        "Cuantas horas juegas a la semana": "Horas a la Semana",
        "Indique su peso": "Peso",
        "Indique su altura": "Altura",
        "Indique su Lado de Juego": "Lado de Juego",
        "Indique su nivel de juego": "Nivel de Juego",
        "Que tipo de balance te gusta": "Balance",
        "Has tenido alguna de las siguientes lesiones ...": "Lesiones Antiguas",
        "Con que frecuencia": "Frecuencia Lesion",
        "Hace cuanto": "Tiempo entre Lesiones"
    }, inplace=True)

    # Eliminar columnas no deseadas
    df_form = df_form.drop(columns=["Score", "Score_Escalar", "Rango de precio dispuesto a pagar"], errors='ignore')
    return df_form

# Mostrar detalles del registro seleccionado en forma tabular
def mostrar_detalles_registro_tabular(df_form, index):
    # Seleccionar la fila correspondiente
    selected_row = df_form.iloc[index]

    # Convertir el registro a un DataFrame con columnas Característica y Valor
    detalles_df = pd.DataFrame({
        "Característica": selected_row.index,
        "Valor": selected_row.values
    })

    return detalles_df

# Encontrar vecinos más cercanos con columnas específicas
def encontrar_vecinos_mas_cercanos(df_palas, x_random, y_random):
    reference_points = pd.DataFrame({
        'score_lesion': [x_random] * 3,
        'score_nivel': [y_random] * 3,
        'Balance': [1.0, 2.0, 3.0]
    })
    
    # Preparar datos relevantes
    palas_data = df_palas[['Palas', 'Nivel de Juego', 'Tipo de Juego', 'Balance', 'Precio', 'Dureza', 'Forma']].copy()

    # Convertir valores numéricos a etiquetas descriptivas
    for columna in ['Nivel de Juego', 'Tipo de Juego', 'Balance', 'Dureza', 'Forma']:
        palas_data[columna] = palas_data[columna].map(label_mapping[columna])

    # Entrenar kNN con las columnas relevantes
    knn = NearestNeighbors(n_neighbors=1)
    knn.fit(df_palas[['score_lesion', 'score_nivel', 'Balance']])
    
    resultados_tabular = []
    for _, point in reference_points.iterrows():
        distances, indices = knn.kneighbors([point])
        closest_point = palas_data.iloc[indices[0][0]].to_dict()
        closest_point['Punto'] = f"Punto {point['Balance']}"
        resultados_tabular.append(closest_point)
    
    return pd.DataFrame(resultados_tabular)

# Mostrar detalles de una pala seleccionada
def mostrar_detalle_pala(pala_nombre, vecinos_df):
    detalles_pala = vecinos_df[vecinos_df["Palas"] == pala_nombre]
    return detalles_pala.reset_index(drop=True)

# Función principal para Gradio
def main(index):
    try:
        # Cargar y sincronizar DataFrames
        df_form, df_palas = cargar_dataframes()
        df_form, df_palas = sincronizar_dataframes(df_form, df_palas)

        # Renombrar y limpiar columnas del DataFrame
        df_form = renombrar_columnas(df_form)

        # Seleccionar fila del DataFrame
        selected_row = df_palas.iloc[index]
        x_random, y_random, z_random = selected_row['score_lesion'], selected_row['score_nivel'], selected_row['Score_Escalar']

        # Crear gráfico interactivo (opcional)
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(df_palas['score_lesion'], df_palas['score_nivel'], df_palas['Score_Escalar'], color='blue', label='Datos Palas')
        ax.scatter(x_random, y_random, z_random, color='red', s=200, label='Pala Seleccionada')
        ax.set_xlabel('Lesión (%)')
        ax.set_ylabel('Nivel (%)')
        ax.set_zlabel('Formulario (%)')
        ax.legend()

        # Encontrar vecinos más cercanos
        vecinos_df = encontrar_vecinos_mas_cercanos(df_palas, x_random, y_random)

        # Mostrar detalles del registro seleccionado en forma tabular
        detalles_registro_df = mostrar_detalles_registro_tabular(df_form, index)

        return fig, vecinos_df, detalles_registro_df
    
    except Exception as e:
        return None, None, f"Error: {str(e)}"

# Interfaz Gradio con tabla personalizada y eventos con paleta de colores integrada
with gr.Blocks(css=".gradio-container {background-color: #FFFFFF; color: #0072CE;}") as demo:
    
    with gr.Row():
        with gr.Column(scale=1):  
            gr.Markdown("<h1 style='color:#3CB043;'>Plai Padel Pro</h1>")
        
        with gr.Column(scale=1):  
            index_slider = gr.Slider(0, 1000, step=1, label="Índice del Registro")
    
    with gr.Row():
        with gr.Column(scale=1):
            registro_detalle_tabla = gr.Dataframe(
                label="Detalles del Registro Seleccionado",
                column_widths=[50, 50],
                interactive=False       
            )
        
        with gr.Column(scale=2):
            output_plot = gr.Plot(label="Gráfico Interactivo")
    
    with gr.Row():
        output_table = gr.Dataframe(label="Vecinos Más Cercanos", interactive=True)
    
    with gr.Row():
        detalle_output = gr.Dataframe(label="Detalle de la Pala Seleccionada")

    # Conexión de eventos
    index_slider.change(fn=main, inputs=index_slider, outputs=[output_plot, output_table, registro_detalle_tabla])
    
demo.launch(share=True)