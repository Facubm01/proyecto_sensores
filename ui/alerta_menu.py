"""
Módulo de gestión de alertas
Gestiona alertas del sistema (solo técnicos/administradores)
"""

from services.alerta_service import AlertaService
from utils.menu import *
from colorama import Fore


class AlertaMenu:
    """Menú de gestión de alertas"""
    
    def __init__(self, user_data):
        """
        Args:
            user_data: Información del usuario autenticado
        """
        self.user_data = user_data
    
    def mostrar_menu(self):
        """Ver alertas del sistema"""
        while True:
            limpiar_pantalla()
            
            # Mostrar resumen
            conteos = AlertaService.contar_alertas_por_estado()
            print(f"{Fore.YELLOW}Resumen de Alertas:")
            print(f"  Activas: {conteos['activa']}")
            print(f"  Resueltas: {conteos['resuelta']}\n")
            
            opciones = [
                (1, "Ver Todas las Alertas"),
                (2, "Ver Alertas Activas"),
                (3, "Ver Alertas Resueltas"),
            ]
            
            if 'administrador' in self.user_data['roles']:
                opciones.extend([
                    (4, "Crear Nueva Alerta"),
                    (5, "Resolver Alerta"),
                ])
            
            seleccion = mostrar_menu("ALERTAS DEL SISTEMA", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.listar_alertas(None)
            elif seleccion == '2':
                self.listar_alertas('activa')
            elif seleccion == '3':
                self.listar_alertas('resuelta')
            elif seleccion == '4' and 'administrador' in self.user_data['roles']:
                self.crear_alerta()
            elif seleccion == '5' and 'administrador' in self.user_data['roles']:
                self.resolver_alerta()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def listar_alertas(self, filtro_estado):
        """Lista alertas con filtro opcional"""
        limpiar_pantalla()
        titulo = "TODAS LAS ALERTAS" if not filtro_estado else f"ALERTAS {filtro_estado.upper()}S"
        mostrar_titulo(titulo)
        
        alertas = AlertaService.listar_alertas(filtro_estado)
        
        if not alertas:
            mostrar_info("No hay alertas")
        else:
            headers = ['ID', 'Tipo', 'Sensor', 'Ciudad', 'Fecha', 'Estado']
            filas = []
            
            for a in alertas:
                sensor_info = a.get('sensor_nombre', 'N/A')
                ciudad = a.get('sensor_ciudad', 'N/A')
                filas.append([
                    str(a['_id'])[:8] + '...',
                    a['tipo'],
                    sensor_info[:20],
                    ciudad,
                    str(a['timestamp'])[:19],
                    a['estado']
                ])
            
            mostrar_tabla(headers, filas)
            
            # Mostrar detalles
            if confirmar("¿Ver detalles de una alerta?"):
                print(f"\n{Fore.CYAN}Alertas completas:\n")
                for i, a in enumerate(alertas[:10], 1):
                    print(f"{i}. [{a['estado'].upper()}] {a['descripcion']}")
                    print(f"   Sensor: {a.get('sensor_nombre', 'N/A')} ({a.get('sensor_ciudad', 'N/A')})")
                    print(f"   Fecha: {a['timestamp']}")
                    print()
        
        pausar()
    
    def crear_alerta(self):
        """Crea una nueva alerta"""
        limpiar_pantalla()
        mostrar_titulo("CREAR NUEVA ALERTA")
        
        tipo = solicitar_entrada("Tipo de alerta (sensor/climatica)", str, ['sensor', 'climatica'])
        if not tipo:
            return
        
        sensor_id = solicitar_entrada("ID del sensor", int)
        if not sensor_id:
            return
        
        descripcion = solicitar_entrada("Descripción de la alerta", str)
        if not descripcion:
            return
        
        success, mensaje = AlertaService.crear_alerta(tipo, sensor_id, descripcion)
        
        if success:
            mostrar_exito(mensaje)
        else:
            mostrar_error(mensaje)
        
        pausar()
    
    def resolver_alerta(self):
        """Marca una alerta como resuelta"""
        limpiar_pantalla()
        mostrar_titulo("RESOLVER ALERTA")
        
        # Mostrar alertas activas
        alertas = AlertaService.listar_alertas('activa', limite=20)
        
        if not alertas:
            mostrar_info("No hay alertas activas")
            pausar()
            return
        
        print(f"{Fore.CYAN}Alertas Activas:\n")
        for i, a in enumerate(alertas, 1):
            print(f"{i}. ID: {str(a['_id'])[:12]}... - {a['descripcion'][:60]}")
        
        print()
        alerta_id = solicitar_entrada("ID de la alerta (copiar de arriba)", str)
        if not alerta_id:
            return
        
        if confirmar("¿Marcar esta alerta como resuelta?"):
            success, mensaje = AlertaService.resolver_alerta(alerta_id)
            
            if success:
                mostrar_exito(mensaje)
            else:
                mostrar_error(mensaje)
        
        pausar()
    
