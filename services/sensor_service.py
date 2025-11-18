"""
Servicio de gestión de sensores
"""

from datetime import datetime, timedelta
from utils.db_manager import db_manager

class SensorService:
    """Servicio para gestión de sensores"""
    
    @staticmethod
    def listar_sensores(filtro_estado=None, filtro_pais=None):
        """
        Lista sensores del sistema
        
        Args:
            filtro_estado: 'activo', 'inactivo', 'falla' o None
            filtro_pais: Nombre del país o None
        
        Returns:
            Lista de sensores
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Construir query
            query = "SELECT * FROM sensores WHERE 1=1"
            params = []
            
            if filtro_estado:
                query += " AND estado = %s"
                params.append(filtro_estado)
            
            if filtro_pais:
                query += " AND pais = %s"
                params.append(filtro_pais)
            
            query += " ORDER BY pais, ciudad, nombre"
            
            cursor.execute(query, tuple(params))
            sensores = cursor.fetchall()
            cursor.close()
            
            return sensores
            
        except Exception as e:
            print(f"❌ Error listando sensores: {e}")
            return []
    
    @staticmethod
    def obtener_sensor(sensor_id):
        """
        Obtiene información detallada de un sensor
        
        Args:
            sensor_id: ID del sensor
        
        Returns:
            Diccionario con datos del sensor o None
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("SELECT * FROM sensores WHERE id = %s", (sensor_id,))
            sensor = cursor.fetchone()
            cursor.close()
            
            return sensor
            
        except Exception as e:
            print(f"❌ Error obteniendo sensor: {e}")
            return None
    
    @staticmethod
    def registrar_sensor(nombre, codigo, tipo, latitud, longitud, ciudad, pais):
        """
        Registra un nuevo sensor
        
        Returns:
            (success: bool, mensaje: str, sensor_id: int)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Verificar que el código no exista
            cursor.execute("SELECT id FROM sensores WHERE codigo = %s", (codigo,))
            if cursor.fetchone():
                cursor.close()
                return False, "El código de sensor ya existe", None
            
            # Insertar sensor
            query = """
                INSERT INTO sensores (nombre, codigo, tipo, latitud, longitud, ciudad, pais, estado, fecha_inicio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'activo', NOW())
            """
            cursor.execute(query, (nombre, codigo, tipo, latitud, longitud, ciudad, pais))
            sensor_id = cursor.lastrowid
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, "Sensor registrado exitosamente", sensor_id
            
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error registrando sensor: {e}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def cambiar_estado_sensor(sensor_id, nuevo_estado):
        """
        Cambia el estado de un sensor
        
        Args:
            sensor_id: ID del sensor
            nuevo_estado: 'activo', 'inactivo' o 'falla'
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            cursor.execute(
                "UPDATE sensores SET estado = %s WHERE id = %s",
                (nuevo_estado, sensor_id)
            )
            
            if cursor.rowcount > 0:
                db_manager.commit_mysql()
                cursor.close()
                return True, f"Estado cambiado a '{nuevo_estado}'"
            else:
                cursor.close()
                return False, "Sensor no encontrado"
            
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error cambiando estado: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_ultima_medicion(sensor_id):
        """
        Obtiene la última medición de un sensor desde MongoDB
        
        Returns:
            Diccionario con la última medición o None
        """
        try:
            db = db_manager.conectar_mongodb()
            
            medicion = db.mediciones.find_one(
                {'sensor_id': sensor_id},
                sort=[('timestamp', -1)]
            )
            
            return medicion
            
        except Exception as e:
            print(f"❌ Error obteniendo última medición: {e}")
            return None
    
    @staticmethod
    def obtener_estadisticas_sensor(sensor_id, dias=7):
        """
        Obtiene estadísticas de un sensor en los últimos X días
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            db = db_manager.conectar_mongodb()
            
            fecha_inicio = datetime.now() - timedelta(days=dias)
            
            pipeline = [
                {
                    '$match': {
                        'sensor_id': sensor_id,
                        'timestamp': {'$gte': fecha_inicio}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'temp_promedio': {'$avg': '$temperatura'},
                        'temp_max': {'$max': '$temperatura'},
                        'temp_min': {'$min': '$temperatura'},
                        'hum_promedio': {'$avg': '$humedad'},
                        'hum_max': {'$max': '$humedad'},
                        'hum_min': {'$min': '$humedad'},
                        'total_mediciones': {'$sum': 1}
                    }
                }
            ]
            
            resultado = list(db.mediciones.aggregate(pipeline))
            
            if resultado:
                stats = resultado[0]
                # Redondear valores
                for key in stats:
                    if key != '_id' and key != 'total_mediciones' and stats[key]:
                        stats[key] = round(stats[key], 2)
                return stats
            else:
                return None
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return None
    
    @staticmethod
    def listar_paises():
        """
        Lista todos los países únicos de los sensores
        
        Returns:
            Lista de países
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("SELECT DISTINCT pais FROM sensores ORDER BY pais")
            paises = [row['pais'] for row in cursor.fetchall()]
            cursor.close()
            return paises
            
        except Exception as e:
            print(f"❌ Error listando países: {e}")
            return []
    
    @staticmethod
    def contar_sensores_por_estado():
        """
        Cuenta sensores agrupados por estado
        
        Returns:
            Diccionario con conteos
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("""
                SELECT estado, COUNT(*) as total
                FROM sensores
                GROUP BY estado
            """)
            
            resultado = cursor.fetchall()
            cursor.close()
            
            conteos = {'activo': 0, 'inactivo': 0, 'falla': 0}
            for row in resultado:
                conteos[row['estado']] = row['total']
            
            return conteos
            
        except Exception as e:
            print(f"❌ Error contando sensores: {e}")
            return {'activo': 0, 'inactivo': 0, 'falla': 0}
