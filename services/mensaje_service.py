"""
Servicio de mensajería
"""

from datetime import datetime
from utils.db_manager import db_manager

class MensajeService:
    """Servicio para gestión de mensajes"""
    
    @staticmethod
    def enviar_mensaje_privado(remitente_id, destinatario_id, contenido):
        """
        Envía un mensaje privado a otro usuario
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            # Verificar que el destinatario existe
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("SELECT id FROM usuarios WHERE id = %s AND estado = 'activo'", (destinatario_id,))
            if not cursor.fetchone():
                cursor.close()
                return False, "Destinatario no encontrado o inactivo"
            cursor.close()
            
            # Insertar mensaje en MongoDB
            db = db_manager.conectar_mongodb()
            
            mensaje = {
                'remitente_id': remitente_id,
                'destinatario_id': destinatario_id,
                'grupo_id': None,
                'timestamp': datetime.now(),
                'contenido': contenido,
                'tipo': 'privado',
                'leido': False
            }
            
            resultado = db.mensajes.insert_one(mensaje)
            
            if resultado.inserted_id:
                return True, "Mensaje enviado"
            else:
                return False, "Error al enviar mensaje"
            
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def enviar_mensaje_grupal(remitente_id, grupo_id, contenido):
        """
        Envía un mensaje a un grupo
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            # Verificar que el grupo existe y el usuario es miembro
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("""
                SELECT g.id FROM grupos g
                JOIN grupos_miembros gm ON g.id = gm.grupo_id
                WHERE g.id = %s AND gm.usuario_id = %s
            """, (grupo_id, remitente_id))
            
            if not cursor.fetchone():
                cursor.close()
                return False, "Grupo no encontrado o no es miembro"
            cursor.close()
            
            # Insertar mensaje en MongoDB
            db = db_manager.conectar_mongodb()
            
            mensaje = {
                'remitente_id': remitente_id,
                'destinatario_id': None,
                'grupo_id': grupo_id,
                'timestamp': datetime.now(),
                'contenido': contenido,
                'tipo': 'grupal'
            }
            
            resultado = db.mensajes.insert_one(mensaje)
            
            if resultado.inserted_id:
                return True, "Mensaje enviado al grupo"
            else:
                return False, "Error al enviar mensaje"
            
        except Exception as e:
            print(f"❌ Error enviando mensaje grupal: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def listar_mensajes_recibidos(usuario_id, limite=50):
        """
        Lista mensajes recibidos por un usuario (privados y grupales)
        
        Returns:
            Lista de mensajes con información del remitente
        """
        try:
            db = db_manager.conectar_mongodb()
            
            # Obtener grupos del usuario
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("""
                SELECT grupo_id FROM grupos_miembros WHERE usuario_id = %s
            """, (usuario_id,))
            grupos_ids = [row['grupo_id'] for row in cursor.fetchall()]
            
            # Buscar mensajes privados y grupales
            query = {
                '$or': [
                    {'destinatario_id': usuario_id},  # Mensajes privados
                    {'grupo_id': {'$in': grupos_ids}} if grupos_ids else {'grupo_id': None}  # Mensajes grupales
                ]
            }
            
            mensajes = list(db.mensajes.find(query).sort('timestamp', -1).limit(limite))
            
            # Enriquecer con datos del remitente y grupo
            for mensaje in mensajes:
                # Datos del remitente
                cursor.execute("""
                    SELECT nombre_completo, email FROM usuarios WHERE id = %s
                """, (mensaje['remitente_id'],))
                remitente = cursor.fetchone()
                if remitente:
                    mensaje['remitente_nombre'] = remitente['nombre_completo']
                    mensaje['remitente_email'] = remitente['email']
                
                # Si es grupal, datos del grupo
                if mensaje.get('grupo_id'):
                    cursor.execute("""
                        SELECT nombre FROM grupos WHERE id = %s
                    """, (mensaje['grupo_id'],))
                    grupo = cursor.fetchone()
                    if grupo:
                        mensaje['grupo_nombre'] = grupo['nombre']
            
            cursor.close()
            return mensajes
            
        except Exception as e:
            print(f"❌ Error listando mensajes: {e}")
            return []
    
    @staticmethod
    def listar_mensajes_enviados(usuario_id, limite=50):
        """
        Lista mensajes enviados por un usuario
        
        Returns:
            Lista de mensajes
        """
        try:
            db = db_manager.conectar_mongodb()
            
            mensajes = list(db.mensajes.find(
                {'remitente_id': usuario_id}
            ).sort('timestamp', -1).limit(limite))
            
            # Enriquecer con datos del destinatario o grupo
            cursor = db_manager.get_mysql_cursor()
            
            for mensaje in mensajes:
                if mensaje['tipo'] == 'privado':
                    cursor.execute("""
                        SELECT nombre_completo, email FROM usuarios WHERE id = %s
                    """, (mensaje['destinatario_id'],))
                    destinatario = cursor.fetchone()
                    if destinatario:
                        mensaje['destinatario_nombre'] = destinatario['nombre_completo']
                        mensaje['destinatario_email'] = destinatario['email']
                else:
                    cursor.execute("""
                        SELECT nombre FROM grupos WHERE id = %s
                    """, (mensaje['grupo_id'],))
                    grupo = cursor.fetchone()
                    if grupo:
                        mensaje['grupo_nombre'] = grupo['nombre']
            
            cursor.close()
            return mensajes
            
        except Exception as e:
            print(f"❌ Error listando mensajes enviados: {e}")
            return []
    
    @staticmethod
    def marcar_como_leido(mensaje_id):
        """
        Marca un mensaje como leído
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            from bson.objectid import ObjectId
            db = db_manager.conectar_mongodb()
            
            resultado = db.mensajes.update_one(
                {'_id': ObjectId(mensaje_id)},
                {'$set': {'leido': True}}
            )
            
            if resultado.modified_count > 0:
                return True, "Mensaje marcado como leído"
            else:
                return False, "Mensaje no encontrado"
            
        except Exception as e:
            print(f"❌ Error marcando mensaje: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def contar_mensajes_no_leidos(usuario_id):
        """
        Cuenta mensajes privados no leídos
        
        Returns:
            Número de mensajes no leídos
        """
        try:
            db = db_manager.conectar_mongodb()
            
            count = db.mensajes.count_documents({
                'destinatario_id': usuario_id,
                'leido': False
            })
            
            return count
            
        except Exception as e:
            print(f"❌ Error contando mensajes: {e}")
            return 0
    
    @staticmethod
    def listar_usuarios_disponibles(excluir_usuario_id=None):
        """
        Lista usuarios activos para enviar mensajes
        
        Returns:
            Lista de usuarios
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            query = "SELECT id, nombre_completo, email FROM usuarios WHERE estado = 'activo'"
            params = []
            
            if excluir_usuario_id:
                query += " AND id != %s"
                params.append(excluir_usuario_id)
            
            query += " ORDER BY nombre_completo"
            
            cursor.execute(query, tuple(params))
            usuarios = cursor.fetchall()
            cursor.close()
            
            return usuarios
            
        except Exception as e:
            print(f"❌ Error listando usuarios: {e}")
            return []
    
    @staticmethod
    def listar_grupos_usuario(usuario_id):
        """
        Lista grupos a los que pertenece un usuario
        
        Returns:
            Lista de grupos
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            cursor.execute("""
                SELECT g.id, g.nombre, g.descripcion,
                       COUNT(gm2.usuario_id) as total_miembros
                FROM grupos g
                JOIN grupos_miembros gm ON g.id = gm.grupo_id
                LEFT JOIN grupos_miembros gm2 ON g.id = gm2.grupo_id
                WHERE gm.usuario_id = %s
                GROUP BY g.id, g.nombre, g.descripcion
                ORDER BY g.nombre
            """, (usuario_id,))
            
            grupos = cursor.fetchall()
            cursor.close()
            
            return grupos
            
        except Exception as e:
            print(f"❌ Error listando grupos: {e}")
            return []
    
    @staticmethod
    def crear_grupo(nombre, descripcion, creador_id):
        """
        Crea un nuevo grupo y agrega al creador como miembro
        
        Returns:
            (success: bool, mensaje: str, grupo_id: int)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Crear grupo
            cursor.execute("""
                INSERT INTO grupos (nombre, descripcion)
                VALUES (%s, %s)
            """, (nombre, descripcion))
            
            grupo_id = cursor.lastrowid
            
            # Agregar creador como miembro
            cursor.execute("""
                INSERT INTO grupos_miembros (grupo_id, usuario_id)
                VALUES (%s, %s)
            """, (grupo_id, creador_id))
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, "Grupo creado exitosamente", grupo_id
            
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error creando grupo: {e}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def agregar_miembro_grupo(grupo_id, usuario_id):
        """
        Agrega un usuario a un grupo
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Verificar que el grupo existe
            cursor.execute("SELECT id FROM grupos WHERE id = %s", (grupo_id,))
            if not cursor.fetchone():
                cursor.close()
                return False, "Grupo no encontrado"
            
            # Verificar que el usuario existe y está activo
            cursor.execute("SELECT id FROM usuarios WHERE id = %s AND estado = 'activo'", (usuario_id,))
            if not cursor.fetchone():
                cursor.close()
                return False, "Usuario no encontrado o inactivo"
            
            # Agregar miembro
            cursor.execute("""
                INSERT INTO grupos_miembros (grupo_id, usuario_id)
                VALUES (%s, %s)
            """, (grupo_id, usuario_id))
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, "Usuario agregado al grupo"
            
        except Exception as e:
            db_manager.rollback_mysql()
            if "Duplicate entry" in str(e):
                return False, "El usuario ya es miembro del grupo"
            print(f"❌ Error agregando miembro: {e}")
            return False, f"Error: {str(e)}"
