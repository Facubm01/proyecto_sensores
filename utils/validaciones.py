"""
Módulo de validaciones para inputs del usuario
"""

import re
from datetime import datetime
from typing import Tuple, Optional
from colorama import Fore


def validar_email(email: str) -> Tuple[bool, str]:
    """
    Valida formato de email
    
    Args:
        email: Email a validar
    
    Returns:
        (es_valido, mensaje_error)
    """
    if not email or not email.strip():
        return False, "El email no puede estar vacío"
    
    email = email.strip().lower()
    
    # Patrón básico de email
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(patron, email):
        return False, "Formato de email inválido. Debe ser: usuario@dominio.com"
    
    # Validaciones adicionales
    if email.count('@') != 1:
        return False, "El email debe tener exactamente un símbolo @"
    
    partes = email.split('@')
    usuario = partes[0]
    dominio = partes[1]
    
    if len(usuario) < 1:
        return False, "El nombre de usuario del email no puede estar vacío"
    
    if len(usuario) > 64:
        return False, "El nombre de usuario del email es demasiado largo (máx. 64 caracteres)"
    
    if '.' not in dominio:
        return False, "El dominio del email debe tener al menos un punto"
    
    if dominio.startswith('.') or dominio.endswith('.'):
        return False, "El dominio no puede empezar o terminar con punto"
    
    if '..' in email:
        return False, "El email no puede tener puntos consecutivos"
    
    return True, ""


def validar_password(password: str) -> Tuple[bool, str]:
    """
    Valida contraseña
    
    Args:
        password: Contraseña a validar
    
    Returns:
        (es_valido, mensaje_error)
    """
    if not password:
        return False, "La contraseña no puede estar vacía"
    
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    if len(password) > 128:
        return False, "La contraseña es demasiado larga (máx. 128 caracteres)"
    
    return True, ""


def validar_nombre(nombre: str) -> Tuple[bool, str]:
    """
    Valida nombre completo
    
    Args:
        nombre: Nombre a validar
    
    Returns:
        (es_valido, mensaje_error)
    """
    if not nombre or not nombre.strip():
        return False, "El nombre no puede estar vacío"
    
    nombre = nombre.strip()
    
    if len(nombre) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"
    
    if len(nombre) > 100:
        return False, "El nombre es demasiado largo (máx. 100 caracteres)"
    
    # Permitir letras, espacios, guiones y apóstrofes
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\']+$', nombre):
        return False, "El nombre solo puede contener letras, espacios, guiones y apóstrofes"
    
    # No puede ser solo espacios
    if not nombre.replace(' ', ''):
        return False, "El nombre no puede ser solo espacios"
    
    return True, ""


def validar_fecha(fecha_str: str, formato: str = "%Y-%m-%d") -> Tuple[bool, str, Optional[datetime]]:
    """
    Valida formato de fecha
    
    Args:
        fecha_str: Fecha en formato string
        formato: Formato esperado (default: YYYY-MM-DD)
    
    Returns:
        (es_valido, mensaje_error, fecha_datetime)
    """
    if not fecha_str or not fecha_str.strip():
        return False, "La fecha no puede estar vacía", None
    
    fecha_str = fecha_str.strip()
    
    try:
        fecha = datetime.strptime(fecha_str, formato)
        return True, "", fecha
    except ValueError:
        return False, f"Formato de fecha inválido. Use: {formato.replace('%Y', 'YYYY').replace('%m', 'MM').replace('%d', 'DD')}", None


def validar_rango_fechas(fecha_inicio: str, fecha_fin: str) -> Tuple[bool, str]:
    """
    Valida que fecha_inicio sea anterior a fecha_fin
    
    Args:
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
    
    Returns:
        (es_valido, mensaje_error)
    """
    valido_inicio, mensaje_inicio, fecha_ini = validar_fecha(fecha_inicio)
    if not valido_inicio:
        return False, f"Fecha inicio: {mensaje_inicio}"
    
    valido_fin, mensaje_fin, fecha_fin_dt = validar_fecha(fecha_fin)
    if not valido_fin:
        return False, f"Fecha fin: {mensaje_fin}"
    
    if fecha_ini > fecha_fin_dt:
        return False, "La fecha de inicio debe ser anterior a la fecha de fin"
    
    return True, ""


def validar_numero_positivo(valor: str, tipo: type = float, min_valor: Optional[float] = None, max_valor: Optional[float] = None) -> Tuple[bool, str, Optional[float]]:
    """
    Valida número positivo
    
    Args:
        valor: Valor a validar
        tipo: int o float
        min_valor: Valor mínimo permitido
        max_valor: Valor máximo permitido
    
    Returns:
        (es_valido, mensaje_error, valor_convertido)
    """
    if not valor or not valor.strip():
        return False, "El valor no puede estar vacío", None
    
    try:
        if tipo == int:
            num = int(valor)
        else:
            num = float(valor)
        
        if num < 0:
            return False, "El valor debe ser positivo", None
        
        if min_valor is not None and num < min_valor:
            return False, f"El valor debe ser mayor o igual a {min_valor}", None
        
        if max_valor is not None and num > max_valor:
            return False, f"El valor debe ser menor o igual a {max_valor}", None
        
        return True, "", num
    
    except ValueError:
        return False, f"Debe ingresar un número válido ({tipo.__name__})", None


def validar_no_vacio(valor: str, nombre_campo: str = "campo") -> Tuple[bool, str]:
    """
    Valida que un campo no esté vacío
    
    Args:
        valor: Valor a validar
        nombre_campo: Nombre del campo para el mensaje de error
    
    Returns:
        (es_valido, mensaje_error)
    """
    if not valor or not valor.strip():
        return False, f"El {nombre_campo} no puede estar vacío"
    
    return True, ""


def validar_longitud(valor: str, min_len: Optional[int] = None, max_len: Optional[int] = None, nombre_campo: str = "campo") -> Tuple[bool, str]:
    """
    Valida longitud de un string
    
    Args:
        valor: Valor a validar
        min_len: Longitud mínima
        max_len: Longitud máxima
        nombre_campo: Nombre del campo para el mensaje de error
    
    Returns:
        (es_valido, mensaje_error)
    """
    if not valor:
        valor = ""
    
    longitud = len(valor.strip())
    
    if min_len is not None and longitud < min_len:
        return False, f"El {nombre_campo} debe tener al menos {min_len} caracteres"
    
    if max_len is not None and longitud > max_len:
        return False, f"El {nombre_campo} debe tener máximo {max_len} caracteres"
    
    return True, ""


def validar_id(id_str: str, nombre_campo: str = "ID", min_valor: int = 1) -> Tuple[bool, str, Optional[int]]:
    """
    Valida que sea un ID válido (entero positivo)
    
    Args:
        id_str: ID a validar
        nombre_campo: Nombre del campo para el mensaje
        min_valor: Valor mínimo permitido
    
    Returns:
        (es_valido, mensaje_error, id_convertido)
    """
    if not id_str or not id_str.strip():
        return False, f"El {nombre_campo} no puede estar vacío", None
    
    try:
        id_num = int(id_str.strip())
        
        if id_num < min_valor:
            return False, f"El {nombre_campo} debe ser mayor o igual a {min_valor}", None
        
        return True, "", id_num
    
    except ValueError:
        return False, f"El {nombre_campo} debe ser un número entero válido", None

