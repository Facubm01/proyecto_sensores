"""
Módulo de gestión de procesos
Gestiona solicitudes de procesos por parte de usuarios
"""

from services.proceso_service import ProcesoService
from utils.menu import *
from colorama import Fore


class ProcesoMenu:
    """Menú de gestión de procesos"""
    
    def __init__(self, user_data):
        """
        Args:
            user_data: Información del usuario autenticado
        """
        self.user_data = user_data
    
    def mostrar_menu(self):
        """Menú principal de gestión de procesos"""
        while True:
            limpiar_pantalla()
            
            opciones = [
                (1, "Ver Procesos Disponibles"),
                (2, "Solicitar Nuevo Proceso"),
            ]
            
            seleccion = mostrar_menu("GESTIÓN DE PROCESOS", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.ver_procesos_disponibles()
            elif seleccion == '2':
                self.solicitar_proceso()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def ver_procesos_disponibles(self):
        """Muestra los procesos disponibles"""
        limpiar_pantalla()
        mostrar_titulo("PROCESOS DISPONIBLES")
        
        procesos = ProcesoService.listar_procesos_disponibles()
        
        if not procesos:
            mostrar_info("No hay procesos disponibles")
        else:
            headers = ['ID', 'Nombre', 'Tipo', 'Costo']
            filas = [[p['id'], p['nombre'], p['tipo'], f"${p['costo']:.2f}"] for p in procesos]
            mostrar_tabla(headers, filas)
            
            # Mostrar detalles de un proceso
            if confirmar("¿Desea ver detalles de un proceso?"):
                proceso_id = solicitar_entrada("ID del proceso", int)
                if proceso_id:
                    proceso = next((p for p in procesos if p['id'] == proceso_id), None)
                    if proceso:
                        print(f"\n{Fore.CYAN}Proceso: {proceso['nombre']}")
                        print(f"Tipo: {proceso['tipo']}")
                        print(f"Costo: ${proceso['costo']:.2f}")
                        print(f"Descripción: {proceso['descripcion']}\n")
        
        pausar()
    
    def solicitar_proceso(self):
        """Solicita un nuevo proceso"""
        limpiar_pantalla()
        mostrar_titulo("SOLICITAR PROCESO")
        
        # Listar procesos
        procesos = ProcesoService.listar_procesos_disponibles()
        
        if not procesos:
            mostrar_error("No hay procesos disponibles")
            pausar()
            return
        
        headers = ['ID', 'Nombre', 'Costo']
        filas = [[p['id'], p['nombre'], f"${p['costo']:.2f}"] for p in procesos]
        mostrar_tabla(headers, filas)
        
        proceso_id = solicitar_entrada("ID del proceso a solicitar", int)
        if not proceso_id:
            return
        
        proceso = next((p for p in procesos if p['id'] == proceso_id), None)
        if not proceso:
            mostrar_error("Proceso no válido")
            pausar()
            return
        
        # Solicitar parámetros básicos (simplificado)
        mostrar_subtitulo(f"Parámetros para: {proceso['nombre']}")
        
        parametros = {}
        
        # Parámetros comunes según tipo de proceso
        if 'informe' in proceso['tipo']:
            parametros['ciudad'] = solicitar_entrada("Ciudad (dejar vacío para todas)", str) or None
            parametros['pais'] = solicitar_entrada("País (dejar vacío para todos)", str) or None
            parametros['fecha_inicio'] = solicitar_entrada("Fecha inicio (YYYY-MM-DD)", str)
            parametros['fecha_fin'] = solicitar_entrada("Fecha fin (YYYY-MM-DD)", str)
        elif 'alerta' in proceso['tipo']:
            parametros['ciudad'] = solicitar_entrada("Ciudad", str)
            parametros['temp_min'] = solicitar_entrada("Temperatura mínima", float)
            parametros['temp_max'] = solicitar_entrada("Temperatura máxima", float)
            parametros['fecha_inicio'] = solicitar_entrada("Fecha inicio (YYYY-MM-DD)", str)
            parametros['fecha_fin'] = solicitar_entrada("Fecha fin (YYYY-MM-DD)", str)
        elif 'consulta' in proceso['tipo']:
            parametros['zona'] = solicitar_entrada("Zona/Ciudad", str)
        
        if confirmar(f"¿Confirmar solicitud? Costo: ${proceso['costo']:.2f}"):
            success, mensaje, solicitud_id = ProcesoService.solicitar_proceso(
                self.user_data['user_id'],
                proceso_id,
                parametros
            )
            
            if success:
                mostrar_exito(mensaje)
                mostrar_info(f"ID de solicitud: {solicitud_id}")
            else:
                mostrar_error(mensaje)
        
        pausar()
    
    def ver_mis_solicitudes(self):
        """Ver solicitudes del usuario"""
        while True:
            limpiar_pantalla()
            mostrar_titulo("MIS SOLICITUDES")
            
            # Mostrar resumen
            conteos = ProcesoService.contar_solicitudes_por_estado(self.user_data['user_id'])
            print(f"{Fore.YELLOW}Resumen:")
            print(f"  Pendientes: {conteos['pendiente']}")
            print(f"  En proceso: {conteos['en_proceso']}")
            print(f"  Completadas: {conteos['completado']}")
            print(f"  Con error: {conteos['error']}\n")
            
            opciones = [
                (1, "Ver Todas"),
                (2, "Ver Pendientes"),
                (3, "Ver Completadas"),
                (4, "Cancelar Solicitud"),
            ]
            
            seleccion = mostrar_menu("", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.listar_solicitudes(None)
            elif seleccion == '2':
                self.listar_solicitudes('pendiente')
            elif seleccion == '3':
                self.listar_solicitudes('completado')
            elif seleccion == '4':
                self.cancelar_solicitud()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def listar_solicitudes(self, filtro_estado):
        """Lista solicitudes con filtro opcional"""
        limpiar_pantalla()
        titulo = "TODAS LAS SOLICITUDES" if not filtro_estado else f"SOLICITUDES {filtro_estado.upper()}S"
        mostrar_subtitulo(titulo)
        
        solicitudes = ProcesoService.listar_solicitudes_usuario(
            self.user_data['user_id'],
            filtro_estado
        )
        
        if not solicitudes:
            mostrar_info("No hay solicitudes")
        else:
            headers = ['ID', 'Proceso', 'Fecha', 'Estado', 'Costo']
            filas = [
                [
                    s['id'],
                    s['proceso_nombre'][:30],
                    str(s['fecha_solicitud'])[:19],
                    s['estado'],
                    f"${s['costo']:.2f}"
                ]
                for s in solicitudes
            ]
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def cancelar_solicitud(self):
        """Cancela una solicitud pendiente"""
        limpiar_pantalla()
        mostrar_subtitulo("CANCELAR SOLICITUD")
        
        solicitud_id = solicitar_entrada("ID de la solicitud a cancelar", int)
        if not solicitud_id:
            return
        
        if confirmar("¿Está seguro de cancelar esta solicitud?"):
            success, mensaje = ProcesoService.cancelar_solicitud(
                solicitud_id,
                self.user_data['user_id']
            )
            
            if success:
                mostrar_exito(mensaje)
            else:
                mostrar_error(mensaje)
        
        pausar()
