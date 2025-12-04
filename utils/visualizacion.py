"""
Módulo de visualización de datos con gráficos ASCII
"""

import math
from colorama import Fore, Style
from typing import List, Dict, Any


def grafico_temperatura(datos: List[Dict[str, Any]], ancho: int = 60, alto: int = 15):
    """
    Genera un gráfico ASCII de temperatura
    
    Args:
        datos: Lista de diccionarios con 'fecha' y 'temperatura'
        ancho: Ancho del gráfico en caracteres
        alto: Alto del gráfico en líneas
    """
    if not datos:
        print(f"{Fore.YELLOW}No hay datos para graficar{Style.RESET_ALL}")
        return
    
    # Extraer valores
    temperaturas = [d.get('temperatura', 0) for d in datos]
    fechas = [str(d.get('fecha', ''))[:10] for d in datos]
    
    if not temperaturas:
        return
    
    # Calcular rangos
    temp_min = min(temperaturas)
    temp_max = max(temperaturas)
    rango = temp_max - temp_min if temp_max != temp_min else 1
    
    # Normalizar valores
    valores_normalizados = [(t - temp_min) / rango for t in temperaturas]
    
    # Crear matriz del gráfico
    matriz = [[' ' for _ in range(ancho)] for _ in range(alto)]
    
    # Dibujar líneas de referencia
    for i in range(alto):
        valor_y = temp_max - (i / (alto - 1)) * rango
        if i == alto - 1:
            matriz[i][0:5] = f"{temp_min:.1f}".ljust(5)
        elif i == 0:
            matriz[i][0:5] = f"{temp_max:.1f}".ljust(5)
        elif i == alto // 2:
            matriz[i][0:5] = f"{(temp_min + temp_max)/2:.1f}".ljust(5)
    
    # Dibujar datos
    puntos_por_dato = max(1, ancho // len(datos))
    for idx, valor_norm in enumerate(valores_normalizados):
        x = min(ancho - 1, 5 + int(idx * puntos_por_dato))
        y = alto - 1 - int(valor_norm * (alto - 1))
        y = max(0, min(alto - 1, y))
        
        # Dibujar punto
        if 0 <= y < alto and 5 <= x < ancho:
            matriz[y][x] = '●'
            
            # Dibujar línea conectando puntos
            if idx > 0:
                prev_x = min(ancho - 1, 5 + int((idx - 1) * puntos_por_dato))
                prev_y = alto - 1 - int(valores_normalizados[idx - 1] * (alto - 1))
                prev_y = max(0, min(alto - 1, prev_y))
                
                # Dibujar línea
                if prev_x != x:
                    for px in range(min(prev_x, x), max(prev_x, x) + 1):
                        py = int(prev_y + (y - prev_y) * (px - prev_x) / (x - prev_x))
                        py = max(0, min(alto - 1, py))
                        if 0 <= py < alto and 5 <= px < ancho and matriz[py][px] == ' ':
                            matriz[py][px] = '·'
    
    # Imprimir gráfico
    print(f"\n{Fore.CYAN}{'='*ancho}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Temperatura (°C){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*ancho}{Style.RESET_ALL}\n")
    
    for fila in matriz:
        linea = ''.join(fila)
        # Colorear según temperatura
        if '●' in linea:
            print(f"{Fore.RED}{linea}{Style.RESET_ALL}")
        else:
            print(linea)
    
    # Eje X con fechas
    print(f"\n{Fore.YELLOW}{' ' * 5}", end='')
    if len(fechas) <= 10:
        for fecha in fechas:
            print(f"{fecha[:5]:<6}", end='')
    else:
        # Mostrar solo algunas fechas
        step = len(fechas) // 10
        for i in range(0, len(fechas), step):
            print(f"{fechas[i][:5]:<6}", end='')
    print(Style.RESET_ALL)
    print()


def grafico_barras_horizontal(datos: Dict[str, float], titulo: str = "", ancho: int = 50):
    """
    Genera un gráfico de barras horizontal ASCII
    
    Args:
        datos: Diccionario {etiqueta: valor}
        titulo: Título del gráfico
        ancho: Ancho máximo de las barras
    """
    if not datos:
        print(f"{Fore.YELLOW}No hay datos para graficar{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    if titulo:
        print(f"{Fore.CYAN}{titulo.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    # Normalizar valores
    max_valor = max(datos.values()) if datos.values() else 1
    if max_valor == 0:
        max_valor = 1
    
    # Ordenar por valor
    items_ordenados = sorted(datos.items(), key=lambda x: x[1], reverse=True)
    
    for etiqueta, valor in items_ordenados:
        # Calcular longitud de barra
        longitud = int((valor / max_valor) * ancho)
        barra = '█' * longitud
        
        # Color según valor
        if valor == max_valor:
            color = Fore.RED
        elif valor >= max_valor * 0.7:
            color = Fore.YELLOW
        else:
            color = Fore.GREEN
        
        # Formatear etiqueta
        etiqueta_formateada = etiqueta[:20].ljust(20)
        valor_formateado = f"{valor:.2f}".rjust(10)
        
        print(f"{etiqueta_formateada} {color}{barra}{Style.RESET_ALL} {valor_formateado}")
    
    print()


def grafico_comparativo(datos: List[Dict[str, Any]], campo1: str, campo2: str, 
                        titulo: str = "", ancho: int = 50):
    """
    Genera un gráfico comparativo de dos campos
    
    Args:
        datos: Lista de diccionarios con los datos
        campo1: Nombre del primer campo a comparar
        campo2: Nombre del segundo campo a comparar
        titulo: Título del gráfico
        ancho: Ancho del gráfico
    """
    if not datos:
        print(f"{Fore.YELLOW}No hay datos para graficar{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    if titulo:
        print(f"{Fore.CYAN}{titulo.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    # Extraer valores
    valores1 = [d.get(campo1, 0) for d in datos]
    valores2 = [d.get(campo2, 0) for d in datos]
    
    max_valor = max(max(valores1, default=0), max(valores2, default=0), 1)
    
    # Crear gráfico
    for i, dato in enumerate(datos):
        etiqueta = str(dato.get('etiqueta', f'Item {i+1}'))[:15].ljust(15)
        val1 = dato.get(campo1, 0)
        val2 = dato.get(campo2, 0)
        
        barra1_len = int((val1 / max_valor) * ancho)
        barra2_len = int((val2 / max_valor) * ancho)
        
        barra1 = '█' * barra1_len
        barra2 = '▓' * barra2_len
        
        print(f"{etiqueta} {Fore.RED}{barra1}{Style.RESET_ALL} {val1:.1f}")
        print(f"{' ' * 15} {Fore.BLUE}{barra2}{Style.RESET_ALL} {val2:.1f}")
        print()
    
    print(f"{Fore.RED}█{Style.RESET_ALL} = {campo1}  {Fore.BLUE}▓{Style.RESET_ALL} = {campo2}\n")


def mostrar_estadisticas_box(datos: Dict[str, Any], titulo: str = "Estadísticas"):
    """
    Muestra estadísticas en formato de caja visual
    
    Args:
        datos: Diccionario con estadísticas
        titulo: Título de la caja
    """
    ancho = 50
    print(f"\n{Fore.CYAN}{'═'*ancho}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{titulo.center(ancho)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═'*ancho}{Style.RESET_ALL}")
    
    for clave, valor in datos.items():
        clave_formateada = clave.replace('_', ' ').title().ljust(25)
        if isinstance(valor, float):
            valor_formateado = f"{valor:.2f}"
        elif isinstance(valor, int):
            valor_formateado = f"{valor:,}"
        else:
            valor_formateado = str(valor)
        
        print(f"{Fore.YELLOW}{clave_formateada}{Style.RESET_ALL}: {Fore.GREEN}{valor_formateado}{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'═'*ancho}{Style.RESET_ALL}\n")


def grafico_heatmap_simple(datos: List[List[float]], etiquetas_x: List[str], 
                          etiquetas_y: List[str], titulo: str = ""):
    """
    Genera un heatmap simple ASCII
    
    Args:
        datos: Matriz de valores
        etiquetas_x: Etiquetas para el eje X
        etiquetas_y: Etiquetas para el eje Y
        titulo: Título del gráfico
    """
    if not datos or not datos[0]:
        print(f"{Fore.YELLOW}No hay datos para graficar{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    if titulo:
        print(f"{Fore.CYAN}{titulo.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    # Encontrar min y max
    todos_valores = [val for fila in datos for val in fila]
    min_val = min(todos_valores)
    max_val = max(todos_valores)
    rango = max_val - min_val if max_val != min_val else 1
    
    # Caracteres para el heatmap
    caracteres = [' ', '░', '▒', '▓', '█']
    
    # Imprimir header
    print(f"{'':12}", end='')
    for etiqueta in etiquetas_x:
        print(f"{etiqueta[:6]:>6}", end='')
    print()
    
    # Imprimir datos
    for i, (fila, etiqueta_y) in enumerate(zip(datos, etiquetas_y)):
        print(f"{etiqueta_y[:10]:<10} ", end='')
        for valor in fila:
            # Normalizar
            norm = (valor - min_val) / rango
            idx = min(len(caracteres) - 1, int(norm * (len(caracteres) - 1)))
            
            # Color según intensidad
            if norm < 0.2:
                color = Fore.BLUE
            elif norm < 0.5:
                color = Fore.GREEN
            elif norm < 0.8:
                color = Fore.YELLOW
            else:
                color = Fore.RED
            
            print(f"{color}{caracteres[idx] * 2}{Style.RESET_ALL}", end='')
        print()
    
    print()


