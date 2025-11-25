"""
Módulo de control de funcionamiento
Gestiona controles de funcionamiento de sensores (solo técnicos/administradores)
"""

from services.control_service import ControlService
from services.sensor_service import SensorService
from utils.menu import *
from colorama import Fore


class ControlMenu:
    """Menú de control de funcionamiento"""
    
    def __init__(self, user_data):
        """
        Args:
            user_data: Información del usuario autenticado
        """
        self.user_data = user_data
    
    def mostrar_menu(self):
        """Control de funcionamiento de sensores"""
        while True:
            limpiar_pantalla()
            
            # Mostrar estadísticas
            stats = ControlService.obtener_estadisticas_controles()
            print(f"{Fore.YELLOW}Estadísticas de Controles:")
            print(f"  Total controles registrados: {stats['total']}")
            print(f"  Controles últimos 7 días: {stats['ultimos_7_dias']}")
            if stats['por_estado']:
                print(f"  Por estado: {stats['por_estado']}\n")
            
            opciones = [
                (1, "Ver Todos los Controles"),
                (2, "Ver Controles de un Sensor"),
                (3, "Registrar Nuevo Control"),
            ]
            
            seleccion = mostrar_menu("CONTROL DE FUNCIONAMIENTO", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.ver_todos_controles()
            elif seleccion == '2':
                self.ver_controles_sensor()
            elif seleccion == '3':
                self.registrar_control()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def ver_todos_controles(self):
        """Ver todos los controles registrados"""
        limpiar_pantalla()
        mostrar_titulo("CONTROLES DE FUNCIONAMIENTO")
        
        controles = ControlService.listar_todos_controles()
        
        if not controles:
            mostrar_info("No hay controles registrados")
        else:
            headers = ['Sensor', 'Ciudad', 'Fecha', 'Estado', 'Observaciones']
            filas = []
            
            for c in controles:
                filas.append([
                    c.get('sensor_nombre', 'N/A')[:20],
                    c.get('sensor_ciudad', 'N/A'),
                    str(c['fecha_revision'])[:19],
                    c['estado'],
                    c['observaciones'][:40]
                ])
            
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def ver_controles_sensor(self):
        """Ver controles de un sensor específico"""
        limpiar_pantalla()
        mostrar_titulo("CONTROLES DE UN SENSOR")
        
        sensor_id = solicitar_entrada("ID del sensor", int)
        if not sensor_id:
            return
        
        # Verificar que existe
        sensor = SensorService.obtener_sensor(sensor_id)
        if not sensor:
            mostrar_error("Sensor no encontrado")
            pausar()
            return
        
        print(f"\n{Fore.CYAN}Sensor: {sensor['nombre']} ({sensor['codigo']})")
        print(f"Estado actual: {sensor['estado']}\n")
        
        controles = ControlService.listar_controles_sensor(sensor_id)
        
        if not controles:
            mostrar_info("No hay controles registrados para este sensor")
        else:
            headers = ['Fecha', 'Estado', 'Observaciones']
            filas = [
                [str(c['fecha_revision'])[:19], c['estado'], c['observaciones'][:50]]
                for c in controles
            ]
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def registrar_control(self):
        """Registra un nuevo control de funcionamiento"""
        limpiar_pantalla()
        mostrar_titulo("REGISTRAR CONTROL DE FUNCIONAMIENTO")
        
        sensor_id = solicitar_entrada("ID del sensor", int)
        if not sensor_id:
            return
        
        # Verificar que existe
        sensor = SensorService.obtener_sensor(sensor_id)
        if not sensor:
            mostrar_error("Sensor no encontrado")
            pausar()
            return
        
        print(f"\n{Fore.CYAN}Sensor: {sensor['nombre']} ({sensor['codigo']})")
        print(f"Estado actual: {sensor['estado']}\n")
        
        estado = solicitar_entrada("Estado del sensor (activo/inactivo/falla)", str, 
                                  ['activo', 'inactivo', 'falla'])
        if not estado:
            return
        
        observaciones = solicitar_entrada("Observaciones", str)
        if not observaciones:
            return
        
        if confirmar("¿Registrar control?"):
            success, mensaje = ControlService.registrar_control(sensor_id, estado, observaciones)
            
            if success:
                mostrar_exito(mensaje)
                
                # Preguntar si quiere cambiar el estado del sensor
                if estado != sensor['estado']:
                    if confirmar(f"¿Cambiar estado del sensor de '{sensor['estado']}' a '{estado}'?"):
                        SensorService.cambiar_estado_sensor(sensor_id, estado)
                        mostrar_exito("Estado del sensor actualizado")
            else:
                mostrar_error(mensaje)
        
        pausar()
    
