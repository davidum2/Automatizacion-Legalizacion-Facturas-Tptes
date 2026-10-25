from datetime import datetime
from babel.dates import format_date
import locale

def convert_fecha_to_texto(fecha_str):
    """
    Convierte una fecha en formato YYYY-MM-DD a texto en español.
    
    Args:
        fecha_str (str): Fecha en formato YYYY-MM-DD
        
    Returns:
        str: Fecha formateada en texto español
    """
    try:
        # Convertir la fecha a objeto datetime
        fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
        
        # Establecer la configuración regional a español
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except:
            # Alternativa para Windows
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
            except:
                pass  # Si no se puede establecer, usar la configuración por defecto
        
        # Formatear la fecha en español con la primera letra en mayúscula
        fecha_formateada = format_date(fecha_dt, format="d 'de' MMMM 'del' y", locale='es')
        fecha_formateada = fecha_formateada[0].upper() + fecha_formateada[1:]
        
        return fecha_formateada
    except ValueError:
        raise ValueError("La fecha debe estar en formato YYYY-MM-DD")

def format_fecha_mensaje(fecha_str):
    """
    Formatea la fecha del mensaje en un formato especial.
    
    Args:
        fecha_str (str): Fecha en formato YYYY-MM-DD
        
    Returns:
        str: Fecha formateada para mensajes
    """
    try:
        # Convertir la fecha a objeto datetime
        fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
        
        # Establecer la configuración regional a español
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except:
            # Alternativa para Windows
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
            except:
                pass
        
        # Formatear la fecha en formato especial
        fecha_formateada = format_date(fecha_dt, format="d MMM y", locale='es').upper()
        
        # Reemplazar abreviaturas de meses
        for mes_abr, mes_nuevo in [
            ('ENE', 'Ene.'), ('FEB', 'Feb.'), ('MAR', 'Mar.'), ('ABR', 'Abr.'),
            ('MAY', 'May.'), ('JUN', 'Jun.'), ('JUL', 'Jul.'), ('AGO', 'Ago.'),
            ('SEP', 'Sep.'), ('OCT', 'Oct.'), ('NOV', 'Nov.'), ('DIC', 'Dic.')
        ]:
            fecha_formateada = fecha_formateada.replace(mes_abr, mes_nuevo)
        
        return fecha_formateada
    except ValueError:
        raise ValueError("La fecha debe estar en formato YYYY-MM-DD")

def format_monto(monto):
    """
    Formatea un monto como moneda.
    
    Args:
        monto (float): Monto a formatear
        
    Returns:
        str: Monto formateado como moneda
    """
    return "$ {:,.2f}".format(monto)

def formatear_combustible(diccionario):
    """
    Identifica y formatea conceptos de combustible desde un diccionario de conceptos.
    
    Args:
        diccionario: Diccionario con conceptos de la factura
        
    Returns:
        str: Descripción formateada del combustible
    """
    # Palabras clave para identificar tipos de combustible
    diesel_keywords = ['diesel', 'diésel', 'gasóleo']
    gasolina_keywords = ['gasolina', 'premium', 'magna', 'regular', 'sin', 'verde', 'roja']
    
    litros_diesel = 0
    litros_gasolina = 0
    
    # Buscar en todas las claves del diccionario
    for concepto, cantidad in diccionario.items():
        concepto_lower = concepto.lower()
        
        # Verificar si es diesel
        if any(keyword in concepto_lower for keyword in diesel_keywords):
            litros_diesel += cantidad
        
        # Verificar si es gasolina
        elif any(keyword in concepto_lower for keyword in gasolina_keywords):
            litros_gasolina += cantidad
        
        # Si contiene la palabra "combustible" o "petrolífero" pero no se identificó tipo específico
        elif any(keyword in concepto_lower for keyword in ['combustible', 'petrolifero', 'petrolífero']):
            # Verificar si hay indicios de diesel
            if any(keyword in concepto_lower for keyword in ['pesado', 'alto azufre']):
                litros_diesel += cantidad
            else:
                # Por defecto, asumimos que es gasolina
                litros_gasolina += cantidad
    
    # Si se identificaron ambos tipos de combustible
    if litros_diesel > 0 and litros_gasolina > 0:
        return f"{litros_diesel:.3f} Lts. de diesel y {litros_gasolina:.3f} Lts. de gasolina"
    
    # Si solo se identificó diesel
    elif litros_diesel > 0:
        return f"{litros_diesel:.3f} Lts. de diesel"
    
    # Si solo se identificó gasolina
    elif litros_gasolina > 0:
        return f"{litros_gasolina:.3f} Lts. de gasolina"
    
    # Si no se identificó ningún combustible específico, buscar por unidades
    else:
        litros_total = 0
        for concepto, cantidad in diccionario.items():
            concepto_lower = concepto.lower()
            # Buscar indicios de que el concepto es medido en litros
            if any(unit in concepto_lower for unit in ['lt', 'lts', 'litro', 'litros', '(lt)', '(l)']):
                litros_total += cantidad
        
        if litros_total > 0:
            return f"{litros_total:.3f} Lts. de combustible"
    
    # Si nada de lo anterior funciona, devolver un mensaje genérico o los conceptos originales
    conceptos_str = ", ".join([f"{concepto}: {cantidad}" for concepto, cantidad in diccionario.items()])
    if len(conceptos_str) > 100:  # Si es muy largo, cortarlo
        conceptos_str = conceptos_str[:97] + "..."
    
    return f"combustible ({conceptos_str})"