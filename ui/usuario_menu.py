"""
Módulo de gestión de usuarios (solo administradores)
"""

from services.usuario_service import UsuarioService
from utils.menu import *
from colorama import Fore
import getpass


class UsuarioMenu:
    """Menú de gestión de usuarios (admin)"""
    
    def __init__(self, user_data):
        """
        Args:
            user_data: Información del usuario autenticado
        """
        self.user_data = user_data
    
    def mostrar_menu(self):
        """Menú principal de gestión de usuarios"""
        while True:
            limpiar_pantalla()
            
            opciones = [
                (1, "Listar Todos los Usuarios"),
                (2, "Ver Detalle de Usuario"),
                (3, "Cambiar Estado (Activar/Desactivar)"),
                (4, "Asignar/Quitar Roles"),
                (5, "Ver Usuarios por Rol"),
                (6, "Resetear Contraseña"),
            ]
            
            seleccion = mostrar_menu("GESTIÓN DE USUARIOS", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.listar_usuarios()
            elif seleccion == '2':
                self.ver_detalle_usuario()
            elif seleccion == '3':
                self.cambiar_estado()
            elif seleccion == '4':
                self.asignar_roles()
            elif seleccion == '5':
                self.listar_por_rol()
            elif seleccion == '6':
                self.resetear_password()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def listar_usuarios(self):
        """Lista todos los usuarios del sistema"""
        limpiar_pantalla()
        mostrar_titulo("TODOS LOS USUARIOS")
        
        usuarios = UsuarioService.listar_usuarios()
        
        if not usuarios:
            mostrar_info("No hay usuarios registrados")
        else:
            headers = ['ID', 'Nombre', 'Email', 'Roles', 'Estado']
            filas = [
                [
                    u['id'],
                    u['nombre_completo'][:25],
                    u['email'][:30],
                    u['roles'][:30] if u['roles'] else 'Sin roles',
                    u['estado']
                ]
                for u in usuarios
            ]
            mostrar_tabla(headers, filas)
            
            print(f"\n{Fore.CYAN}Total de usuarios: {len(usuarios)}{Fore.RESET}")
        
        pausar()
    
    def ver_detalle_usuario(self):
        """Muestra información detallada de un usuario"""
        limpiar_pantalla()
        mostrar_subtitulo("DETALLE DE USUARIO")
        
        usuario_id = solicitar_entrada("ID del usuario", int)
        if not usuario_id:
            return
        
        usuario = UsuarioService.obtener_detalle_usuario(usuario_id)
        
        if not usuario:
            mostrar_error("Usuario no encontrado")
            pausar()
            return
        
        limpiar_pantalla()
        mostrar_titulo(f"DETALLE DE USUARIO #{usuario_id}")
        
        # Información básica
        print(f"{Fore.CYAN}Nombre:{Fore.RESET} {usuario['nombre_completo']}")
        print(f"{Fore.CYAN}Email:{Fore.RESET} {usuario['email']}")
        print(f"{Fore.CYAN}Estado:{Fore.RESET} {usuario['estado']}")
        print(f"{Fore.CYAN}Fecha registro:{Fore.RESET} {usuario['fecha_registro']}")
        
        # Roles
        print(f"\n{Fore.YELLOW}Roles asignados:{Fore.RESET}")
        if usuario['roles']:
            for rol in usuario['roles']:
                print(f"  • {rol}")
        else:
            print("  (Sin roles asignados)")
        
        # Cuenta corriente
        print(f"\n{Fore.GREEN}Cuenta Corriente:{Fore.RESET}")
        print(f"  💰 Saldo actual: ${usuario['saldo']:.2f}")
        print(f"  📊 Total facturado: ${usuario['total_facturado']:.2f}")
        print(f"  ⏳ Facturas pendientes: ${usuario['facturas_pendientes']:.2f}")
        
        # Actividad
        print(f"\n{Fore.MAGENTA}Actividad:{Fore.RESET}")
        sol = usuario['solicitudes']
        print(f"  📋 Solicitudes totales: {sol['total']}")
        print(f"     - Pendientes: {sol['pendientes']}")
        print(f"     - Completadas: {sol['completadas']}")
        print(f"     - Con error: {sol['errores']}")
        
        pausar()
    
    def cambiar_estado(self):
        """Cambia el estado de un usuario"""
        limpiar_pantalla()
        mostrar_subtitulo("CAMBIAR ESTADO DE USUARIO")
        
        usuario_id = solicitar_entrada("ID del usuario", int)
        if not usuario_id:
            return
        
        # Obtener usuario
        usuario = UsuarioService.obtener_detalle_usuario(usuario_id)
        
        if not usuario:
            mostrar_error("Usuario no encontrado")
            pausar()
            return
        
        print(f"\n{Fore.CYAN}Usuario:{Fore.RESET} {usuario['nombre_completo']}")
        print(f"{Fore.CYAN}Estado actual:{Fore.RESET} {usuario['estado']}")
        
        # Determinar nuevo estado
        nuevo_estado = 'activo' if usuario['estado'] == 'inactivo' else 'inactivo'
        
        if confirmar(f"\n¿Cambiar a '{nuevo_estado}'?"):
            success, mensaje = UsuarioService.cambiar_estado_usuario(usuario_id, nuevo_estado)
            
            if success:
                mostrar_exito(mensaje)
                if nuevo_estado == 'inactivo':
                    mostrar_info("El usuario no podrá iniciar sesión")
            else:
                mostrar_error(mensaje)
        
        pausar()
    
    def asignar_roles(self):
        """Asigna o quita roles a un usuario"""
        limpiar_pantalla()
        mostrar_subtitulo("ASIGNAR/QUITAR ROLES")
        
        usuario_id = solicitar_entrada("ID del usuario", int)
        if not usuario_id:
            return
        
        # Obtener usuario
        usuario = UsuarioService.obtener_detalle_usuario(usuario_id)
        
        if not usuario:
            mostrar_error("Usuario no encontrado")
            pausar()
            return
        
        print(f"\n{Fore.CYAN}Usuario:{Fore.RESET} {usuario['nombre_completo']}")
        print(f"{Fore.CYAN}Roles actuales:{Fore.RESET}")
        if usuario['roles']:
            for rol in usuario['roles']:
                print(f"  • {rol}")
        else:
            print("  (Sin roles)")
        
        # Mostrar roles disponibles
        roles_disponibles = UsuarioService.obtener_roles_disponibles()
        
        print(f"\n{Fore.YELLOW}Roles disponibles:{Fore.RESET}")
        for rol in roles_disponibles:
            print(f"  [{rol['id']}] {rol['descripcion']}")
        
        # Solicitar nuevos roles
        print(f"\n{Fore.CYAN}Ingrese los IDs de roles separados por coma (ej: 1,2){Fore.RESET}")
        roles_input = solicitar_entrada("IDs de roles", str)
        
        if not roles_input:
            return
        
        try:
            # Parsear IDs
            roles_ids = [int(r.strip()) for r in roles_input.split(',')]
            
            # Validar que existan
            ids_validos = [r['id'] for r in roles_disponibles]
            if not all(rid in ids_validos for rid in roles_ids):
                mostrar_error("Uno o más IDs de roles son inválidos")
                pausar()
                return
            
            if confirmar("\n¿Confirmar cambio de roles?"):
                success, mensaje = UsuarioService.asignar_roles(usuario_id, roles_ids)
                
                if success:
                    mostrar_exito(mensaje)
                    
                    # Mostrar nuevos roles
                    nuevos_roles = UsuarioService.obtener_roles_usuario(usuario_id)
                    print(f"\n{Fore.GREEN}Roles actualizados:{Fore.RESET}")
                    for rol in nuevos_roles:
                        print(f"  • {rol}")
                else:
                    mostrar_error(mensaje)
        
        except ValueError:
            mostrar_error("Formato inválido. Use números separados por coma")
        
        pausar()
    
    def listar_por_rol(self):
        """Lista usuarios filtrados por rol"""
        limpiar_pantalla()
        mostrar_subtitulo("USUARIOS POR ROL")
        
        # Mostrar roles disponibles
        roles_disponibles = UsuarioService.obtener_roles_disponibles()
        
        print(f"{Fore.YELLOW}Seleccione rol:{Fore.RESET}")
        for rol in roles_disponibles:
            print(f"  [{rol['id']}] {rol['descripcion']}")
        
        rol_id = solicitar_entrada("\nID del rol", int)
        if not rol_id:
            return
        
        # Buscar descripción del rol
        rol_seleccionado = next((r for r in roles_disponibles if r['id'] == rol_id), None)
        
        if not rol_seleccionado:
            mostrar_error("Rol no válido")
            pausar()
            return
        
        # Listar usuarios
        limpiar_pantalla()
        mostrar_titulo(f"USUARIOS CON ROL: {rol_seleccionado['descripcion'].upper()}")
        
        usuarios = UsuarioService.listar_usuarios_por_rol(rol_seleccionado['descripcion'])
        
        if not usuarios:
            mostrar_info(f"No hay usuarios con el rol '{rol_seleccionado['descripcion']}'")
        else:
            headers = ['ID', 'Nombre', 'Email', 'Estado']
            filas = [
                [
                    u['id'],
                    u['nombre_completo'][:30],
                    u['email'][:35],
                    u['estado']
                ]
                for u in usuarios
            ]
            mostrar_tabla(headers, filas)
            
            print(f"\n{Fore.CYAN}Total: {len(usuarios)} usuario(s){Fore.RESET}")
        
        pausar()
    
    def resetear_password(self):
        """Resetea la contraseña de un usuario"""
        limpiar_pantalla()
        mostrar_subtitulo("RESETEAR CONTRASEÑA")
        
        usuario_id = solicitar_entrada("ID del usuario", int)
        if not usuario_id:
            return
        
        # Obtener usuario
        usuario = UsuarioService.obtener_detalle_usuario(usuario_id)
        
        if not usuario:
            mostrar_error("Usuario no encontrado")
            pausar()
            return
        
        print(f"\n{Fore.CYAN}Usuario:{Fore.RESET} {usuario['nombre_completo']}")
        print(f"{Fore.CYAN}Email:{Fore.RESET} {usuario['email']}")
        
        # Solicitar nueva contraseña
        print(f"\n{Fore.YELLOW}Ingrese la nueva contraseña:{Fore.RESET}")
        nueva_password = getpass.getpass("Nueva contraseña: ")
        
        if not nueva_password:
            mostrar_error("La contraseña no puede estar vacía")
            pausar()
            return
        
        confirmar_password = getpass.getpass("Confirmar contraseña: ")
        
        if nueva_password != confirmar_password:
            mostrar_error("Las contraseñas no coinciden")
            pausar()
            return
        
        if confirmar("\n¿Confirmar reseteo de contraseña?"):
            success, mensaje = UsuarioService.resetear_password(usuario_id, nueva_password)
            
            if success:
                mostrar_exito(mensaje)
                mostrar_info(f"Informar al usuario ({usuario['email']}) su nueva contraseña")
            else:
                mostrar_error(mensaje)
        
        pausar()
