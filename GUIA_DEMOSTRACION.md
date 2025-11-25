# 🎯 Guía de Demostración - Sistema de Gestión de Sensores

## 📋 Preparación Previa

### 1. Iniciar las Bases de Datos

```bash
# En el directorio del proyecto:
cd /Users/facundobustamante/proyecto_sensores

# Iniciar contenedores Docker
docker-compose up -d

# Verificar que estén corriendo
docker ps
```

Deberías ver 3 contenedores activos:
- `sensores_mysql` (puerto 3307)
- `sensores_mongodb` (puerto 27017)
- `sensores_redis` (puerto 6379)

### 2. Ejecutar la Aplicación

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar aplicación
python main.py
```

---

## 🎬 Demostración Completa - Flujo de Proceso

### **ESCENARIO 1: Flujo Completo con Datos Correctos** ✅

#### **Paso 1: Registro de Usuario**

```
╔════════════════════════════════════════╗
║  SISTEMA DE GESTIÓN DE SENSORES       ║
╠════════════════════════════════════════╣
║  [1] Iniciar Sesión                   ║
║  [2] Registrar Nuevo Usuario          ║
║  [3] Salir                            ║
╚════════════════════════════════════════╝
```

**Seleccionar: `2`**

**Datos a ingresar:**
```
Nombre completo: Juan Perez
Email: juan.perez@test.com
Contraseña: test123
Confirmar contraseña: test123
```

**Resultado esperado:**
```
✅ Usuario registrado exitosamente
ℹ️  Ahora puede iniciar sesión
```

> **Explicación al profesor:** El sistema crea automáticamente:
> - Usuario en MySQL con password hasheado (bcrypt)
> - Cuenta corriente con saldo $0
> - Rol de 'cliente' por defecto

---

#### **Paso 2: Iniciar Sesión**

**Seleccionar: `1`**

**Datos a ingresar:**
```
Email: juan.perez@test.com
Contraseña: test123
```

**Resultado esperado:**
```
✅ Login exitoso
📊 Usuario: Juan Perez
📧 Email: juan.perez@test.com
🎭 Roles: cliente
```

> **Explicación al profesor:** 
> - Valida credenciales contra MySQL
> - Crea sesión en Redis con TTL de 1 hora
> - Retorna session_id único (UUID)
> - El menú se adapta dinámicamente según roles

---

#### **Paso 3: Cargar Saldo** (para poder pagar el proceso)

```
MENÚ PRINCIPAL
[1] Gestión de Procesos
[2] Ver Mis Solicitudes
[3] Facturación y Cuenta Corriente  ← Seleccionar esta
[4] Mensajería
[99] Cerrar Sesión
```

**Seleccionar: `3` → `5` (Cargar Saldo)**

**Datos a ingresar:**
```
Monto a cargar: 500
Concepto: Carga inicial
```

**Resultado esperado:**
```
✅ Saldo cargado: $500.00
```

> **Explicación al profesor:**
> - Registra movimiento tipo 'crédito' en MySQL
> - Actualiza saldo en cuenta_corriente (mediante Stored Procedure)
> - Almacena historial en movimientos_cuenta

---

#### **Paso 4: Ver Procesos Disponibles**

**Desde Menú Principal → `1` (Gestión de Procesos) → `1` (Ver Procesos Disponibles)**

**Resultado esperado:**
```
┌────┬─────────────────────────┬──────────┬─────────┐
│ ID │ Nombre                  │ Tipo     │ Costo   │
├────┼─────────────────────────┼──────────┼─────────┤
│ 1  │ Informe Temp. Max/Min   │ informe  │ $150.00 │
│ 2  │ Informe Promedio Mensual│ informe  │ $200.00 │
│ 3  │ Alerta Rango Temp.      │ alerta   │ $50.00  │
└────┴─────────────────────────┴──────────┴─────────┘
```

> **Explicación al profesor:**
> - Lee de tabla `procesos` en MySQL
> - Muestra solo procesos activos
> - Cada proceso tiene tipo y costo específico

---

#### **Paso 5: Solicitar Proceso (DATOS CORRECTOS)**

**Seleccionar → `2` (Solicitar Nuevo Proceso)**

**Elegir proceso: `1` (Informe Temp. Max/Min)**

**DATOS CORRECTOS:**
```
Parámetros para: Informe Temp. Max/Min

Ciudad (dejar vacío para todas): Buenos Aires
País (dejar vacío para todos): Argentina
Fecha inicio (YYYY-MM-DD): 2024-01-01
Fecha fin (YYYY-MM-DD): 2024-12-31

¿Confirmar solicitud? Costo: $150.00 (s/n): s
```

**Resultado esperado:**
```
✅ Solicitud creada exitosamente
ℹ️  ID de solicitud: 1
```

> **Explicación al profesor - Lo que pasa internamente:**
> 1. **MySQL**: INSERT en `solicitudes_proceso` (estado='pendiente')
> 2. **Redis**: Agrega ID a cola `cola:procesos_pendientes` con `lpush()`
> 3. El proceso queda en espera de ejecución por el administrador

**Verificar estado:**
```
Ver Mis Solicitudes → Ver Pendientes

┌────┬────────────────────┬──────────────┬───────────┬─────────┐
│ ID │ Proceso            │ Fecha        │ Estado    │ Costo   │
├────┼────────────────────┼──────────────┼───────────┼─────────┤
│ 1  │ Informe Temp...    │ 2025-01-15   │ pendiente │ $150.00 │
└────┴────────────────────┴──────────────┴───────────┴─────────┘
```

---

#### **Paso 6: Ejecutar Proceso (Como Administrador)**

**Cerrar sesión → Iniciar sesión como Admin**

```
Email: admin@sensores.com
Contraseña: admin123
```

**Seleccionar: `8` (Ejecutar Procesos Pendientes)**

**Resultado esperado:**
```
✅ Proceso ejecutado: Informe Temp. Max/Min
📊 Resultado:
   - Temperatura Máxima: 32.10°C
   - Temperatura Mínima: 18.50°C
   - Humedad Máxima: 85.00%
   - Humedad Mínima: 45.00%
   - Total Mediciones: 8760
```

> **Explicación al profesor - Flujo completo:**
> 1. **Redis**: `rpop()` saca solicitud_id de la cola
> 2. **MySQL**: UPDATE estado='en_proceso'
> 3. **MongoDB**: Ejecuta Aggregation Pipeline:
>    ```javascript
>    db.mediciones.aggregate([
>        {$match: {ciudad: "Buenos Aires", timestamp: {...}}},
>        {$group: {
>            temperatura_maxima: {$max: "$temperatura"},
>            temperatura_minima: {$min: "$temperatura"},
>            // ...
>        }}
>    ])
>    ```
> 4. **MongoDB**: Guarda resultado en `historial_ejecucion`
> 5. **MySQL**: UPDATE estado='completado'
> 6. **Facturación**: Genera factura automática (débito $150)

---

#### **Paso 7: Ver Resultado (Como Usuario Original)**

**Cerrar sesión Admin → Iniciar sesión como juan.perez@test.com**

**Ver Mis Solicitudes → Ver Completadas**

```
┌────┬────────────────────┬──────────────┬────────────┬─────────┐
│ ID │ Proceso            │ Fecha        │ Estado     │ Costo   │
├────┼────────────────────┼──────────────┼────────────┼─────────┤
│ 1  │ Informe Temp...    │ 2025-01-15   │ completado │ $150.00 │
└────┴────────────────────┴──────────────┴────────────┴─────────┘

Detalles del resultado:
🌡️  Temperatura Máxima: 32.10°C
🌡️  Temperatura Mínima: 18.50°C
💧 Humedad Máxima: 85.00%
💧 Humedad Mínima: 45.00%
📊 Total Mediciones analizadas: 8760
📅 Fecha ejecución: 2025-01-15 14:30:00
```

---

#### **Paso 8: Verificar Facturación**

**Menú Principal → `3` (Facturación) → `2` (Ver Mis Facturas)**

```
┌────┬────────────┬──────────┬───────────┬──────────────┬───────┐
│ ID │ Fecha      │ Monto    │ Estado    │ Vencimiento  │ Items │
├────┼────────────┼──────────┼───────────┼──────────────┼───────┤
│ 1  │ 2025-01-15 │ $150.00  │ pendiente │ 2025-02-14   │ 1     │
└────┴────────────┴──────────┴───────────┴──────────────┴───────┘

Resumen Financiero:
💰 Saldo actual: $350.00  (500 - 150)
📊 Total facturado: $150.00
⏳ Facturas pendientes: 1 ($150.00)
```

> **Explicación al profesor:**
> - Factura generada automáticamente al completar proceso
> - Débito registrado en cuenta_corriente
> - Vencimiento: 30 días automático

---

### **ESCENARIO 2: Validaciones con Datos Incorrectos** ❌

#### **Prueba 1: Email Duplicado al Registrar**

**Intentar registrar con email existente:**
```
Email: juan.perez@test.com  ← Ya existe
```

**Resultado esperado:**
```
❌ El email ya está registrado
```

> **Explicación:** Validación en MySQL con UNIQUE constraint

---

#### **Prueba 2: Contraseña Incorrecta al Login**

```
Email: juan.perez@test.com
Contraseña: incorrecta123  ← Incorrecta
```

**Resultado esperado:**
```
❌ Contraseña incorrecta
```

> **Explicación:** bcrypt.checkpw() falla la verificación

---

#### **Prueba 3: Formato de Fecha Inválido**

**Al solicitar proceso:**
```
Fecha inicio (YYYY-MM-DD): 15/01/2024  ← Formato incorrecto
```

**Resultado esperado:**
```
❌ Formato de fecha inválido. Use YYYY-MM-DD
```

---

#### **Prueba 4: Fecha Fin Menor que Fecha Inicio**

```
Fecha inicio: 2024-12-01
Fecha fin: 2024-01-01  ← Antes que inicio
```

**Resultado esperado:**
```
❌ La fecha fin debe ser posterior a la fecha inicio
```

---

#### **Prueba 5: Sin Saldo Suficiente**

**Si el saldo es $0 e intenta solicitar proceso de $150:**

**Resultado esperado:**
```
❌ Saldo insuficiente. Saldo actual: $0.00, Costo del proceso: $150.00
⚠️  Por favor, cargue saldo en su cuenta corriente
```

---

#### **Prueba 6: Cancelar Proceso Ya Ejecutado**

**Intentar cancelar solicitud con estado 'completado':**

**Resultado esperado:**
```
❌ Solo se pueden cancelar solicitudes pendientes
```

---

#### **Prueba 7: Parámetros Faltantes**

**Solicitar proceso sin completar todos los campos requeridos:**
```
Ciudad: [vacío]
Fecha inicio: [vacío]  ← Campo requerido
```

**Resultado esperado:**
```
❌ Faltan parámetros requeridos: fecha_inicio
```

---

## 🎭 Script de Demostración Sugerido

### **Para el Profesor - Secuencia Recomendada (10 minutos)**

1. **Mostrar Docker** (1 min)
   ```bash
   docker ps
   # Explicar las 3 bases de datos
   ```

2. **Ejecutar Programa** (1 min)
   ```bash
   python main.py
   # Mostrar menú principal
   ```

3. **Registro + Login** (2 min)
   - Registrar usuario nuevo
   - Mostrar que crea cuenta corriente automática
   - Login exitoso

4. **Cargar Saldo** (1 min)
   - Cargar $500
   - Mostrar movimiento en cuenta

5. **Solicitar Proceso** (2 min)
   - Ver procesos disponibles
   - Solicitar con datos correctos
   - Verificar que queda pendiente

6. **Ejecutar Como Admin** (2 min)
   - Login como admin
   - Ejecutar proceso pendiente
   - Mostrar resultado de agregación MongoDB

7. **Ver Resultado + Factura** (2 min)
   - Volver al usuario
   - Ver solicitud completada con resultado
   - Mostrar factura generada

8. **Probar Validaciones** (opcional, si hay tiempo)
   - Email duplicado
   - Contraseña incorrecta
   - Formato de fecha inválido

---

## 📊 Puntos Clave para Destacar al Profesor

### **Persistencia Políglota**
- ✅ **MySQL**: Datos transaccionales (usuarios, procesos, facturas)
- ✅ **MongoDB**: Big data (millones de mediciones, resultados)
- ✅ **Redis**: Sesiones temporales y cola de procesos

### **Arquitectura**
- 🏗️ **Separación de capas**: CLI → Services → DBs
- 🔐 **Seguridad**: bcrypt para passwords, sesiones con TTL
- 💰 **Facturación automática**: Stored Procedures para integridad

### **Flujo Completo**
1. Usuario solicita → MySQL + Redis (cola)
2. Admin ejecuta → Procesa MongoDB (Aggregation)
3. Resultado guardado → MongoDB (historial)
4. Factura generada → MySQL (automático)
5. Usuario ve resultado → Combina MySQL + MongoDB

### **Validaciones Implementadas**
- ✅ Email único
- ✅ Contraseñas hasheadas
- ✅ Formato de fechas
- ✅ Saldo suficiente
- ✅ Estados de solicitudes
- ✅ Permisos por rol

---

## 🚀 Comandos Útiles Durante la Demo

### Verificar Contenedores
```bash
docker ps
docker logs sensores_mysql
docker logs sensores_mongodb
docker logs sensores_redis
```

### Conectarse a las BDs Directamente (si el profesor pregunta)

**MySQL:**
```bash
mysql -h 127.0.0.1 -P 3307 -u admin -padmin123 sensores_db

# Ver usuarios
SELECT id, nombre_completo, email FROM usuarios;

# Ver solicitudes
SELECT id, estado, fecha_solicitud FROM solicitudes_proceso;
```

**MongoDB:**
```bash
mongosh mongodb://admin:admin123@localhost:27017

use sensores_db

# Ver resultado de ejecución
db.historial_ejecucion.find().pretty()

# Contar mediciones
db.mediciones.countDocuments()
```

**Redis:**
```bash
redis-cli -a redis123

# Ver sesiones activas
KEYS session:*

# Ver cola de procesos
LRANGE cola:procesos_pendientes 0 -1
```

---

## ✅ Checklist Pre-Demostración

- [ ] Docker containers corriendo (`docker ps`)
- [ ] Base de datos inicializadas (tablas creadas)
- [ ] Datos de prueba cargados (mediciones en MongoDB)
- [ ] Usuario admin existe (`admin@sensores.com / admin123`)
- [ ] Entorno virtual activado
- [ ] Programa ejecuta sin errores (`python main.py`)

---

## 🎯 Preguntas Frecuentes del Profesor

**P: ¿Por qué 3 bases de datos?**
R: Persistencia políglota - cada BD optimizada para su propósito:
- MySQL: Integridad transaccional
- MongoDB: Escalabilidad para big data
- Redis: Performance para sesiones

**P: ¿Cómo se garantiza la consistencia?**
R: 
- Transacciones en MySQL (ACID)
- IDs de referencia entre BDs
- Validaciones en capa de servicios
- Stored Procedures para operaciones críticas

**P: ¿Qué pasa si falla la ejecución?**
R: 
- Try-catch en cada nivel
- Rollback en MySQL si falla transacción
- Estado='error' si el proceso falla
- No se genera factura si hay error

**P: ¿Cómo escala el sistema?**
R:
- MongoDB: Sharding horizontal para mediciones
- Redis: Cluster para alta disponibilidad
- MySQL: Read replicas para consultas

---

¡Buena suerte con la demostración! 🚀
