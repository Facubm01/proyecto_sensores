"""
Módulo de mensajería
Gestiona mensajes privados y grupales entre usuarios
"""

from services.mensaje_service import MensajeService
from utils.menu import *
from colorama import Fore


class MensajeriaMenu:
    """Menú de mensajería del sistema"""
    
    def __init__(self, user_data):
        """
        Args:
            user_data: Información del usuario autenticado
        """
        self.user_data = user_data
    
    def mostrar_menu(self):
        """Menú principal de mensajería"""
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
