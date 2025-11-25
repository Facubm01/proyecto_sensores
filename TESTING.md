# Guía de Testing - Sistema de Gestión de Sensores

## 🎯 Objetivo
Esta guía te ayudará a testear todas las funcionalidades del sistema de manera sistemática.

---

## 📋 Credenciales de Prueba

### Usuario Administrador (acceso completo)
```
Email: admin@sensores.com
Contraseña: admin123
Roles: administrador (incluye permisos de técnico)
```

### Usuario Técnico
```
Email: tecnico@sensores.com
Contraseña: tecnico123
Roles: tecnico
```

### Usuario Regular
```
Email: usuario@sensores.com
Contraseña: usuario123
Roles: usuario
```

---

## ✅ Plan de Testing por Módulo

### 1️⃣ Autenticación (Todos los usuarios)

#### Login
- [  ] Iniciar sesión con credenciales correctas
- [  ] Intentar login con credenciales incorrectas
- [  ] Verificar que muestra el nombre y rol del usuario

#### Registro
- [  ] Registrar un nuevo usuario
- [  ] Intentar registrar con email duplicado
- [  ] Verificar que contraseñas coincidan

#### Logout
- [  ] Cerrar sesión correctamente
- [  ] Verificar que regresa al menú principal

---

### 2️⃣ Gestión de Procesos (Usuario Regular)

Login como: `usuario@sensores.com` / `usuario123`

#### Ver Procesos Disponibles
- [  ] Listar todos los procesos del catálogo
- [  ] Ver detalles de un proceso específico
- [  ] Verificar que muestra: ID, nombre, tipo, costo, descripción

#### Solicitar Proceso
- [  ] Seleccionar un proceso de tipo "informe"
- [  ] Completar parámetros (ciudad, país, fechas)
- [  ] Confirmar solicitud
- [  ] Verificar que muestra ID de solicitud

#### Ver Mis Solicitudes
- [  ] Ver todas las solicitudes
- [  ] Filtrar por estado: pendiente
- [  ] Filtrar por estado: completado
- [  ] Verificar resumen de contadores

#### Cancelar Solicitud
- [  ] Cancelar una solicitud pendiente
- [  ] Verificar que cambia de estado

---

### 3️⃣ Facturación y Cuenta Corriente (Usuario Regular)

Login como: `usuario@sensores.com` / `usuario123`

#### Cuenta Corriente
- [  ] Ver saldo actual
- [  ] Ver movimientos de la cuenta
- [  ] Verificar formato de débitos (-$) y créditos (+$)

#### Facturas
- [  ] Listar todas las facturas
- [  ] Ver detalle completo de una factura
- [  ] Verificar items de la factura

#### Pagos
- [  ] Ver facturas pendientes
- [  ] Registrar pago de factura
- [  ] Seleccionar método de pago (tarjeta/transferencia/efectivo)
- [  ] Verificar que actualiza estado

#### Cargar Saldo
- [  ] Cargar saldo a la cuenta
- [  ] Verificar que se refleja en el saldo actual

---

### 4️⃣ Mensajería (Usuario Regular)

Login como: `usuario@sensores.com` / `usuario123`

#### Mensajes Privados
- [  ] Ver mensajes recibidos
- [  ] Ver mensajes enviados
- [  ] Enviar mensaje privado a otro usuario
- [  ] Verificar contador de mensajes no leídos

#### Grupos
- [  ] Ver mis grupos
- [  ] Crear un nuevo grupo
- [  ] Enviar mensaje a grupo
- [  ] Agregar miembro a grupo

---

### 5️⃣ Gestión de Sensores (Técnico/Admin)

Login como: `tecnico@sensores.com` / `tecnico123` o `admin@sensores.com` / `admin123`

#### Listar Sensores
- [  ] Ver todos los sensores
- [  ] Filtrar por estado (activo/inactivo/falla)
- [  ] Filtrar por país
- [  ] Verificar resumen de contadores

#### Detalles de Sensor
- [  ] Ver información completa de un sensor
- [  ] Ver últimas mediciones del sensor
- [  ] Verificar datos de ubicación

#### Registrar Sensor (Solo Admin)
- [  ] Crear nuevo sensor
- [  ] Completar: código, nombre, ciudad, país, descripción
- [  ] Verificar que se crea correctamente

#### Cambiar Estado (Solo Admin)
- [  ] Cambiar estado de un sensor
- [  ] Verificar que actualiza correctamente

---

### 6️⃣ Alertas (Técnico/Admin)

Login como: `tecnico@sensores.com` / `tecnico123` o `admin@sensores.com` / `admin123`

#### Listar Alertas
- [  ] Ver todas las alertas
- [  ] Filtrar por estado (activa/resuelta)
- [  ] Verificar información: tipo, sensor, fecha, descripción

#### Crear Alerta
- [  ] Crear alerta manualmente
- [  ] Seleccionar sensor y tipo
- [  ] Agregar descripción

#### Resolver Alerta
- [  ] Marcar alerta como resuelta
- [  ] Agregar observaciones de resolución
- [  ] Verificar cambio de estado

---

### 7️⃣ Control de Funcionamiento (Técnico/Admin)

Login como: `tecnico@sensores.com` / `tecnico123` o `admin@sensores.com` / `admin123`

#### Ver Controles
- [  ] Ver todos los controles registrados
- [  ] Ver controles de un sensor específico
- [  ] Verificar estadísticas

#### Registrar Control
- [  ] Registrar nuevo control de funcionamiento
- [  ] Seleccionar sensor
- [  ] Indicar estado (activo/inactivo/falla)
- [  ] Agregar observaciones
- [  ] Opcionalmente actualizar estado del sensor

---

### 8️⃣ Ejecutar Procesos Pendientes (Solo Admin)

Login como: `admin@sensores.com` / `admin123`

#### Ejecución Individual
- [  ] Ver procesos en cola
- [  ] Ejecutar un proceso específico
- [  ] Verificar resultado de ejecución

#### Ejecución Masiva
- [  ] Ejecutar todos los procesos pendientes
- [  ] Verificar contador de procesados/errores

---

### 9️⃣ Gestión de Usuarios (Solo Admin)

Login como: `admin@sensores.com` / `admin123`

- [  ] Acceder al menú (actualmente placeholder)
- [  ] Verificar mensaje de "funcionalidad en desarrollo"

---

### 🔟 Ver Sesiones Activas (Solo Admin)

Login como: `admin@sensores.com` / `admin123`

- [  ] Ver sesiones activas en Redis
- [  ] Verificar información: email, nombre, roles, tiempo activo
- [  ] Comprobar expiración de sesiones

---

### 1️⃣1️⃣ Reportes del Sistema (Solo Admin)

Login como: `admin@sensores.com` / `admin123`

#### Resumen General
- [  ] Ver estadísticas generales del sistema
- [  ] Verificar contadores de: usuarios, sensores, mediciones, procesos, facturas

#### Reporte de Sensores
- [  ] Ver estadísticas por país
- [  ] Ver estadísticas por estado
- [  ] Verificar totales

#### Reporte de Mediciones
- [  ] Ver estadísticas de mediciones
- [  ] Verificar promedios de temperatura y humedad
- [  ] Ver distribución por ciudad

#### Reporte de Procesos
- [  ] Ver estadísticas de solicitudes
- [  ] Ver por tipo de proceso
- [  ] Ver por estado

#### Reporte de Facturación
- [  ] Ver totales facturados
- [  ] Ver facturas pendientes vs pagadas
- [  ] Ver distribución de montos

#### Reporte de Usuarios
- [  ] Ver estadísticas de usuarios
- [  ] Ver distribución por rol
- [  ] Ver usuarios activos

---

## 🚀 Orden de Testing Recomendado

### Fase 1: Flujo Básico (30 min)
1. Autenticación (login/logout)
2. Procesos (solicitar un proceso)
3. Facturación (ver cuenta, facturas)
4. Mensajería (enviar mensaje)

### Fase 2: Funcionalidades Técnicas (30 min)
1. Sensores (listar, ver detalles)
2. Alertas (crear, resolver)
3. Control (registrar)

### Fase 3: Funcionalidades Admin (30 min)
1. Ejecutar procesos pendientes
2. Ver sesiones activas
3. Reportes del sistema (todos)

### Fase 4: Testing Exhaustivo (1-2 horas)
- Completar todos los checkboxes anteriores
- Probar casos de error
- Verificar validaciones

---

## 🐛 Casos de Error a Probar

### Validaciones de Input
- [  ] Dejar campos vacíos en formularios
- [  ] Ingresar IDs inexistentes
- [  ] Ingresar tipos de datos incorrectos

### Permisos
- [  ] Intentar acceder a opciones de admin con usuario regular
- [  ] Intentar acceder a opciones de técnico con usuario regular

### Estados
- [  ] Cancelar solicitud ya completada
- [  ] Pagar factura ya pagada
- [  ] Resolver alerta ya resuelta

---

## 📝 Checklist de Verificación Final

- [  ] Todas las funcionalidades listadas funcionan
- [  ] No hay errores de Python en consola
- [  ] Los menús se ven correctamente
- [  ] La navegación (volver, salir) funciona
- [  ] Los datos se persisten correctamente
- [  ] Las 3 bases de datos se usan apropiadamente:
  - MySQL: datos relacionales (usuarios, sensores, procesos, facturas)
  - MongoDB: datos no estructurados (mediciones, mensajes, alertas)
  - Redis: sesiones y cola de procesos

---

## 💡 Tips de Testing

1. **Usa diferentes usuarios** para probar permisos
2. **Anota los IDs** al crear entidades para referenciarlas después
3. **Prueba el flujo completo**: solicitar proceso → ver factura → pagar → ejecutar proceso
4. **Revisa las bases de datos** directamente para verificar persistencia
5. **Prueba casos extremos**: fechas inválidas, montos negativos, etc.

---

## 🔧 Comandos Útiles

```bash
# Ejecutar aplicación
python main.py

# Verificar bases de datos
docker ps  # Ver contenedores activos

# MySQL
docker exec -it [container_id] mysql -u root -p

# MongoDB
docker exec -it [container_id] mongosh

# Redis
docker exec -it [container_id] redis-cli
```

---

## ✅ Testing Completado

Una vez completados todos los checks, puedes estar seguro de que:
- ✅ El sistema está completamente funcional
- ✅ La modularización no rompió ninguna funcionalidad
- ✅ Todas las bases de datos funcionan correctamente
- ✅ Los permisos por rol funcionan como esperado
