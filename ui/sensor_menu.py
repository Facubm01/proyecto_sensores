"""
Módulo de gestión de sensores
Gestiona sensores del sistema (solo técnicos/administradores)
"""

from services.sensor_service import SensorService
from utils.menu import *
from colorama import Fore


class SensorMenu:
    """Menú de gestión de sensores"""
    
    def __init__(self, user_data):
        """
        Args:
            user_data: Información del usuario autenticado
        """
        self.user_data = user_data
    
    def mostrar_menu(self):
        """Menú de gestión de sensores"""
        while True:
            limpiar_pantalla()
            
            # Mostrar resumen
            conteos = SensorService.contar_sensores_por_estado()
            print(f"{Fore.YELLOW}Resumen de Sensores:")
            print(f"  Activos: {conteos['activo']}")
            print(f"  Inactivos: {conteos['inactivo']}")
            print(f"  Con falla: {conteos['falla']}\n")
            
            opciones = [
                (1, "Listar Todos los Sensores"),
                (2, "Ver Detalles de un Sensor"),
                (3, "Filtrar por Estado"),
                (4, "Filtrar por País"),
            ]
            
            if 'administrador' in self.user_data['roles']:
                opciones.extend([
                    (5, "Registrar Nuevo Sensor"),
                    (6, "Cambiar Estado de Sensor"),
                ])
            
            seleccion = mostrar_menu("GESTIÓN DE SENSORES", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.listar_sensores(None, None)
            elif seleccion == '2':
                self.ver_detalles_sensor()
            elif seleccion == '3':
                self.listar_sensores_por_estado()
            elif seleccion == '4':
                self.listar_sensores_por_pais()
            elif seleccion == '5' and 'administrador' in self.user_data['roles']:
                self.registrar_sensor()
            elif seleccion == '6' and 'administrador' in self.user_data['roles']:
                self.cambiar_estado_sensor()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def listar_sensores(self, filtro_estado, filtro_pais):
        """Lista sensores con filtros opcionales"""
        limpiar_pantalla()
        titulo = "TODOS LOS SENSORES"
        if filtro_estado:
            titulo = f"SENSORES {filtro_estado.upper()}S"
        if filtro_pais:
            titulo = f"SENSORES DE {filtro_pais.upper()}"
        
        mostrar_titulo(titulo)
        
        sensores = SensorService.listar_sensores(filtro_estado, filtro_pais)
        
        if not sensores:
            mostrar_info("No hay sensores")
        else:
            headers = ['ID', 'Código', 'Nombre', 'Ciudad', 'País', 'Estado']
            filas = [
                [s['id'], s['codigo'], s['nombre'][:25], s['ciudad'], s['pais'], s['estado']]
                for s in sensores
            ]
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def listar_sensores_por_estado(self):
        """Filtra sensores por estado"""
        limpiar_pantalla()
        mostrar_subtitulo("FILTRAR POR ESTADO")
        
        estado = solicitar_entrada("Estado (activo/inactivo/falla)", str, ['activo', 'inactivo', 'falla'])
        if estado:
            self.listar_sensores(estado, None)
    
    def listar_sensores_por_pais(self):
        """Filtra sensores por país"""
        limpiar_pantalla()
        mostrar_subtitulo("FILTRAR POR PAÍS")
        
        paises = SensorService.listar_paises()
        print(f"{Fore.CYAN}Países disponibles: {', '.join(paises)}\n")
        
        pais = solicitar_entrada("País", str)
        if pais:
            self.listar_sensores(None, pais)
    
    def ver_detalles_sensor(self):
        """Muestra detalles completos de un sensor"""
        limpiar_pantalla()
        mostrar_titulo("DETALLES DE SENSOR")
        
        sensor_id = solicitar_entrada("ID del sensor", int)
        if not sensor_id:
            return
        
        sensor = SensorService.obtener_sensor(sensor_id)
        
        if not sensor:
            mostrar_error("Sensor no encontrado")
            pausar()
            return
        
        # Información básica
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.GREEN}ID: {sensor['id']}")
        print(f"Código: {sensor['codigo']}")
        print(f"Nombre: {sensor['nombre']}")
        print(f"Tipo: {sensor['tipo']}")
        print(f"Estado: {sensor['estado']}")
        print(f"\n{Fore.YELLOW}Ubicación:")
        print(f"  Ciudad: {sensor['ciudad']}")
        print(f"  País: {sensor['pais']}")
        print(f"  Coordenadas: {sensor['latitud']}, {sensor['longitud']}")
        print(f"\nFecha inicio: {sensor['fecha_inicio']}")
        
        # Última medición
        ultima = SensorService.obtener_ultima_medicion(sensor_id)
        if ultima:
            print(f"\n{Fore.YELLOW}Última Medición:")
            print(f"  Fecha: {ultima['timestamp']}")
            print(f"  Temperatura: {ultima['temperatura']}°C")
            print(f"  Humedad: {ultima['humedad']}%")
        
        # Estadísticas
        stats = SensorService.obtener_estadisticas_sensor(sensor_id, dias=7)
        if stats:
            print(f"\n{Fore.YELLOW}Estadísticas (últimos 7 días):")
            print(f"  Temperatura promedio: {stats['temp_promedio']}°C")
            print(f"  Temperatura máxima: {stats['temp_max']}°C")
            print(f"  Temperatura mínima: {stats['temp_min']}°C")
            print(f"  Humedad promedio: {stats['hum_promedio']}%")
            print(f"  Total mediciones: {stats['total_mediciones']}")
        
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        pausar()
    
    def registrar_sensor(self):
        """Registra un nuevo sensor"""
        limpiar_pantalla()
        mostrar_titulo("REGISTRAR NUEVO SENSOR")
        
        nombre = solicitar_entrada("Nombre del sensor", str)
        if not nombre:
            return
        
        codigo = solicitar_entrada("Código único", str)
        if not codigo:
            return
        
        tipo = solicitar_entrada("Tipo (temperatura/humedad/ambos)", str, ['temperatura', 'humedad', 'ambos'])
        if not tipo:
            return
        
        latitud = solicitar_entrada("Latitud", float)
        if latitud is None:
            return
        
        longitud = solicitar_entrada("Longitud", float)
        if longitud is None:
            return
        
        ciudad = solicitar_entrada("Ciudad", str)
        if not ciudad:
            return
        
        pais = solicitar_entrada("País", str)
        if not pais:
            return
        
        success, mensaje, sensor_id = SensorService.registrar_sensor(
            nombre, codigo, tipo, latitud, longitud, ciudad, pais
        )
        
        if success:
            mostrar_exito(mensaje)
            mostrar_info(f"ID del sensor: {sensor_id}")
        else:
            mostrar_error(mensaje)
        
        pausar()
    
    def cambiar_estado_sensor(self):
        """Cambia el estado de un sensor"""
        limpiar_pantalla()
        mostrar_titulo("CAMBIAR ESTADO DE SENSOR")
        
        sensor_id = solicitar_entrada("ID del sensor", int)
        if not sensor_id:
            return
        
        sensor = SensorService.obtener_sensor(sensor_id)
        if not sensor:
            mostrar_error("Sensor no encontrado")
            pausar()
            return
        
        print(f"\nSensor: {sensor['nombre']} ({sensor['codigo']})")
        print(f"Estado actual: {sensor['estado']}\n")
        
        nuevo_estado = solicitar_entrada("Nuevo estado (activo/inactivo/falla)", str, ['activo', 'inactivo', 'falla'])
        if not nuevo_estado:
            return
        
        if confirmar(f"¿Cambiar estado a '{nuevo_estado}'?"):
            success, mensaje = SensorService.cambiar_estado_sensor(sensor_id, nuevo_estado)
            
            if success:
                mostrar_exito(mensaje)
            else:
                mostrar_error(mensaje)
        
        pausar()
    
