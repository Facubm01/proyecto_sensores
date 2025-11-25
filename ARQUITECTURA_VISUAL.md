# 📊 Resumen Visual - Arquitectura del Sistema

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO (CLI)                             │
│                      main.py                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  CAPA DE SERVICIOS                           │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ Auth     │ Proceso  │ Sensor   │ Factura  │ Ejecución│  │
│  │ Service  │ Service  │ Service  │ Service  │ Service  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│  MySQL   │    │ MongoDB  │    │  Redis   │
│  (3307)  │    │ (27017)  │    │  (6379)  │
└──────────┘    └──────────┘    └──────────┘
```

---

## 🗄️ Distribución de Datos - Persistencia Políglota

### MySQL - Datos Transaccionales y Relacionales
```
┌────────────────────────────────────────┐
│ MYSQL - Integridad y Transacciones     │
├────────────────────────────────────────┤
│                                        │
│ 📁 Usuarios                            │
│    └─ id, nombre, email, password_hash│
│                                        │
│ 🎭 Roles                               │
│    └─ usuarios_roles (N:N)            │
│                                        │
│ 📟 Sensores (Catálogo)                │
│    └─ id, código, ubicación, estado   │
│                                        │
│ ⚙️  Procesos                           │
│    └─ id, nombre, tipo, costo         │
│                                        │
│ 📋 Solicitudes                         │
│    └─ id, usuario_id, proceso_id      │
│       estado, parámetros              │
│                                        │
│ 💰 Facturación                         │
│    ├─ cuenta_corriente (saldo)        │
│    ├─ facturas                        │
│    ├─ items_factura                   │
│    ├─ pagos                           │
│    └─ movimientos_cuenta              │
│                                        │
└────────────────────────────────────────┘

POR QUÉ: 
✅ ACID transactions
✅ Integridad referencial
✅ Relaciones complejas
✅ Stored Procedures
```

### MongoDB - Big Data y Documentos
```
┌────────────────────────────────────────┐
│ MONGODB - Escalabilidad y Flexibilidad│
├────────────────────────────────────────┤
│                                        │
│ 📊 mediciones                          │
│    {                                   │
│      sensor_id: 1,                     │
│      temperatura: 25.5,                │
│      humedad: 68.3,                    │
│      timestamp: ISODate(...),          │
│      ciudad: "Buenos Aires"            │
│    }                                   │
│    👉 Millones de documentos           │
│                                        │
│ 📈 historial_ejecucion                │
│    {                                   │
│      solicitud_id: 42,                 │
│      resultado: {...},                 │
│      fecha_ejecucion: ISODate(...)     │
│    }                                   │
│                                        │
│ 🚨 alertas                             │
│    {                                   │
│      tipo: "climatica",                │
│      sensor_id: 1,                     │
│      descripcion: "Temp alta",         │
│      estado: "activa"                  │
│    }                                   │
│                                        │
│ 📧 mensajes                            │
│    └─ tipo: privado/grupal             │
│                                        │
└────────────────────────────────────────┘

POR QUÉ:
✅ Volumen masivo (time-series)
✅ Esquema flexible
✅ Aggregation Pipeline
✅ Escalabilidad horizontal
```

### Redis - Cache y Colas
```
┌────────────────────────────────────────┐
│ REDIS - Performance y Temporalidad    │
├────────────────────────────────────────┤
│                                        │
│ 🔐 session:{uuid}                      │
│    └─ {user_id, nombre, roles}        │
│    └─ TTL: 3600s (1 hora)             │
│                                        │
│ 📋 cola:procesos_pendientes            │
│    └─ [44, 43, 42] (FIFO)             │
│                                        │
└────────────────────────────────────────┘

POR QUÉ:
✅ Ultra rápido (RAM)
✅ TTL automático
✅ Estructuras de datos (listas, hashes)
✅ Pub/Sub para eventos
```

---

## 🔄 Flujo de un Proceso Completo

```
┌──────────────────────────────────────────────────────────────┐
│                   FLUJO COMPLETO                             │
└──────────────────────────────────────────────────────────────┘

1️⃣  USUARIO → Solicitar Proceso
    ┌────────────────────────────┐
    │ ProcesoService             │
    │ .solicitar_proceso()       │
    └──────┬─────────────────────┘
           │
           ├─→ MySQL: INSERT solicitudes (estado='pendiente')
           └─→ Redis: lpush("cola:procesos_pendientes", 42)

2️⃣  ADMIN → Ejecutar Proceso
    ┌────────────────────────────┐
    │ EjecucionService           │
    │ .ejecutar_proceso()        │
    └──────┬─────────────────────┘
           │
           ├─→ Redis: rpop() → obtiene solicitud_id
           ├─→ MySQL: UPDATE estado='en_proceso'
           ├─→ MongoDB: Aggregation Pipeline
           │           ├─ $match (filtrar)
           │           ├─ $group (agregar)
           │           └─ resultado = {...}
           ├─→ MongoDB: INSERT historial con resultado
           ├─→ MySQL: UPDATE estado='completado'
           └─→ FacturacionService.generar_factura()
               ├─ MySQL: INSERT facturas
               └─ MySQL: CALL registrar_movimiento()

3️⃣  USUARIO → Ver Resultado
    ┌────────────────────────────┐
    │ ProcesoService             │
    │ .listar_solicitudes()      │
    └──────┬─────────────────────┘
           │
           ├─→ MySQL: SELECT * FROM solicitudes
           └─→ MongoDB: find_one(historial_ejecucion)
               └─ Combina ambos resultados
```

---

## 🔐 Seguridad y Autenticación

```
┌──────────────────────────────────────────────────────────────┐
│              FLUJO DE AUTENTICACIÓN                          │
└──────────────────────────────────────────────────────────────┘

REGISTRO:
Usuario → main.py → AuthService.registrar_usuario()
          ↓
          ├─→ bcrypt.hashpw(password) → hash
          ├─→ MySQL: INSERT usuarios (password_hash)
          ├─→ MySQL: INSERT usuarios_roles
          └─→ MySQL: INSERT cuenta_corriente (saldo=0)

LOGIN:
Usuario → main.py → AuthService.login(email, password)
          ↓
          ├─→ MySQL: SELECT * FROM usuarios WHERE email=...
          ├─→ bcrypt.checkpw(password, hash) → ✅/❌
          ├─→ uuid.uuid4() → session_id
          ├─→ Redis: hset(session:{uuid}, user_data)
          └─→ Redis: expire(session:{uuid}, 3600)

VERIFICACIÓN (en cada operación):
main.py → AuthService.verificar_sesion(session_id)
          ↓
          ├─→ Redis: hgetall(session:{uuid})
          ├─→ Si existe → ✅ válida
          └─→ Redis: expire(session, 3600) → renueva TTL
```

---

## 💰 Sistema de Facturación

```
┌──────────────────────────────────────────────────────────────┐
│          FACTURACIÓN AUTOMÁTICA                              │
└──────────────────────────────────────────────────────────────┘

Al completar proceso:
┌─────────────────────────────────┐
│ FacturacionService              │
│ .generar_factura()              │
└────────┬────────────────────────┘
         │
         ├─→ MySQL: INSERT facturas
         │          (monto_total, fecha_vencimiento+30días)
         │
         ├─→ MySQL: INSERT items_factura
         │          (vincula solicitud con factura)
         │
         └─→ MySQL: CALL registrar_movimiento('debito', monto)
                    ├─ SELECT saldo FROM cuenta_corriente
                    ├─ saldo_nuevo = saldo - monto
                    ├─ UPDATE cuenta_corriente SET saldo
                    └─ INSERT movimientos_cuenta

STORED PROCEDURE: registrar_movimiento()
┌────────────────────────────────────────────┐
│ Ventajas:                                  │
│ ✅ Atomicidad (todo o nada)               │
│ ✅ Concurrencia (FOR UPDATE lock)         │
│ ✅ Consistencia (saldo siempre correcto)  │
│ ✅ Reutilizable (mismo SP para débito/crédito)│
└────────────────────────────────────────────┘
```

---

## 📊 Aggregation Pipeline de MongoDB

```
┌──────────────────────────────────────────────────────────────┐
│        EJEMPLO: Informe Temperatura Max/Min                  │
└──────────────────────────────────────────────────────────────┘

Entrada: Millones de mediciones
[
  {sensor_id: 1, temperatura: 25.5, timestamp: "2024-01-15", ciudad: "BA"},
  {sensor_id: 1, temperatura: 28.2, timestamp: "2024-01-16", ciudad: "BA"},
  {sensor_id: 2, temperatura: 22.0, timestamp: "2024-01-15", ciudad: "Córdoba"},
  ...
]

Pipeline:
┌─────────────────────────────────────────────────────┐
│ ETAPA 1: $match (filtrar)                          │
│ {                                                   │
│   ciudad: "Buenos Aires",                           │
│   timestamp: {$gte: "2024-01-01", $lte: "2024-12-31"}│
│ }                                                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ ETAPA 2: $group (agregar)                          │
│ {                                                   │
│   _id: null,                                        │
│   temperatura_maxima: {$max: "$temperatura"},      │
│   temperatura_minima: {$min: "$temperatura"},      │
│   humedad_maxima: {$max: "$humedad"},             │
│   humedad_minima: {$min: "$humedad"},             │
│   total_mediciones: {$sum: 1}                      │
│ }                                                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
Resultado:
{
  temperatura_maxima: 32.10,
  temperatura_minima: 18.50,
  humedad_maxima: 85.00,
  humedad_minima: 45.00,
  total_mediciones: 8760
}
```

---

## 🎯 Ventajas de la Arquitectura

### Persistencia Políglota
```
┌────────────────────────────────────────────────────┐
│ Problema         │ Solución        │ Base de Datos│
├──────────────────┼─────────────────┼──────────────┤
│ Transacciones    │ ACID garantizado│ MySQL        │
│ Integridad       │ Foreign Keys    │ MySQL        │
│ Big Data         │ Escalable       │ MongoDB      │
│ Análisis         │ Aggregation     │ MongoDB      │
│ Sesiones         │ TTL automático  │ Redis        │
│ Cola FIFO        │ Lists           │ Redis        │
└────────────────────────────────────────────────────┘
```

### Separación de Responsabilidades
```
┌────────────────────────────────────────────────────┐
│ Capa             │ Responsabilidad                │
├──────────────────┼────────────────────────────────┤
│ main.py          │ Interfaz usuario (CLI)         │
│ services/        │ Lógica de negocio              │
│ db_manager.py    │ Gestión de conexiones          │
│ MySQL/Mongo/Redis│ Persistencia                   │
└────────────────────────────────────────────────────┘
```

### Seguridad
```
✅ Passwords hasheados (bcrypt)
✅ Sesiones con expiración (Redis TTL)
✅ Control de acceso basado en roles (RBAC)
✅ Validaciones en múltiples capas
✅ SQL injection prevention (parámetros preparados)
✅ Transacciones ACID (MySQL)
```

---

## 📈 Escalabilidad

```
┌────────────────────────────────────────────────────┐
│ Componente   │ Estrategia de Escalabilidad        │
├──────────────┼────────────────────────────────────┤
│ MySQL        │ Read replicas                      │
│              │ Particionamiento por tabla         │
│              │                                    │
│ MongoDB      │ Sharding horizontal                │
│              │ Replicación (replica sets)         │
│              │ Time-series collections            │
│              │                                    │
│ Redis        │ Clustering                         │
│              │ Sentinel (alta disponibilidad)     │
│              │                                    │
│ Aplicación   │ Stateless (sesión en Redis)        │
│              │ Múltiples instancias               │
└────────────────────────────────────────────────────┘
```

---

## 🔍 Números del Sistema

```
┌────────────────────────────────────────────────────┐
│ Métrica                        │ Valor            │
├────────────────────────────────┼──────────────────┤
│ Bases de datos                 │ 3                │
│ Servicios (módulos)            │ 8                │
│ Tipos de procesos              │ 7                │
│ Roles de usuario               │ 3                │
│ TTL sesión (segundos)          │ 3600 (1 hora)    │
│ Vencimiento factura (días)     │ 30               │
│ Mediciones esperadas/año       │ ~50M (estimado)  │
└────────────────────────────────────────────────────┘
```

---

## 💡 Puntos para Destacar al Profesor

1. **Persistencia Políglota en Producción**
   - Cada BD hace lo que mejor sabe hacer
   - No es "usar 3 BDs porque sí", hay justificación técnica

2. **Arquitectura Real**
   - Patrón MVC/Service Layer
   - Stored Procedures para lógica crítica
   - Aggregation Pipeline para analytics

3. **Seguridad Industrial**
   - bcrypt con salt único por usuario
   - Sesiones con expiración automática
   - RBAC con verificación doble

4. **Manejo de Errores Robusto**
   - Try-catch en todos los niveles
   - Rollback automático en transacciones
   - Estados de error persistidos

5. **Escalabilidad Considerada**
   - Diseño stateless (sesión en Redis)
   - Sharding-ready (MongoDB)
   - FIFO queue (procesamiento async)

---

¡Este resumen te ayudará a explicar la arquitectura de manera clara y profesional! 🚀
