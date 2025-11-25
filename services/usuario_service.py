"""
Servicio de gestión de usuarios
Funcionalidades administrativas para gestionar usuarios del sistema
"""

from utils.db_manager import db_manager
import bcrypt
from datetime import datetime

class UsuarioService:
    """Servicio para gestión administrativa de usuarios"""
    
    @staticmethod
    def listar_usuarios():
        """
        Lista todos los usuarios del sistema con sus roles
        
        Returns:
            Lista de usuarios con información básica
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            query = """
                SELECT 
                    u.id,
                    u.nombre_completo,
                    u.email,
                    u.estado,
                    u.fecha_registro,
                    GROUP_CONCAT(r.descripcion ORDER BY r.descripcion SEPARATOR ', ') as roles
                FROM usuarios u
                LEFT JOIN usuarios_roles ur ON u.id = ur.usuario_id
                LEFT JOIN roles r ON ur.rol_id = r.id
                GROUP BY u.id, u.nombre_completo, u.email, u.estado, u.fecha_registro
                ORDER BY u.id
            """
            
            cursor.execute(query)
            usuarios = cursor.fetchall()
            cursor.close()
            
            return usuarios
            
        except Exception as e:
            print(f"❌ Error listando usuarios: {e}")
            return []
    
    @staticmethod
    def obtener_detalle_usuario(usuario_id):
        """
        Obtiene información detallada de un usuario
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Diccionario con información completa del usuario
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Información básica
            cursor.execute("""
                SELECT id, nombre_completo, email, estado, fecha_registro
                FROM usuarios
                WHERE id = %s
            """, (usuario_id,))
            
            usuario = cursor.fetchone()
            
            if not usuario:
                cursor.close()
                return None
            
            # Roles
            cursor.execute("""
                SELECT r.descripcion
                FROM usuarios_roles ur
                JOIN roles r ON ur.rol_id = r.id
                WHERE ur.usuario_id = %s
                ORDER BY r.descripcion
            """, (usuario_id,))
            
            roles = [row['descripcion'] for row in cursor.fetchall()]
            usuario['roles'] = roles
            
            # Cuenta corriente
            cursor.execute("""
                SELECT saldo
                FROM cuenta_corriente
                WHERE usuario_id = %s
            """, (usuario_id,))
            
            cuenta = cursor.fetchone()
            usuario['saldo'] = cuenta['saldo'] if cuenta else 0.00
            
            # Estadísticas de facturación
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(monto_total), 0) as total_facturado,
                    COALESCE(SUM(CASE WHEN estado = 'pendiente' THEN monto_total ELSE 0 END), 0) as pendiente
                FROM facturas
                WHERE usuario_id = %s
            """, (usuario_id,))
            
            facturacion = cursor.fetchone()
            usuario['total_facturado'] = facturacion['total_facturado']
            usuario['facturas_pendientes'] = facturacion['pendiente']
            
            # Estadísticas de solicitudes
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) as pendientes,
                    SUM(CASE WHEN estado = 'completado' THEN 1 ELSE 0 END) as completadas,
                    SUM(CASE WHEN estado = 'error' THEN 1 ELSE 0 END) as errores
                FROM solicitudes_proceso
                WHERE usuario_id = %s
            """, (usuario_id,))
            
            solicitudes = cursor.fetchone()
            usuario['solicitudes'] = solicitudes
            
            cursor.close()
            
            return usuario
            
        except Exception as e:
            print(f"❌ Error obteniendo detalle de usuario: {e}")
            return None
    
    @staticmethod
    def cambiar_estado_usuario(usuario_id, nuevo_estado):
        """
        Cambia el estado de un usuario (activo/inactivo)
        
        Args:
            usuario_id: ID del usuario
            nuevo_estado: 'activo' o 'inactivo'
            
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            cursor.execute("""
                UPDATE usuarios
                SET estado = %s
                WHERE id = %s
            """, (nuevo_estado, usuario_id))
            
            if cursor.rowcount > 0:
                db_manager.commit_mysql()
                cursor.close()
                return True, f"Usuario cambiado a estado '{nuevo_estado}'"
            else:
                cursor.close()
                return False, "Usuario no encontrado"
                
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error cambiando estado: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_roles_disponibles():
        """
        Obtiene la lista de roles disponibles
        
        Returns:
            Lista de roles
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("SELECT id, descripcion FROM roles ORDER BY id")
            roles = cursor.fetchall()
            cursor.close()
            return roles
            
        except Exception as e:
            print(f"❌ Error obteniendo roles: {e}")
            return []
    
    @staticmethod
    def asignar_roles(usuario_id, roles_ids):
        """
        Asigna roles a un usuario (reemplaza los existentes)
        
        Args:
            usuario_id: ID del usuario
            roles_ids: Lista de IDs de roles a asignar
            
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Eliminar roles actuales
            cursor.execute("DELETE FROM usuarios_roles WHERE usuario_id = %s", (usuario_id,))
            
            # Asignar nuevos roles
            for rol_id in roles_ids:
                cursor.execute("""
                    INSERT INTO usuarios_roles (usuario_id, rol_id)
                    VALUES (%s, %s)
                """, (usuario_id, rol_id))
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, "Roles actualizados exitosamente"
            
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error asignando roles: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def listar_usuarios_por_rol(rol_descripcion):
        """
        Lista usuarios que tienen un rol específico
        
        Args:
            rol_descripcion: Descripción del rol ('usuario', 'tecnico', 'administrador')
            
        Returns:
            Lista de usuarios con ese rol
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            query = """
                SELECT DISTINCT u.id, u.nombre_completo, u.email, u.estado
                FROM usuarios u
                JOIN usuarios_roles ur ON u.id = ur.usuario_id
                JOIN roles r ON ur.rol_id = r.id
                WHERE r.descripcion = %s
                ORDER BY u.nombre_completo
            """
            
            cursor.execute(query, (rol_descripcion,))
            usuarios = cursor.fetchall()
            cursor.close()
            
            return usuarios
            
        except Exception as e:
            print(f"❌ Error listando usuarios por rol: {e}")
            return []
    
    @staticmethod
    def resetear_password(usuario_id, nueva_password):
        """
        Resetea la contraseña de un usuario
        
        Args:
            usuario_id: ID del usuario
            nueva_password: Nueva contraseña en texto plano
            
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            # Hashear la nueva contraseña
            password_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt())
            
            cursor = db_manager.get_mysql_cursor()
            
            cursor.execute("""
                UPDATE usuarios
                SET password_hash = %s
                WHERE id = %s
            """, (password_hash.decode('utf-8'), usuario_id))
            
            if cursor.rowcount > 0:
                db_manager.commit_mysql()
                cursor.close()
                return True, "Contraseña reseteada exitosamente"
            else:
                cursor.close()
                return False, "Usuario no encontrado"
                
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error reseteando contraseña: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_roles_usuario(usuario_id):
        """
        Obtiene los roles actuales de un usuario
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de descripciones de roles
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            cursor.execute("""
                SELECT r.descripcion
                FROM usuarios_roles ur
                JOIN roles r ON ur.rol_id = r.id
                WHERE ur.usuario_id = %s
                ORDER BY r.descripcion
            """, (usuario_id,))
            
            roles = [row['descripcion'] for row in cursor.fetchall()]
            cursor.close()
            
            return roles
            
        except Exception as e:
            print(f"❌ Error obteniendo roles de usuario: {e}")
            return []
