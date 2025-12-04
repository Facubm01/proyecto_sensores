"""
Servicio de notificaciones usando Redis pub/sub
"""

import json
import threading
from datetime import datetime
from utils.db_manager import db_manager
from utils.logger import logger


class NotificacionService:
    """Servicio para manejar notificaciones en tiempo real"""
    
    @staticmethod
    def enviar_notificacion(usuario_id: int, tipo: str, mensaje: str, datos: dict = None):
        """
        Envía una notificación a un usuario
        
        Args:
            usuario_id: ID del usuario destinatario
            tipo: Tipo de notificación (proceso_completado, alerta, etc.)
            mensaje: Mensaje de la notificación
            datos: Datos adicionales
        """
        try:
            redis_client = db_manager.get_redis_client()
            
            notificacion = {
                'usuario_id': usuario_id,
                'tipo': tipo,
                'mensaje': mensaje,
                'fecha': datetime.now().isoformat(),
                'datos': datos or {}
            }
            
            # Guardar en lista de notificaciones del usuario
            clave = f"notificaciones:{usuario_id}"
            redis_client.lpush(clave, json.dumps(notificacion))
            redis_client.ltrim(clave, 0, 99)  # Mantener solo las últimas 100
            redis_client.expire(clave, 86400 * 7)  # Expirar en 7 días
            
            # Publicar en canal (para notificaciones en tiempo real)
            canal = f"usuario:{usuario_id}"
            redis_client.publish(canal, json.dumps(notificacion))
            
            logger.info(f"Notificación enviada a usuario {usuario_id}: {tipo}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
    
    @staticmethod
    def obtener_notificaciones(usuario_id: int, cantidad: int = 10) -> list:
        """
        Obtiene las notificaciones de un usuario
        
        Args:
            usuario_id: ID del usuario
            cantidad: Cantidad de notificaciones a obtener
        
        Returns:
            Lista de notificaciones
        """
        try:
            redis_client = db_manager.get_redis_client()
            clave = f"notificaciones:{usuario_id}"
            
            notificaciones_raw = redis_client.lrange(clave, 0, cantidad - 1)
            notificaciones = []
            
            for notif_raw in notificaciones_raw:
                try:
                    notif = json.loads(notif_raw)
                    notificaciones.append(notif)
                except:
                    continue
            
            return notificaciones
        
        except Exception as e:
            logger.error(f"Error obteniendo notificaciones: {e}")
            return []
    
    @staticmethod
    def marcar_leida(usuario_id: int, notificacion_id: str):
        """
        Marca una notificación como leída
        
        Args:
            usuario_id: ID del usuario
            notificacion_id: ID de la notificación (fecha en ISO)
        """
        try:
            redis_client = db_manager.get_redis_client()
            clave = f"notificaciones_leidas:{usuario_id}"
            redis_client.sadd(clave, notificacion_id)
            redis_client.expire(clave, 86400 * 7)
        except Exception as e:
            logger.error(f"Error marcando notificación como leída: {e}")
    
    @staticmethod
    def contar_no_leidas(usuario_id: int) -> int:
        """
        Cuenta las notificaciones no leídas
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            Cantidad de notificaciones no leídas
        """
        try:
            notificaciones = NotificacionService.obtener_notificaciones(usuario_id, 100)
            redis_client = db_manager.get_redis_client()
            clave_leidas = f"notificaciones_leidas:{usuario_id}"
            leidas = redis_client.smembers(clave_leidas)
            
            no_leidas = 0
            for notif in notificaciones:
                if notif.get('fecha') not in leidas:
                    no_leidas += 1
            
            return no_leidas
        
        except Exception as e:
            logger.error(f"Error contando notificaciones: {e}")
            return 0
    
    @staticmethod
    def suscribir_notificaciones(usuario_id: int, callback):
        """
        Suscribe a notificaciones en tiempo real (para uso en threads)
        
        Args:
            usuario_id: ID del usuario
            callback: Función a llamar cuando llegue una notificación
        """
        def escuchar():
            try:
                redis_client = db_manager.get_redis_client()
                pubsub = redis_client.pubsub()
                canal = f"usuario:{usuario_id}"
                pubsub.subscribe(canal)
                
                for mensaje in pubsub.listen():
                    if mensaje['type'] == 'message':
                        try:
                            notif = json.loads(mensaje['data'])
                            callback(notif)
                        except:
                            continue
            except Exception as e:
                logger.error(f"Error en suscripción de notificaciones: {e}")
        
        thread = threading.Thread(target=escuchar, daemon=True)
        thread.start()
        return thread


