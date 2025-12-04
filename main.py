#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Gestión de Sensores - Aplicación Principal
Trabajo Práctico - Persistencia Políglota
"""

import sys
import os

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    os.system('chcp 65001 >nul 2>&1')

from ui.app import SistemaSensores
from utils.db_manager import db_manager


def main():
    """Función principal"""
    try:
        app = SistemaSensores()
        app.run()
    except KeyboardInterrupt:
        print("\n\n[!] Aplicación interrumpida por el usuario")
        db_manager.cerrar_conexiones()
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        db_manager.cerrar_conexiones()


if __name__ == "__main__":

    main()