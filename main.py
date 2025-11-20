#!/usr/bin/env python3
"""
Sistema de Gestión de Sensores - Aplicación Principal
Trabajo Práctico - Persistencia Políglota
"""

from services.auth_service import AuthService
from services.alerta_service import AlertaService
from services.sensor_service import SensorService
from services.proceso_service import ProcesoService
from services.mensaje_service import MensajeService
from services.facturacion_service import FacturacionService
from services.ejecucion_service import EjecucionService
from services.control_service import ControlService
from utils.menu import *
from utils.db_manager import db_manager

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
        limpiar_pantalla()
        mostrar_titulo("INICIO DE SESIÓN")
        
        email = solicitar_entrada("Email")
        if not email:
            return
        
        import getpass
        password = getpass.getpass("Contraseña: ")
        
        print("\nVerificando credenciales...")
        success, mensaje, session_id, user_data = AuthService.login(email, password)
        
        if success:
            self.session_id = session_id
            self.user_data = user_data
            mostrar_exito(mensaje)
            pausar()
            self.menu_usuario()
        else:
            mostrar_error(mensaje)
            pausar()
    
    def registrar_usuario(self):
        """Registro de nuevo usuario"""
        limpiar_pantalla()
        mostrar_titulo("REGISTRO DE NUEVO USUARIO")
        
        nombre = solicitar_entrada("Nombre completo")
        if not nombre:
            return
        
        email = solicitar_entrada("Email")
        if not email:
            return
        
        import getpass
        password = getpass.getpass("Contraseña: ")
        password_confirm = getpass.getpass("Confirmar contraseña: ")
        
        if password != password_confirm:
            mostrar_error("Las contraseñas no coinciden")
            pausar()
            return
        
        print("\nRegistrando usuario...")
        success, mensaje = AuthService.registrar_usuario(nombre, email, password)
        
        if success:
            mostrar_exito(mensaje)
            mostrar_info("Ahora puede iniciar sesión")
        else:
            mostrar_error(mensaje)
        
        pausar()
    
    def menu_usuario(self):
        """Menú principal para usuario autenticado"""
        while self.session_id:
            limpiar_pantalla()
            mostrar_usuario_info(self.user_data)
            
            # Opciones base para todos los usuarios
            opciones = [
                (1, "Gestión de Procesos"),
                (2, "Ver Mis Solicitudes"),
                (3, "Facturación y Cuenta Corriente"),
                (4, "Mensajería"),
            ]
            
            # Opciones adicionales para técnicos
            if 'tecnico' in self.user_data['roles'] or 'administrador' in self.user_data['roles']:
                opciones.extend([
                    (5, "Gestión de Sensores"),
                    (6, "Ver Alertas"),
                    (7, "Control de Funcionamiento"),
                ])
            
            # Opciones adicionales para administradores
            if 'administrador' in self.user_data['roles']:
                opciones.extend([
                    (8, "Ejecutar Procesos Pendientes"),
                    (9, "Gestión de Usuarios"),
                    (10, "Ver Sesiones Activas"),
                    (11, "Reportes del Sistema"),
                ])
            
            opciones.append((99, "Cerrar Sesión"))
            
            seleccion = mostrar_menu("MENÚ PRINCIPAL", opciones, mostrar_salir=False)
            
            if seleccion == '1':
                self.menu_procesos()
            elif seleccion == '2':
                self.ver_mis_solicitudes()
            elif seleccion == '3':
                self.menu_facturacion()
            elif seleccion == '4':
                self.menu_mensajeria()
            elif seleccion == '5' and ('tecnico' in self.user_data['roles'] or 'administrador' in self.user_data['roles']):
                self.menu_sensores()
            elif seleccion == '6' and ('tecnico' in self.user_data['roles'] or 'administrador' in self.user_data['roles']):
                self.ver_alertas()
            elif seleccion == '7' and ('tecnico' in self.user_data['roles'] or 'administrador' in self.user_data['roles']):
                self.control_funcionamiento()
            elif seleccion == '8' and 'administrador' in self.user_data['roles']:
                self.ejecutar_procesos_pendientes()
            elif seleccion == '9' and 'administrador' in self.user_data['roles']:
                self.gestion_usuarios()
            elif seleccion == '10' and 'administrador' in self.user_data['roles']:
                self.ver_sesiones_activas()
            elif seleccion == '11' and 'administrador' in self.user_data['roles']:
                self.reportes_sistema()
            elif seleccion == '99':
                self.cerrar_sesion()
            else:
                mostrar_error("Opción inválida o sin permisos")
                pausar()
    
    def menu_procesos(self):
        """Menú de gestión de procesos"""
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
    
    def menu_facturacion(self):
        """Menú de facturación"""
        while True:
            limpiar_pantalla()
            
            # Mostrar resumen
            resumen = FacturacionService.obtener_resumen_financiero(self.user_data['user_id'])
            print(f"{Fore.YELLOW}Resumen Financiero:")
            print(f"  Saldo actual: ${resumen['saldo']:.2f}")
            print(f"  Total facturado: ${resumen['total_facturado']:.2f}")
            print(f"  Facturas pendientes: {resumen['facturas_pendientes']} (${resumen['monto_pendiente']:.2f})")
            print(f"  Facturas pagadas: {resumen['facturas_pagadas']}\n")
            
            opciones = [
                (1, "Ver Cuenta Corriente"),
                (2, "Ver Mis Facturas"),
                (3, "Ver Detalle de Factura"),
                (4, "Registrar Pago"),
                (5, "Cargar Saldo"),
            ]
            
            seleccion = mostrar_menu("FACTURACIÓN Y CUENTA CORRIENTE", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.ver_cuenta_corriente()
            elif seleccion == '2':
                self.ver_facturas()
            elif seleccion == '3':
                self.ver_detalle_factura()
            elif seleccion == '4':
                self.registrar_pago()
            elif seleccion == '5':
                self.cargar_saldo()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def ver_cuenta_corriente(self):
        """Muestra la cuenta corriente y movimientos"""
        limpiar_pantalla()
        mostrar_titulo("CUENTA CORRIENTE")
        
        cuenta = FacturacionService.obtener_cuenta_corriente(self.user_data['user_id'])
        
        if not cuenta:
            mostrar_error("No se encontró cuenta corriente")
            pausar()
            return
        
        print(f"\n{Fore.GREEN}Saldo actual: ${cuenta['saldo']:.2f}")
        print(f"Última actualización: {cuenta['ultima_actualizacion']}\n")
        
        # Mostrar movimientos
        if confirmar("¿Ver movimientos de la cuenta?"):
            limpiar_pantalla()
            mostrar_subtitulo("MOVIMIENTOS DE CUENTA")
            
            movimientos = FacturacionService.obtener_movimientos_cuenta(self.user_data['user_id'])
            
            if not movimientos:
                mostrar_info("No hay movimientos")
            else:
                headers = ['Fecha', 'Tipo', 'Concepto', 'Monto', 'Saldo']
                filas = []
                
                for m in movimientos:
                    tipo_symbol = '➖' if m['tipo'] == 'debito' else '➕'
                    monto_str = f"-${m['monto']:.2f}" if m['tipo'] == 'debito' else f"+${m['monto']:.2f}"
                    
                    filas.append([
                        str(m['fecha'])[:19],
                        tipo_symbol + ' ' + m['tipo'],
                        m['concepto'][:40],
                        monto_str,
                        f"${m['saldo_nuevo']:.2f}"
                    ])
                
                mostrar_tabla(headers, filas)
        
        pausar()
    
    def ver_facturas(self):
        """Lista facturas del usuario"""
        limpiar_pantalla()
        mostrar_titulo("MIS FACTURAS")
        
        facturas = FacturacionService.listar_facturas(self.user_data['user_id'])
        
        if not facturas:
            mostrar_info("No hay facturas")
        else:
            headers = ['ID', 'Fecha', 'Monto', 'Estado', 'Vencimiento', 'Items']
            filas = []
            
            for f in facturas:
                color_estado = Fore.GREEN if f['estado'] == 'pagada' else Fore.YELLOW if f['estado'] == 'pendiente' else Fore.RED
                
                filas.append([
                    f['id'],
                    str(f['fecha_emision'])[:10],
                    f"${f['monto_total']:.2f}",
                    f['estado'],
                    str(f['fecha_vencimiento']) if f['fecha_vencimiento'] else 'N/A',
                    f['items']
                ])
            
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def ver_detalle_factura(self):
        """Muestra el detalle completo de una factura"""
        limpiar_pantalla()
        mostrar_titulo("DETALLE DE FACTURA")
        
        factura_id = solicitar_entrada("ID de la factura", int)
        if not factura_id:
            return
        
        factura = FacturacionService.obtener_detalle_factura(factura_id)
        
        if not factura:
            mostrar_error("Factura no encontrada")
            pausar()
            return
        
        # Verificar que pertenece al usuario
        if factura['usuario_id'] != self.user_data['user_id']:
            mostrar_error("Esta factura no le pertenece")
            pausar()
            return
        
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.GREEN}Factura #{factura['id']}")
        print(f"Fecha emisión: {factura['fecha_emision']}")
        print(f"Fecha vencimiento: {factura['fecha_vencimiento']}")
        print(f"Estado: {factura['estado'].upper()}")
        print(f"Monto total: ${factura['monto_total']:.2f}")
        
        print(f"\n{Fore.YELLOW}Items de la Factura:")
        print(f"{Fore.CYAN}{'-' * 60}")
        
        for item in factura['items']:
            print(f"  • {item['proceso_nombre']}")
            print(f"    Monto: ${item['monto']:.2f}")
            print()
        
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        pausar()
    
    def registrar_pago(self):
        """Registra un pago de factura"""
        limpiar_pantalla()
        mostrar_titulo("REGISTRAR PAGO")
        
        # Mostrar facturas pendientes
        facturas = FacturacionService.listar_facturas(self.user_data['user_id'], 'pendiente')
        
        if not facturas:
            mostrar_info("No hay facturas pendientes")
            pausar()
            return
        
        print(f"{Fore.CYAN}Facturas Pendientes:\n")
        for f in facturas:
            print(f"  ID {f['id']}: ${f['monto_total']:.2f} - Vence: {f['fecha_vencimiento']}")
        
        print()
        factura_id = solicitar_entrada("ID de la factura a pagar", int)
        if not factura_id:
            return
        
        # Buscar la factura
        factura = next((f for f in facturas if f['id'] == factura_id), None)
        if not factura:
            mostrar_error("Factura no válida")
            pausar()
            return
        
        print(f"\nFactura #{factura['id']} - Monto: ${factura['monto_total']:.2f}")
        
        monto = solicitar_entrada(f"Monto a pagar (máx ${factura['monto_total']:.2f})", float)
        if not monto:
            return
        
        metodo = solicitar_entrada("Método de pago (tarjeta/transferencia/efectivo)", str, 
                                   ['tarjeta', 'transferencia', 'efectivo'])
        if not metodo:
            return
        
        referencia = solicitar_entrada("Referencia/Número de operación (opcional)", str) or None
        
        if confirmar(f"¿Confirmar pago de ${monto:.2f}?"):
            success, mensaje = FacturacionService.registrar_pago(
                factura_id,
                self.user_data['user_id'],
                monto,
                metodo,
                referencia
            )
            
            if success:
                mostrar_exito(mensaje)
            else:
                mostrar_error(mensaje)
        
        pausar()
    
    def cargar_saldo(self):
        """Carga saldo a la cuenta corriente"""
        limpiar_pantalla()
        mostrar_titulo("CARGAR SALDO")
        
        cuenta = FacturacionService.obtener_cuenta_corriente(self.user_data['user_id'])
        if cuenta:
            print(f"\n{Fore.CYAN}Saldo actual: ${cuenta['saldo']:.2f}\n")
        
        monto = solicitar_entrada("Monto a cargar", float)
        if not monto or monto <= 0:
            mostrar_error("Monto inválido")
            pausar()
            return
        
        concepto = solicitar_entrada("Concepto (opcional)", str) or "Carga de saldo"
        
        if confirmar(f"¿Confirmar carga de ${monto:.2f}?"):
            success, mensaje = FacturacionService.cargar_saldo(
                self.user_data['user_id'],
                monto,
                concepto
            )
            
            if success:
                mostrar_exito(mensaje)
            else:
                mostrar_error(mensaje)
        
        pausar()
    
    def menu_mensajeria(self):
        """Menú de mensajería"""
        while True:
            limpiar_pantalla()
            
            # Mostrar resumen
            no_leidos = MensajeService.contar_mensajes_no_leidos(self.user_data['user_id'])
            if no_leidos > 0:
                print(f"{Fore.RED}⚠️  Tiene {no_leidos} mensaje(s) sin leer\n")
            
            opciones = [
                (1, "Ver Mensajes Recibidos"),
                (2, "Ver Mensajes Enviados"),
                (3, "Enviar Mensaje Privado"),
                (4, "Enviar Mensaje a Grupo"),
                (5, "Ver Mis Grupos"),
                (6, "Crear Nuevo Grupo"),
                (7, "Agregar Miembro a Grupo"),
            ]
            
            seleccion = mostrar_menu("MENSAJERÍA", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.ver_mensajes_recibidos()
            elif seleccion == '2':
                self.ver_mensajes_enviados()
            elif seleccion == '3':
                self.enviar_mensaje_privado()
            elif seleccion == '4':
                self.enviar_mensaje_grupal()
            elif seleccion == '5':
                self.ver_grupos()
            elif seleccion == '6':
                self.crear_grupo()
            elif seleccion == '7':
                self.agregar_miembro_grupo()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def ver_mensajes_recibidos(self):
        """Ver mensajes recibidos"""
        limpiar_pantalla()
        mostrar_titulo("MENSAJES RECIBIDOS")
        
        mensajes = MensajeService.listar_mensajes_recibidos(self.user_data['user_id'])
        
        if not mensajes:
            mostrar_info("No hay mensajes")
        else:
            print(f"{Fore.CYAN}Total: {len(mensajes)} mensajes\n")
            
            for i, m in enumerate(mensajes[:20], 1):  # Mostrar máximo 20
                leido_mark = '' if m.get('leido', True) else f"{Fore.RED}[NUEVO] "
                
                if m['tipo'] == 'privado':
                    print(f"{leido_mark}{i}. De: {m.get('remitente_nombre', 'Desconocido')}")
                else:
                    print(f"{leido_mark}{i}. Grupo: {m.get('grupo_nombre', 'Desconocido')} - De: {m.get('remitente_nombre', 'Desconocido')}")
                
                print(f"   {str(m['timestamp'])[:19]}")
                print(f"   {Fore.WHITE}{m['contenido'][:80]}{'...' if len(m['contenido']) > 80 else ''}")
                print()
        
        pausar()
    
    def ver_mensajes_enviados(self):
        """Ver mensajes enviados"""
        limpiar_pantalla()
        mostrar_titulo("MENSAJES ENVIADOS")
        
        mensajes = MensajeService.listar_mensajes_enviados(self.user_data['user_id'])
        
        if not mensajes:
            mostrar_info("No hay mensajes enviados")
        else:
            print(f"{Fore.CYAN}Total: {len(mensajes)} mensajes\n")
            
            for i, m in enumerate(mensajes[:20], 1):
                if m['tipo'] == 'privado':
                    print(f"{i}. Para: {m.get('destinatario_nombre', 'Desconocido')}")
                else:
                    print(f"{i}. Grupo: {m.get('grupo_nombre', 'Desconocido')}")
                
                print(f"   {str(m['timestamp'])[:19]}")
                print(f"   {Fore.WHITE}{m['contenido'][:80]}{'...' if len(m['contenido']) > 80 else ''}")
                print()
        
        pausar()
    
    def enviar_mensaje_privado(self):
        """Enviar mensaje privado"""
        limpiar_pantalla()
        mostrar_titulo("ENVIAR MENSAJE PRIVADO")
        
        # Listar usuarios disponibles
        usuarios = MensajeService.listar_usuarios_disponibles(self.user_data['user_id'])
        
        if not usuarios:
            mostrar_info("No hay usuarios disponibles")
            pausar()
            return
        
        print(f"{Fore.CYAN}Usuarios disponibles:\n")
        for u in usuarios[:20]:  # Mostrar máximo 20
            print(f"  ID {u['id']}: {u['nombre_completo']} ({u['email']})")
        
        print()
        destinatario_id = solicitar_entrada("ID del destinatario", int)
        if not destinatario_id:
            return
        
        # Verificar que existe
        destinatario = next((u for u in usuarios if u['id'] == destinatario_id), None)
        if not destinatario:
            mostrar_error("Usuario no válido")
            pausar()
            return
        
        print(f"\nEnviando mensaje a: {destinatario['nombre_completo']}\n")
        contenido = solicitar_entrada("Mensaje", str)
        
        if not contenido:
            return
        
        if confirmar("¿Enviar mensaje?"):
            success, mensaje = MensajeService.enviar_mensaje_privado(
                self.user_data['user_id'],
                destinatario_id,
                contenido
            )
            
            if success:
                mostrar_exito(mensaje)
            else:
                mostrar_error(mensaje)
        
        pausar()
    
    def enviar_mensaje_grupal(self):
        """Enviar mensaje a grupo"""
        limpiar_pantalla()
        mostrar_titulo("ENVIAR MENSAJE A GRUPO")
        
        # Listar grupos del usuario
        grupos = MensajeService.listar_grupos_usuario(self.user_data['user_id'])
        
        if not grupos:
            mostrar_info("No pertenece a ningún grupo")
            pausar()
            return
        
        print(f"{Fore.CYAN}Mis grupos:\n")
        for g in grupos:
            print(f"  ID {g['id']}: {g['nombre']} ({g['total_miembros']} miembros)")
        
        print()
        grupo_id = solicitar_entrada("ID del grupo", int)
        if not grupo_id:
            return
        
        # Verificar que existe
        grupo = next((g for g in grupos if g['id'] == grupo_id), None)
        if not grupo:
            mostrar_error("Grupo no válido")
            pausar()
            return
        
        print(f"\nEnviando mensaje al grupo: {grupo['nombre']}\n")
        contenido = solicitar_entrada("Mensaje", str)
        
        if not contenido:
            return
        
        if confirmar("¿Enviar mensaje al grupo?"):
            success, mensaje = MensajeService.enviar_mensaje_grupal(
                self.user_data['user_id'],
                grupo_id,
                contenido
            )
            
            if success:
                mostrar_exito(mensaje)
            else:
                mostrar_error(mensaje)
        
        pausar()
    
    def ver_grupos(self):
        """Ver grupos del usuario"""
        limpiar_pantalla()
        mostrar_titulo("MIS GRUPOS")
        
        grupos = MensajeService.listar_grupos_usuario(self.user_data['user_id'])
        
        if not grupos:
            mostrar_info("No pertenece a ningún grupo")
        else:
            headers = ['ID', 'Nombre', 'Descripción', 'Miembros']
            filas = [
                [g['id'], g['nombre'], g['descripcion'][:40] if g['descripcion'] else 'N/A', g['total_miembros']]
                for g in grupos
            ]
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def crear_grupo(self):
        """Crear nuevo grupo"""
        limpiar_pantalla()
        mostrar_titulo("CREAR NUEVO GRUPO")
        
        nombre = solicitar_entrada("Nombre del grupo", str)
        if not nombre:
            return
        
        descripcion = solicitar_entrada("Descripción (opcional)", str) or None
        
        if confirmar(f"¿Crear grupo '{nombre}'?"):
            success, mensaje, grupo_id = MensajeService.crear_grupo(
                nombre,
                descripcion,
                self.user_data['user_id']
            )
            
            if success:
                mostrar_exito(mensaje)
                mostrar_info(f"ID del grupo: {grupo_id}")
            else:
                mostrar_error(mensaje)
        
        pausar()
    
    def agregar_miembro_grupo(self):
        """Agregar miembro a un grupo"""
        limpiar_pantalla()
        mostrar_titulo("AGREGAR MIEMBRO A GRUPO")
        
        # Listar grupos del usuario
        grupos = MensajeService.listar_grupos_usuario(self.user_data['user_id'])
        
        if not grupos:
            mostrar_info("No pertenece a ningún grupo")
            pausar()
            return
        
        print(f"{Fore.CYAN}Mis grupos:\n")
        for g in grupos:
            print(f"  ID {g['id']}: {g['nombre']}")
        
        print()
        grupo_id = solicitar_entrada("ID del grupo", int)
        if not grupo_id:
            return
        
        # Listar usuarios disponibles
        usuarios = MensajeService.listar_usuarios_disponibles()
        
        print(f"\n{Fore.CYAN}Usuarios disponibles:\n")
        for u in usuarios[:20]:
            print(f"  ID {u['id']}: {u['nombre_completo']} ({u['email']})")
        
        print()
        usuario_id = solicitar_entrada("ID del usuario a agregar", int)
        if not usuario_id:
            return
        
        if confirmar("¿Agregar usuario al grupo?"):
            success, mensaje = MensajeService.agregar_miembro_grupo(grupo_id, usuario_id)
            
            if success:
                mostrar_exito(mensaje)
            else:
                mostrar_error(mensaje)
        
        pausar()
    
    def menu_sensores(self):
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
    
    def ver_alertas(self):
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
    
    def control_funcionamiento(self):
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
    
    def ejecutar_procesos_pendientes(self):
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
        limpiar_pantalla()
        mostrar_titulo("GESTIÓN DE USUARIOS")
        mostrar_info("Funcionalidad en desarrollo...")
        pausar()
    
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
    
    def salir(self):
        """Sale de la aplicación"""
        if confirmar("¿Está seguro que desea salir?"):
            mostrar_info("Cerrando conexiones...")
            db_manager.cerrar_conexiones()
            mostrar_exito("¡Hasta luego!")
            self.ejecutando = False
    
    def iniciar(self):
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

def main():
    """Función principal"""
    try:
        app = SistemaSensores()
        app.iniciar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Aplicación interrumpida por el usuario")
        db_manager.cerrar_conexiones()
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        db_manager.cerrar_conexiones()

if __name__ == "__main__":
    main()