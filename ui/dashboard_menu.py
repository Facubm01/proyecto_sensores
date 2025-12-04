"""
Dashboard con estadísticas visuales del sistema
"""

from services.proceso_service import ProcesoService
from services.facturacion_service import FacturacionService
from services.sensor_service import SensorService
from services.alerta_service import AlertaService
from services.notificacion_service import NotificacionService
from utils.menu import *
from utils.visualizacion import *
from utils.db_manager import db_manager
from colorama import Fore


class DashboardMenu:
    """Menú de dashboard con estadísticas"""
    
    def __init__(self, user_data):
        self.user_data = user_data
    
    def mostrar_menu(self):
        """Menú principal del dashboard"""
        while True:
            limpiar_pantalla()
            
            opciones = [
                (1, "Dashboard General"),
                (2, "Mis Estadísticas"),
                (3, "Estadísticas de Procesos"),
                (4, "Estadísticas de Sensores"),
                (5, "Estadísticas Financieras"),
            ]
            
            # Opciones adicionales para admin
            if 'administrador' in self.user_data['roles']:
                opciones.extend([
                    (6, "Dashboard Administrativo"),
                    (7, "Estadísticas del Sistema"),
                ])
            
            seleccion = mostrar_menu("DASHBOARD", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.dashboard_general()
            elif seleccion == '2':
                self.mis_estadisticas()
            elif seleccion == '3':
                self.estadisticas_procesos()
            elif seleccion == '4':
                self.estadisticas_sensores()
            elif seleccion == '5':
                self.estadisticas_financieras()
            elif seleccion == '6' and 'administrador' in self.user_data['roles']:
                self.dashboard_admin()
            elif seleccion == '7' and 'administrador' in self.user_data['roles']:
                self.estadisticas_sistema()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def dashboard_general(self):
        """Dashboard general del usuario"""
        limpiar_pantalla()
        mostrar_titulo("DASHBOARD GENERAL")
        
        user_id = self.user_data['user_id']
        
        # Obtener datos
        conteos = ProcesoService.contar_solicitudes_por_estado(user_id)
        cuenta = FacturacionService.obtener_cuenta_corriente(user_id)
        notificaciones = NotificacionService.contar_no_leidas(user_id)
        
        # Estadísticas básicas
        stats = {
            'Solicitudes Pendientes': conteos.get('pendiente', 0),
            'Solicitudes Completadas': conteos.get('completado', 0),
            'Solicitudes en Proceso': conteos.get('en_proceso', 0),
            'Saldo Actual': f"${cuenta.get('saldo', 0):.2f}" if cuenta else "$0.00",
            'Notificaciones No Leídas': notificaciones,
        }
        
        mostrar_estadisticas_box(stats, "Mis Estadísticas")
        
        # Gráfico de solicitudes
        datos_grafico = {
            'Pendientes': conteos.get('pendiente', 0),
            'Completadas': conteos.get('completado', 0),
            'En Proceso': conteos.get('en_proceso', 0),
            'Con Error': conteos.get('error', 0),
        }
        
        grafico_barras_horizontal(datos_grafico, "Estado de Mis Solicitudes")
        
        pausar()
    
    def mis_estadisticas(self):
        """Estadísticas detalladas del usuario"""
        limpiar_pantalla()
        mostrar_titulo("MIS ESTADÍSTICAS")
        
        user_id = self.user_data['user_id']
        
        # Obtener solicitudes recientes
        solicitudes = ProcesoService.listar_solicitudes_usuario(user_id, None)
        
        if solicitudes:
            # Estadísticas de costos
            total_gastado = sum(s.get('costo', 0) for s in solicitudes if s.get('estado') == 'completado')
            promedio_por_proceso = total_gastado / len([s for s in solicitudes if s.get('estado') == 'completado']) if any(s.get('estado') == 'completado' for s in solicitudes) else 0
            
            stats = {
                'Total Solicitudes': len(solicitudes),
                'Total Gastado': f"${total_gastado:.2f}",
                'Promedio por Proceso': f"${promedio_por_proceso:.2f}",
                'Procesos Completados': len([s for s in solicitudes if s.get('estado') == 'completado']),
            }
            
            mostrar_estadisticas_box(stats, "Resumen Financiero")
            
            # Gráfico de procesos por tipo
            tipos_proceso = {}
            for s in solicitudes:
                tipo = s.get('proceso_tipo', 'Desconocido')
                tipos_proceso[tipo] = tipos_proceso.get(tipo, 0) + 1
            
            if tipos_proceso:
                grafico_barras_horizontal(tipos_proceso, "Procesos por Tipo")
        else:
            mostrar_info("No hay solicitudes registradas")
        
        pausar()
    
    def estadisticas_procesos(self):
        """Estadísticas de procesos"""
        limpiar_pantalla()
        mostrar_titulo("ESTADÍSTICAS DE PROCESOS")
        
        user_id = self.user_data['user_id']
        solicitudes = ProcesoService.listar_solicitudes_usuario(user_id, None)
        
        if not solicitudes:
            mostrar_info("No hay solicitudes para analizar")
            pausar()
            return
        
        # Agrupar por mes
        from collections import defaultdict
        from datetime import datetime
        
        por_mes = defaultdict(int)
        for s in solicitudes:
            fecha = s.get('fecha_solicitud')
            if fecha:
                if isinstance(fecha, str):
                    fecha = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                mes = fecha.strftime('%Y-%m')
                por_mes[mes] += 1
        
        if por_mes:
            grafico_barras_horizontal(dict(por_mes), "Solicitudes por Mes")
        
        pausar()
    
    def estadisticas_sensores(self):
        """Estadísticas de sensores"""
        limpiar_pantalla()
        mostrar_titulo("ESTADÍSTICAS DE SENSORES")
        
        # Obtener sensores
        sensores = SensorService.listar_sensores()
        
        if not sensores:
            mostrar_info("No hay sensores registrados")
            pausar()
            return
        
        # Agrupar por estado
        por_estado = {}
        for sensor in sensores:
            estado = sensor.get('estado', 'desconocido')
            por_estado[estado] = por_estado.get(estado, 0) + 1
        
        if por_estado:
            grafico_barras_horizontal(por_estado, "Sensores por Estado")
        
        # Agrupar por país
        por_pais = {}
        for sensor in sensores:
            pais = sensor.get('pais', 'Desconocido')
            por_pais[pais] = por_pais.get(pais, 0) + 1
        
        if por_pais:
            grafico_barras_horizontal(por_pais, "Sensores por País")
        
        pausar()
    
    def estadisticas_financieras(self):
        """Estadísticas financieras"""
        limpiar_pantalla()
        mostrar_titulo("ESTADÍSTICAS FINANCIERAS")
        
        user_id = self.user_data['user_id']
        
        # Obtener cuenta corriente
        cuenta = FacturacionService.obtener_cuenta_corriente(user_id)
        if not cuenta:
            mostrar_info("No hay cuenta corriente disponible")
            pausar()
            return
        
        # Obtener movimientos recientes
        movimientos = FacturacionService.obtener_movimientos_cuenta(user_id, limite=20)
        
        stats = {
            'Saldo Actual': f"${cuenta.get('saldo', 0):.2f}",
            'Total Movimientos': len(movimientos) if movimientos else 0,
        }
        
        mostrar_estadisticas_box(stats, "Resumen Financiero")
        
        # Gráfico de movimientos por tipo
        if movimientos:
            por_tipo = {}
            for mov in movimientos:
                tipo = mov.get('tipo', 'desconocido')
                por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
            
            if por_tipo:
                grafico_barras_horizontal(por_tipo, "Movimientos por Tipo")
        
        pausar()
    
    def dashboard_admin(self):
        """Dashboard administrativo"""
        limpiar_pantalla()
        mostrar_titulo("DASHBOARD ADMINISTRATIVO")
        
        # Estadísticas del sistema
        cursor = db_manager.get_mysql_cursor()
        
        # Total usuarios
        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        total_usuarios = cursor.fetchone()['total']
        
        # Total sensores
        cursor.execute("SELECT COUNT(*) as total FROM sensores")
        total_sensores = cursor.fetchone()['total']
        
        # Total solicitudes
        cursor.execute("SELECT COUNT(*) as total FROM solicitudes")
        total_solicitudes = cursor.fetchone()['total']
        
        # Solicitudes por estado
        cursor.execute("""
            SELECT estado, COUNT(*) as total 
            FROM solicitudes 
            GROUP BY estado
        """)
        solicitudes_estado = {row['estado']: row['total'] for row in cursor.fetchall()}
        
        cursor.close()
        
        stats = {
            'Total Usuarios': total_usuarios,
            'Total Sensores': total_sensores,
            'Total Solicitudes': total_solicitudes,
        }
        
        mostrar_estadisticas_box(stats, "Estadísticas del Sistema")
        
        if solicitudes_estado:
            grafico_barras_horizontal(solicitudes_estado, "Solicitudes por Estado (Sistema)")
        
        pausar()
    
    def estadisticas_sistema(self):
        """Estadísticas detalladas del sistema (solo admin)"""
        limpiar_pantalla()
        mostrar_titulo("ESTADÍSTICAS DEL SISTEMA")
        
        cursor = db_manager.get_mysql_cursor()
        
        # Facturación total
        cursor.execute("SELECT SUM(monto_total) as total FROM facturas WHERE estado = 'pagada'")
        facturacion_total = cursor.fetchone()['total'] or 0
        
        # Procesos más solicitados
        cursor.execute("""
            SELECT p.nombre, COUNT(s.id) as cantidad
            FROM procesos p
            LEFT JOIN solicitudes s ON p.id = s.proceso_id
            GROUP BY p.id, p.nombre
            ORDER BY cantidad DESC
            LIMIT 10
        """)
        procesos_populares = {row['nombre']: row['cantidad'] for row in cursor.fetchall()}
        
        cursor.close()
        
        stats = {
            'Facturación Total': f"${facturacion_total:.2f}",
        }
        
        mostrar_estadisticas_box(stats, "Resumen Financiero del Sistema")
        
        if procesos_populares:
            grafico_barras_horizontal(procesos_populares, "Procesos Más Solicitados")
        
        pausar()


