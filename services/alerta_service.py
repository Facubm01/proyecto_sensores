"""
Servicio de gestión de alertas
"""

from datetime import datetime
from utils.db_manager import db_manager

class AlertaService:
    """Servicio para gestión de alertas"""
    
    @staticmethod
    def listar_alertas(filtro_estado=None, limite=50):
        """
        Lista alertas del sistema
        
        Args:
            filtro_estado: 'activa', 'resuelta' o None para todas
            limite: Número máximo de alertas a retornar
        
        Returns:
            Lista de alertas
        """
        try:
            db = db_manager.conectar_mongodb()
            
            # Construir query
            query = {}
            if filtro_estado:
                query['estado'] = filtro_estado
            
            # Buscar alertas ordenadas por fecha (más recientes primero)
            alertas = list(db.alertas.find(query).sort('timestamp', -1).limit(limite))
            
            # Enriquecer con datos del sensor (de MySQL)
            cursor = db_manager.get_mysql_cursor()
            
            for alerta in alertas:
                if alerta.get('sensor_id'):
                    cursor.execute(
                        "SELECT nombre, codigo, ciudad, pais FROM sensores WHERE id = %s",
                        (alerta['sensor_id'],)
                    )
                    sensor = cursor.fetchone()
                    if sensor:
                        alerta['sensor_nombre'] = sensor['nombre']
                        alerta['sensor_codigo'] = sensor['codigo']
                        alerta['sensor_ciudad'] = sensor['ciudad']
                        alerta['sensor_pais'] = sensor['pais']
            
            cursor.close()
            return alertas
            
        except Exception as e:
            print(f"❌ Error listando alertas: {e}")
            return []
    
    @staticmethod
    def crear_alerta(tipo, sensor_id, descripcion):
        """
        Crea una nueva alerta
        
        Args:
            tipo: 'sensor' o 'climatica'
            sensor_id: ID del sensor relacionado
            descripcion: Descripción de la alerta
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            db = db_manager.conectar_mongodb()
            
            # Obtener datos del sensor de MySQL
            cursor = db_manager.get_mysql_cursor()
            cursor.execute(
                "SELECT ciudad, pais FROM sensores WHERE id = %s",
                (sensor_id,)
            )
            sensor = cursor.fetchone()
            cursor.close()
            
            if not sensor:
                return False, "Sensor no encontrado"
            
            alerta = {
                'tipo': tipo,
                'sensor_id': sensor_id,
                'timestamp': datetime.now(),
                'descripcion': descripcion,
                'estado': 'activa'
            }
            
            resultado = db.alertas.insert_one(alerta)
            
            if resultado.inserted_id:
                return True, "Alerta creada exitosamente"
            else:
                return False, "Error al crear alerta"
            
        except Exception as e:
            print(f"❌ Error creando alerta: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def resolver_alerta(alerta_id):
        """
        Marca una alerta como resuelta
        
        Args:
            alerta_id: ID de la alerta (string de ObjectId)
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            from bson.objectid import ObjectId
            db = db_manager.conectar_mongodb()
            
            resultado = db.alertas.update_one(
                {'_id': ObjectId(alerta_id)},
                {'$set': {'estado': 'resuelta'}}
            )
            
            if resultado.modified_count > 0:
                return True, "Alerta resuelta"
            else:
                return False, "Alerta no encontrada"
            
        except Exception as e:
            print(f"❌ Error resolviendo alerta: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def contar_alertas_por_estado():
        """
        Cuenta alertas agrupadas por estado
        
        Returns:
            Diccionario con conteos
        """
        try:
            db = db_manager.conectar_mongodb()
            
            pipeline = [
                {
                    '$group': {
                        '_id': '$estado',
                        'total': {'$sum': 1}
                    }
                }
            ]
            
            resultado = list(db.alertas.aggregate(pipeline))
            
            conteos = {'activa': 0, 'resuelta': 0}
            for item in resultado:
                conteos[item['_id']] = item['total']
            
            return conteos
            
        except Exception as e:
            print(f"❌ Error contando alertas: {e}")
            return {'activa': 0, 'resuelta': 0}
