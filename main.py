#!/usr/bin/env python3
"""
Sistema de Gestión de Sensores - Aplicación Principal
Trabajo Práctico - Persistencia Políglota
"""

from ui.app import SistemaSensores
from utils.db_manager import db_manager


def main():
    """Función principal"""
    try:
        app = SistemaSensores()
        app.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Aplicación interrumpida por el usuario")
        db_manager.cerrar_conexiones()
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        db_manager.cerrar_conexiones()


if __name__ == "__main__":

    main()