# 📊 Datos de Prueba del Sistema

## 🎯 Resumen

Los datos de prueba se cargan automáticamente al inicializar las bases de datos usando:
- **MySQL**: `config/init_mysql.sql` (se ejecuta automáticamente con Docker)
- **MongoDB**: `config/init_mongodb.py` (script Python para ejecutar manualmente)

---

## 📍 SENSORES REGISTRADOS

### Total: **10 sensores** distribuidos en 5 países

```
┌────┬────────────────────────┬─────────────────┬──────────────┬────────────┐
│ ID │ Nombre                 │ Código          │ Ciudad       │ País       │
├────┼────────────────────────┼─────────────────┼──────────────┼────────────┤
│ 1  │ Sensor Centro BA       │ BA-CENTRO-001   │ Buenos Aires │ Argentina  │
│ 2  │ Sensor Palermo         │ BA-PALERMO-001  │ Buenos Aires │ Argentina  │
│ 3  │ Sensor Recoleta        │ BA-RECOLETA-001 │ Buenos Aires │ Argentina  │
│ 4  │ Sensor Córdoba Centro  │ CBA-CENTRO-001  │ Córdoba      │ Argentina  │
│ 5  │ Sensor Rosario Centro  │ ROS-CENTRO-001  │ Rosario      │ Argentina  │
│ 6  │ Sensor Mendoza Centro  │ MDZ-CENTRO-001  │ Mendoza      │ Argentina  │
│ 7  │ Sensor Santiago Centro │ SCL-CENTRO-001  │ Santiago     │ Chile      │
│ 8  │ Sensor São Paulo       │ SP-CENTRO-001   │ São Paulo    │ Brasil     │
│ 9  │ Sensor Montevideo      │ MVD-CENTRO-001  │ Montevideo   │ Uruguay    │
│ 10 │ Sensor Lima Centro     │ LIM-CENTRO-001  │ Lima         │ Perú       │
└────┴────────────────────────┴─────────────────┴──────────────┴────────────┘
```

**Ubicación en código:** `config/init_mysql.sql` - líneas 194-204

**Características:**
- Todos los sensores miden **temperatura y humedad** (tipo: 'ambos')
- Todos están en estado **'activo'**
- Tienen coordenadas geográficas reales (latitud/longitud)

---

## 📊 MEDICIONES GENERADAS

### Volumen de Datos

**Script:** `config/init_mongodb.py` - función `cargar_mediciones_ejemplo()`

**Cálculo:**
```
10 sensores × 24 mediciones/día × 30 días = 7,200 mediciones
```

**Características:**
- **Periodo**: Últimos 30 días desde la fecha de ejecución
- **Frecuencia**: 1 medición por hora por sensor
- **Datos**: Temperatura y humedad simuladas de forma realista

**Temperaturas base por ciudad:**
```python
Buenos Aires: 22°C (±5°C variación)
Córdoba:      24°C (±5°C variación)
Rosario:      23°C (±5°C variación)
Mendoza:      20°C (±5°C variación)
Santiago:     18°C (±5°C variación)
São Paulo:    25°C (±5°C variación)
Montevideo:   21°C (±5°C variación)
Lima:         23°C (±5°C variación)
```

**Variación por hora del día:**
- **Día (6:00-18:00)**: Temperatura base + variación de -3°C a +5°C
- **Noche (19:00-5:00)**: Temperatura base + variación de -5°C a +2°C

**Humedad:** Aleatoria entre 40% y 85%

**Estructura de cada medición:**
```javascript
{
    sensor_id: 1,
    ciudad: "Buenos Aires",
    pais: "Argentina",
    timestamp: ISODate("2024-12-25T14:00:00Z"),
    temperatura: 25.3,
    humedad: 68.5
}
```

---

## 👥 USUARIOS PRECARGADOS

### Usuario Administrador

```
Nombre: Administrador Sistema
Email:  admin@sensores.com
Password: admin123
Rol:    administrador
Saldo:  $10,000.00
```

**Ubicación:** `config/init_mysql.sql` - líneas 174-181

**Permisos:**
- ✅ Todas las funcionalidades del sistema
- ✅ Ejecutar procesos pendientes
- ✅ Gestión de usuarios
- ✅ Ver sesiones activas
- ✅ Reportes del sistema

---

## ⚙️ PROCESOS DISPONIBLES

### Total: **7 tipos de procesos**

```
┌────┬────────────────────────────────┬─────────────────────────┬─────────┐
│ ID │ Nombre                         │ Tipo                    │ Costo   │
├────┼────────────────────────────────┼─────────────────────────┼─────────┤
│ 1  │ Informe Temp. Máximas/Mínimas │ informe_max_min         │ $50.00  │
│ 2  │ Informe Temp. Promedio        │ informe_promedio        │ $75.00  │
│ 3  │ Informe Humedad Max/Min       │ informe_humedad_max_min │ $50.00  │
│ 4  │ Informe Humedad Promedio      │ informe_humedad_promedio│ $75.00  │
│ 5  │ Generación de Alertas         │ alertas_rango           │ $100.00 │
│ 6  │ Consulta en Línea             │ consulta_online         │ $30.00  │
│ 7  │ Proceso Periódico Mensual     │ proceso_periodico_...   │ $200.00 │
└────┴────────────────────────────────┴─────────────────────────┴─────────┘
```

**Ubicación:** `config/init_mysql.sql` - líneas 184-191

---

## ⚠️ ALERTAS DE EJEMPLO

### Total: **3 alertas**

```javascript
// Alerta 1: Sensor sin reportar (resuelta)
{
    tipo: 'sensor',
    sensor_id: 3,
    timestamp: hace 2 días,
    descripcion: 'Sensor BA-RECOLETA-001 sin reportar mediciones por 2 horas',
    estado: 'resuelta'
}

// Alerta 2: Temperatura alta (activa)
{
    tipo: 'climatica',
    sensor_id: 8,
    timestamp: hace 1 día,
    descripcion: 'Temperatura superior a 35°C en São Paulo',
    estado: 'activa'
}

// Alerta 3: Humedad alta (activa)
{
    tipo: 'climatica',
    sensor_id: 10,
    timestamp: hace 6 horas,
    descripcion: 'Humedad superior a 90% en Lima',
    estado: 'activa'
}
```

**Ubicación:** `config/init_mongodb.py` - líneas 183-212

---

## 💬 MENSAJES DE EJEMPLO

### Total: **2 mensajes grupales**

```javascript
// Mensaje 1: Mantenimiento programado
{
    remitente_id: 1,  // Admin
    grupo_id: 1,      // Grupo "Técnicos de Mantenimiento"
    timestamp: hace 12 horas,
    contenido: 'Recordatorio: mantenimiento programado de sensores en Buenos Aires este fin de semana',
    tipo: 'grupal'
}

// Mensaje 2: Alerta de sensor
{
    remitente_id: 1,  // Admin
    grupo_id: 1,
    timestamp: hace 3 horas,
    contenido: 'Sensor SP-CENTRO-001 reportando temperaturas anormales. Favor revisar.',
    tipo: 'grupal'
}
```

**Ubicación:** `config/init_mongodb.py` - líneas 214-238

---

## 🔧 CONTROLES DE FUNCIONAMIENTO

### Total: **3 registros de control**

```javascript
// Control Sensor 1
{
    sensor_id: 1,
    fecha_revision: hace 7 días,
    estado: 'activo',
    observaciones: 'Funcionamiento normal. Batería al 92%. Señal estable.'
}

// Control Sensor 2
{
    sensor_id: 2,
    fecha_revision: hace 7 días,
    estado: 'activo',
    observaciones: 'Funcionamiento normal. Batería al 88%. Señal estable.'
}

// Control Sensor 3
{
    sensor_id: 3,
    fecha_revision: hace 2 días,
    estado: 'activo',
    observaciones: 'Sensor reiniciado tras interrupción. Ahora funcionando correctamente.'
}
```

**Ubicación:** `config/init_mongodb.py` - líneas 240-266

---

## 👥 GRUPOS DE MENSAJERÍA

### Total: **1 grupo**

```
ID:          1
Nombre:      Técnicos de Mantenimiento
Descripción: Grupo para coordinación de técnicos de campo
```

**Ubicación:** `config/init_mysql.sql` - líneas 206-208

---

## 🗄️ ÍNDICES CREADOS EN MONGODB

Para optimizar las consultas, se crean los siguientes índices:

### Colección: mediciones
```
1. idx_sensor_timestamp:  (sensor_id ASC, timestamp DESC)
2. idx_ciudad_timestamp:  (ciudad ASC, timestamp DESC)
3. idx_pais_timestamp:    (pais ASC, timestamp DESC)
```

### Colección: alertas
```
1. idx_estado_timestamp:  (estado ASC, timestamp DESC)
2. idx_sensor_alerta:     (sensor_id ASC, timestamp DESC)
```

### Colección: mensajes
```
1. idx_destinatario_timestamp: (destinatario_id ASC, timestamp DESC)
2. idx_remitente_timestamp:    (remitente_id ASC, timestamp DESC)
3. idx_grupo:                  (grupo_id ASC)
```

### Colección: historial_ejecucion
```
1. idx_solicitud:         (solicitud_id ASC) - UNIQUE
2. idx_fecha_ejecucion:   (fecha_ejecucion DESC)
```

### Colección: control_funcionamiento
```
1. idx_sensor_revision:   (sensor_id ASC, fecha_revision DESC)
```

**Ubicación:** `config/init_mongodb.py` - líneas 51-124

---

## 🚀 Cómo Cargar los Datos

### 1. MySQL (Automático con Docker)

Los datos de MySQL se cargan **automáticamente** al iniciar el contenedor:

```bash
docker-compose up -d mysql
```

El archivo `init_mysql.sql` se ejecuta automáticamente la primera vez.

### 2. MongoDB (Manual)

Para cargar datos en MongoDB, ejecuta el script Python:

```bash
cd /Users/facundobustamante/proyecto_sensores
source venv/bin/activate
python config/init_mongodb.py
```

**Interacción:**
```
¿Deseas cargar datos de ejemplo? (s/n): s
```

**Resultado:**
```
✓ 7,200 mediciones insertadas
✓ 3 alertas insertadas
✓ 2 mensajes insertados
✓ 3 controles insertados
```

---

## 📊 Estadísticas Finales

Después de cargar todos los datos:

```
┌────────────────────────────────────┬──────────────┐
│ Colección                          │ Documentos   │
├────────────────────────────────────┼──────────────┤
│ mediciones                         │ 7,200        │
│ alertas                            │ 3            │
│ mensajes                           │ 2            │
│ historial_ejecucion                │ 0 (inicial)  │
│ control_funcionamiento             │ 3            │
└────────────────────────────────────┴──────────────┘
```

---

## 🔍 Verificar Datos Cargados

### MySQL

```bash
mysql -h 127.0.0.1 -P 3307 -u admin -padmin123 sensores_db
```

```sql
-- Ver sensores
SELECT id, nombre, ciudad, pais, estado FROM sensores;

-- Ver procesos
SELECT id, nombre, tipo, costo FROM procesos;

-- Ver usuario admin
SELECT * FROM usuarios WHERE email = 'admin@sensores.com';
```

### MongoDB

```bash
mongosh mongodb://admin:admin123@localhost:27017
```

```javascript
use sensores_db

// Contar mediciones
db.mediciones.countDocuments()
// Resultado: 7200

// Ver una medición
db.mediciones.findOne()

// Mediciones por ciudad
db.mediciones.aggregate([
    {$group: {_id: "$ciudad", total: {$sum: 1}}},
    {$sort: {total: -1}}
])

// Ver alertas activas
db.alertas.find({estado: "activa"})
```

---

## 💡 Datos Útiles para la Demo

### Para Solicitar un Proceso

**Datos correctos:**
```
Proceso: Informe Temp. Max/Min (ID: 1)
Ciudad: Buenos Aires
País: Argentina
Fecha inicio: 2024-11-01
Fecha fin: 2024-11-30
```

**Resultado esperado:**
- Procesará ~720 mediciones (30 días × 24 horas × 1 sensor)
- Mostrará temperatura máxima y mínima del periodo
- Generará factura de $50.00

### Para Probar Consulta Online

```
Proceso: Consulta en Línea (ID: 6)
Zona: Buenos Aires
```

**Resultado esperado:**
- Mostrará 3 sensores de Buenos Aires (IDs: 1, 2, 3)
- Última medición de cada uno
- Costo: $30.00

---

## 🎯 Resumen

**Total de datos de prueba:**
- ✅ 10 sensores en 5 países
- ✅ 7,200 mediciones (30 días de datos)
- ✅ 7 tipos de procesos disponibles
- ✅ 1 usuario administrador
- ✅ 3 alertas de ejemplo
- ✅ 2 mensajes grupales
- ✅ 3 controles de funcionamiento
- ✅ 1 grupo de mensajería

**Suficiente para demostrar:**
- ✅ Aggregation Pipeline con volumen real
- ✅ Consultas por ciudad/país/fecha
- ✅ Sistema de alertas
- ✅ Mensajería
- ✅ Control de sensores
- ✅ Facturación completa

---

¡Todo listo para una demostración completa! 🚀
