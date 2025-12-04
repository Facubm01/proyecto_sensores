"""
Menú de notificaciones
"""

from services.notificacion_service import NotificacionService
from utils.menu import *
from colorama import Fore
from datetime import datetime


class NotificacionMenu:
    """Menú para gestionar notificaciones"""
    
    def __init__(self, user_data):
        self.user_data = user_data
    
    def mostrar_menu(self):
        """Menú principal de notificaciones"""
        while True:
            limpiar_pantalla()
            
            # Contar no leídas
            no_leidas = NotificacionService.contar_no_leidas(self.user_data['user_id'])
            titulo_extra = f" ({no_leidas} no leídas)" if no_leidas > 0 else ""
            
            opciones = [
                (1, f"Ver Notificaciones{titulo_extra}"),
                (2, "Marcar Todas como Leídas"),
                (3, "Configuración"),
            ]
            
            seleccion = mostrar_menu("NOTIFICACIONES", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.ver_notificaciones()
            elif seleccion == '2':
                self.marcar_todas_leidas()
            elif seleccion == '3':
                self.configuracion()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def ver_notificaciones(self):
        """Muestra las notificaciones del usuario"""
        limpiar_pantalla()
        mostrar_titulo("MIS NOTIFICACIONES")
        
        notificaciones = NotificacionService.obtener_notificaciones(self.user_data['user_id'], 20)
        
        if not notificaciones:
            mostrar_info("No hay notificaciones")
            pausar()
            return
        
        # Mostrar notificaciones
        for i, notif in enumerate(notificaciones, 1):
            fecha = notif.get('fecha', '')
            try:
                if isinstance(fecha, str):
                    fecha_obj = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                    fecha_str = fecha_obj.strftime('%Y-%m-%d %H:%M')
                else:
                    fecha_str = str(fecha)
            except:
                fecha_str = str(fecha)
            
            tipo = notif.get('tipo', 'general')
            mensaje = notif.get('mensaje', 'Sin mensaje')
            
            # Color según tipo
            if tipo == 'proceso_completado':
                color = Fore.GREEN
                icono = '✓'
            elif tipo == 'proceso_error':
                color = Fore.RED
                icono = '✗'
            elif tipo == 'alerta':
                color = Fore.YELLOW
                icono = '⚠'
            else:
                color = Fore.BLUE
                icono = 'ℹ'
            
            print(f"{color}{icono}{Style.RESET_ALL} [{fecha_str}] {mensaje}")
        
        print()
        
        # Opciones
        opciones = [
            (1, "Marcar como leída"),
            (2, "Ver detalle de notificación"),
            (0, "Volver"),
        ]
        
        seleccion = mostrar_menu("", opciones)
        
        if seleccion == '1':
            notif_id = solicitar_entrada("Número de notificación a marcar como leída", int)
            if notif_id and 1 <= notif_id <= len(notificaciones):
                notif = notificaciones[notif_id - 1]
                NotificacionService.marcar_leida(
                    self.user_data['user_id'],
                    notif.get('fecha', '')
                )
                mostrar_exito("Notificación marcada como leída")
                pausar()
        elif seleccion == '2':
            notif_id = solicitar_entrada("Número de notificación a ver", int)
            if notif_id and 1 <= notif_id <= len(notificaciones):
                self.ver_detalle_notificacion(notificaciones[notif_id - 1])
    
    def ver_detalle_notificacion(self, notificacion):
        """Muestra el detalle de una notificación"""
        limpiar_pantalla()
        mostrar_titulo("DETALLE DE NOTIFICACIÓN")
        
        print(f"{Fore.CYAN}Tipo:{Fore.RESET} {notificacion.get('tipo', 'N/A')}")
        print(f"{Fore.CYAN}Fecha:{Fore.RESET} {notificacion.get('fecha', 'N/A')}")
        print(f"{Fore.CYAN}Mensaje:{Fore.RESET} {notificacion.get('mensaje', 'N/A')}")
        
        datos = notificacion.get('datos', {})
        if datos:
            print(f"\n{Fore.YELLOW}Datos adicionales:{Fore.RESET}")
            for clave, valor in datos.items():
                print(f"  • {clave}: {valor}")
        
        pausar()
    
    def marcar_todas_leidas(self):
        """Marca todas las notificaciones como leídas"""
        if confirmar("¿Marcar todas las notificaciones como leídas?"):
            notificaciones = NotificacionService.obtener_notificaciones(self.user_data['user_id'], 100)
            for notif in notificaciones:
                NotificacionService.marcar_leida(
                    self.user_data['user_id'],
                    notif.get('fecha', '')
                )
            mostrar_exito("Todas las notificaciones fueron marcadas como leídas")
        pausar()
    
    def configuracion(self):
        """Configuración de notificaciones"""
        limpiar_pantalla()
        mostrar_titulo("CONFIGURACIÓN DE NOTIFICACIONES")
        
        mostrar_info("Las notificaciones se muestran automáticamente cuando:")
        print("  • Un proceso se completa")
        print("  • Un proceso tiene error")
        print("  • Se genera una alerta")
        print("  • Hay actualizaciones del sistema")
        
        pausar()


