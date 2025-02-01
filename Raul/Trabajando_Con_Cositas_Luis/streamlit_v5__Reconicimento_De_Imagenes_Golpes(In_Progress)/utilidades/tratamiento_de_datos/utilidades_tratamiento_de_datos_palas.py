import ast
import streamlit as st


# METODOS PARA LIMPIAR Y TRATAR LOS DATOS DE LAS PALAS


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
    
    
# METODOS GENERICOS UTILIZADOS PARA EL TRATAMIENTO DE LOS DATOS DE LAS PALAS 

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


# Registro global para controlar mensajes únicos
mensajes_mostrados = set()

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
   
