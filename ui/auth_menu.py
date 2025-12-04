"""
Módulo de autenticación
Gestiona login y registro de usuarios
"""

from services.auth_service import AuthService
from utils.menu import *
from utils.validaciones import validar_email, validar_password, validar_nombre
import getpass


class AuthMenu:
    """Menú de autenticación del sistema"""
    
    @staticmethod
    def iniciar_sesion():
        """
        Proceso de inicio de sesión
        
        Returns:
            tuple: (success, session_id, user_data) o (False, None, None) si falla
        """
        limpiar_pantalla()
        mostrar_titulo("INICIO DE SESIÓN")
        
        email = solicitar_entrada("Email", validador=lambda e: validar_email(e))
        if not email:
            return False, None, None
        
        password = getpass.getpass("Contraseña: ")
        
        print("\nVerificando credenciales...")
        success, mensaje, session_id, user_data = AuthService.login(email, password)
        
        if success:
            mostrar_exito(mensaje)
            pausar()
            return True, session_id, user_data
        else:
            mostrar_error(mensaje)
            pausar()
            return False, None, None
    
    @staticmethod
    def registrar_usuario():
        """
        Registro de nuevo usuario
        
        Returns:
            bool: True si el registro fue exitoso
        """
        limpiar_pantalla()
        mostrar_titulo("REGISTRO DE NUEVO USUARIO")
        
        nombre = solicitar_entrada("Nombre completo", validador=lambda n: validar_nombre(n))
        if not nombre:
            return False
        
        email = solicitar_entrada("Email", validador=lambda e: validar_email(e))
        if not email:
            return False
        
        # Validar contraseña
        while True:
            password = getpass.getpass("Contraseña: ")
            es_valida, mensaje = validar_password(password)
            if not es_valida:
                mostrar_error(mensaje)
                continue
            break
        
        # Confirmar contraseña
        while True:
            password_confirm = getpass.getpass("Confirmar contraseña: ")
            if password != password_confirm:
                mostrar_error("Las contraseñas no coinciden")
                continue
            break
        
        print("\nRegistrando usuario...")
        success, mensaje = AuthService.registrar_usuario(nombre, email, password)
        
        if success:
            mostrar_exito(mensaje)
            mostrar_info("Ahora puede iniciar sesión")
        else:
            mostrar_error(mensaje)
        
        pausar()
        return success
