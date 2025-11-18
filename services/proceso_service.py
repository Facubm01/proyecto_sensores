"""
Servicio de gestión de procesos y solicitudes
"""

import json
from datetime import datetime
from utils.db_manager import db_manager

class ProcesoService:
    """Servicio para gestión de procesos"""
    
    @staticmethod
    def listar_procesos_disponibles():
        """
        Lista todos los procesos disponibles
        
        Returns:
            Lista de procesos
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("""
                SELECT * FROM procesos
                WHERE activo = TRUE
                ORDER BY nombre
            """)
            procesos = cursor.fetchall()
            cursor.close()
            return procesos
            
        except Exception as e:
            print(f"❌ Error listando procesos: {e}")
            return []
    
    @staticmethod
    def obtener_proceso(proceso_id):
        """
        Obtiene información de un proceso específico
        
        Returns:
            Diccionario con datos del proceso o None
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("SELECT * FROM procesos WHERE id = %s", (proceso_id,))
            proceso = cursor.fetchone()
            cursor.close()
            return proceso
            
        except Exception as e:
            print(f"❌ Error obteniendo proceso: {e}")
            return None
    
    @staticmethod
    def solicitar_proceso(usuario_id, proceso_id, parametros):
        """
        Crea una solicitud de proceso
        
        Args:
            usuario_id: ID del usuario solicitante
            proceso_id: ID del proceso a ejecutar
            parametros: Diccionario con parámetros del proceso
        
        Returns:
            (success: bool, mensaje: str, solicitud_id: int)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Verificar que el proceso exista
            cursor.execute("SELECT costo FROM procesos WHERE id = %s AND activo = TRUE", (proceso_id,))
            proceso = cursor.fetchone()
            
            if not proceso:
                cursor.close()
                return False, "Proceso no encontrado", None
            
            # Insertar solicitud
            query = """
                INSERT INTO solicitudes_proceso (usuario_id, proceso_id, parametros, estado)
                VALUES (%s, %s, %s, 'pendiente')
            """
            cursor.execute(query, (usuario_id, proceso_id, json.dumps(parametros)))
            solicitud_id = cursor.lastrowid
            
            # Agregar a la cola de Redis
            redis_client = db_manager.conectar_redis()
            redis_client.lpush("cola:procesos_pendientes", solicitud_id)
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, f"Proceso solicitado. Costo: ${proceso['costo']}", solicitud_id
            
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error solicitando proceso: {e}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def listar_solicitudes_usuario(usuario_id, filtro_estado=None, limite=50):
        """
        Lista solicitudes de un usuario
        
        Args:
            usuario_id: ID del usuario
            filtro_estado: 'pendiente', 'en_proceso', 'completado', 'error' o None
            limite: Número máximo de solicitudes
        
        Returns:
            Lista de solicitudes
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Construir query
            query = """
                SELECT s.*, p.nombre as proceso_nombre, p.descripcion as proceso_descripcion,
                       p.tipo as proceso_tipo, p.costo
                FROM solicitudes_proceso s
                JOIN procesos p ON s.proceso_id = p.id
                WHERE s.usuario_id = %s
            """
            params = [usuario_id]
            
            if filtro_estado:
                query += " AND s.estado = %s"
                params.append(filtro_estado)
            
            query += " ORDER BY s.fecha_solicitud DESC LIMIT %s"
            params.append(limite)
            
            cursor.execute(query, tuple(params))
            solicitudes = cursor.fetchall()
            
            # Enriquecer con resultado de MongoDB si está completado
            db = db_manager.conectar_mongodb()
            
            for solicitud in solicitudes:
                if solicitud['estado'] == 'completado':
                    historial = db.historial_ejecucion.find_one({'solicitud_id': solicitud['id']})
                    if historial:
                        solicitud['resultado'] = historial.get('resultado')
                        solicitud['fecha_ejecucion'] = historial.get('fecha_ejecucion')
            
            cursor.close()
            return solicitudes
            
        except Exception as e:
            print(f"❌ Error listando solicitudes: {e}")
            return []
    
    @staticmethod
    def contar_solicitudes_por_estado(usuario_id):
        """
        Cuenta solicitudes de un usuario agrupadas por estado
        
        Returns:
            Diccionario con conteos
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("""
                SELECT estado, COUNT(*) as total
                FROM solicitudes_proceso
                WHERE usuario_id = %s
                GROUP BY estado
            """, (usuario_id,))
            
            resultado = cursor.fetchall()
            cursor.close()
            
            conteos = {'pendiente': 0, 'en_proceso': 0, 'completado': 0, 'error': 0}
            for row in resultado:
                conteos[row['estado']] = row['total']
            
            return conteos
            
        except Exception as e:
            print(f"❌ Error contando solicitudes: {e}")
            return {'pendiente': 0, 'en_proceso': 0, 'completado': 0, 'error': 0}
    
    @staticmethod
    def obtener_procesos_pendientes(limite=10):
        """
        Obtiene procesos pendientes de la cola (para ejecutar)
        
        Returns:
            Lista de IDs de solicitudes pendientes
        """
        try:
            redis_client = db_manager.conectar_redis()
            
            # Obtener hasta 'limite' elementos de la cola sin eliminarlos
            solicitudes_ids = redis_client.lrange("cola:procesos_pendientes", 0, limite - 1)
            
            return [int(sid) for sid in solicitudes_ids]
            
        except Exception as e:
            print(f"❌ Error obteniendo procesos pendientes: {e}")
            return []
    
    @staticmethod
    def cancelar_solicitud(solicitud_id, usuario_id):
        """
        Cancela una solicitud pendiente
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Verificar que la solicitud sea del usuario y esté pendiente
            cursor.execute("""
                SELECT estado FROM solicitudes_proceso
                WHERE id = %s AND usuario_id = %s
            """, (solicitud_id, usuario_id))
            
            solicitud = cursor.fetchone()
            
            if not solicitud:
                cursor.close()
                return False, "Solicitud no encontrada"
            
            if solicitud['estado'] != 'pendiente':
                cursor.close()
                return False, "Solo se pueden cancelar solicitudes pendientes"
            
            # Eliminar de MySQL
            cursor.execute("DELETE FROM solicitudes_proceso WHERE id = %s", (solicitud_id,))
            
            # Eliminar de la cola de Redis
            redis_client = db_manager.conectar_redis()
            redis_client.lrem("cola:procesos_pendientes", 0, str(solicitud_id))
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, "Solicitud cancelada"
            
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error cancelando solicitud: {e}")
            return False, f"Error: {str(e)}"
