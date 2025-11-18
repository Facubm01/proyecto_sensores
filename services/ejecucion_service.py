"""
Servicio de ejecución de procesos
Motor que ejecuta los diferentes tipos de reportes y procesos
"""

from datetime import datetime
from utils.db_manager import db_manager
from services.facturacion_service import FacturacionService
import json

class EjecucionService:
    """Servicio para ejecución de procesos y generación de reportes"""
    
    @staticmethod
    def ejecutar_proceso_pendiente():
        """
        Saca un proceso de la cola y lo ejecuta
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            # Obtener proceso de la cola de Redis
            redis_client = db_manager.conectar_redis()
            solicitud_id = redis_client.rpop("cola:procesos_pendientes")
            
            if not solicitud_id:
                return False, "No hay procesos pendientes"
            
            solicitud_id = int(solicitud_id)
            
            # Obtener datos de la solicitud
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("""
                SELECT sp.*, p.tipo, p.nombre, p.costo
                FROM solicitudes_proceso sp
                JOIN procesos p ON sp.proceso_id = p.id
                WHERE sp.id = %s
            """, (solicitud_id,))
            
            solicitud = cursor.fetchone()
            
            if not solicitud:
                cursor.close()
                return False, f"Solicitud {solicitud_id} no encontrada"
            
            # Cambiar estado a 'en_proceso'
            cursor.execute("""
                UPDATE solicitudes_proceso SET estado = 'en_proceso'
                WHERE id = %s
            """, (solicitud_id,))
            db_manager.commit_mysql()
            cursor.close()
            
            # Parsear parámetros
            parametros = json.loads(solicitud['parametros']) if solicitud['parametros'] else {}
            
            # Ejecutar según tipo de proceso
            tipo = solicitud['tipo']
            resultado = None
            
            if tipo == 'informe_max_min':
                resultado = EjecucionService._ejecutar_informe_max_min(parametros)
            elif tipo == 'informe_promedio':
                resultado = EjecucionService._ejecutar_informe_promedio(parametros)
            elif tipo == 'informe_humedad_max_min':
                resultado = EjecucionService._ejecutar_humedad_max_min(parametros)
            elif tipo == 'informe_humedad_promedio':
                resultado = EjecucionService._ejecutar_humedad_promedio(parametros)
            elif tipo == 'alertas_rango':
                resultado = EjecucionService._ejecutar_generacion_alertas(parametros)
            elif tipo == 'consulta_online':
                resultado = EjecucionService._ejecutar_consulta_online(parametros)
            elif tipo == 'proceso_periodico_mensual':
                resultado = EjecucionService._ejecutar_proceso_periodico(parametros)
            else:
                resultado = {'error': f'Tipo de proceso desconocido: {tipo}'}
            
            # Guardar resultado en MongoDB
            db = db_manager.conectar_mongodb()
            historial = {
                'solicitud_id': solicitud_id,
                'fecha_ejecucion': datetime.now(),
                'resultado': resultado,
                'estado': 'completado' if 'error' not in resultado else 'error'
            }
            db.historial_ejecucion.insert_one(historial)
            
            # Actualizar estado en MySQL
            cursor = db_manager.get_mysql_cursor()
            nuevo_estado = 'completado' if 'error' not in resultado else 'error'
            cursor.execute("""
                UPDATE solicitudes_proceso SET estado = %s
                WHERE id = %s
            """, (nuevo_estado, solicitud_id))
            
            # Si completó exitosamente, generar factura
            if nuevo_estado == 'completado':
                FacturacionService.generar_factura(
                    solicitud['usuario_id'],
                    [solicitud_id],
                    f"Factura por proceso: {solicitud['nombre']}"
                )
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, f"Proceso ejecutado: {solicitud['nombre']}"
            
        except Exception as e:
            # Revertir cambios
            try:
                cursor = db_manager.get_mysql_cursor()
                cursor.execute("""
                    UPDATE solicitudes_proceso SET estado = 'error'
                    WHERE id = %s
                """, (solicitud_id,))
                db_manager.commit_mysql()
                cursor.close()
            except:
                pass
            
            print(f"❌ Error ejecutando proceso: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def _ejecutar_informe_max_min(parametros):
        """
        Genera informe de temperaturas máximas y mínimas
        """
        try:
            db = db_manager.conectar_mongodb()
            
            # Construir filtro
            filtro = {}
            if parametros.get('ciudad'):
                filtro['ciudad'] = parametros['ciudad']
            if parametros.get('pais'):
                filtro['pais'] = parametros['pais']
            
            # Rango de fechas
            if parametros.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(parametros['fecha_inicio'], '%Y-%m-%d')
                filtro['timestamp'] = {'$gte': fecha_inicio}
            if parametros.get('fecha_fin'):
                fecha_fin = datetime.strptime(parametros['fecha_fin'], '%Y-%m-%d')
                if 'timestamp' in filtro:
                    filtro['timestamp']['$lte'] = fecha_fin
                else:
                    filtro['timestamp'] = {'$lte': fecha_fin}
            
            # Agregación
            pipeline = [
                {'$match': filtro},
                {
                    '$group': {
                        '_id': None,
                        'temperatura_maxima': {'$max': '$temperatura'},
                        'temperatura_minima': {'$min': '$temperatura'},
                        'humedad_maxima': {'$max': '$humedad'},
                        'humedad_minima': {'$min': '$humedad'},
                        'total_mediciones': {'$sum': 1}
                    }
                }
            ]
            
            resultado = list(db.mediciones.aggregate(pipeline))
            
            if resultado:
                data = resultado[0]
                return {
                    'tipo': 'informe_max_min',
                    'temperatura_maxima': round(data['temperatura_maxima'], 2),
                    'temperatura_minima': round(data['temperatura_minima'], 2),
                    'humedad_maxima': round(data['humedad_maxima'], 2),
                    'humedad_minima': round(data['humedad_minima'], 2),
                    'total_mediciones': data['total_mediciones'],
                    'parametros': parametros
                }
            else:
                return {'error': 'No se encontraron mediciones con los criterios especificados'}
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def _ejecutar_informe_promedio(parametros):
        """
        Genera informe de temperaturas promedio (mensual/anual)
        """
        try:
            db = db_manager.conectar_mongodb()
            
            # Construir filtro
            filtro = {}
            if parametros.get('ciudad'):
                filtro['ciudad'] = parametros['ciudad']
            if parametros.get('pais'):
                filtro['pais'] = parametros['pais']
            
            # Rango de fechas
            if parametros.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(parametros['fecha_inicio'], '%Y-%m-%d')
                filtro['timestamp'] = {'$gte': fecha_inicio}
            if parametros.get('fecha_fin'):
                fecha_fin = datetime.strptime(parametros['fecha_fin'], '%Y-%m-%d')
                if 'timestamp' in filtro:
                    filtro['timestamp']['$lte'] = fecha_fin
                else:
                    filtro['timestamp'] = {'$lte': fecha_fin}
            
            # Agregación mensual
            pipeline = [
                {'$match': filtro},
                {
                    '$group': {
                        '_id': {
                            'año': {'$year': '$timestamp'},
                            'mes': {'$month': '$timestamp'}
                        },
                        'temperatura_promedio': {'$avg': '$temperatura'},
                        'humedad_promedio': {'$avg': '$humedad'},
                        'total_mediciones': {'$sum': 1}
                    }
                },
                {'$sort': {'_id.año': 1, '_id.mes': 1}}
            ]
            
            resultado = list(db.mediciones.aggregate(pipeline))
            
            if resultado:
                datos_mensuales = []
                for item in resultado:
                    datos_mensuales.append({
                        'periodo': f"{item['_id']['año']}-{item['_id']['mes']:02d}",
                        'temperatura_promedio': round(item['temperatura_promedio'], 2),
                        'humedad_promedio': round(item['humedad_promedio'], 2),
                        'total_mediciones': item['total_mediciones']
                    })
                
                return {
                    'tipo': 'informe_promedio',
                    'datos_mensuales': datos_mensuales,
                    'parametros': parametros
                }
            else:
                return {'error': 'No se encontraron mediciones'}
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def _ejecutar_humedad_max_min(parametros):
        """
        Genera informe de humedad máxima y mínima
        """
        try:
            db = db_manager.conectar_mongodb()
            
            filtro = {}
            if parametros.get('ciudad'):
                filtro['ciudad'] = parametros['ciudad']
            if parametros.get('pais'):
                filtro['pais'] = parametros['pais']
            
            if parametros.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(parametros['fecha_inicio'], '%Y-%m-%d')
                filtro['timestamp'] = {'$gte': fecha_inicio}
            if parametros.get('fecha_fin'):
                fecha_fin = datetime.strptime(parametros['fecha_fin'], '%Y-%m-%d')
                if 'timestamp' in filtro:
                    filtro['timestamp']['$lte'] = fecha_fin
                else:
                    filtro['timestamp'] = {'$lte': fecha_fin}
            
            pipeline = [
                {'$match': filtro},
                {
                    '$group': {
                        '_id': None,
                        'humedad_maxima': {'$max': '$humedad'},
                        'humedad_minima': {'$min': '$humedad'},
                        'total_mediciones': {'$sum': 1}
                    }
                }
            ]
            
            resultado = list(db.mediciones.aggregate(pipeline))
            
            if resultado:
                data = resultado[0]
                return {
                    'tipo': 'informe_humedad_max_min',
                    'humedad_maxima': round(data['humedad_maxima'], 2),
                    'humedad_minima': round(data['humedad_minima'], 2),
                    'total_mediciones': data['total_mediciones'],
                    'parametros': parametros
                }
            else:
                return {'error': 'No se encontraron mediciones'}
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def _ejecutar_humedad_promedio(parametros):
        """
        Genera informe de humedad promedio
        """
        try:
            db = db_manager.conectar_mongodb()
            
            filtro = {}
            if parametros.get('ciudad'):
                filtro['ciudad'] = parametros['ciudad']
            if parametros.get('pais'):
                filtro['pais'] = parametros['pais']
            
            if parametros.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(parametros['fecha_inicio'], '%Y-%m-%d')
                filtro['timestamp'] = {'$gte': fecha_inicio}
            if parametros.get('fecha_fin'):
                fecha_fin = datetime.strptime(parametros['fecha_fin'], '%Y-%m-%d')
                if 'timestamp' in filtro:
                    filtro['timestamp']['$lte'] = fecha_fin
                else:
                    filtro['timestamp'] = {'$lte': fecha_fin}
            
            pipeline = [
                {'$match': filtro},
                {
                    '$group': {
                        '_id': {
                            'año': {'$year': '$timestamp'},
                            'mes': {'$month': '$timestamp'}
                        },
                        'humedad_promedio': {'$avg': '$humedad'},
                        'total_mediciones': {'$sum': 1}
                    }
                },
                {'$sort': {'_id.año': 1, '_id.mes': 1}}
            ]
            
            resultado = list(db.mediciones.aggregate(pipeline))
            
            if resultado:
                datos_mensuales = []
                for item in resultado:
                    datos_mensuales.append({
                        'periodo': f"{item['_id']['año']}-{item['_id']['mes']:02d}",
                        'humedad_promedio': round(item['humedad_promedio'], 2),
                        'total_mediciones': item['total_mediciones']
                    })
                
                return {
                    'tipo': 'informe_humedad_promedio',
                    'datos_mensuales': datos_mensuales,
                    'parametros': parametros
                }
            else:
                return {'error': 'No se encontraron mediciones'}
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def _ejecutar_generacion_alertas(parametros):
        """
        Genera alertas para mediciones fuera de rango
        """
        try:
            db = db_manager.conectar_mongodb()
            
            filtro = {}
            if parametros.get('ciudad'):
                filtro['ciudad'] = parametros['ciudad']
            
            if parametros.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(parametros['fecha_inicio'], '%Y-%m-%d')
                filtro['timestamp'] = {'$gte': fecha_inicio}
            if parametros.get('fecha_fin'):
                fecha_fin = datetime.strptime(parametros['fecha_fin'], '%Y-%m-%d')
                if 'timestamp' in filtro:
                    filtro['timestamp']['$lte'] = fecha_fin
                else:
                    filtro['timestamp'] = {'$lte': fecha_fin}
            
            # Buscar mediciones fuera de rango
            temp_min = parametros.get('temp_min', -999)
            temp_max = parametros.get('temp_max', 999)
            
            filtro['$or'] = [
                {'temperatura': {'$lt': temp_min}},
                {'temperatura': {'$gt': temp_max}}
            ]
            
            mediciones_fuera_rango = list(db.mediciones.find(filtro).limit(100))
            
            # Crear alertas
            alertas_generadas = 0
            for medicion in mediciones_fuera_rango:
                alerta = {
                    'tipo': 'climatica',
                    'sensor_id': medicion['sensor_id'],
                    'timestamp': datetime.now(),
                    'descripcion': f"Temperatura fuera de rango ({medicion['temperatura']}°C) en {medicion.get('ciudad', 'N/A')}",
                    'estado': 'activa'
                }
                db.alertas.insert_one(alerta)
                alertas_generadas += 1
            
            return {
                'tipo': 'generacion_alertas',
                'alertas_generadas': alertas_generadas,
                'mediciones_analizadas': len(mediciones_fuera_rango),
                'parametros': parametros
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def _ejecutar_consulta_online(parametros):
        """
        Consulta en tiempo real de sensores
        """
        try:
            db = db_manager.conectar_mongodb()
            cursor = db_manager.get_mysql_cursor()
            
            zona = parametros.get('zona', '')
            
            # Buscar sensores en la zona
            cursor.execute("""
                SELECT id, nombre, ciudad, pais, estado
                FROM sensores
                WHERE ciudad LIKE %s OR pais LIKE %s
            """, (f'%{zona}%', f'%{zona}%'))
            
            sensores = cursor.fetchall()
            cursor.close()
            
            if not sensores:
                return {'error': f'No se encontraron sensores en la zona: {zona}'}
            
            # Obtener última medición de cada sensor
            datos_sensores = []
            for sensor in sensores:
                ultima_medicion = db.mediciones.find_one(
                    {'sensor_id': sensor['id']},
                    sort=[('timestamp', -1)]
                )
                
                if ultima_medicion:
                    datos_sensores.append({
                        'sensor_id': sensor['id'],
                        'sensor_nombre': sensor['nombre'],
                        'ciudad': sensor['ciudad'],
                        'pais': sensor['pais'],
                        'estado': sensor['estado'],
                        'temperatura': round(ultima_medicion['temperatura'], 2),
                        'humedad': round(ultima_medicion['humedad'], 2),
                        'ultima_actualizacion': str(ultima_medicion['timestamp'])
                    })
            
            return {
                'tipo': 'consulta_online',
                'zona': zona,
                'total_sensores': len(datos_sensores),
                'sensores': datos_sensores,
                'parametros': parametros
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def _ejecutar_proceso_periodico(parametros):
        """
        Proceso periódico mensual
        """
        # Similar a informe_promedio pero con más detalles
        return EjecucionService._ejecutar_informe_promedio(parametros)
