"""
Configuración de conexiones a bases de datos
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración MySQL
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3307)),
    'user': os.getenv('MYSQL_USER', 'admin'),
    'password': os.getenv('MYSQL_PASSWORD', 'admin123'),
    'database': os.getenv('MYSQL_DATABASE', 'sensores_db'),
    'autocommit': False,
    'charset': 'utf8mb4'
}

# Configuración MongoDB
MONGODB_CONFIG = {
    'host': os.getenv('MONGODB_HOST', 'localhost'),
    'port': int(os.getenv('MONGODB_PORT', 27017)),
    'username': os.getenv('MONGODB_USER', 'admin'),
    'password': os.getenv('MONGODB_PASSWORD', 'admin123'),
    'database': os.getenv('MONGODB_DATABASE', 'sensores_db')
}

# Configuración Redis
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'password': os.getenv('REDIS_PASSWORD', 'redis123'),
    'db': int(os.getenv('REDIS_DB', 0)),
    'decode_responses': True
}

# Configuración de la aplicación
APP_CONFIG = {
    'session_timeout': int(os.getenv('SESSION_TIMEOUT', 3600)),
    'cache_timeout': int(os.getenv('CACHE_TIMEOUT', 1800))
}