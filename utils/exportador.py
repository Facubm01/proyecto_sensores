"""
Módulo para exportar datos a diferentes formatos
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from colorama import Fore, Style


def exportar_json(datos: List[Dict[str, Any]], nombre_archivo: str = None) -> str:
    """
    Exporta datos a formato JSON
    
    Args:
        datos: Lista de diccionarios con los datos
        nombre_archivo: Nombre del archivo (si None, genera automático)
    
    Returns:
        Ruta del archivo creado
    """
    if not nombre_archivo:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"export_{timestamp}.json"
    
    # Asegurar extensión
    if not nombre_archivo.endswith('.json'):
        nombre_archivo += '.json'
    
    # Crear directorio exports si no existe
    directorio = Path("exports")
    directorio.mkdir(exist_ok=True)
    
    ruta_completa = directorio / nombre_archivo
    
    try:
        with open(ruta_completa, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"{Fore.GREEN}✓ Datos exportados a: {ruta_completa}{Style.RESET_ALL}")
        return str(ruta_completa)
    
    except Exception as e:
        print(f"{Fore.RED}✗ Error exportando JSON: {e}{Style.RESET_ALL}")
        return None


def exportar_csv(datos: List[Dict[str, Any]], nombre_archivo: str = None) -> str:
    """
    Exporta datos a formato CSV
    
    Args:
        datos: Lista de diccionarios con los datos
        nombre_archivo: Nombre del archivo (si None, genera automático)
    
    Returns:
        Ruta del archivo creado
    """
    if not datos:
        print(f"{Fore.YELLOW}⚠ No hay datos para exportar{Style.RESET_ALL}")
        return None
    
    if not nombre_archivo:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"export_{timestamp}.csv"
    
    # Asegurar extensión
    if not nombre_archivo.endswith('.csv'):
        nombre_archivo += '.csv'
    
    # Crear directorio exports si no existe
    directorio = Path("exports")
    directorio.mkdir(exist_ok=True)
    
    ruta_completa = directorio / nombre_archivo
    
    try:
        # Obtener todas las claves posibles
        todas_claves = set()
        for item in datos:
            todas_claves.update(item.keys())
        
        # Ordenar claves
        claves_ordenadas = sorted(todas_claves)
        
        with open(ruta_completa, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=claves_ordenadas)
            writer.writeheader()
            
            for item in datos:
                # Convertir valores complejos a string
                fila = {}
                for clave in claves_ordenadas:
                    valor = item.get(clave, '')
                    if isinstance(valor, (dict, list)):
                        valor = json.dumps(valor, ensure_ascii=False)
                    fila[clave] = valor
                
                writer.writerow(fila)
        
        print(f"{Fore.GREEN}✓ Datos exportados a: {ruta_completa}{Style.RESET_ALL}")
        return str(ruta_completa)
    
    except Exception as e:
        print(f"{Fore.RED}✗ Error exportando CSV: {e}{Style.RESET_ALL}")
        return None


def exportar_resultado_proceso(resultado: Dict[str, Any], solicitud_id: int, 
                               formato: str = 'json') -> str:
    """
    Exporta el resultado de un proceso
    
    Args:
        resultado: Diccionario con el resultado del proceso
        solicitud_id: ID de la solicitud
        formato: 'json' o 'csv'
    
    Returns:
        Ruta del archivo creado
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if formato.lower() == 'json':
        nombre = f"proceso_{solicitud_id}_{timestamp}.json"
        return exportar_json([resultado], nombre)
    elif formato.lower() == 'csv':
        # Aplanar resultado para CSV
        datos_planos = []
        for clave, valor in resultado.items():
            if isinstance(valor, (dict, list)):
                datos_planos.append({
                    'campo': clave,
                    'valor': json.dumps(valor, ensure_ascii=False)
                })
            else:
                datos_planos.append({
                    'campo': clave,
                    'valor': valor
                })
        
        nombre = f"proceso_{solicitud_id}_{timestamp}.csv"
        return exportar_csv(datos_planos, nombre)
    else:
        print(f"{Fore.RED}✗ Formato no soportado: {formato}{Style.RESET_ALL}")
        return None


