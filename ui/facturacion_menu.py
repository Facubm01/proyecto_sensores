"""
Módulo de facturación y cuenta corriente
Gestiona facturas, pagos y saldo de usuarios
"""

from services.facturacion_service import FacturacionService
from utils.menu import *
from colorama import Fore


class FacturacionMenu:
    """Menú de facturación y cuenta corriente"""
    
    def __init__(self, user_data):
        """
        Args:
            user_data: Información del usuario autenticado
        """
        self.user_data = user_data
    
    def mostrar_menu(self):
        """Menú principal de facturación"""
        while True:
            limpiar_pantalla()
            
            # Mostrar resumen
            resumen = FacturacionService.obtener_resumen_financiero(self.user_data['user_id'])
            print(f"{Fore.YELLOW}Resumen Financiero:")
            print(f"  Saldo actual: ${resumen['saldo']:.2f}")
            print(f"  Total facturado: ${resumen['total_facturado']:.2f}")
            print(f"  Facturas pendientes: {resumen['facturas_pendientes']} (${resumen['monto_pendiente']:.2f})")
            print(f"  Facturas pagadas: {resumen['facturas_pagadas']}\n")
            
            opciones = [
                (1, "Ver Cuenta Corriente"),
                (2, "Ver Mis Facturas"),
                (3, "Ver Detalle de Factura"),
                (4, "Registrar Pago"),
                (5, "Cargar Saldo"),
            ]
            
            seleccion = mostrar_menu("FACTURACIÓN Y CUENTA CORRIENTE", opciones)
            
            if seleccion == '0':
                break
            elif seleccion == '1':
                self.ver_cuenta_corriente()
            elif seleccion == '2':
                self.ver_facturas()
            elif seleccion == '3':
                self.ver_detalle_factura()
            elif seleccion == '4':
                self.registrar_pago()
            elif seleccion == '5':
                self.cargar_saldo()
            else:
                mostrar_error("Opción inválida")
                pausar()
    
    def ver_cuenta_corriente(self):
        """Muestra la cuenta corriente y movimientos"""
        limpiar_pantalla()
        mostrar_titulo("CUENTA CORRIENTE")
        
        cuenta = FacturacionService.obtener_cuenta_corriente(self.user_data['user_id'])
        
        if not cuenta:
            mostrar_error("No se encontró cuenta corriente")
            pausar()
            return
        
        print(f"\n{Fore.GREEN}Saldo actual: ${cuenta['saldo']:.2f}")
        print(f"Última actualización: {cuenta['ultima_actualizacion']}\n")
        
        # Mostrar movimientos
        if confirmar("¿Ver movimientos de la cuenta?"):
            limpiar_pantalla()
            mostrar_subtitulo("MOVIMIENTOS DE CUENTA")
            
            movimientos = FacturacionService.obtener_movimientos_cuenta(self.user_data['user_id'])
            
            if not movimientos:
                mostrar_info("No hay movimientos")
            else:
                headers = ['Fecha', 'Tipo', 'Concepto', 'Monto', 'Saldo']
                filas = []
                
                for m in movimientos:
                    tipo_symbol = '➖' if m['tipo'] == 'debito' else '➕'
                    monto_str = f"-${m['monto']:.2f}" if m['tipo'] == 'debito' else f"+${m['monto']:.2f}"
                    
                    filas.append([
                        str(m['fecha'])[:19],
                        tipo_symbol + ' ' + m['tipo'],
                        m['concepto'][:40],
                        monto_str,
                        f"${m['saldo_nuevo']:.2f}"
                    ])
                
                mostrar_tabla(headers, filas)
        
        pausar()
    
    def ver_facturas(self):
        """Lista facturas del usuario"""
        limpiar_pantalla()
        mostrar_titulo("MIS FACTURAS")
        
        facturas = FacturacionService.listar_facturas(self.user_data['user_id'])
        
        if not facturas:
            mostrar_info("No hay facturas")
        else:
            headers = ['ID', 'Fecha', 'Monto', 'Estado', 'Vencimiento', 'Items']
            filas = []
            
            for f in facturas:
                color_estado = Fore.GREEN if f['estado'] == 'pagada' else Fore.YELLOW if f['estado'] == 'pendiente' else Fore.RED
                
                filas.append([
                    f['id'],
                    str(f['fecha_emision'])[:10],
                    f"${f['monto_total']:.2f}",
                    f['estado'],
                    str(f['fecha_vencimiento']) if f['fecha_vencimiento'] else 'N/A',
                    f['items']
                ])
            
            mostrar_tabla(headers, filas)
        
        pausar()
    
    def ver_detalle_factura(self):
        """Muestra el detalle completo de una factura"""
        limpiar_pantalla()
        mostrar_titulo("DETALLE DE FACTURA")
        
        factura_id = solicitar_entrada("ID de la factura", int)
        if not factura_id:
            return
        
        factura = FacturacionService.obtener_detalle_factura(factura_id)
        
        if not factura:
            mostrar_error("Factura no encontrada")
            pausar()
            return
        
        # Verificar que pertenece al usuario
        if factura['usuario_id'] != self.user_data['user_id']:
            mostrar_error("Esta factura no le pertenece")
            pausar()
            return
        
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.GREEN}Factura #{factura['id']}")
        print(f"Fecha emisión: {factura['fecha_emision']}")
        print(f"Fecha vencimiento: {factura['fecha_vencimiento']}")
        print(f"Estado: {factura['estado'].upper()}")
        print(f"Monto total: ${factura['monto_total']:.2f}")
        
        print(f"\n{Fore.YELLOW}Items de la Factura:")
        print(f"{Fore.CYAN}{'-' * 60}")
        
        for item in factura['items']:
            print(f"  • {item['proceso_nombre']}")
            print(f"    Monto: ${item['monto']:.2f}")
            print()
        
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        pausar()
    
    def registrar_pago(self):
        """Registra un pago de factura"""
        limpiar_pantalla()
        mostrar_titulo("REGISTRAR PAGO")
        
        # Mostrar facturas pendientes
        facturas = FacturacionService.listar_facturas(self.user_data['user_id'], 'pendiente')
        
        if not facturas:
            mostrar_info("No hay facturas pendientes")
            pausar()
            return
        
        print(f"{Fore.CYAN}Facturas Pendientes:\n")
        for f in facturas:
            print(f"  ID {f['id']}: ${f['monto_total']:.2f} - Vence: {f['fecha_vencimiento']}")
        
        print()
        factura_id = solicitar_entrada("ID de la factura a pagar", int)
        if not factura_id:
            return
        
        # Buscar la factura
        factura = next((f for f in facturas if f['id'] == factura_id), None)
        if not factura:
            mostrar_error("Factura no válida")
            pausar()
            return
        
        print(f"\nFactura #{factura['id']} - Monto: ${factura['monto_total']:.2f}")
        
        monto = solicitar_entrada(f"Monto a pagar (máx ${factura['monto_total']:.2f})", float)
        if not monto:
            return
        
        metodo = solicitar_entrada("Método de pago (tarjeta/transferencia/efectivo)", str, 
                                   ['tarjeta', 'transferencia', 'efectivo'])
        if not metodo:
            return
        
        referencia = solicitar_entrada("Referencia/Número de operación (opcional)", str) or None
        
        if confirmar(f"¿Confirmar pago de ${monto:.2f}?"):
            success, mensaje = FacturacionService.registrar_pago(
                factura_id,
                self.user_data['user_id'],
                monto,
                metodo,
                referencia
            )
            
            if success:
                mostrar_exito(mensaje)
            else:
                mostrar_error(mensaje)
        
        pausar()
    
    def cargar_saldo(self):
        """Carga saldo a la cuenta corriente"""
        limpiar_pantalla()
        mostrar_titulo("CARGAR SALDO")
        
        cuenta = FacturacionService.obtener_cuenta_corriente(self.user_data['user_id'])
        if cuenta:
            print(f"\n{Fore.CYAN}Saldo actual: ${cuenta['saldo']:.2f}\n")
        
        monto = solicitar_entrada("Monto a cargar", float)
        if not monto or monto <= 0:
            mostrar_error("Monto inválido")
            pausar()
            return
        
        concepto = solicitar_entrada("Concepto (opcional)", str) or "Carga de saldo"
        
        if confirmar(f"¿Confirmar carga de ${monto:.2f}?"):
            success, mensaje = FacturacionService.cargar_saldo(
                self.user_data['user_id'],
                monto,
                concepto
            )
            
            if success:
                mostrar_exito(mensaje)
            else:
                mostrar_error(mensaje)
        
        pausar()
