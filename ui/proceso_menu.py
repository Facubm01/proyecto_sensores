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
            
            # Permitir ver detalle de solicitudes completadas
            if filtro_estado == 'completado' or any(s['estado'] == 'completado' for s in solicitudes):
                if confirmar("\n¿Desea ver el detalle de alguna solicitud?"):
                    solicitud_id = solicitar_entrada("ID de la solicitud", int)
                    if solicitud_id:
                        self.ver_detalle_solicitud(solicitud_id, solicitudes)
                        return  # No pausar aquí, pausar después del detalle
        
        pausar()
    
    def ver_detalle_solicitud(self, solicitud_id, solicitudes):
        """Muestra el detalle completo de una solicitud con su resultado"""
        limpiar_pantalla()
        
        # Buscar la solicitud
        solicitud = next((s for s in solicitudes if s['id'] == solicitud_id), None)
        
        if not solicitud:
            mostrar_error("Solicitud no encontrada")
            pausar()
            return
        
        mostrar_titulo(f"DETALLE DE SOLICITUD #{solicitud_id}")
        
        # Información básica
        print(f"{Fore.CYAN}Proceso:{Fore.RESET} {solicitud['proceso_nombre']}")
        print(f"{Fore.CYAN}Tipo:{Fore.RESET} {solicitud['proceso_tipo']}")
        print(f"{Fore.CYAN}Estado:{Fore.RESET} {solicitud['estado']}")
        print(f"{Fore.CYAN}Fecha solicitud:{Fore.RESET} {solicitud['fecha_solicitud']}")
        print(f"{Fore.CYAN}Costo:{Fore.RESET} ${solicitud['costo']:.2f}")
        
        # Si está completada, mostrar resultado
        if solicitud['estado'] == 'completado' and 'resultado' in solicitud:
            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"RESULTADO DEL PROCESO")
            print(f"{'='*60}{Fore.RESET}\n")
            
            resultado = solicitud['resultado']
            
            # Mostrar fecha de ejecución
            if 'fecha_ejecucion' in solicitud:
                print(f"{Fore.CYAN}Fecha de ejecución:{Fore.RESET} {solicitud['fecha_ejecucion']}\n")
            
            # Mostrar resultado según el tipo
            if 'temperatura_maxima' in resultado:
                print(f"🌡️  {Fore.YELLOW}Temperatura Máxima:{Fore.RESET} {resultado['temperatura_maxima']}°C")
            if 'temperatura_minima' in resultado:
                print(f"🌡️  {Fore.CYAN}Temperatura Mínima:{Fore.RESET} {resultado['temperatura_minima']}°C")
            if 'temperatura_promedio' in resultado:
                print(f"🌡️  {Fore.GREEN}Temperatura Promedio:{Fore.RESET} {resultado['temperatura_promedio']}°C")
            
            if 'humedad_maxima' in resultado:
                print(f"💧 {Fore.YELLOW}Humedad Máxima:{Fore.RESET} {resultado['humedad_maxima']}%")
            if 'humedad_minima' in resultado:
                print(f"💧 {Fore.CYAN}Humedad Mínima:{Fore.RESET} {resultado['humedad_minima']}%")
            if 'humedad_promedio' in resultado:
                print(f"💧 {Fore.GREEN}Humedad Promedio:{Fore.RESET} {resultado['humedad_promedio']}%")
            
            if 'total_mediciones' in resultado:
                print(f"\n📊 {Fore.MAGENTA}Total de mediciones analizadas:{Fore.RESET} {resultado['total_mediciones']:,}")
            
            # Datos mensuales (si existen)
            if 'datos_mensuales' in resultado:
                print(f"\n{Fore.YELLOW}Datos Mensuales:{Fore.RESET}")
                headers = ['Periodo', 'Temp. Promedio', 'Hum. Promedio', 'Mediciones']
                filas = []
                for dato in resultado['datos_mensuales'][:12]:  # Máximo 12 meses
                    filas.append([
                        dato.get('periodo', 'N/A'),
                        f"{dato.get('temperatura_promedio', 0):.2f}°C" if 'temperatura_promedio' in dato else 'N/A',
                        f"{dato.get('humedad_promedio', 0):.2f}%" if 'humedad_promedio' in dato else 'N/A',
                        dato.get('total_mediciones', 0)
                    ])
                mostrar_tabla(headers, filas)
            
            # Alertas generadas (si existen)
            if 'alertas_generadas' in resultado:
                print(f"\n⚠️  {Fore.RED}Alertas generadas:{Fore.RESET} {resultado['alertas_generadas']}")
                if 'mediciones_analizadas' in resultado:
                    print(f"📊 Mediciones analizadas: {resultado['mediciones_analizadas']}")
            
            # Sensores (para consulta online)
            if 'sensores' in resultado:
                print(f"\n{Fore.YELLOW}Sensores en la zona:{Fore.RESET}")
                headers = ['ID', 'Nombre', 'Ciudad', 'Temp.', 'Hum.', 'Última Act.']
                filas = []
                for sensor in resultado['sensores'][:10]:  # Máximo 10 sensores
                    filas.append([
                        sensor.get('sensor_id', 'N/A'),
                        sensor.get('sensor_nombre', 'N/A')[:20],
                        sensor.get('ciudad', 'N/A'),
                        f"{sensor.get('temperatura', 0):.1f}°C",
                        f"{sensor.get('humedad', 0):.1f}%",
                        str(sensor.get('ultima_actualizacion', 'N/A'))[:16]
                    ])
                mostrar_tabla(headers, filas)
            
            # Parámetros usados
            if 'parametros' in resultado:
                print(f"\n{Fore.CYAN}Parámetros utilizados:{Fore.RESET}")
                params = resultado['parametros']
                if 'ciudad' in params and params['ciudad']:
                    print(f"  • Ciudad: {params['ciudad']}")
                if 'pais' in params and params['pais']:
                    print(f"  • País: {params['pais']}")
                if 'fecha_inicio' in params:
                    print(f"  • Fecha inicio: {params['fecha_inicio']}")
                if 'fecha_fin' in params:
                    print(f"  • Fecha fin: {params['fecha_fin']}")
                if 'zona' in params:
                    print(f"  • Zona: {params['zona']}")
        
        elif solicitud['estado'] == 'error':
            print(f"\n{Fore.RED}❌ El proceso finalizó con error{Fore.RESET}")
            if 'resultado' in solicitud and 'error' in solicitud['resultado']:
                print(f"Error: {solicitud['resultado']['error']}")
        
        elif solicitud['estado'] == 'pendiente':
            print(f"\n{Fore.YELLOW}⏳ La solicitud está pendiente de ejecución{Fore.RESET}")
        
        elif solicitud['estado'] == 'en_proceso':
            print(f"\n{Fore.BLUE}⚙️  La solicitud se está procesando actualmente{Fore.RESET}")
        
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
