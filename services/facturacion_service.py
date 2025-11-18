"""
Servicio de facturación y cuenta corriente
"""

from datetime import datetime, timedelta
from utils.db_manager import db_manager

class FacturacionService:
    """Servicio para gestión de facturación"""
    
    @staticmethod
    def obtener_cuenta_corriente(usuario_id):
        """
        Obtiene la cuenta corriente de un usuario
        
        Returns:
            Diccionario con datos de cuenta corriente o None
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            cursor.execute("""
                SELECT * FROM cuenta_corriente WHERE usuario_id = %s
            """, (usuario_id,))
            cuenta = cursor.fetchone()
            cursor.close()
            
            return cuenta
            
        except Exception as e:
            print(f"❌ Error obteniendo cuenta corriente: {e}")
            return None
    
    @staticmethod
    def obtener_movimientos_cuenta(usuario_id, limite=50):
        """
        Obtiene movimientos de la cuenta corriente
        
        Returns:
            Lista de movimientos
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Primero obtener el ID de la cuenta
            cursor.execute("SELECT id FROM cuenta_corriente WHERE usuario_id = %s", (usuario_id,))
            cuenta = cursor.fetchone()
            
            if not cuenta:
                cursor.close()
                return []
            
            cursor.execute("""
                SELECT * FROM movimientos_cuenta
                WHERE cuenta_id = %s
                ORDER BY fecha DESC
                LIMIT %s
            """, (cuenta['id'], limite))
            
            movimientos = cursor.fetchall()
            cursor.close()
            
            return movimientos
            
        except Exception as e:
            print(f"❌ Error obteniendo movimientos: {e}")
            return []
    
    @staticmethod
    def listar_facturas(usuario_id, filtro_estado=None, limite=50):
        """
        Lista facturas de un usuario
        
        Args:
            filtro_estado: 'pendiente', 'pagada', 'vencida' o None
        
        Returns:
            Lista de facturas
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            query = """
                SELECT f.*, 
                       (SELECT COUNT(*) FROM facturas_detalle WHERE factura_id = f.id) as items
                FROM facturas f
                WHERE f.usuario_id = %s
            """
            params = [usuario_id]
            
            if filtro_estado:
                query += " AND f.estado = %s"
                params.append(filtro_estado)
            
            query += " ORDER BY f.fecha_emision DESC LIMIT %s"
            params.append(limite)
            
            cursor.execute(query, tuple(params))
            facturas = cursor.fetchall()
            cursor.close()
            
            return facturas
            
        except Exception as e:
            print(f"❌ Error listando facturas: {e}")
            return []
    
    @staticmethod
    def obtener_detalle_factura(factura_id):
        """
        Obtiene el detalle completo de una factura
        
        Returns:
            Diccionario con factura y sus items
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Datos de la factura
            cursor.execute("SELECT * FROM facturas WHERE id = %s", (factura_id,))
            factura = cursor.fetchone()
            
            if not factura:
                cursor.close()
                return None
            
            # Detalle de items
            cursor.execute("""
                SELECT fd.*, p.nombre as proceso_nombre
                FROM facturas_detalle fd
                JOIN solicitudes_proceso sp ON fd.solicitud_id = sp.id
                JOIN procesos p ON sp.proceso_id = p.id
                WHERE fd.factura_id = %s
            """, (factura_id,))
            
            items = cursor.fetchall()
            cursor.close()
            
            factura['items'] = items
            return factura
            
        except Exception as e:
            print(f"❌ Error obteniendo detalle de factura: {e}")
            return None
    
    @staticmethod
    def generar_factura(usuario_id, solicitudes_ids, descripcion="Servicios de procesos"):
        """
        Genera una factura para solicitudes completadas
        
        Args:
            usuario_id: ID del usuario
            solicitudes_ids: Lista de IDs de solicitudes a facturar
            descripcion: Descripción de la factura
        
        Returns:
            (success: bool, mensaje: str, factura_id: int)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Verificar que todas las solicitudes existen y están completadas
            if not solicitudes_ids:
                return False, "No hay solicitudes para facturar", None
            
            placeholders = ','.join(['%s'] * len(solicitudes_ids))
            cursor.execute(f"""
                SELECT sp.id, sp.estado, p.costo, p.nombre
                FROM solicitudes_proceso sp
                JOIN procesos p ON sp.proceso_id = p.id
                WHERE sp.id IN ({placeholders}) AND sp.usuario_id = %s
            """, (*solicitudes_ids, usuario_id))
            
            solicitudes = cursor.fetchall()
            
            if len(solicitudes) != len(solicitudes_ids):
                cursor.close()
                return False, "Algunas solicitudes no existen o no pertenecen al usuario", None
            
            # Verificar que todas estén completadas
            for sol in solicitudes:
                if sol['estado'] != 'completado':
                    cursor.close()
                    return False, f"La solicitud {sol['id']} no está completada", None
            
            # Calcular monto total
            monto_total = sum(sol['costo'] for sol in solicitudes)
            
            # Crear factura
            fecha_vencimiento = datetime.now() + timedelta(days=30)
            cursor.execute("""
                INSERT INTO facturas (usuario_id, monto_total, estado, fecha_vencimiento)
                VALUES (%s, %s, 'pendiente', %s)
            """, (usuario_id, monto_total, fecha_vencimiento))
            
            factura_id = cursor.lastrowid
            
            # Crear items de factura
            for sol in solicitudes:
                cursor.execute("""
                    INSERT INTO facturas_detalle (factura_id, solicitud_id, concepto, monto)
                    VALUES (%s, %s, %s, %s)
                """, (factura_id, sol['id'], sol['nombre'], sol['costo']))
            
            # Registrar movimiento en cuenta corriente (débito)
            cursor.execute("SELECT id FROM cuenta_corriente WHERE usuario_id = %s", (usuario_id,))
            cuenta = cursor.fetchone()
            
            if cuenta:
                cursor.execute("CALL registrar_movimiento(%s, 'debito', %s, %s, %s)",
                              (cuenta['id'], monto_total, f"Factura #{factura_id}", factura_id))
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, f"Factura generada por ${monto_total:.2f}", factura_id
            
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error generando factura: {e}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def registrar_pago(factura_id, usuario_id, monto, metodo_pago, referencia=None):
        """
        Registra un pago para una factura
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Verificar que la factura existe y pertenece al usuario
            cursor.execute("""
                SELECT id, usuario_id, monto_total, estado
                FROM facturas
                WHERE id = %s
            """, (factura_id,))
            
            factura = cursor.fetchone()
            
            if not factura:
                cursor.close()
                return False, "Factura no encontrada"
            
            if factura['usuario_id'] != usuario_id:
                cursor.close()
                return False, "Esta factura no pertenece al usuario"
            
            if factura['estado'] == 'pagada':
                cursor.close()
                return False, "Esta factura ya está pagada"
            
            # Validar monto
            if monto <= 0 or monto > factura['monto_total']:
                cursor.close()
                return False, f"Monto inválido. Debe ser entre 0 y ${factura['monto_total']:.2f}"
            
            # Registrar pago
            cursor.execute("""
                INSERT INTO pagos (factura_id, monto, metodo, referencia)
                VALUES (%s, %s, %s, %s)
            """, (factura_id, monto, metodo_pago, referencia))
            
            # Actualizar estado de factura
            cursor.execute("""
                UPDATE facturas SET estado = 'pagada'
                WHERE id = %s
            """, (factura_id,))
            
            # Registrar movimiento en cuenta corriente (crédito)
            cursor.execute("SELECT id FROM cuenta_corriente WHERE usuario_id = %s", (usuario_id,))
            cuenta = cursor.fetchone()
            
            if cuenta:
                cursor.execute("CALL registrar_movimiento(%s, 'credito', %s, %s, %s)",
                              (cuenta['id'], monto, f"Pago Factura #{factura_id}", factura_id))
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, f"Pago registrado exitosamente por ${monto:.2f}"
            
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error registrando pago: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_resumen_financiero(usuario_id):
        """
        Obtiene resumen financiero del usuario
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Saldo actual
            cursor.execute("""
                SELECT saldo FROM cuenta_corriente WHERE usuario_id = %s
            """, (usuario_id,))
            cuenta = cursor.fetchone()
            saldo = cuenta['saldo'] if cuenta else 0.0
            
            # Total facturado
            cursor.execute("""
                SELECT COALESCE(SUM(monto_total), 0) as total
                FROM facturas
                WHERE usuario_id = %s
            """, (usuario_id,))
            total_facturado = cursor.fetchone()['total']
            
            # Facturas pendientes
            cursor.execute("""
                SELECT COUNT(*) as cantidad, COALESCE(SUM(monto_total), 0) as monto
                FROM facturas
                WHERE usuario_id = %s AND estado = 'pendiente'
            """, (usuario_id,))
            pendientes = cursor.fetchone()
            
            # Facturas pagadas
            cursor.execute("""
                SELECT COUNT(*) as cantidad
                FROM facturas
                WHERE usuario_id = %s AND estado = 'pagada'
            """, (usuario_id,))
            pagadas = cursor.fetchone()
            
            cursor.close()
            
            return {
                'saldo': float(saldo),
                'total_facturado': float(total_facturado),
                'facturas_pendientes': pendientes['cantidad'],
                'monto_pendiente': float(pendientes['monto']),
                'facturas_pagadas': pagadas['cantidad']
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo resumen: {e}")
            return {
                'saldo': 0.0,
                'total_facturado': 0.0,
                'facturas_pendientes': 0,
                'monto_pendiente': 0.0,
                'facturas_pagadas': 0
            }
    
    @staticmethod
    def cargar_saldo(usuario_id, monto, concepto="Carga de saldo"):
        """
        Carga saldo a la cuenta corriente del usuario
        
        Returns:
            (success: bool, mensaje: str)
        """
        try:
            cursor = db_manager.get_mysql_cursor()
            
            # Obtener cuenta
            cursor.execute("SELECT id FROM cuenta_corriente WHERE usuario_id = %s", (usuario_id,))
            cuenta = cursor.fetchone()
            
            if not cuenta:
                cursor.close()
                return False, "Cuenta corriente no encontrada"
            
            # Registrar movimiento (crédito)
            cursor.execute("CALL registrar_movimiento(%s, 'credito', %s, %s, NULL)",
                          (cuenta['id'], monto, concepto))
            
            db_manager.commit_mysql()
            cursor.close()
            
            return True, f"Saldo cargado: ${monto:.2f}"
            
        except Exception as e:
            db_manager.rollback_mysql()
            print(f"❌ Error cargando saldo: {e}")
            return False, f"Error: {str(e)}"
