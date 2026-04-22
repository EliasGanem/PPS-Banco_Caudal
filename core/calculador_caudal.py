def calcular_caudal_masico(peso_inicial: float, peso_final: float, tiempo: float) -> float:
    """
    Calcula el caudal másico del fluido.
    
    Args:
        peso_inicial: Peso al inicio del ensayo (kg).
        peso_final: Peso al finalizar el ensayo (kg).
        tiempo: Tiempo de duración del ensayo (s).
        
    Returns:
        float: Caudal másico en kg/s.
    """
    if tiempo <= 0:
        raise ValueError("El tiempo debe ser mayor a 0 para calcular el caudal.")
    return (peso_final - peso_inicial) / tiempo


def calcular_caudal_volumetrico(peso_inicial: float, peso_final: float, tiempo: float, densidad: float) -> float:
    """
    Calcula el caudal volumétrico del fluido.
    
    Args:
        peso_inicial: Peso al inicio del ensayo (kg).
        peso_final: Peso al finalizar el ensayo (kg).
        tiempo: Tiempo de duración del ensayo (s).
        densidad: Densidad del fluido (kg/m^3).
        
    Returns:
        float: Caudal volumétrico en m^3/s.
    """
    if densidad <= 0:
        raise ValueError("La densidad debe ser mayor a 0.")
    caudal_masico = calcular_caudal_masico(peso_inicial, peso_final, tiempo)
    return caudal_masico / densidad
