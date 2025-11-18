#!/usr/bin/env python3
"""
Script de inicialización de MongoDB
Crea colecciones, índices y datos de ejemplo
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timedelta
import random

# Configuración de conexión
MONGO_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'username': 'admin',
    'password': 'admin123',
    'database': 'sensores_db'
}

def conectar_mongodb():
    """Conecta a MongoDB"""
    try:
        client = MongoClient(
            f"mongodb://{MONGO_CONFIG['username']}:{MONGO_CONFIG['password']}@{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}/"
        )
        db = client[MONGO_CONFIG['database']]
        print(f"✅ Conectado a MongoDB - Base de datos: {MONGO_CONFIG['database']}")
        return db
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return None

def crear_colecciones(db):
    """Crea las colecciones necesarias"""
    colecciones = [
        'mediciones',
        'alertas',
        'mensajes',
        'historial_ejecucion',
        'control_funcionamiento'
    ]
    
    print("\n📦 Creando colecciones...")
    for coleccion in colecciones:
        if coleccion not in db.list_collection_names():
            db.create_collection(coleccion)
            print(f"  ✓ Colección '{coleccion}' creada")
        else:
            print(f"  ℹ️  Colección '{coleccion}' ya existe")

def crear_indices(db):
    """Crea índices para optimizar queries"""
    print("\n🔍 Creando índices...")
    
    # Índices para MEDICIONES
    # Índice compuesto para queries por sensor y fecha (más común)
    db.mediciones.create_index([
        ('sensor_id', ASCENDING),
        ('timestamp', DESCENDING)
    ], name='idx_sensor_timestamp')
    print("  ✓ Índice mediciones: sensor_id + timestamp")
    
    # Índice para queries por ciudad y fecha
    db.mediciones.create_index([
        ('ciudad', ASCENDING),
        ('timestamp', DESCENDING)
    ], name='idx_ciudad_timestamp')
    print("  ✓ Índice mediciones: ciudad + timestamp")
    
    # Índice para queries por país y fecha
    db.mediciones.create_index([
        ('pais', ASCENDING),
        ('timestamp', DESCENDING)
    ], name='idx_pais_timestamp')
    print("  ✓ Índice mediciones: pais + timestamp")
    
    # Índices para ALERTAS
    db.alertas.create_index([
        ('estado', ASCENDING),
        ('timestamp', DESCENDING)
    ], name='idx_estado_timestamp')
    print("  ✓ Índice alertas: estado + timestamp")
    
    db.alertas.create_index([
        ('sensor_id', ASCENDING),
        ('timestamp', DESCENDING)
    ], name='idx_sensor_alerta')
    print("  ✓ Índice alertas: sensor_id + timestamp")
    
    # Índices para MENSAJES
    db.mensajes.create_index([
        ('destinatario_id', ASCENDING),
        ('timestamp', DESCENDING)
    ], name='idx_destinatario_timestamp')
    print("  ✓ Índice mensajes: destinatario_id + timestamp")
    
    db.mensajes.create_index([
        ('remitente_id', ASCENDING),
        ('timestamp', DESCENDING)
    ], name='idx_remitente_timestamp')
    print("  ✓ Índice mensajes: remitente_id + timestamp")
    
    db.mensajes.create_index([
        ('grupo_id', ASCENDING)
    ], name='idx_grupo')
    print("  ✓ Índice mensajes: grupo_id")
    
    # Índices para HISTORIAL_EJECUCION
    db.historial_ejecucion.create_index([
        ('solicitud_id', ASCENDING)
    ], name='idx_solicitud', unique=True)
    print("  ✓ Índice historial: solicitud_id (único)")
    
    db.historial_ejecucion.create_index([
        ('fecha_ejecucion', DESCENDING)
    ], name='idx_fecha_ejecucion')
    print("  ✓ Índice historial: fecha_ejecucion")
    
    # Índices para CONTROL_FUNCIONAMIENTO
    db.control_funcionamiento.create_index([
        ('sensor_id', ASCENDING),
        ('fecha_revision', DESCENDING)
    ], name='idx_sensor_revision')
    print("  ✓ Índice control: sensor_id + fecha_revision")

def cargar_mediciones_ejemplo(db):
    """Carga mediciones de ejemplo para los últimos 30 días"""
    print("\n📊 Cargando mediciones de ejemplo...")
    
    # IDs de sensores (del init_mysql.sql)
    sensores = [
        {'id': 1, 'ciudad': 'Buenos Aires', 'pais': 'Argentina'},
        {'id': 2, 'ciudad': 'Buenos Aires', 'pais': 'Argentina'},
        {'id': 3, 'ciudad': 'Buenos Aires', 'pais': 'Argentina'},
        {'id': 4, 'ciudad': 'Córdoba', 'pais': 'Argentina'},
        {'id': 5, 'ciudad': 'Rosario', 'pais': 'Argentina'},
        {'id': 6, 'ciudad': 'Mendoza', 'pais': 'Argentina'},
        {'id': 7, 'ciudad': 'Santiago', 'pais': 'Chile'},
        {'id': 8, 'ciudad': 'São Paulo', 'pais': 'Brasil'},
        {'id': 9, 'ciudad': 'Montevideo', 'pais': 'Uruguay'},
        {'id': 10, 'ciudad': 'Lima', 'pais': 'Perú'}
    ]
    
    mediciones = []
    fecha_inicio = datetime.now() - timedelta(days=30)
    
    # Generar mediciones cada 1 hora para cada sensor
    for dias in range(30):
        for hora in range(0, 24, 1):  # Cada 1 hora
            timestamp = fecha_inicio + timedelta(days=dias, hours=hora)
            
            for sensor in sensores:
                # Temperatura base según ciudad (simulación realista)
                temp_base = {
                    'Buenos Aires': 22, 'Córdoba': 24, 'Rosario': 23,
                    'Mendoza': 20, 'Santiago': 18, 'São Paulo': 25,
                    'Montevideo': 21, 'Lima': 23
                }
                
                # Variación por hora del día
                variacion_hora = random.uniform(-3, 5) if 6 <= hora <= 18 else random.uniform(-5, 2)
                
                temperatura = temp_base.get(sensor['ciudad'], 20) + variacion_hora + random.uniform(-2, 2)
                humedad = random.uniform(40, 85)
                
                medicion = {
                    'sensor_id': sensor['id'],
                    'ciudad': sensor['ciudad'],
                    'pais': sensor['pais'],
                    'timestamp': timestamp,
                    'temperatura': round(temperatura, 2),
                    'humedad': round(humedad, 2)
                }
                mediciones.append(medicion)
    
    # Insertar en lotes (más eficiente)
    if mediciones:
        db.mediciones.insert_many(mediciones)
        print(f"  ✓ {len(mediciones)} mediciones insertadas")
        print(f"  ℹ️  Periodo: últimos 30 días")
        print(f"  ℹ️  Frecuencia: 1 medición por hora por sensor")

def cargar_alertas_ejemplo(db):
    """Carga alertas de ejemplo"""
    print("\n⚠️  Cargando alertas de ejemplo...")
    
    alertas = [
        {
            'tipo': 'sensor',
            'sensor_id': 3,
            'timestamp': datetime.now() - timedelta(days=2),
            'descripcion': 'Sensor BA-RECOLETA-001 sin reportar mediciones por 2 horas',
            'estado': 'resuelta'
        },
        {
            'tipo': 'climatica',
            'sensor_id': 8,
            'timestamp': datetime.now() - timedelta(days=1),
            'descripcion': 'Temperatura superior a 35°C en São Paulo',
            'estado': 'activa'
        },
        {
            'tipo': 'climatica',
            'sensor_id': 10,
            'timestamp': datetime.now() - timedelta(hours=6),
            'descripcion': 'Humedad superior a 90% en Lima',
            'estado': 'activa'
        }
    ]
    
    db.alertas.insert_many(alertas)
    print(f"  ✓ {len(alertas)} alertas insertadas")

def cargar_mensajes_ejemplo(db):
    """Carga mensajes de ejemplo"""
    print("\n💬 Cargando mensajes de ejemplo...")
    
    mensajes = [
        {
            'remitente_id': 1,
            'destinatario_id': None,
            'grupo_id': 1,
            'timestamp': datetime.now() - timedelta(hours=12),
            'contenido': 'Recordatorio: mantenimiento programado de sensores en Buenos Aires este fin de semana',
            'tipo': 'grupal'
        },
        {
            'remitente_id': 1,
            'destinatario_id': None,
            'grupo_id': 1,
            'timestamp': datetime.now() - timedelta(hours=3),
            'contenido': 'Sensor SP-CENTRO-001 reportando temperaturas anormales. Favor revisar.',
            'tipo': 'grupal'
        }
    ]
    
    db.mensajes.insert_many(mensajes)
    print(f"  ✓ {len(mensajes)} mensajes insertados")

def cargar_control_ejemplo(db):
    """Carga registros de control de funcionamiento"""
    print("\n🔧 Cargando controles de funcionamiento...")
    
    controles = [
        {
            'sensor_id': 1,
            'fecha_revision': datetime.now() - timedelta(days=7),
            'estado': 'activo',
            'observaciones': 'Funcionamiento normal. Batería al 92%. Señal estable.'
        },
        {
            'sensor_id': 2,
            'fecha_revision': datetime.now() - timedelta(days=7),
            'estado': 'activo',
            'observaciones': 'Funcionamiento normal. Batería al 88%. Señal estable.'
        },
        {
            'sensor_id': 3,
            'fecha_revision': datetime.now() - timedelta(days=2),
            'estado': 'activo',
            'observaciones': 'Sensor reiniciado tras interrupción. Ahora funcionando correctamente.'
        }
    ]
    
    db.control_funcionamiento.insert_many(controles)
    print(f"  ✓ {len(controles)} controles insertados")

def mostrar_estadisticas(db):
    """Muestra estadísticas de las colecciones"""
    print("\n📈 Estadísticas de MongoDB:")
    print("=" * 50)
    
    colecciones = {
        'mediciones': 'Mediciones de sensores',
        'alertas': 'Alertas generadas',
        'mensajes': 'Mensajes intercambiados',
        'historial_ejecucion': 'Historiales de procesos',
        'control_funcionamiento': 'Controles de funcionamiento'
    }
    
    for nombre, descripcion in colecciones.items():
        count = db[nombre].count_documents({})
        print(f"  {descripcion:.<40} {count:>6} documentos")
    
    print("=" * 50)

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 INICIALIZACIÓN DE MONGODB")
    print("=" * 60)
    
    # Conectar
    db = conectar_mongodb()
    if db is None:
        return
    
    # Crear colecciones
    crear_colecciones(db)
    
    # Crear índices
    crear_indices(db)
    
    # Cargar datos de ejemplo
    respuesta = input("\n¿Deseas cargar datos de ejemplo? (s/n): ").lower()
    if respuesta == 's':
        cargar_mediciones_ejemplo(db)
        cargar_alertas_ejemplo(db)
        cargar_mensajes_ejemplo(db)
        cargar_control_ejemplo(db)
    
    # Mostrar estadísticas
    mostrar_estadisticas(db)
    
    print("\n✅ Inicialización completada exitosamente!")
    print("=" * 60)

if __name__ == "__main__":
    main()