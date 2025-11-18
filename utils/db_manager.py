"""
Manejador centralizado de conexiones a bases de datos
"""

import mysql.connector
from pymongo import MongoClient
import redis
from config.db_config import MYSQL_CONFIG, MONGODB_CONFIG, REDIS_CONFIG

class DatabaseManager:
    """Clase singleton para manejar conexiones a las bases de datos"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.mysql_conn = None
        self.mongo_client = None
        self.mongo_db = None
        self.redis_client = None
        self._initialized = True
    
    def conectar_mysql(self):
        """Conecta a MySQL"""
        try:
            if self.mysql_conn is None or not self.mysql_conn.is_connected():
                self.mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
            return self.mysql_conn
        except mysql.connector.Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            raise
    
    def conectar_mongodb(self):
        """Conecta a MongoDB"""
        try:
            if self.mongo_client is None:
                connection_string = f"mongodb://{MONGODB_CONFIG['username']}:{MONGODB_CONFIG['password']}@{MONGODB_CONFIG['host']}:{MONGODB_CONFIG['port']}/"
                self.mongo_client = MongoClient(connection_string)
                self.mongo_db = self.mongo_client[MONGODB_CONFIG['database']]
            return self.mongo_db
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            raise
    
    def conectar_redis(self):
        """Conecta a Redis"""
        try:
            if self.redis_client is None:
                self.redis_client = redis.Redis(**REDIS_CONFIG)
                self.redis_client.ping()
            return self.redis_client
        except redis.RedisError as e:
            print(f"❌ Error conectando a Redis: {e}")
            raise
    
    def get_mysql_cursor(self, dictionary=True):
        """Obtiene un cursor de MySQL"""
        conn = self.conectar_mysql()
        return conn.cursor(dictionary=dictionary)
    
    def commit_mysql(self):
        """Hace commit en MySQL"""
        if self.mysql_conn and self.mysql_conn.is_connected():
            self.mysql_conn.commit()
    
    def rollback_mysql(self):
        """Hace rollback en MySQL"""
        if self.mysql_conn and self.mysql_conn.is_connected():
            self.mysql_conn.rollback()
    
    def cerrar_conexiones(self):
        """Cierra todas las conexiones"""
        if self.mysql_conn and self.mysql_conn.is_connected():
            self.mysql_conn.close()
            self.mysql_conn = None
        
        if self.mongo_client:
            self.mongo_client.close()
            self.mongo_client = None
            self.mongo_db = None
        
        if self.redis_client:
            self.redis_client.close()
            self.redis_client = None

# Instancia global
db_manager = DatabaseManager()
