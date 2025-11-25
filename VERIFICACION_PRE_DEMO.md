# 🧪 Script de Verificación Rápida Pre-Demostración

## Ejecutar ANTES de mostrar al profesor

### 1. Verificar Docker
```bash
# Ver contenedores activos
docker ps

# Deberías ver 3 contenedores:
# - sensores_mysql (puerto 3307)
# - sensores_mongodb (puerto 27017)  
# - sensores_redis (puerto 6379)

# Si no están corriendo:
docker-compose up -d
```

### 2. Verificar MySQL - Datos Base

```bash
mysql -h 127.0.0.1 -P 3307 -u admin -padmin123 sensores_db
```

```sql
-- Verificar que existan procesos
SELECT id, nombre, tipo, costo FROM procesos LIMIT 5;

-- Debería ver procesos como:
-- 1 | Informe Temp. Max/Min | informe_max_min | 150.00

-- Verificar que exista usuario admin
SELECT id, nombre_completo, email FROM usuarios WHERE email = 'admin@sensores.com';

-- Verificar sensores
SELECT id, nombre, ciudad, estado FROM sensores LIMIT 5;

-- Si no hay datos, revisar que se ejecutó init_mysql.sql
```

### 3. Verificar MongoDB - Mediciones

```bash
mongosh mongodb://admin:admin123@localhost:27017
```

```javascript
use sensores_db

// Contar mediciones
db.mediciones.countDocuments()
// Debería haber al menos algunas mediciones

// Ver una medición de ejemplo
db.mediciones.findOne()
// Debería ver estructura: {sensor_id, temperatura, humedad, timestamp, ciudad, pais}

// Ver distribución por ciudad
db.mediciones.aggregate([
    {$group: {_id: "$ciudad", total: {$sum: 1}}},
    {$sort: {total: -1}},
    {$limit: 5}
])
```

### 4. Verificar Redis

```bash
redis-cli -a redis123
```

```redis
# Ver todas las keys (debería estar vacío o con pocas sesiones)
KEYS *

# Ver cola de procesos pendientes
LRANGE cola:procesos_pendientes 0 -1

# Limpiar cola si hay datos viejos (opcional)
DEL cola:procesos_pendientes
```

### 5. Test Rápido del Programa

```bash
cd /Users/facundobustamante/proyecto_sensores
source venv/bin/activate
python main.py
```

**Flujo de prueba rápida (3 minutos):**

1. **Seleccionar**: `1` (Login)
   - Email: `admin@sensores.com`
   - Password: `admin123`
   - ✅ Debería entrar exitosamente

2. **Ver que el menú de admin tenga más opciones**
   - Debería verse opciones 1-11 y 99
   - Opciones 8-11 son solo para admin

3. **Seleccionar**: `99` (Cerrar sesión)
   - ✅ Debería volver al menú principal

4. **Ctrl+C** para salir

---

## 📝 Crear Usuario de Prueba Fresco

Si quieres empezar limpio para la demo:

```sql
-- En MySQL
-- Eliminar usuario de prueba anterior (si existe)
DELETE FROM movimientos_cuenta WHERE cuenta_id IN (SELECT id FROM cuenta_corriente WHERE usuario_id IN (SELECT id FROM usuarios WHERE email LIKE '%test.com'));
DELETE FROM usuarios_roles WHERE usuario_id IN (SELECT id FROM usuarios WHERE email LIKE '%test.com');
DELETE FROM cuenta_corriente WHERE usuario_id IN (SELECT id FROM usuarios WHERE email LIKE '%test.com');
DELETE FROM solicitudes_proceso WHERE usuario_id IN (SELECT id FROM usuarios WHERE email LIKE '%test.com');
DELETE FROM usuarios WHERE email LIKE '%test.com';
```

---

## 🎯 Datos Recomendados para la Demo

### Usuario de Prueba
- **Nombre**: Juan Perez
- **Email**: juan.perez@demo.com
- **Password**: demo123

### Proceso a Solicitar
- **Tipo**: Informe Temp. Max/Min (ID: 1)
- **Ciudad**: Buenos Aires
- **País**: Argentina
- **Fecha inicio**: 2024-01-01
- **Fecha fin**: 2024-12-31

### Saldo Inicial
- **Monto**: 500.00

---

## ⚠️ Problemas Comunes y Soluciones

### Error: "Connection refused" al conectar MySQL
```bash
# Verificar que el contenedor esté corriendo
docker ps | grep mysql

# Si no está, iniciarlo
docker-compose up -d mysql

# Esperar 10 segundos para que inicialice
sleep 10
```

### Error: "No module named 'pymongo'"
```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Error: "No hay procesos disponibles"
```bash
# Conectar a MySQL
mysql -h 127.0.0.1 -P 3307 -u admin -padmin123 sensores_db

# Insertar proceso de ejemplo
INSERT INTO procesos (nombre, descripcion, tipo, costo, activo) 
VALUES 
('Informe Temp. Max/Min', 'Análisis de temperaturas máximas y mínimas', 'informe_max_min', 150.00, TRUE);
```

### Error: "No se encontraron mediciones"
```javascript
// En MongoDB, insertar mediciones de ejemplo
use sensores_db

db.mediciones.insertMany([
    {
        sensor_id: 1,
        temperatura: 25.5,
        humedad: 68.3,
        timestamp: new Date("2024-01-15T10:00:00Z"),
        ciudad: "Buenos Aires",
        pais: "Argentina"
    },
    {
        sensor_id: 1,
        temperatura: 28.2,
        humedad: 72.1,
        timestamp: new Date("2024-06-20T14:00:00Z"),
        ciudad: "Buenos Aires",
        pais: "Argentina"
    },
    {
        sensor_id: 1,
        temperatura: 32.1,
        humedad: 55.8,
        timestamp: new Date("2024-12-10T16:00:00Z"),
        ciudad: "Buenos Aires",
        pais: "Argentina"
    }
])
```

---

## ✅ Checklist Final Pre-Demo

- [ ] Docker containers corriendo (3/3)
- [ ] MySQL responde en puerto 3307
- [ ] MongoDB responde en puerto 27017
- [ ] Redis responde en puerto 6379
- [ ] Tabla `procesos` tiene datos
- [ ] Usuario `admin@sensores.com` existe
- [ ] Colección `mediciones` tiene documentos
- [ ] Programa ejecuta sin errores
- [ ] Usuario de prueba NO existe (para registrar en vivo)
- [ ] Guía de demostración abierta en otra ventana

---

## 🎬 Orden de Demostración Recomendado

1. **Mostrar Docker** → `docker ps`
2. **Mostrar estructura** → `ls -la`
3. **Ejecutar programa** → `python main.py`
4. **Registro** → Crear usuario en vivo
5. **Login** → Entrar con usuario nuevo
6. **Cargar saldo** → $500
7. **Ver procesos** → Mostrar catálogo
8. **Solicitar** → Con datos correctos
9. **Logout + Login admin** → Cambiar usuario
10. **Ejecutar** → Procesar de la cola
11. **Logout + Login user** → Volver al usuario
12. **Ver resultado** → Mostrar datos procesados
13. **Ver factura** → Mostrar facturación automática
14. **Probar validación** → 1-2 ejemplos de error

**Tiempo total**: 8-10 minutos

---

## 💬 Explicaciones Clave al Profesor

### Al registrar usuario:
> "El sistema usa bcrypt para hashear la contraseña y crea automáticamente una cuenta corriente con saldo $0"

### Al hacer login:
> "La sesión se almacena en Redis con un TTL de 1 hora y se renueva con cada actividad"

### Al solicitar proceso:
> "Se guarda en MySQL con estado 'pendiente' y se agrega a una cola FIFO en Redis"

### Al ejecutar proceso:
> "Se saca de Redis, se procesa MongoDB con Aggregation Pipeline, se guarda resultado y se factura automáticamente"

### Al ver resultado:
> "Los datos básicos vienen de MySQL y el resultado detallado de MongoDB - persistencia políglota en acción"

---

¡Todo listo para la demo! 🚀
