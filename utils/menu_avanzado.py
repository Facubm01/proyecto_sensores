"""
Utilidades avanzadas para menús interactivos
Incluye navegación con flechas, paginación, búsqueda, etc.
"""

import sys
import os
from typing import List, Tuple, Callable, Any, Optional
from colorama import Fore, Style, init

init(autoreset=True)

# Importaciones condicionales para compatibilidad multiplataforma
try:
    import msvcrt
    WINDOWS = True
except ImportError:
    WINDOWS = False
    try:
        import select
        import tty
        import termios
    except ImportError:
        select = None
        tty = None
        termios = None


def _getch_windows():
    """Obtiene un carácter en Windows"""
    if WINDOWS and msvcrt.kbhit():
        ch = msvcrt.getch()
        if ch == b'\xe0':  # Tecla especial
            ch = msvcrt.getch()
            if ch == b'H':  # Flecha arriba
                return 'UP'
            elif ch == b'P':  # Flecha abajo
                return 'DOWN'
            elif ch == b'K':  # Flecha izquierda
                return 'LEFT'
            elif ch == b'M':  # Flecha derecha
                return 'RIGHT'
        elif ch == b'\r':  # Enter
            return 'ENTER'
        elif ch == b'\x1b':  # ESC
            return 'ESC'
        elif ch == b'\x08':  # Backspace
            return 'BACKSPACE'
        else:
            try:
                return ch.decode('utf-8')
            except:
                return None
    return None


def _getch_unix():
    """Obtiene un carácter en Unix/Linux"""
    if select and select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # ESC sequence
            ch = sys.stdin.read(2)
            if ch == '[A':
                return 'UP'
            elif ch == '[B':
                return 'DOWN'
            elif ch == '[D':
                return 'LEFT'
            elif ch == '[C':
                return 'RIGHT'
        elif ch == '\n' or ch == '\r':
            return 'ENTER'
        elif ch == '\x7f':  # Backspace
            return 'BACKSPACE'
        else:
            return ch
    return None


def getch():
    """Obtiene un carácter según el sistema operativo"""
    if WINDOWS:
        return _getch_windows()
    else:
        return _getch_unix()


def mostrar_menu_interactivo(titulo: str, opciones: List[Tuple[Any, str]], 
                             mostrar_salir: bool = True, 
                             ayuda: str = None) -> Optional[str]:
    """
    Muestra un menú interactivo con navegación por flechas
    
    Args:
        titulo: Título del menú
        opciones: Lista de tuplas (valor, descripcion)
        mostrar_salir: Si True, agrega opción de salir
        ayuda: Texto de ayuda a mostrar (presionar '?')
    
    Returns:
        Valor de la opción seleccionada o None si se cancela
    """
    if not opciones:
        return None
    
    seleccionado = 0
    mostrar_ayuda = False
    
    while True:
        os.system('clear' if os.name != 'posix' else 'cls')
        
        # Título
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}{titulo.center(60)}")
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        # Ayuda si está activa
        if mostrar_ayuda and ayuda:
            print(f"{Fore.YELLOW}{ayuda}\n{Style.RESET_ALL}")
        
        # Opciones
        for i, (valor, descripcion) in enumerate(opciones):
            if i == seleccionado:
                print(f"  {Fore.GREEN}▶ {Fore.CYAN}{descripcion}{Style.RESET_ALL}")
            else:
                print(f"    {descripcion}")
        
        if mostrar_salir:
            if seleccionado == len(opciones):
                print(f"  {Fore.RED}▶ Volver / Salir{Style.RESET_ALL}")
            else:
                print(f"    {Fore.RED}Volver / Salir{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}↑↓: Navegar  Enter: Seleccionar  ESC: Cancelar  ?: Ayuda{Style.RESET_ALL}")
        
        # Leer tecla
        tecla = getch()
        
        if tecla == 'UP':
            seleccionado = (seleccionado - 1) % (len(opciones) + (1 if mostrar_salir else 0))
        elif tecla == 'DOWN':
            seleccionado = (seleccionado + 1) % (len(opciones) + (1 if mostrar_salir else 0))
        elif tecla == 'ENTER':
            if seleccionado < len(opciones):
                return str(opciones[seleccionado][0])
            elif mostrar_salir:
                return '0'
        elif tecla == 'ESC':
            return None
        elif tecla == '?' or tecla == 'h' or tecla == 'H':
            mostrar_ayuda = not mostrar_ayuda


def mostrar_lista_paginada(items: List[Any], 
                           formatear_item: Callable[[Any], str],
                           titulo: str = "Lista",
                           items_por_pagina: int = 10,
                           mostrar_busqueda: bool = True) -> Optional[Any]:
    """
    Muestra una lista paginada con búsqueda
    
    Args:
        items: Lista de items a mostrar
        formatear_item: Función que formatea un item para mostrar
        titulo: Título de la lista
        items_por_pagina: Cantidad de items por página
        mostrar_busqueda: Si True, permite buscar
    
    Returns:
        Item seleccionado o None
    """
    if not items:
        print(f"{Fore.YELLOW}No hay items para mostrar{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Presione Enter para continuar...{Style.RESET_ALL}")
        return None
    
    pagina_actual = 0
    busqueda = ""
    items_filtrados = items
    
    while True:
        os.system('clear' if os.name != 'posix' else 'cls')
        
        # Aplicar búsqueda
        if busqueda:
            items_filtrados = [item for item in items 
                             if busqueda.lower() in formatear_item(item).lower()]
        else:
            items_filtrados = items
        
        if not items_filtrados:
            print(f"\n{Fore.YELLOW}No se encontraron items con '{busqueda}'{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Presione ESC para cancelar o cualquier tecla para buscar de nuevo...{Style.RESET_ALL}")
            tecla = getch()
            if tecla == 'ESC':
                return None
            busqueda = ""
            continue
        
        # Calcular paginación
        total_paginas = (len(items_filtrados) + items_por_pagina - 1) // items_por_pagina
        pagina_actual = min(pagina_actual, total_paginas - 1)
        
        inicio = pagina_actual * items_por_pagina
        fin = min(inicio + items_por_pagina, len(items_filtrados))
        items_pagina = items_filtrados[inicio:fin]
        
        # Mostrar título
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}{titulo.center(60)}")
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        # Búsqueda
        if mostrar_busqueda:
            print(f"{Fore.YELLOW}Búsqueda: {busqueda if busqueda else '(vacío - mostrar todos)'}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Escriba para buscar, ESC para limpiar{Style.RESET_ALL}\n")
        
        # Items
        for i, item in enumerate(items_pagina):
            print(f"  {Fore.GREEN}{inicio + i + 1}.{Style.RESET_ALL} {formatear_item(item)}")
        
        # Paginación
        print(f"\n{Fore.YELLOW}Página {pagina_actual + 1} de {total_paginas} ({len(items_filtrados)} items total){Style.RESET_ALL}")
        print(f"{Fore.CYAN}← →: Navegar páginas  Enter: Seleccionar  ESC: Cancelar  /: Buscar{Style.RESET_ALL}")
        
        # Leer tecla
        tecla = getch()
        
        if tecla == 'LEFT' or tecla == 'a' or tecla == 'A':
            if pagina_actual > 0:
                pagina_actual -= 1
        elif tecla == 'RIGHT' or tecla == 'd' or tecla == 'D':
            if pagina_actual < total_paginas - 1:
                pagina_actual += 1
        elif tecla == 'ENTER':
            # Permitir seleccionar por número
            print(f"\n{Fore.CYAN}Ingrese número del item (1-{len(items_pagina)}): {Style.RESET_ALL}", end='')
            try:
                num = int(input().strip())
                if 1 <= num <= len(items_pagina):
                    return items_pagina[num - 1]
            except (ValueError, KeyboardInterrupt):
                pass
        elif tecla == 'ESC':
            return None
        elif tecla == '/' or tecla == 's' or tecla == 'S':
            # Modo búsqueda
            print(f"\n{Fore.CYAN}Ingrese término de búsqueda: {Style.RESET_ALL}", end='')
            busqueda = input().strip()
            pagina_actual = 0
        elif tecla and tecla not in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            # Búsqueda incremental
            if mostrar_busqueda:
                busqueda += tecla
                pagina_actual = 0


def mostrar_progreso(actual: int, total: int, mensaje: str = "Procesando"):
    """
    Muestra una barra de progreso
    
    Args:
        actual: Valor actual
        total: Valor total
        mensaje: Mensaje a mostrar
    """
    if total == 0:
        porcentaje = 0
    else:
        porcentaje = min(100, int((actual / total) * 100))
    
    ancho_barra = 40
    lleno = int((porcentaje / 100) * ancho_barra)
    vacio = ancho_barra - lleno
    
    barra = f"{Fore.GREEN}{'█' * lleno}{Fore.YELLOW}{'░' * vacio}{Style.RESET_ALL}"
    
    print(f"\r{Fore.CYAN}{mensaje}: {Style.RESET_ALL}{barra} {porcentaje}% ({actual}/{total})", end='', flush=True)
    
    if actual >= total:
        print()  # Nueva línea al completar


def confirmar_con_timeout(mensaje: str, timeout: int = 5, default: bool = False) -> bool:
    """
    Solicita confirmación con timeout
    
    Args:
        mensaje: Mensaje a mostrar
        timeout: Segundos de timeout
        default: Valor por defecto si expira el timeout
    
    Returns:
        True si confirma, False si no (o timeout)
    """
    import time
    
    print(f"{Fore.CYAN}{mensaje} (s/n) [default: {'s' if default else 'n'}, timeout: {timeout}s]{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Presione s/n o espere {timeout} segundos...{Style.RESET_ALL}")
    
    inicio = time.time()
    respuesta = None
    
    while time.time() - inicio < timeout:
        tecla = getch()
        if tecla and tecla.lower() in ['s', 'n']:
            respuesta = tecla.lower() == 's'
            break
        time.sleep(0.1)
    
    if respuesta is None:
        respuesta = default
        print(f"{Fore.YELLOW}Timeout - usando valor por defecto: {'sí' if default else 'no'}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Respuesta: {'sí' if respuesta else 'no'}{Style.RESET_ALL}")
    
    return respuesta


def autocompletar(prompt: str, opciones: List[str], mostrar_sugerencias: bool = True) -> Optional[str]:
    """
    Input con autocompletado
    
    Args:
        prompt: Mensaje a mostrar
        opciones: Lista de opciones válidas
        mostrar_sugerencias: Si True, muestra sugerencias mientras escribe
    
    Returns:
        Opción seleccionada o None
    """
    texto = ""
    sugerencia_actual = None
    
    print(f"{Fore.CYAN}{prompt}: {Style.RESET_ALL}", end='', flush=True)
    
    while True:
        tecla = getch()
        
        if tecla == 'ENTER':
            if sugerencia_actual:
                print(f"\n{Fore.GREEN}✓ Seleccionado: {sugerencia_actual}{Style.RESET_ALL}")
                return sugerencia_actual
            elif texto in opciones:
                print(f"\n{Fore.GREEN}✓ Seleccionado: {texto}{Style.RESET_ALL}")
                return texto
            else:
                print(f"\n{Fore.RED}✗ Opción no válida{Style.RESET_ALL}")
                return None
        elif tecla == 'ESC':
            print(f"\n{Fore.YELLOW}Cancelado{Style.RESET_ALL}")
            return None
        elif tecla == 'BACKSPACE':
            if texto:
                texto = texto[:-1]
                print('\b \b', end='', flush=True)
        elif tecla and len(tecla) == 1 and tecla.isprintable():
            texto += tecla
            print(tecla, end='', flush=True)
        
        # Buscar sugerencias
        if texto:
            sugerencias = [op for op in opciones if op.lower().startswith(texto.lower())]
            if sugerencias:
                sugerencia_actual = sugerencias[0]
                if mostrar_sugerencias and len(sugerencias) == 1:
                    # Mostrar sugerencia
                    resto = sugerencia_actual[len(texto):]
                    print(f"{Fore.YELLOW}{resto}{Style.RESET_ALL}", end='\r')
                    print(f"{Fore.CYAN}{prompt}: {Style.RESET_ALL}{texto}", end='', flush=True)
            else:
                sugerencia_actual = None
        
        # Tab para autocompletar
        if tecla == '\t' and sugerencia_actual:
            texto = sugerencia_actual
            print(f"\r{Fore.CYAN}{prompt}: {Style.RESET_ALL}{texto}", end='', flush=True)

