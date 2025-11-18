"""
Utilidades para menús de consola
"""

import os
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

def limpiar_pantalla():
    """Limpia la pantalla de la consola"""
    os.system('clear' if os.name != 'nt' else 'cls')

def mostrar_titulo(texto):
    """Muestra un título destacado"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{texto.center(60)}")
    print(f"{Fore.CYAN}{'=' * 60}\n")

def mostrar_subtitulo(texto):
    """Muestra un subtítulo"""
    print(f"\n{Fore.YELLOW}{'-' * 60}")
    print(f"{Fore.YELLOW}{texto}")
    print(f"{Fore.YELLOW}{'-' * 60}")

def mostrar_exito(mensaje):
    """Muestra un mensaje de éxito"""
    print(f"{Fore.GREEN}✓ {mensaje}")

def mostrar_error(mensaje):
    """Muestra un mensaje de error"""
    print(f"{Fore.RED}✗ {mensaje}")

def mostrar_info(mensaje):
    """Muestra un mensaje informativo"""
    print(f"{Fore.BLUE}ℹ {mensaje}")

def mostrar_advertencia(mensaje):
    """Muestra una advertencia"""
    print(f"{Fore.YELLOW}⚠ {mensaje}")

def solicitar_entrada(mensaje, tipo=str, opciones=None):
    """
    Solicita entrada del usuario con validación
    
    Args:
        mensaje: Mensaje a mostrar
        tipo: Tipo de dato esperado (str, int, float)
        opciones: Lista de opciones válidas (si aplica)
    
    Returns:
        Valor ingresado por el usuario (validado)
    """
    while True:
        try:
            valor = input(f"{Fore.CYAN}{mensaje}: {Style.RESET_ALL}")
            
            if tipo == str:
                valor_convertido = valor.strip()
            elif tipo == int:
                valor_convertido = int(valor)
            elif tipo == float:
                valor_convertido = float(valor)
            else:
                valor_convertido = valor
            
            # Validar opciones si se especificaron
            if opciones is not None:
                if valor_convertido not in opciones:
                    mostrar_error(f"Opción inválida. Opciones válidas: {opciones}")
                    continue
            
            return valor_convertido
            
        except ValueError:
            mostrar_error(f"Entrada inválida. Se esperaba tipo {tipo.__name__}")
        except KeyboardInterrupt:
            print("\n")
            return None

def mostrar_menu(titulo, opciones, mostrar_salir=True):
    """
    Muestra un menú y retorna la opción seleccionada
    
    Args:
        titulo: Título del menú
        opciones: Lista de tuplas (opcion, descripcion)
        mostrar_salir: Si True, agrega opción de salir/volver
    
    Returns:
        Opción seleccionada (str o int)
    """
    mostrar_titulo(titulo)
    
    for opcion, descripcion in opciones:
        print(f"  {Fore.GREEN}{opcion}.{Style.RESET_ALL} {descripcion}")
    
    if mostrar_salir:
        print(f"  {Fore.RED}0.{Style.RESET_ALL} Volver / Salir")
    
    print()
    
    opciones_validas = [str(opcion) for opcion, _ in opciones]
    if mostrar_salir:
        opciones_validas.append('0')
    
    seleccion = solicitar_entrada("Seleccione una opción", str, opciones_validas)
    return seleccion

def pausar():
    """Pausa la ejecución esperando que el usuario presione Enter"""
    input(f"\n{Fore.CYAN}Presione Enter para continuar...{Style.RESET_ALL}")

def confirmar(mensaje):
    """
    Solicita confirmación al usuario
    
    Returns:
        True si confirma, False si no
    """
    respuesta = solicitar_entrada(f"{mensaje} (s/n)", str, ['s', 'n', 'S', 'N'])
    return respuesta.lower() == 's'

def mostrar_tabla(headers, filas, titulo=None):
    """
    Muestra datos en formato de tabla
    
    Args:
        headers: Lista de nombres de columnas
        filas: Lista de listas con los datos
        titulo: Título opcional de la tabla
    """
    from tabulate import tabulate
    
    if titulo:
        mostrar_subtitulo(titulo)
    
    print(tabulate(filas, headers=headers, tablefmt='grid'))
    print()

def mostrar_usuario_info(user_data):
    """Muestra información del usuario logueado"""
    print(f"\n{Fore.GREEN}Usuario: {user_data['nombre']}")
    print(f"{Fore.GREEN}Email: {user_data['email']}")
    print(f"{Fore.GREEN}Rol(es): {', '.join(user_data['roles'])}\n")
