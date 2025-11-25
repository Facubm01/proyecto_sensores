# 🧪 Casos de Prueba - Hoja de Ruta para la Demo

## 📝 Formato de Casos de Prueba

Cada caso tiene:
- **Entrada**: Lo que ingresas
- **Esperado**: Lo que debería pasar
- **Explicación**: Por qué pasa eso

---

## ✅ CASOS EXITOSOS (Datos Correctos)

### Caso 1: Registro de Usuario Nuevo

**ENTRADA:**
```
Opción: 2 (Registrar)
Nombre: Juan Perez
Email: juan.perez@demo2025.com
Contraseña: demo123
Confirmar: demo123
```

**ESPERADO:**
```
✅ Usuario registrado exitosamente
ℹ️  Ahora puede iniciar sesión
```

**EXPLICACIÓN AL PROFESOR:**
- bcrypt hashea la contraseña con salt automático
- MySQL crea el usuario con UNIQUE constraint en email
- Se crea cuenta_corriente automáticamente con saldo $0
- Se asigna rol 'cliente' por defecto

**VERIFICAR EN MySQL:**
```sql
SELECT u.id, u.nombre_completo, u.email, cc.saldo 
FROM usuarios u 
JOIN cuenta_corriente cc ON u.id = cc.usuario_id 
WHERE u.email = 'juan.perez@demo2025.com';
```

---

### Caso 2: Login Exitoso

**ENTRADA:**
```
Opción: 1 (Login)
Email: juan.perez@demo2025.com
Contraseña: demo123
```

**ESPERADO:**
```
✅ Login exitoso
📊 Usuario: Juan Perez
📧 Email: juan.perez@demo2025.com
🎭 Roles: cliente
```

**EXPLICACIÓN AL PROFESOR:**
- bcrypt.checkpw() verifica hash contra contraseña ingresada
- Se genera UUID único para session_id
- Redis almacena sesión como Hash con TTL=3600s
- El menú se adapta según roles del usuario

**VERIFICAR EN Redis:**
```bash
redis-cli -a redis123
KEYS session:*
HGETALL session:{el-uuid-que-aparece}
TTL session:{el-uuid}
```

---

### Caso 3: Cargar Saldo

**ENTRADA:**
```
Menú: 3 (Facturación) → 5 (Cargar Saldo)
Monto: 500
Concepto: Carga inicial de prueba
```

**ESPERADO:**
```
✅ Saldo cargado: $500.00

Saldo actualizado:
💰 Saldo actual: $500.00
```

**EXPLICACIÓN AL PROFESOR:**
- Ejecuta Stored Procedure `registrar_movimiento()`
- SP actualiza saldo en cuenta_corriente (UPDATE)
- SP inserta registro en movimientos_cuenta
- Todo en una transacción ACID

**VERIFICAR EN MySQL:**
```sql
SELECT * FROM movimientos_cuenta WHERE cuenta_id = 1 ORDER BY fecha DESC LIMIT 1;
-- Debería mostrar: tipo='credito', monto=500.00, saldo_nuevo=500.00

SELECT saldo FROM cuenta_corriente WHERE usuario_id = 1;
-- Debería mostrar: 500.00
```

---

### Caso 4: Solicitar Proceso con Datos Válidos

**ENTRADA:**
```
Menú: 1 (Procesos) → 2 (Solicitar)
Proceso ID: 1 (Informe Temp. Max/Min)

Parámetros:
Ciudad: Buenos Aires
País: Argentina
Fecha inicio: 2024-01-01
Fecha fin: 2024-12-31

Confirmar: s
```

**ESPERADO:**
```
✅ Solicitud creada exitosamente
ℹ️  ID de solicitud: 1
💰 Costo: $150.00
⏳ Estado: pendiente
```

**EXPLICACIÓN AL PROFESOR:**
- MySQL: INSERT en solicitudes_proceso con estado='pendiente'
- Parámetros guardados como JSON: '{"ciudad":"Buenos Aires",...}'
- Redis: lpush() agrega ID a cola FIFO
- Usuario puede ver solicitud en "Mis Solicitudes"

**VERIFICAR:**
```sql
-- MySQL
SELECT id, proceso_id, estado, parametros 
FROM solicitudes_proceso 
WHERE id = 1;

-- Redis
redis-cli -a redis123
LRANGE cola:procesos_pendientes 0 -1
-- Debería mostrar: "1"
```

---

### Caso 5: Ejecutar Proceso (Como Admin)

**ENTRADA:**
```
Login como admin@sensores.com / admin123
Menú: 8 (Ejecutar Procesos Pendientes)
Confirmar: s
```

**ESPERADO:**
```
⚙️  Procesando solicitud #1...

✅ Proceso ejecutado: Informe Temp. Max/Min
📊 Resultado:
   - Temperatura Máxima: 32.10°C
   - Temperatura Mínima: 18.50°C
   - Humedad Máxima: 85.00%
   - Humedad Minima: 45.00%
   - Total Mediciones: 8760
   
💰 Factura generada automáticamente
   - Factura #1: $150.00
```

**EXPLICACIÓN AL PROFESOR (MUY IMPORTANTE):**

**Paso 1:** Redis rpop()
```
Cola antes: [1]
rpop() → retorna: 1
Cola después: []
```

**Paso 2:** MySQL UPDATE estado='en_proceso'
```sql
UPDATE solicitudes_proceso SET estado='en_proceso' WHERE id=1;
```

**Paso 3:** MongoDB Aggregation Pipeline
```javascript
db.mediciones.aggregate([
    {
        $match: {
            ciudad: "Buenos Aires",
            timestamp: {
                $gte: ISODate("2024-01-01"),
                $lte: ISODate("2024-12-31")
            }
        }
    },
    {
        $group: {
            _id: null,
            temperatura_maxima: {$max: "$temperatura"},
            temperatura_minima: {$min: "$temperatura"},
            humedad_maxima: {$max: "$humedad"},
            humedad_minima: {$min: "$humedad"},
            total_mediciones: {$sum: 1}
        }
    }
])

// Procesa MILLONES de documentos
// Retorna resultado agregado
```

**Paso 4:** MongoDB INSERT resultado
```javascript
db.historial_ejecucion.insert_one({
    solicitud_id: 1,
    fecha_ejecucion: ISODate("2025-01-15T14:30:00Z"),
    resultado: {
        temperatura_maxima: 32.10,
        temperatura_minima: 18.50,
        ...
    },
    estado: "completado"
})
```

**Paso 5:** MySQL UPDATE estado='completado'
```sql
UPDATE solicitudes_proceso SET estado='completado' WHERE id=1;
```

**Paso 6:** Facturación automática
```sql
-- Llama a FacturacionService.generar_factura()
INSERT INTO facturas (usuario_id, monto_total, estado) VALUES (1, 150.00, 'pendiente');
-- factura_id = 1

INSERT INTO items_factura (factura_id, solicitud_id, concepto, monto) 
VALUES (1, 1, 'Informe Temp. Max/Min', 150.00);

CALL registrar_movimiento(1, 'debito', 150.00, 'Factura #1', 1);
-- Actualiza saldo: 500 - 150 = 350
```

**VERIFICAR TODO:**
```sql
-- MySQL - Solicitud completada
SELECT id, estado FROM solicitudes_proceso WHERE id=1;
-- estado='completado'

-- MySQL - Factura generada
SELECT * FROM facturas WHERE id=1;
-- monto_total=150.00, estado='pendiente'

-- MySQL - Saldo descontado
SELECT saldo FROM cuenta_corriente WHERE usuario_id=1;
-- saldo=350.00

-- MongoDB - Resultado guardado
db.historial_ejecucion.find({solicitud_id: 1})
```

---

### Caso 6: Ver Resultado (Como Usuario)

**ENTRADA:**
```
Login como juan.perez@demo2025.com
Menú: 2 (Mis Solicitudes) → 1 (Ver Todas)
Seleccionar solicitud: 1
```

**ESPERADO:**
```
╔═══════════════════════════════════════════════════╗
║  SOLICITUD #1 - COMPLETADA                       ║
╠═══════════════════════════════════════════════════╣
║  Proceso: Informe Temp. Max/Min                  ║
║  Fecha solicitud: 2025-01-15 10:00              ║
║  Fecha ejecución: 2025-01-15 14:30              ║
║  Costo: $150.00 (facturado)                     ║
╠═══════════════════════════════════════════════════╣
║  RESULTADO:                                      ║
║  🌡️  Temp. Máxima: 32.10°C                      ║
║  🌡️  Temp. Mínima: 18.50°C                      ║
║  💧 Humedad Máxima: 85.00%                       ║
║  💧 Humedad Mínima: 45.00%                       ║
║  📊 Total Mediciones: 8,760                      ║
║                                                  ║
║  Parámetros usados:                              ║
║  - Ciudad: Buenos Aires                          ║
║  - País: Argentina                               ║
║  - Período: 2024-01-01 a 2024-12-31             ║
╚═══════════════════════════════════════════════════╝
```

**EXPLICACIÓN AL PROFESOR:**
- **Integración MySQL + MongoDB**
- MySQL provee: id, estado, fecha_solicitud, parámetros
- MongoDB provee: resultado detallado, fecha_ejecución
- Se combinan en la capa de servicio (proceso_service.py)

**Código que hace la magia:**
```python
# En proceso_service.py - líneas 136-144
for solicitud in solicitudes:
    if solicitud['estado'] == 'completado':
        # Buscar en MongoDB
        historial = db.historial_ejecucion.find_one({
            'solicitud_id': solicitud['id']
        })
        if historial:
            # ENRIQUECER datos de MySQL con resultado de MongoDB
            solicitud['resultado'] = historial.get('resultado')
            solicitud['fecha_ejecucion'] = historial.get('fecha_ejecucion')
```

---

### Caso 7: Verificar Factura y Pagar

**ENTRADA:**
```
Menú: 3 (Facturación) → 2 (Ver Facturas)
```

**ESPERADO:**
```
┌────┬────────────┬──────────┬───────────┬──────────────┬───────┐
│ ID │ Fecha      │ Monto    │ Estado    │ Vencimiento  │ Items │
├────┼────────────┼──────────┼───────────┼──────────────┼───────┤
│ 1  │ 2025-01-15 │ $150.00  │ pendiente │ 2025-02-14   │ 1     │
└────┴────────────┴──────────┴───────────┴──────────────┴───────┘
```

**ENTRADA (Pagar):**
```
Menú: 3 → 3 (Pagar Factura)
Factura ID: 1
Monto: 150
Método: transferencia
Referencia: DEMO123
```

**ESPERADO:**
```
✅ Pago registrado exitosamente por $150.00
✅ Factura marcada como pagada

💰 Saldo actualizado: $500.00
   (350 + 150 del pago)
```

**EXPLICACIÓN AL PROFESOR:**
- INSERT en tabla pagos
- UPDATE facturas SET estado='pagada'
- CALL registrar_movimiento('credito', 150.00)
- Saldo vuelve a $500 (se acredita el pago)

---

## ❌ CASOS DE ERROR (Datos Incorrectos)

### Error 1: Email Duplicado

**ENTRADA:**
```
Opción: 2 (Registrar)
Email: juan.perez@demo2025.com  ← YA EXISTE
```

**ESPERADO:**
```
❌ El email ya está registrado
```

**EXPLICACIÓN:**
- MySQL valida UNIQUE constraint
- catch en auth_service.py línea 50

---

### Error 2: Contraseña Incorrecta

**ENTRADA:**
```
Opción: 1 (Login)
Email: juan.perez@demo2025.com
Contraseña: incorrecta
```

**ESPERADO:**
```
❌ Contraseña incorrecta
```

**EXPLICACIÓN:**
- bcrypt.checkpw() retorna False
- No se crea sesión

---

### Error 3: Contraseñas No Coinciden

**ENTRADA:**
```
Opción: 2 (Registrar)
Contraseña: demo123
Confirmar: demo456  ← DIFERENTE
```

**ESPERADO:**
```
❌ Las contraseñas no coinciden
```

**EXPLICACIÓN:**
- Validación en main.py antes de llamar service

---

### Error 4: Formato de Fecha Inválido

**ENTRADA:**
```
Fecha inicio: 15/01/2024  ← Formato incorrecto
```

**ESPERADO:**
```
❌ Formato de fecha inválido. Use YYYY-MM-DD
```

**EXPLICACIÓN:**
- datetime.strptime() lanza ValueError
- Se captura y muestra mensaje amigable

---

### Error 5: Fecha Fin < Fecha Inicio

**ENTRADA:**
```
Fecha inicio: 2024-12-01
Fecha fin: 2024-01-01  ← Anterior
```

**ESPERADO:**
```
❌ La fecha fin debe ser posterior a la fecha inicio
```

**EXPLICACIÓN:**
- Validación lógica antes de solicitar proceso

---

### Error 6: Saldo Insuficiente

**ENTRADA:**
```
Saldo actual: $0.00
Intentar solicitar proceso de: $150.00
```

**ESPERADO:**
```
❌ Saldo insuficiente
💰 Saldo actual: $0.00
💵 Costo del proceso: $150.00
⚠️  Por favor, cargue saldo primero
```

**EXPLICACIÓN:**
- Validación en proceso_service.py
- Consulta saldo antes de crear solicitud

---

### Error 7: Proceso No Encontrado

**ENTRADA:**
```
Proceso ID: 999  ← No existe
```

**ESPERADO:**
```
❌ Proceso no válido
```

**EXPLICACIÓN:**
- Validación en main.py
- Verifica que ID esté en lista de procesos

---

### Error 8: Sesión Expirada

**ENTRADA:**
```
(Esperar más de 1 hora sin actividad)
Intentar cualquier operación
```

**ESPERADO:**
```
❌ Sesión expirada. Por favor, inicie sesión nuevamente
```

**EXPLICACIÓN:**
- Redis TTL elimina la key automáticamente
- verificar_sesion() retorna None
- Vuelve al menú principal

---

### Error 9: Sin Permisos (Role-Based)

**ENTRADA:**
```
Usuario 'cliente' intenta:
Menú: 8 (Ejecutar Procesos)  ← Solo admin
```

**ESPERADO:**
```
❌ Opción inválida o sin permisos
```

**EXPLICACIÓN:**
- Doble verificación de roles:
  1. La opción no aparece en el menú (líneas 146-160 main.py)
  2. Si ingresa el número manualmente, se valida de nuevo (línea 180)

---

### Error 10: Cancelar Proceso No Pendiente

**ENTRADA:**
```
Intentar cancelar solicitud con estado='completado'
```

**ESPERADO:**
```
❌ Solo se pueden cancelar solicitudes pendientes
🔒 Estado actual: completado
```

**EXPLICACIÓN:**
- Validación en proceso_service.py línea 226
- Solo estado='pendiente' puede cancelarse

---

## 🎬 Secuencia Recomendada Para la Demo (15 min)

### Parte 1: Flujo Feliz (8 min)
1. ✅ Caso 1: Registrar usuario (1 min)
2. ✅ Caso 2: Login (30 seg)
3. ✅ Caso 3: Cargar saldo (1 min)
4. ✅ Caso 4: Solicitar proceso (2 min)
5. ✅ Caso 5: Ejecutar como admin (2 min)
6. ✅ Caso 6: Ver resultado (1 min)
7. ✅ Caso 7: Verificar factura (30 seg)

### Parte 2: Validaciones (5 min)
8. ❌ Error 1: Email duplicado (30 seg)
9. ❌ Error 2: Contraseña incorrecta (30 seg)
10. ❌ Error 4: Formato fecha inválido (1 min)
11. ❌ Error 9: Sin permisos (role) (1 min)

### Parte 3: Bonus (si hay tiempo - 2 min)
12. Mostrar datos en MySQL directamente
13. Mostrar aggregation en MongoDB
14. Mostrar sesiones en Redis

---

## 📊 Datos de Prueba Recomendados

### Usuario de Demo
```
Nombre: María García
Email: maria.garcia@demo.com
Password: demo2025
Saldo inicial: $1000
```

### Proceso a Ejecutar
```
Tipo: Informe Promedio Mensual (ID: 2)
Ciudad: Córdoba
País: Argentina
Fecha inicio: 2024-01-01
Fecha fin: 2024-06-30
Costo: $200.00
```

### Validaciones a Probar
```
1. Email duplicado: maria.garcia@demo.com
2. Password incorrecta: wrong123
3. Fecha inválida: 01-01-2024
4. Fecha fin < inicio: 2024-12-01 a 2024-01-01
```

---

¡Todo listo para una demostración exitosa! 🚀
