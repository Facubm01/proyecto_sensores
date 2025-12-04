"""
Aplicación principal del sistema de sensores
Coordina todos los menús y la navegación
"""

from services.auth_service import AuthService
from utils.menu import *
from utils.db_manager import db_manager

# Import de módulos UI
from ui.auth_menu import AuthMenu
from ui.proceso_menu import ProcesoMenu
from ui.facturacion_menu import FacturacionMenu
from ui.mensajeria_menu import MensajeriaMenu
from ui.sensor_menu import SensorMenu
from ui.alerta_menu import AlertaMenu
from ui.control_menu import ControlMenu
from ui.admin_menu import AdminMenu
from ui.dashboard_menu import DashboardMenu
from ui.notificacion_menu import NotificacionMenu
from services.notificacion_service import NotificacionService
from utils.logger import logger


class SistemaSensores:
    """Clase principal de la aplicación"""
    
    def __init__(self):
        self.session_id = None
        self.user_data = None
        self.ejecutando = True
    
    def verificar_conexiones(self):
        """Verifica que las conexiones a las bases de datos funcionen"""
        try:
            mostrar_info("Verificando conexiones a bases de datos...")
            
            # MySQL
            db_manager.conectar_mysql()
            mostrar_exito("MySQL conectado")
            
            # MongoDB
            db_manager.conectar_mongodb()
            mostrar_exito("MongoDB conectado")
            
            # Redis
            db_manager.conectar_redis()
            mostrar_exito("Redis conectado")
            
            print()
            return True
            
        except Exception as e:
            mostrar_error(f"Error en conexiones: {e}")
            return False
    
    def run(self):
        """Inicia la aplicación"""
        limpiar_pantalla()
        mostrar_titulo("SISTEMA DE GESTIÓN DE SENSORES")
        mostrar_info("Trabajo Práctico - Persistencia Políglota")
        mostrar_info("Ingeniería de Datos II\n")
        
        if not self.verificar_conexiones():
            mostrar_error("No se pudo conectar a las bases de datos")
            mostrar_info("Verifique que Docker esté ejecutando los contenedores")
            return
        
        pausar()
        self.menu_principal()
    
    def menu_principal(self):
        """Menú principal (sin autenticación)"""
        while self.ejecutando:
            limpiar_pantalla()
            
            opciones = [
                (1, "Iniciar Sesión"),
                (2, "Registrar Nuevo Usuario"),
                (3, "Salir")
            ]
            
            seleccion = mostrar_menu("SISTEMA DE GESTIÓN DE SENSORES", opciones, mostrar_salir=False)
            
            if seleccion == '1':
                self.iniciar_sesion()
            elif seleccion == '2':
                self.registrar_usuario()
            elif seleccion == '3':
                self.salir()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def iniciar_sesion(self):
        """Proceso de inicio de sesión"""
        success, session_id, user_data = AuthMenu.iniciar_sesion()
        
        if success:
            self.session_id = session_id
            self.user_data = user_data
            logger.log_operacion("Inicio de sesión", user_data['user_id'])
            self.menu_usuario()
    
    def registrar_usuario(self):
        """Registro de nuevo usuario"""
        AuthMenu.registrar_usuario()
    
    def menu_usuario(self):
        """Menú principal para usuario autenticado"""
        while self.session_id:
            limpiar_pantalla()
            mostrar_usuario_info(self.user_data)
            
            # Verificar notificaciones
            notificaciones_no_leidas = NotificacionService.contar_no_leidas(self.user_data['user_id'])
            notif_texto = f" ({notificaciones_no_leidas} nuevas)" if notificaciones_no_leidas > 0 else ""
            
            # Opciones base para todos los usuarios
            opciones = [
                (1, "Dashboard"),
                (2, "Gestión de Procesos"),
                (3, "Ver Mis Solicitudes"),
                (4, "Facturación y Cuenta Corriente"),
                (5, f"Mensajería{notif_texto}"),
                (6, f"Notificaciones{notif_texto}"),
            ]
            
            # Opciones adicionales para técnicos
            if 'tecnico' in self.user_data['roles'] or 'administrador' in self.user_data['roles']:
                opciones.extend([
                    (7, "Gestión de Sensores"),
                    (8, "Ver Alertas"),
                    (9, "Control de Funcionamiento"),
                ])
            
            # Opciones adicionales para administradores
            if 'administrador' in self.user_data['roles']:
                opciones.extend([
                    (10, "Ejecutar Procesos Pendientes"),
                    (11, "Gestión de Usuarios"),
                    (12, "Ver Sesiones Activas"),
                    (13, "Reportes del Sistema"),
                ])
            
            opciones.append((99, "Cerrar Sesión"))
            
            seleccion = mostrar_menu("MENÚ PRINCIPAL", opciones, mostrar_salir=False)
            
            if seleccion == '1':
                menu = DashboardMenu(self.user_data)
                menu.mostrar_menu()
            elif seleccion == '2':
                menu = ProcesoMenu(self.user_data)
                menu.mostrar_menu()
            elif seleccion == '3':
                menu = ProcesoMenu(self.user_data)
                menu.ver_mis_solicitudes()
            elif seleccion == '4':
                menu = FacturacionMenu(self.user_data)
                menu.mostrar_menu()
            elif seleccion == '5':
                menu = MensajeriaMenu(self.user_data)
                menu.mostrar_menu()
            elif seleccion == '6':
                menu = NotificacionMenu(self.user_data)
                menu.mostrar_menu()
            elif seleccion == '7' and ('tecnico' in self.user_data['roles'] or 'administrador' in self.user_data['roles']):
                menu = SensorMenu(self.user_data)
                menu.mostrar_menu()
            elif seleccion == '8' and ('tecnico' in self.user_data['roles'] or 'administrador' in self.user_data['roles']):
                menu = AlertaMenu(self.user_data)
                menu.mostrar_menu()
            elif seleccion == '9' and ('tecnico' in self.user_data['roles'] or 'administrador' in self.user_data['roles']):
                menu = ControlMenu(self.user_data)
                menu.mostrar_menu()
            elif seleccion == '10' and 'administrador' in self.user_data['roles']:
                menu = AdminMenu(self.user_data)
                menu.menu_ejecutar_procesos()
            elif seleccion == '11' and 'administrador' in self.user_data['roles']:
                menu = AdminMenu(self.user_data)
                menu.gestion_usuarios()
            elif seleccion == '12' and 'administrador' in self.user_data['roles']:
                menu = AdminMenu(self.user_data)
                menu.ver_sesiones_activas()
            elif seleccion == '13' and 'administrador' in self.user_data['roles']:
                menu = AdminMenu(self.user_data)
                menu.reportes_sistema()
            elif seleccion == '99':
                self.cerrar_sesion()
            else:
                mostrar_error("Opción inválida o sin permisos")
                pausar()
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        if self.session_id:
            AuthService.logout(self.session_id)
            mostrar_info("Sesión cerrada correctamente")
            self.session_id = None
            self.user_data = None
            pausar()
    
    def salir(self):
        """Sale de la aplicación"""
        if self.session_id:
            self.cerrar_sesion()
        
        limpiar_pantalla()
        mostrar_titulo("¡HASTA LUEGO!")
        mostrar_info("Gracias por usar el Sistema de Gestión de Sensores\n")
        db_manager.cerrar_conexiones()
        self.ejecutando = False
