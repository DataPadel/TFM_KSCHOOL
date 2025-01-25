import ast
import json
import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from utilidades.utilidades import LABEL_MAPPING, PESO_LESION, PESO_NIVEL, SCORE_LESION, SCORE_NIVEL

# Inicializar session_state para almacenar los DataFrames
if "df" not in st.session_state:
    st.session_state["df"] = None
if "df_labelizado" not in st.session_state:
    st.session_state["df_labelizado"] = None
if "df_scaled" not in st.session_state:
    st.session_state["df_scaled"] = None


def lectura_tratamiento_datos_palas():
    """
    Realiza el tratamiento de las columnas del DataFrame almacenado en session_state como 'df_caracteristicas_palas'
    y guarda el resultado procesado en session_state como 'df'.
    """
    try:
        # Verificar si el DataFrame 'df_caracteristicas_palas' está disponible en session_state
        if "df_caracteristicas_palas" not in st.session_state or st.session_state["df_caracteristicas_palas"] is None:
            raise ValueError("El DataFrame 'df_caracteristicas_palas' no está definido en session_state.")

        # Obtener el DataFrame desde session_state
        df = st.session_state["df_caracteristicas_palas"]
        
        # Leer el archivo CSV nuevamente (opcional)
        df_csv = pd.read_csv("PNpalas_DF_3.csv")
        
         # Procesar cada fila de la columna 'data' para expandirla
        df_expandido = pd.DataFrame(df_csv['data'].apply(procesar_fila).tolist())
        
        """
        # Procesar cada fila de la columna 'data' para expandirla
        pd.DataFrame(df_csv['data'].apply(procesar_fila).tolist())
        df_expandido = df.to_csv("df_expandido.csv", index=False, encoding="utf-8")
        """
        
        # Eliminación de columnas no necesarias
        columnas_a_eliminar = ['Producto', 'Acabado', 'producto', 'acabado', 'colección jugadores', 'producto oficial', 'formato']
        if any(col in df_expandido.columns for col in columnas_a_eliminar):
            df_expandido = df_expandido.drop(columns=columnas_a_eliminar, errors='ignore')
        
        # ---------------------------------------------------------------------
        # renombrer columnas
        
        nuevos_nombres = {
            'nombre': 'Palas',
            'precio': 'Precio',
            'url': 'URL',
            'imagen_url': 'Imagen URL',
            'marca': 'Marca',
            'color': 'Color',
            'color 2': 'Color 2',
            'producto': 'Producto',
            'balance': 'Balance',
            'núcleo': 'Nucleo',
            'cara': 'Cara',
            'formato': 'Formato',
            'nivel de juego': 'Nivel de Juego',
            'forma': 'Forma',
            'superfície': 'Superficie',
            'tipo de juego': 'Tipo de Juego',
            'jugador': 'Jugador',
            'dureza': 'Dureza'
        }

        # Cambiar los nombres de las columnas
        df_expandido.rename(columns=nuevos_nombres, inplace=True)
        
        # ---------------------------------------------------------------------

        # Reemplazar None o NaN por 'No data' en todo el DataFrame
        df_expandido.fillna('No data', inplace=True)

        # ---------------------------------------------------------------------

        # Transformaciones de columnas
        if 'Precio' in df_expandido.columns:
            df_expandido['Precio'] = df_expandido['Precio'].apply(limpiar_precio)
        if 'Balance' in df_expandido.columns:
            df_expandido['Balance'] = df_expandido['Balance'].apply(tratar_balance)
        if 'Nucleo' in df_expandido.columns:
            df_expandido['Nucleo'] = df_expandido['Nucleo'].apply(tratar_nucleo)
        if 'Cara' in df_expandido.columns:
            df_expandido['Cara'] = df_expandido['Cara'].apply(tratar_cara)
        if 'Dureza' in df_expandido.columns:
            df_expandido['Dureza'] = df_expandido['Dureza'].apply(tratar_dureza)
        if 'Forma' in df_expandido.columns:
            df_expandido['Forma'] = df_expandido['Dureza'].apply(tratar_forma)
        if 'Superficie' in df_expandido.columns:
            df_expandido['Superficie'] = df_expandido['Superficie'].apply(tratar_superficie)
        if 'Nivel de Juego' in df_expandido.columns:
            df_expandido['Nivel de Juego'] = df_expandido['Nivel de Juego'].apply(tratar_nivel_juego)
        if 'Tipo de Juego' in df_expandido.columns:
            df_expandido['Tipo de Juego'] = df_expandido['Tipo de Juego'].apply(tratar_tipo_juego)
        if 'Jugador' in df_expandido.columns:
            df_expandido['Jugador'] = df_expandido['Jugador'].apply(tratar_jugador)

        # Guardar el DataFrame procesado en session_state
        st.session_state["df"] = df_expandido
        
        # Mostrar mensaje de éxito
        mostrar_mensaje("Carga de Palas/Tratamiento Datos Palas Realizado Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al leer o procesar el archivo CSV: {e}")


def limpiar_precio(precio):
    """Convierte el precio a formato float eliminando símbolos y caracteres innecesarios."""
    try:
        # Manejar valores nulos o vacíos
        if precio is None or precio == '':
            return None

        # Si ya es float, devolver directamente
        if isinstance(precio, (float, int)):
            return float(precio)

        # Convertir a cadena y limpiar caracteres no deseados
        precio = str(precio).replace('€', '').replace(',', '.').strip()

        # Intentar convertir a float
        return float(precio)
    except (ValueError, AttributeError, TypeError):
        # Devolver None si no se puede procesar
        return None

def tratar_balance(balance):
    """
    Transforma los valores de la columna 'Balance' según las reglas especificadas.
    - Si el valor es 'medio', 'alto' o 'bajo', lo deja tal cual.
    - Si contiene 'principiante' o 'intermedio', lo transforma a 'medio'.
    - Si contiene 'avanzado' o 'competición', lo transforma a 'alto'.
    - Para cualquier otro caso, devuelve 'No data'.
    """
    try:
        # Manejar valores nulos o vacíos
        if balance is None or balance == '':
            return 'No data'

        # Devolver directamente si el valor es válido
        if balance in ['medio', 'alto', 'bajo']:
            return balance

        # Verificar si es una cadena y buscar palabras clave
        if isinstance(balance, str):
            if 'principiante' in balance or 'intermedio' in balance:
                return 'medio'
            if 'avanzado' in balance or 'competición' in balance:
                return 'alto'

        # Para cualquier otro caso
        return 'No data'
    except Exception:
        # Manejar errores inesperados
        return 'No data'

def tratar_nucleo(nucleo):
    """
    Transforma los valores de la columna 'Nucleo' según las reglas especificadas:
    - Si el valor es 'soft eva', 'medium eva', 'hard eva' o 'foam', lo deja tal cual.
    - Si contiene 'ultrasoft eva', 'black eva, soft eva' o 'supersoft eva', lo transforma a 'soft eva'.
    - Si contiene 'eva, polietileno', lo transforma a 'foam'.
    - Si contiene 'black eva hr9', lo transforma a 'hard eva'.
    - Si contiene 'black eva hr3', 'eva' o 'multieva', lo transforma a 'medium eva'.
    - Para cualquier otro caso, devuelve 'No data'.
    """
    try:
        # Manejar valores nulos o vacíos
        if nucleo is None or nucleo == '':
            return 'No data'

        # Devolver directamente si el valor es válido
        if nucleo in ['soft eva', 'medium eva', 'hard eva', 'foam']:
            return nucleo

        # Verificar si es una cadena y buscar palabras clave
        if isinstance(nucleo, str):
            if any(sub in nucleo for sub in ['ultrasoft eva', 'black eva, soft eva', 'supersoft eva']):
                return 'soft eva'
            if 'eva, polietileno' in nucleo:
                return 'foam'
            if 'black eva hr9' in nucleo:
                return 'hard eva'
            if any(sub in nucleo for sub in ['black eva hr3', 'eva', 'multieva']):
                return 'medium eva'

        # Para cualquier otro caso
        return 'No data'
    except Exception:
        # Manejar errores inesperados
        return 'No data'

def tratar_cara(cara):
    """
    Transforma los valores de la columna 'Cara' según las reglas especificadas:
    - Si el valor es 'fibra de carbono' o 'fibra de vidrio', lo deja tal cual.
    - Si contiene 'carbono 12k, fibra de vidrio', 'fibra de vidrio, carbono 15k', o 'carbono, fibra de vidrio', lo transforma a 'mix'.
    - Para cualquier otro caso, devuelve 'No data'.
    """
    try:
        # Manejar valores nulos o vacíos
        if cara is None or cara == '':
            return 'No data'

        # Devolver directamente si el valor es válido
        if cara in ['fibra de carbono', 'fibra de vidrio']:
            return cara

        # Verificar si es una cadena y buscar palabras clave
        if isinstance(cara, str):
            if any(sub in cara for sub in ['carbono 12k, fibra de vidrio',
                                           'fibra de vidrio, carbono 15k',
                                           'carbono, fibra de vidrio']):
                return 'mix'

        # Para cualquier otro caso
        return 'No data'
    except Exception:
        # Manejar errores inesperados
        return 'No data'
    

def tratar_dureza(dureza):
    """Transforma los valores de la columna Dureza según las reglas especificadas."""
    if dureza is None:  # Manejar valores nulos
        return 'No data'
    if dureza in ['media', 'blanda', 'dura']:
        return dureza
    if isinstance(dureza, str):  # Verificar que sea cadena antes de buscar palabras clave
        if 'dura, media' in dureza:
            return 'dura'
        if 'media, blanda' in dureza:
            return 'blanda'
    return 'No data'

def tratar_forma(forma):
    """
    Transforma los valores de la columna 'Forma' según las reglas especificadas.
    
    - Reemplaza 'híbrida' por 'lágrima'.
    - Elimina espacios adicionales al principio y al final.
    - Convierte el valor a cadena si no lo es.
    - Devuelve 'No data' si el valor es nulo o no válido.
    """
    try:
        # Manejar valores nulos o vacíos
        if forma is None or forma == '':
            return 'No data'

        # Convertir a cadena y aplicar transformaciones
        forma = str(forma).replace('híbrida', 'lágrima').strip()

        return forma
    except Exception as e:
        # Manejar cualquier error inesperado
        return 'No data'

def tratar_superficie(superficie):
    """
    Transforma los valores de la columna 'Superficie' según las reglas especificadas.
    - Si el valor está en ['rugosa', 'lisa', 'No data'], lo deja tal cual.
    - Para cualquier otro valor, lo reemplaza por 'rugosa'.
    - Maneja valores nulos devolviendo 'No data'.
    """
    try:
        # Manejar valores nulos o vacíos
        if superficie is None or superficie == '':
            return 'No data'

        # Verificar si el valor es válido
        if superficie in ['rugosa', 'lisa', 'No data']:
            return superficie

        # Reemplazar cualquier otro valor por 'rugosa'
        return 'rugosa'
    except Exception:
        # Manejar cualquier error inesperado
        return 'No data'


def tratar_nivel_juego(nivel):
    """
    Transforma los valores de la columna 'Nivel de Juego' según las reglas especificadas:
    - Si el valor es 'No data', lo deja tal cual.
    - Si contiene 'profesional', lo transforma a 'pro'.
    - Si contiene 'avanzado / competición', 'avanzado / competición, profesional' o 'principiante / intermedio, profesional', lo transforma a 'avanzado'.
    - Si contiene 'principiante / intermedio', lo transforma a 'principiante'.
    - Para cualquier otro caso, devuelve 'No data'.
    """
    try:
        # Manejar valores nulos o vacíos
        if nivel is None or nivel == '':
            return 'No data'

        # Devolver directamente si el valor es 'No data'
        if nivel == 'No data':
            return nivel

        # Verificar si es una cadena y buscar palabras clave
        if isinstance(nivel, str):
            if 'profesional' in nivel:
                return 'pro'
            if any(sub in nivel for sub in ['avanzado / competición',
                                            'avanzado / competición, profesional',
                                            'principiante / intermedio, profesional']):
                return 'avanzado'
            if 'principiante / intermedio' in nivel:
                return 'principiante'

        # Para cualquier otro caso
        return 'No data'
    except Exception:
        # Manejar errores inesperados
        return 'No data'


def tratar_tipo_juego(tipo_juego):
    """
    Transforma los valores de la columna 'Tipo de Juego' según las reglas especificadas:
    - Si el valor es 'control', 'polivalente' o 'potencia', lo deja tal cual.
    - Si contiene 'control, potencia', lo transforma a 'polivalente'.
    - Para cualquier otro caso, devuelve 'No data'.
    """
    try:
        # Manejar valores nulos o vacíos
        if tipo_juego is None or tipo_juego == '':
            return 'No data'

        # Devolver directamente si el valor es válido
        if tipo_juego in ['control', 'polivalente', 'potencia']:
            return tipo_juego

        # Verificar si es una cadena y buscar palabras clave
        if isinstance(tipo_juego, str):
            if 'control, potencia' in tipo_juego:
                return 'polivalente'

        # Para cualquier otro caso
        return 'No data'
    except Exception:
        # Manejar errores inesperados
        return 'No data'


def tratar_jugador(jugador):
    """
    Transforma los valores de la columna 'Jugador' según las reglas especificadas:
    - Elimina valores que contienen la palabra 'junior'.
    - Mantiene solo 'hombre', 'mujer' y 'mixta'.
    - Los valores nulos, vacíos o no válidos se consideran 'mixta'.
    """
    try:
        if not jugador:  # Manejar valores nulos o vacíos
            return 'mixta'

        jugador = jugador.strip().lower()  # Eliminar espacios y convertir a minúsculas

        if 'junior' in jugador:  # Eliminar valores que contienen 'junior'
            return None

        if jugador in ['hombre', 'mujer']:
            return jugador

        # Cualquier otro caso se considera 'mixta'
        return 'mixta'
    except Exception:
        return 'mixta'




# Función para procesar cada fila del DataFrame y expandirla
def procesar_fila(fila):
    # Convertir el string en un diccionario
    fila_dict = ast.literal_eval(fila)
    producto_data = fila_dict['producto']
    
    # Transformar las características en un diccionario
    caracteristicas_dict = {item['nombre']: item['valor'] for item in producto_data.pop('caracteristicas')}
    
    # Unir las características con los demás datos
    producto_data.update(caracteristicas_dict)
    return producto_data


def mostrar_mensaje(mensaje):
    """Muestra un mensaje en consola."""
    print(mensaje)
    
def ejecutar_una_vez(func, estado_key):
    """
    Ejecuta una función solo si no ha sido ejecutada previamente en la sesión.

    Args:
        func (callable): La función a ejecutar.
        estado_key (str): Clave en st.session_state para rastrear si la función ya fue ejecutada.
    """
    if not st.session_state.get(estado_key, False):
        func()
        st.session_state[estado_key] = True
    else:
        print(f"La función '{func.__name__}' ya fue ejecutada previamente.")
   
def labelizar_columnas():
    """Labeliza las columnas del DataFrame según un mapeo especificado."""
    try:
        # Validar si "df" está disponible en session_state
        if "df" not in st.session_state or st.session_state["df"] is None:
            raise ValueError("El DataFrame no ha sido inicializado en session_state.")

        # Crear una copia para evitar modificar el original
        df_labelizado = st.session_state["df"].copy()
        

        for columna in df_labelizado.columns:
            if columna in LABEL_MAPPING:
                if "No data" not in LABEL_MAPPING[columna]:
                    LABEL_MAPPING[columna]["No data"] = 0

                # Aplicar el mapeo y manejar valores faltantes (NaN)
                df_labelizado[columna] = df_labelizado[columna].map(
                    LABEL_MAPPING[columna]
                ).fillna(0)

        # Guardar el DataFrame procesado en session_state
        st.session_state["df_labelizado"] = df_labelizado
        print("df_labelizado",df_labelizado.head())
        

        mostrar_mensaje("Labelización de Columnas de Palas Realizada Correctamente")
    except Exception as e:
        raise RuntimeError(f"Error al labelizar las columnas: {e}")

def calcular_scores():
    """Calcula los scores de lesión y nivel para cada fila."""
    try:
        if "df_labelizado" not in st.session_state or st.session_state["df_labelizado"] is None:
            raise ValueError("Calcular Scores (Funcion) . El DataFrame labelizado no ha sido inicializado.")

        df_labelizado = st.session_state["df_labelizado"]

        df_labelizado["score_lesion"] = 0
        df_labelizado["score_nivel"] = 0

        for columna in df_labelizado.columns:
            if columna in PESO_LESION:
                df_labelizado["score_lesion"] += (
                    df_labelizado[columna].map(SCORE_LESION.get(columna, {})) * PESO_LESION[columna]
                )
            if columna in PESO_NIVEL:
                df_labelizado["score_nivel"] += (
                    df_labelizado[columna].map(SCORE_NIVEL.get(columna, {})) * PESO_NIVEL[columna]
                )

        df_labelizado.fillna(0, inplace=True)
        st.session_state["df_labelizado"] = df_labelizado

        mostrar_mensaje("Cálculo de Scores y de Nivel Realizado Correctamente")

    except Exception as e:
        raise RuntimeError(f"Error al calcular los scores: {e}")

def escalar_columnas():
    """Escala las columnas seleccionadas usando MinMaxScaler."""
    try:
        if "df_labelizado" not in st.session_state or st.session_state["df_labelizado"] is None:
            raise ValueError("Escalar Columnas (Funcion). El DataFrame labelizado no ha sido inicializado.")

        scaler = MinMaxScaler()
        columnas_a_escalar = ["score_lesion", "score_nivel"]

        df_scaled = st.session_state["df_labelizado"].copy()
        df_scaled[columnas_a_escalar] = scaler.fit_transform(df_scaled[columnas_a_escalar])

        st.session_state["df_scaled"] = df_scaled
        
        print("df_scaled" , df_scaled)

        mostrar_mensaje("Columnas Escaladas Correctamente")

    except Exception as e:
        raise RuntimeError(f"Error al escalar las columnas: {e}")
    
    
def regresion_a_la_media_palas():
    """Aplica una regresión a la media a las columnas específicas y guarda el DataFrame procesado en session_state."""
    try:
        # Verificar si 'df_scaled' está inicializado en session_state
        if "df_scaled" not in st.session_state or st.session_state["df_scaled"] is None:
            raise ValueError("Regresion A La Media Palas (Funcion). El DataFrame 'df_scaled' no ha sido inicializado.")

        # Obtener el DataFrame desde session_state
        df_scaled = st.session_state["df_scaled"]

        # Definir la función para ajustar valores
        def ajustar_valor(valor, es_score_nivel):
            if es_score_nivel:
                if 0.0 <= valor <= 0.2:
                    return 0.2
                elif 0.2 < valor <= 0.3:
                    return valor * 1.3
                elif 0.3 < valor <= 0.4:
                    return valor * 1.1
                else:
                    return valor
            else:
                if 0.9 <= valor <= 1:
                    return 0.9
                elif 0.7 <= valor < 0.9:
                    return valor * 0.8
                elif 0.6 <= valor < 0.7:
                    return valor * 0.9
                elif 0.0 <= valor <= 0.2:
                    return 0.2
                elif 0.2 < valor <= 0.3:
                    return valor * 1.3
                elif 0.3 < valor <= 0.4:
                    return valor * 1.1
                else:
                    return valor

        # Aplicar ajustes a las columnas relevantes
        df_scaled['score_lesion_ajustado'] = df_scaled['score_lesion'].apply(lambda x: ajustar_valor(x, es_score_nivel=False))
        df_scaled['score_nivel_ajustado'] = df_scaled['score_nivel'].apply(lambda x: ajustar_valor(x, es_score_nivel=True))

        # Guardar el DataFrame ajustado como archivo CSV
        nombre_archivo = 'df_scaled_palas_3.0.csv'
        df_scaled.to_csv(nombre_archivo, index=False)
        
        # Guardar el DataFrame ajustado en session_state como 'df_scaled_palas'
        st.session_state["df_scaled_palas"] = df_scaled
        print("Dataframe ajustado df_sacled_palas",st.session_state["df_scaled_palas"])

        print(f"Archivo '{nombre_archivo}' guardado correctamente.")
        print("DataFrame ajustado guardado en session_state como 'df_scaled_palas'.")

    except Exception as e:
        raise RuntimeError(f"Error al aplicar la regresión a la media: {e}")


def limpieza_df_expandido(df_expandido):
    
    df_expandido = df_expandido.drop(['producto', 'acabado', 'colección jugadores', 'producto oficial','formato'], axis=1)
        
    # Diccionario con los nuevos nombres de las columnas
    nuevos_nombres = {
            'nombre': 'Palas',
            'precio': 'Precio',
            'url': 'URL',
            'imagen_url': 'Imagen URL',
            'marca': 'Marca',
            'color': 'Color',
            'color 2': 'Color 2',
            'producto': 'Producto',
            'balance': 'Balance',
            'núcleo': 'Nucleo',
            'cara': 'Cara',
            'formato': 'Formato',
            'nivel de juego': 'Nivel de Juego',
            'forma': 'Forma',
            'superfície': 'Superficie',
            'tipo de juego': 'Tipo de Juego',
            'jugador': 'Jugador',
            'dureza': 'Dureza'
     }

    # Cambiar los nombres de las columnas
    df_expandido.rename(columns=nuevos_nombres, inplace=True)

    filas_con_none = df_expandido.isnull().any(axis=1).sum()

    print(f'Número de filas con al menos un None o NaN: {filas_con_none}')

    # Asumimos que ya tienes un DataFrame llamado 'df'

    # Reemplazar None o NaN por 'No data' en todo el DataFrame
    df_expandido.fillna('No data', inplace=True)

    """
    #Ajustando Columnas

    df_csv['Forma'] = df_csv['Forma'].apply(lambda x: str(x.replace('híbrida', 'lágrima').replace(',', '.').strip()))
    df_csv['Superficie'] = df_csv['Superficie'].apply(lambda x: x if x in ['rugosa', 'lisa', 'No data'] else 'rugosa')
    # Aplicamos la función lambda para transformar los valores
    df_csv['Balance'] = df_csv['Balance'].apply(lambda x: 
        x if x == 'medio' or x == 'alto' or x == 'bajo'                               
        else 'medio' if 'principiante' in x or 'intermedio' in x 
        else 'alto' if 'avanzado' in x or 'competición' in x 
        else 'No data')

 
    df_csv['Nucleo'] = df_csv['Nucleo'].apply(
        lambda x: (
            x if x in ['soft eva', 'medium eva', 'hard eva', 'foam']
            else 'soft eva' if any(sub in x for sub in ['ultrasoft eva', 'black eva, soft eva', 'supersoft eva'])
            else 'foam' if 'eva, polietileno' in x
            else 'hard eva' if 'black eva hr9' in x
            else 'medium eva' if any(sub in x for sub in ['black eva hr3', 'eva', 'multieva'])
            else 'No data'
        )
    )
    
    
    df_csv['Cara'] = df_csv['Cara'].apply(lambda x: 
    x if x == 'fibra de carbono' or x == 'fibra de vidrio' 
    else 'mix' if 'carbono 12k, fibra de vidrio' in x or 'fibra de vidrio, carbono 15k' in x or 'carbono, fibra de vidrio' in x
    else 'No data')
    
    
    df_csv['Dureza'] = df_csv['Dureza'].apply(lambda x: 
    x if x == 'media' or x == 'blanda' or x == 'dura'
    else 'dura' if 'dura, media'in x 
    else 'blanda' if 'media, blanda' in x 
    else 'No data')
    
    
    df_csv['Nivel de Juego'] = df_csv['Nivel de Juego'].apply(lambda x: 
    x if x == 'No data' else
    'pro' if 'profesional' in x else
    'avanzado' if 'avanzado / competición' in x or 'avanzado / competición, profesional' in x or 'principiante / intermedio, profesional' in x else
    'principiante' if 'principiante / intermedio' in x else
    None 
    )
    
    
    df_csv['Tipo de Juego'] = df_csv['Tipo de Juego'].apply(lambda x:
    x if x == 'control' or x == 'polivalente' or x == 'potencia'
    else 'polivalente' if 'control, potencia' in x
    else 'No data' )
    
    
    #Quitamos 18 palas de pickleball

    df_csv = df_csv[~df_csv['Palas'].str.contains('PICKLEBALL', na=False)]
    df_csv = df_csv[~df_csv['Forma'].str.contains('beach tennis', na=False)]
    
    #Nos quedamos con los valores hombre, mujer y mixta. Los valores sin datos los consideramos mixta.

    df_csv['Jugador'] = df_csv['Jugador'].apply(lambda x:
    x if x in ['hombre', 'mujer']
    else 'mixta' 
    )
    
    # Ver el resultado
    print(df_csv[['Jugador']])
    
    
    #Existen 4 palas que se repiten en el dataset, se eliminan los duplicados

    df_csv = df_csv.drop_duplicates(subset='Palas') 
    
    
    variables = mostrar_variables_columnas(df_csv)
    """
    
    
    
    
def mostrar_variables_columnas(df):
    """
    Muestra las variables únicas presentes en cada columna del DataFrame.

    Args:
    - df (pd.DataFrame): El DataFrame a analizar.

    Returns:
    - dict: Un diccionario donde las claves son los nombres de las columnas y
            los valores son listas de las variables únicas en cada columna.
    """
    variables_por_columna = {}
    for columna in df.columns:
        variables_por_columna[columna] = df[columna].unique().tolist()
        print(f"Columna: {columna}")
        print(f"Variables: {variables_por_columna[columna]}")
        print("-" * 40)
    return variables_por_columna


# Registro global para controlar mensajes únicos
mensajes_mostrados = set()

def mostrar_mensaje(mensaje):
    """Muestra un mensaje solo si no ha sido mostrado antes."""
    if mensaje not in mensajes_mostrados:
        print(mensaje)
        mensajes_mostrados.add(mensaje)

def ejecutar_una_vez(func, estado_key):
    """
    Ejecuta una función solo si no ha sido ejecutada previamente en la sesión.

    Args:
        func (callable): La función a ejecutar.
        estado_key (str): Clave en st.session_state para rastrear si la función ya fue ejecutada.
    """
    if not st.session_state.get(estado_key, False):
        func()
        st.session_state[estado_key] = True
    else:
        print(f"La función '{func.__name__}' ya fue ejecutada previamente.")
    
    

    



