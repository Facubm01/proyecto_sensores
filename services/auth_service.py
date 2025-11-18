"""
Servicio de autenticación y gestión de sesiones
"""

import bcrypt
import uuid
import json
from datetime import datetime
from utils.db_manager import db_manager
from config.db_config import APP_CONFIG

class AuthService:
    """Servicio para autenticación de usuarios"""
    
    @staticmethod
    def hashear_password(password):
        """Genera hash de password con bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verificar_password(password, password_hash):
        """Verifica si el password coincide con el hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def login(email, password):
        """
        Realiza login de usuario
        Retorna: (success: bool, mensaje: str, session_id: str, user_data: dict)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Buscar usuario
            query = """
                SELECT u.id, u.nombre_completo, u.email, u.password_hash, u.estado
                FROM usuarios u
                WHERE u.email = %s
            """
            cursor.execute(query, (email,))
            usuario = cursor.fetchone()
            
            if not usuario:
                return False, "Usuario no encontrado", None, None
            
            if usuario['estado'] != 'activo':
                return False, "Usuario inactivo", None, None
            
            # Verificar password
            if not AuthService.verificar_password(password, usuario['password_hash']):
                return False, "Contraseña incorrecta", None, None
            
            # Obtener roles
            query = """
                SELECT r.descripcion
                FROM usuarios_roles ur
                JOIN roles r ON ur.rol_id = r.id
                WHERE ur.usuario_id = %s
            """
            cursor.execute(query, (usuario['id'],))
            roles = [row['descripcion'] for row in cursor.fetchall()]
            
            if not roles:
                return False, "Usuario sin roles asignados", None, None
            
            cursor.close()
            
            # Crear sesión en Redis
            session_id = str(uuid.uuid4())
            user_data = {
                'user_id': usuario['id'],
                'nombre': usuario['nombre_completo'],
                'email': usuario['email'],
                'roles': roles,
                'login_time': datetime.now().isoformat()
            }
            
            redis_client = db_manager.conectar_redis()
            redis_client.hset(
                f"session:{session_id}",
                mapping={k: json.dumps(v) if isinstance(v, list) else str(v) for k, v in user_data.items()}
            )
            redis_client.expire(f"session:{session_id}", APP_CONFIG['session_timeout'])
            
            return True, "Login exitoso", session_id, user_data
            
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False, f"Error: {str(e)}", None, None
    
    @staticmethod
    def logout(session_id):
        """Cierra sesión eliminando la sesión de Redis"""
        try:
            redis_client = db_manager.conectar_redis()
            redis_client.delete(f"session:{session_id}")
            return True, "Sesión cerrada"
        except Exception as e:
            return False, f"Error al cerrar sesión: {str(e)}"
    
    @staticmethod
    def verificar_sesion(session_id):
        """
        Verifica si una sesión es válida
        Retorna: (valida: bool, user_data: dict)
        """
        try:
            redis_client = db_manager.conectar_redis()
            session_data = redis_client.hgetall(f"session:{session_id}")
            
            if not session_data:
                return False, None
            
            # Reconstruir user_data
            user_data = {}
            for key, value in session_data.items():
                if key == 'roles':
                    user_data[key] = json.loads(value)
                elif key == 'user_id':
                    user_data[key] = int(value)
                else:
                    user_data[key] = value
            
            # Renovar TTL
            redis_client.expire(f"session:{session_id}", APP_CONFIG['session_timeout'])
            
            return True, user_data
            
        except Exception as e:
            print(f"❌ Error verificando sesión: {e}")
            return False, None
    
    @staticmethod
    def registrar_usuario(nombre_completo, email, password, rol='usuario'):
        """
        Registra un nuevo usuario
        Retorna: (success: bool, mensaje: str)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Verificar si el email ya existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                return False, "El email ya está registrado"
            
            # Hashear password
            password_hash = AuthService.hashear_password(password)
            
            # Insertar usuario
            query = """
                INSERT INTO usuarios (nombre_completo, email, password_hash, estado)
                VALUES (%s, %s, %s, 'activo')
            """
            cursor.execute(query, (nombre_completo, email, password_hash))
            user_id = cursor.lastrowid
            
            # Asignar rol
            cursor.execute("SELECT id FROM roles WHERE descripcion = %s", (rol,))
            rol_row = cursor.fetchone()
            
            if rol_row:
                cursor.execute(
                    "INSERT INTO usuarios_roles (usuario_id, rol_id) VALUES (%s, %s)",
                    (user_id, rol_row['id'])
                )
            
            # Crear cuenta corriente
            cursor.execute(
                "INSERT INTO cuenta_corriente (usuario_id, saldo) VALUES (%s, 0.00)",
                (user_id,)
            )
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, "Usuario registrado exitosamente"
            
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error registrando usuario: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def listar_sesiones_activas():
        """Lista todas las sesiones activas (solo para admin)"""
        try:
            redis_client = db_manager.conectar_redis()
            session_keys = redis_client.keys("session:*")
            
            sesiones = []
            for key in session_keys:
                session_data = redis_client.hgetall(key)
                if session_data:
                    sesiones.append({
                        'session_id': key.replace('session:', ''),
                        'user_id': session_data.get('user_id'),
                        'nombre': session_data.get('nombre'),
                        'email': session_data.get('email'),
                        'login_time': session_data.get('login_time')
                    })
            
            return sesiones
            
        except Exception as e:
            print(f"❌ Error listando sesiones: {e}")
            return []
