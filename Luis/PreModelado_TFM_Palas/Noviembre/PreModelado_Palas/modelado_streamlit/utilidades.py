from sklearn.neighbors import NearestNeighbors

#DICCIONARIOS

# Diccionario de mapeo para convertir valores numéricos a etiquetas descriptivas

LABEL_MAPPING = {
    "Balance": {0: "No data", 1: "Bajo", 2: "Medio", 3: "Alto"},
    "Dureza": {0: "No data", 1: "Blanda", 2: "Media", 3: "Dura"},
    "Nivel de Juego": {0: "No Data", 1: "Iniciacion", 2: "Intermedio", 3: "Avanzado"},
    "Forma": {0: "No Data", 1: "Redonda", 2: "Lágrima", 3: "Diamante"},
    "Tipo de Juego": {0: "No Data", 1: "Control", 2: "Polivalente", 3: "Potencia"}
}



# Diccionario de mapeo para convertir valores numéricos a etiquetas descriptivas

LABEL_MAPPING_TIPO_DE_JUEGO = {0: "No Related", 1: "Control", 2: "Polivalente", 3: "Potencia"}

#Diccionario con las opciones y valores asociados de los selectbox  del formulario

OPCIONES_SELECTBOX_FORMULARIO = {
    "opciones_peso":{"Entre 51 y 70 Kg": 0, "Entre 71 y 90 Kg": 0, "Más de 91 Kg": 0.5},
    "opciones_altura": {"Entre 1,51 y 1,70 metros": 0, "Entre 1,71 y 1,80 metros": 0, "Mas de 1,80 metros": 0.5},
    "opciones_nivel_de_juego":{"Iniciacion": 0, "Intermedio": 1, "Avanzado": 2},
    "opciones_tipo_de_juego": {"Ofensivo": 1, "Defensivo": 0},
    "opciones_balance": {"Medio": 0, "Alto": 0.5},
    "opciones_horas_semana":{"Menos de 3,5 horas": 0, "Mas de 3.5 horas": 0.5},
    "opciones_rango_precio": {"Menos de 100": 0, "Entre 100 y 200": 0, "Mas de 200": 0},
    "opciones_rango_juego": {"Drive": 0, "Reves": 0.5},
    "opciones_lesiones_antiguas":{"Lumbares": 0.5,"Epicondilitis": 0.15,"Gemelos o fascitis": 0.5,"Cervicales": 0.25,"Hombros": 0.5,"Ninguna": 0},
    "opciones_frecuencia_lesion": {"Siempre que juego defensivamente": 0.5,"Siempre que juego ofensivamente": 0.5,"Casi siempre que juego intensamente": 0.25,"Rara vez cuando juego": 0.15},
    "opciones_cuanto_lesion": {"Menos de 3 meses": 0.5,"Entre 3 y 6 meses": 0.25,"Mas de 6 meses": 0.15}
}

#Diccionario para la division de las Palas por precio (Aplicable division al clickar checkbox)
PRECIO_MAXIMO_MAP= {"Menos de 100": 100,"Entre 100 y 200 ": 200,"Mas de 200 ": float('inf')}

#----------------------------------------------------------------------------------------------------------------------------------------------------

#ALGORITMO KNN

# Encontrar vecinos más cercanos con KNN considerando el precio si está seleccionado
def encontrar_vecinos_mas_cercanos_knn(df_palas, x_random, y_random, z_random, considerar_precio, precio_maximo):
    knn_features = ['score_lesion', 'score_nivel', 'Score_Escalar']
    
    if considerar_precio:
        knn_features.append('Precio')
        df_palas = df_palas[df_palas['Precio'] <= precio_maximo]
    
    knn = NearestNeighbors(n_neighbors=3)
    knn.fit(df_palas[knn_features])
    
    reference_point = [[x_random, y_random, z_random] + ([precio_maximo] if considerar_precio else [])]
    
    distances, indices = knn.kneighbors(reference_point)
    
    palas_recomendadas = df_palas.iloc[indices[0]]
    
    # Mapear valores numéricos a etiquetas descriptivas
    palas_recomendadas["Nivel de Juego"] = palas_recomendadas["Nivel de Juego"].map(LABEL_MAPPING["Nivel de Juego"])
    palas_recomendadas["Tipo de Juego"] = palas_recomendadas["Tipo de Juego"].map(LABEL_MAPPING["Tipo de Juego"])
    palas_recomendadas["Balance"] = palas_recomendadas["Balance"].map(LABEL_MAPPING["Balance"])
    
    return palas_recomendadas[['Palas', 'Nivel de Juego', 'Tipo de Juego', 'Balance', 'Precio']]
    