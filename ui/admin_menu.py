"""
Módulo de administración
Funciones administrativas del sistema (solo administradores)
"""

from services.ejecucion_service import EjecucionService
from services.auth_service import AuthService
from services.proceso_service import ProcesoService
from utils.menu import *
from utils.db_manager import db_manager
from colorama import Fore


class AdminMenu:
    """Menú de administración"""
    
    def __init__(self, user_data):
        """
        Args:
            user_data: Información del usuario autenticado
        """
        self.user_data = user_data
    
    def menu_ejecutar_procesos(self):
        """Ejecutar procesos pendientes (Admin)"""
        while True:
            limpiar_pantalla()
            
            # Mostrar procesos pendientes
            pendientes_ids = ProcesoService.obtener_procesos_pendientes(10)
            
            print(f"{Fore.YELLOW}Procesos en cola: {len(pendientes_ids)}\n")
            
            if pendientes_ids:
                cursor = db_manager.get_mysql_cursor()
                cursor.execute(f"""
                    SELECT sp.id, sp.fecha_solicitud, u.nombre_completo, p.nombre
                    FROM solicitudes_proceso sp
                    JOIN usuarios u ON sp.usuario_id = u.id
                    JOIN procesos p ON sp.proceso_id = p.id
                    WHERE sp.id IN ({','.join(['%s'] * len(pendientes_ids))})
                """, tuple(pendientes_ids))
                
                solicitudes = cursor.fetchall()
                cursor.close()
                
                headers = ['ID', 'Usuario', 'Proceso', 'Fecha']
                filas = [
                    [s['id'], s['nombre_completo'][:20], s['nombre'][:30], str(s['fecha_solicitud'])[:19]]
                    for s in solicitudes
                ]
                mostrar_tabla(headers, filas)
            
            opciones = [
                (1, "Ejecutar Siguiente Proceso"),
                (2, "Ejecutar TODOS los Procesos"),
            ]
            
            seleccion = mostrar_menu("EJECUTAR PROCESOS PENDIENTES", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.ejecutar_un_proceso()
            elif seleccion == '2':
                self.ejecutar_todos_procesos()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def ejecutar_un_proceso(self):
        """Ejecuta un solo proceso de la cola"""
        limpiar_pantalla()
        mostrar_subtitulo("EJECUTAR PROCESO")
        
        print(f"{Fore.CYAN}Ejecutando proceso...\n")
        
        success, mensaje = EjecucionService.ejecutar_proceso_pendiente()
        
        if success:
            mostrar_exito(mensaje)
            mostrar_info("Factura generada automáticamente")
        else:
            mostrar_error(mensaje)
        
        pausar()
    
    def ejecutar_todos_procesos(self):
        """Ejecuta todos los procesos pendientes"""
        limpiar_pantalla()
        mostrar_subtitulo("EJECUTAR TODOS LOS PROCESOS")
        
        pendientes_ids = ProcesoService.obtener_procesos_pendientes(100)
        
        if not pendientes_ids:
            mostrar_info("No hay procesos pendientes")
            pausar()
            return
        
        print(f"{Fore.YELLOW}Procesos en cola: {len(pendientes_ids)}\n")
        
        if not confirmar(f"¿Ejecutar TODOS los {len(pendientes_ids)} procesos?"):
            return
        
        ejecutados = 0
        errores = 0
        
        print(f"\n{Fore.CYAN}Ejecutando procesos...\n")
        
        while True:
            success, mensaje = EjecucionService.ejecutar_proceso_pendiente()
            
            if not success:
                if "No hay procesos pendientes" in mensaje:
                    break
                else:
                    errores += 1
                    print(f"{Fore.RED}✗ {mensaje}")
            else:
                ejecutados += 1
                print(f"{Fore.GREEN}✓ {mensaje}")
        
        print(f"\n{Fore.YELLOW}Resumen:")
        print(f"  Ejecutados: {ejecutados}")
        print(f"  Errores: {errores}")
        
        pausar()
    
    def gestion_usuarios(self):
        """Gestión de usuarios (Admin)"""
        from ui.usuario_menu import UsuarioMenu
        menu = UsuarioMenu(self.user_data)
        menu.mostrar_menu()
    
    
    def ver_sesiones_activas(self):
        """Ver sesiones activas (Admin)"""
        limpiar_pantalla()
        mostrar_titulo("SESIONES ACTIVAS")
        
        sesiones = AuthService.listar_sesiones_activas()
        
        if not sesiones:
            mostrar_info("No hay sesiones activas")
        else:
            headers = ['Session ID', 'User ID', 'Nombre', 'Email', 'Login']
            filas = [
                [s['session_id'][:8] + '...', s['user_id'], s['nombre'], s['email'], s['login_time'][:19]]
                for s in sesiones
            ]
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def reportes_sistema(self):
        """Reportes del sistema (Admin)"""
        while True:
            limpiar_pantalla()
            
            opciones = [
                (1, "Resumen General del Sistema"),
                (2, "Estadísticas de Sensores"),
                (3, "Estadísticas de Mediciones"),
                (4, "Estadísticas de Procesos"),
                (5, "Estadísticas Financieras"),
            ]
            
            seleccion = mostrar_menu("REPORTES DEL SISTEMA", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.reporte_resumen_general()
            elif seleccion == '2':
                self.reporte_sensores()
            elif seleccion == '3':
                self.reporte_mediciones()
            elif seleccion == '4':
                self.reporte_procesos()
            elif seleccion == '5':
                self.reporte_financiero()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def reporte_resumen_general(self):
        """Resumen general del sistema"""
        limpiar_pantalla()
        mostrar_titulo("RESUMEN GENERAL DEL SISTEMA")
        
        cursor = db_manager.get_mysql_cursor()
        db = db_manager.conectar_mongodb()
        
        # Usuarios
        cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE estado = 'activo'")
        total_usuarios = cursor.fetchone()['total']
        
        # Sensores
        cursor.execute("SELECT COUNT(*) as total FROM sensores")
        total_sensores = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM sensores WHERE estado = 'activo'")
        sensores_activos = cursor.fetchone()['total']
        
        # Procesos
        cursor.execute("SELECT COUNT(*) as total FROM solicitudes_proceso")
        total_solicitudes = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM solicitudes_proceso WHERE estado = 'pendiente'")
        solicitudes_pendientes = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM solicitudes_proceso WHERE estado = 'completado'")
        solicitudes_completadas = cursor.fetchone()['total']
        
        # Facturas
        cursor.execute("SELECT COUNT(*) as total, COALESCE(SUM(monto_total), 0) as monto FROM facturas")
        facturas_data = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as total, COALESCE(SUM(monto_total), 0) as monto FROM facturas WHERE estado = 'pendiente'")
        facturas_pendientes = cursor.fetchone()
        
        cursor.close()
        
        # Mediciones
        total_mediciones = db.mediciones.count_documents({})
        
        # Alertas
        alertas_activas = db.alertas.count_documents({'estado': 'activa'})
        
        # Mensajes
        total_mensajes = db.mensajes.count_documents({})
        
        # Mostrar reporte
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.GREEN}USUARIOS:")
        print(f"  Total usuarios activos: {total_usuarios}")
        
        print(f"\n{Fore.GREEN}SENSORES:")
        print(f"  Total sensores: {total_sensores}")
        print(f"  Activos: {sensores_activos}")
        print(f"  Inactivos/Falla: {total_sensores - sensores_activos}")
        
        print(f"\n{Fore.GREEN}MEDICIONES:")
        print(f"  Total mediciones registradas: {total_mediciones:,}")
        
        print(f"\n{Fore.GREEN}PROCESOS:")
        print(f"  Total solicitudes: {total_solicitudes}")
        print(f"  Pendientes: {solicitudes_pendientes}")
        print(f"  Completadas: {solicitudes_completadas}")
        
        print(f"\n{Fore.GREEN}FACTURACIÓN:")
        print(f"  Total facturas: {facturas_data['total']}")
        print(f"  Monto total facturado: ${facturas_data['monto']:.2f}")
        print(f"  Facturas pendientes: {facturas_pendientes['total']} (${facturas_pendientes['monto']:.2f})")
        
        print(f"\n{Fore.GREEN}ALERTAS:")
        print(f"  Alertas activas: {alertas_activas}")
        
        print(f"\n{Fore.GREEN}MENSAJERÍA:")
        print(f"  Total mensajes: {total_mensajes}")
        
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        pausar()
    
    def reporte_sensores(self):
        """Estadísticas de sensores"""
        limpiar_pantalla()
        mostrar_titulo("ESTADÍSTICAS DE SENSORES")
        
        cursor = db_manager.get_mysql_cursor()
        
        # Por estado
        cursor.execute("""
            SELECT estado, COUNT(*) as total
            FROM sensores
            GROUP BY estado
        """)
        por_estado = cursor.fetchall()
        
        # Por país
        cursor.execute("""
            SELECT pais, COUNT(*) as total
            FROM sensores
            GROUP BY pais
            ORDER BY total DESC
        """)
        por_pais = cursor.fetchall()
        
        cursor.close()
        
        print(f"\n{Fore.YELLOW}Sensores por Estado:")
        headers = ['Estado', 'Total']
        filas = [[e['estado'], e['total']] for e in por_estado]
        mostrar_tabla(headers, filas)
        
        print(f"\n{Fore.YELLOW}Sensores por País:")
        headers = ['País', 'Total']
        filas = [[p['pais'], p['total']] for p in por_pais]
        mostrar_tabla(headers, filas)
        
        pausar()
    
    def reporte_mediciones(self):
        """Estadísticas de mediciones"""
        limpiar_pantalla()
        mostrar_titulo("ESTADÍSTICAS DE MEDICIONES")
        
        db = db_manager.conectar_mongodb()
        
        # Total
        total = db.mediciones.count_documents({})
        
        # Por ciudad (top 10)
        pipeline = [
            {
                '$group': {
                    '_id': '$ciudad',
                    'total': {'$sum': 1}
                }
            },
            {'$sort': {'total': -1}},
            {'$limit': 10}
        ]
        
        por_ciudad = list(db.mediciones.aggregate(pipeline))
        
        # Promedios generales
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'temp_promedio': {'$avg': '$temperatura'},
                    'hum_promedio': {'$avg': '$humedad'}
                }
            }
        ]
        
        promedios = list(db.mediciones.aggregate(pipeline))
        
        print(f"\n{Fore.GREEN}Total mediciones: {total:,}\n")
        
        if promedios:
            print(f"{Fore.YELLOW}Promedios Generales:")
            print(f"  Temperatura: {promedios[0]['temp_promedio']:.2f}°C")
            print(f"  Humedad: {promedios[0]['hum_promedio']:.2f}%\n")
        
        if por_ciudad:
            print(f"{Fore.YELLOW}Top 10 Ciudades con más mediciones:")
            headers = ['Ciudad', 'Total Mediciones']
            filas = [[c['_id'], f"{c['total']:,}"] for c in por_ciudad]
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def reporte_procesos(self):
        """Estadísticas de procesos"""
        limpiar_pantalla()
        mostrar_titulo("ESTADÍSTICAS DE PROCESOS")
        
        cursor = db_manager.get_mysql_cursor()
        
        # Por estado
        cursor.execute("""
            SELECT estado, COUNT(*) as total
            FROM solicitudes_proceso
            GROUP BY estado
        """)
        por_estado = cursor.fetchall()
        
        # Por tipo de proceso (top 10)
        cursor.execute("""
            SELECT p.nombre, COUNT(*) as total
            FROM solicitudes_proceso sp
            JOIN procesos p ON sp.proceso_id = p.id
            GROUP BY p.nombre
            ORDER BY total DESC
            LIMIT 10
        """)
        por_tipo = cursor.fetchall()
        
        cursor.close()
        
        print(f"\n{Fore.YELLOW}Solicitudes por Estado:")
        headers = ['Estado', 'Total']
        filas = [[e['estado'], e['total']] for e in por_estado]
        mostrar_tabla(headers, filas)
        
        if por_tipo:
            print(f"\n{Fore.YELLOW}Top 10 Procesos más Solicitados:")
            headers = ['Proceso', 'Total']
            filas = [[t['nombre'][:40], t['total']] for t in por_tipo]
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def reporte_financiero(self):
        """Estadísticas financieras"""
        limpiar_pantalla()
        mostrar_titulo("ESTADÍSTICAS FINANCIERAS")
        
        cursor = db_manager.get_mysql_cursor()
        
        # Facturación general
        cursor.execute("""
            SELECT 
                COUNT(*) as total_facturas,
                COALESCE(SUM(monto_total), 0) as monto_total
            FROM facturas
        """)
        general = cursor.fetchone()
        
        # Por estado
        cursor.execute("""
            SELECT estado, COUNT(*) as total, COALESCE(SUM(monto_total), 0) as monto
            FROM facturas
            GROUP BY estado
        """)
        por_estado = cursor.fetchall()
        
        # Top usuarios facturados
        cursor.execute("""
            SELECT u.nombre_completo, COUNT(f.id) as facturas, COALESCE(SUM(f.monto_total), 0) as monto
            FROM facturas f
            JOIN usuarios u ON f.usuario_id = u.id
            GROUP BY u.nombre_completo
            ORDER BY monto DESC
            LIMIT 10
        """)
        top_usuarios = cursor.fetchall()
        
        cursor.close()
        
        print(f"\n{Fore.GREEN}Facturación General:")
        print(f"  Total facturas: {general['total_facturas']}")
        print(f"  Monto total: ${general['monto_total']:.2f}\n")
        
        print(f"{Fore.YELLOW}Facturas por Estado:")
        headers = ['Estado', 'Cantidad', 'Monto']
        filas = [[e['estado'], e['total'], f"${e['monto']:.2f}"] for e in por_estado]
        mostrar_tabla(headers, filas)
        
        if top_usuarios:
            print(f"\n{Fore.YELLOW}Top 10 Usuarios por Facturación:")
            headers = ['Usuario', 'Facturas', 'Monto Total']
            filas = [[u['nombre_completo'][:30], u['facturas'], f"${u['monto']:.2f}"] for u in top_usuarios]
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        if confirmar("¿Está seguro que desea cerrar sesión?"):
            AuthService.logout(self.session_id)
            self.session_id = None
            self.user_data = None
            mostrar_exito("Sesión cerrada exitosamente")
            pausar()
    
