"""
Servicio de control de funcionamiento de sensores
"""

from datetime import datetime, timedelta
from utils.db_manager import db_manager

class ControlService:
    """Servicio para control de funcionamiento de sensores"""
    
    @staticmethod
    def registrar_control(sensor_id, estado, observaciones):
        """
        Registra un control de funcionamiento de un sensor
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            # Verificar que el sensor existe
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("SELECT id FROM sensores WHERE id = %s", (sensor_id,))
            if not cursor.fetchone():
                cursor.close()
                return False, "Sensor no encontrado"
            cursor.close()
            
            # Registrar control en MongoDB
            db = db_manager.conectar_mongodb()
            
            control = {
                'sensor_id': sensor_id,
                'fecha_revision': datetime.now(),
                'estado': estado,
                'observaciones': observaciones
            }
            
            resultado = db.control_funcionamiento.insert_one(control)
            
            if resultado.inserted_id:
                return True, "Control registrado exitosamente"
            else:
                return False, "Error al registrar control"
            
        except Exception as e:
            print(f"❌ Error registrando control: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def listar_controles_sensor(sensor_id, limite=20):
        """
        Lista controles de un sensor específico
        
        Returns:
            Lista de controles
        """
        try:
            db = db_manager.conectar_mongodb()
            
            controles = list(db.control_funcionamiento.find(
                {'sensor_id': sensor_id}
            ).sort('fecha_revision', -1).limit(limite))
            
            return controles
            
        except Exception as e:
            print(f"❌ Error listando controles: {e}")
            return []
    
    @staticmethod
    def listar_todos_controles(limite=50):
        """
        Lista todos los controles registrados
        
        Returns:
            Lista de controles con información del sensor
        """
        try:
            db = db_manager.conectar_mongodb()
            
            controles = list(db.control_funcionamiento.find().sort('fecha_revision', -1).limit(limite))
            
            # Enriquecer con datos del sensor
            cursor = db_manager.get_mysql_cursor()
            
            for control in controles:
                cursor.execute("""
                    SELECT nombre, codigo, ciudad, pais, estado
                    FROM sensores
                    WHERE id = %s
                """, (control['sensor_id'],))
                
                sensor = cursor.fetchone()
                if sensor:
                    control['sensor_nombre'] = sensor['nombre']
                    control['sensor_codigo'] = sensor['codigo']
                    control['sensor_ciudad'] = sensor['ciudad']
                    control['sensor_pais'] = sensor['pais']
                    control['sensor_estado_actual'] = sensor['estado']
            
            cursor.close()
            return controles
            
        except Exception as e:
            print(f"❌ Error listando controles: {e}")
            return []
    
    @staticmethod
    def obtener_estadisticas_controles():
        """
        Obtiene estadísticas de controles de funcionamiento
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            db = db_manager.conectar_mongodb()
            
            # Total de controles
            total = db.control_funcionamiento.count_documents({})
            
            # Controles por estado
            pipeline = [
                {
                    '$group': {
                        '_id': '$estado',
                        'total': {'$sum': 1}
                    }
                }
            ]
            
            resultado = list(db.control_funcionamiento.aggregate(pipeline))
            
            por_estado = {}
            for item in resultado:
                por_estado[item['_id']] = item['total']
            
            # Controles recientes (últimos 7 días)
            fecha_limite = datetime.now() - timedelta(days=7)
            recientes = db.control_funcionamiento.count_documents({
                'fecha_revision': {'$gte': fecha_limite}
            })
            
            return {
                'total': total,
                'por_estado': por_estado,
                'ultimos_7_dias': recientes
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {
                'total': 0,
                'por_estado': {},
                'ultimos_7_dias': 0
            }
