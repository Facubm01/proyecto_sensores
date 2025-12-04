"""
Sistema de logging para el sistema de sensores
"""

import logging
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style


class SistemaLogger:
    """Logger configurado para el sistema"""
    
    _instancia = None
    _logger = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(SistemaLogger, cls).__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia
    
    def _inicializar(self):
        """Inicializa el logger"""
        # Crear directorio de logs
        directorio_logs = Path("logs")
        directorio_logs.mkdir(exist_ok=True)
        
        # Configurar logger
        self._logger = logging.getLogger('sistema_sensores')
        self._logger.setLevel(logging.INFO)
        
        # Evitar duplicados
        if not self._logger.handlers:
            # Handler para archivo
            archivo_log = directorio_logs / f"sistema_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(archivo_log, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Handler para consola (solo en modo debug)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            
            # Formato
            formato = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formato)
            console_handler.setFormatter(formato)
            
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)
    
    def info(self, mensaje: str, usuario_id: int = None):
        """Registra un mensaje informativo"""
        if usuario_id:
            mensaje = f"[Usuario {usuario_id}] {mensaje}"
        self._logger.info(mensaje)
    
    def warning(self, mensaje: str, usuario_id: int = None):
        """Registra una advertencia"""
        if usuario_id:
            mensaje = f"[Usuario {usuario_id}] {mensaje}"
        self._logger.warning(mensaje)
    
    def error(self, mensaje: str, usuario_id: int = None, excepcion: Exception = None):
        """Registra un error"""
        if usuario_id:
            mensaje = f"[Usuario {usuario_id}] {mensaje}"
        if excepcion:
            mensaje = f"{mensaje} - {str(excepcion)}"
        self._logger.error(mensaje, exc_info=excepcion is not None)
    
    def debug(self, mensaje: str, usuario_id: int = None):
        """Registra un mensaje de debug"""
        if usuario_id:
            mensaje = f"[Usuario {usuario_id}] {mensaje}"
        self._logger.debug(mensaje)
    
    def log_operacion(self, operacion: str, usuario_id: int, detalles: dict = None):
        """Registra una operación del sistema"""
        mensaje = f"Operación: {operacion}"
        if detalles:
            detalles_str = ", ".join([f"{k}={v}" for k, v in detalles.items()])
            mensaje = f"{mensaje} - {detalles_str}"
        self.info(mensaje, usuario_id)


# Instancia global
logger = SistemaLogger()


