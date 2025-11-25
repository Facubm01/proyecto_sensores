# 🎯 Resumen Ejecutivo - Sistema de Gestión de Sensores

## ¿Qué hace el sistema?

Gestiona **sensores de temperatura/humedad** ubicados en diferentes ciudades del mundo y permite a usuarios solicitar **reportes y análisis** sobre los datos recolectados. Incluye facturación automática por cada servicio.

---

## 🗄️ Persistencia Políglota - 3 Bases de Datos

### **MySQL** - Datos Transaccionales
**¿Por qué?** Necesitamos integridad ACID y relaciones

**Almacena:**
- Usuarios, roles y permisos
- Catálogo de sensores (ubicación, estado)
- Catálogo de procesos (servicios disponibles)
- Solicitudes de procesos (estados)
- **Facturación completa** (facturas, pagos, cuenta corriente)

### **MongoDB** - Big Data
**¿Por qué?** Millones de mediciones, necesitamos escalabilidad

**Almacena:**
- **Mediciones** de sensores (temperatura/humedad) - 7,200+ documentos
- Resultados de procesos ejecutados
- Alertas climáticas y de sensores
- Mensajes entre usuarios

### **Redis** - Performance
**¿Por qué?** Velocidad y expiración automática

**Almacena:**
- Sesiones de usuario (con TTL de 1 hora)
- Cola FIFO de procesos pendientes

---

## 🔄 Flujo Completo (Ejemplo)

1. **Usuario se registra** → MySQL (bcrypt hashea password)
2. **Login** → Redis (crea sesión con TTL)
3. **Carga saldo** → MySQL (Stored Procedure actualiza cuenta)
4. **Solicita "Informe Temp. Max/Min"** → MySQL (INSERT solicitud) + Redis (agrega a cola)
5. **Admin ejecuta proceso** → MongoDB (Aggregation Pipeline procesa 7,200 mediciones)
6. **Sistema guarda resultado** → MongoDB (historial) + MySQL (estado='completado')
7. **Factura automática** → MySQL (genera factura, descuenta saldo)
8. **Usuario ve resultado** → Combina datos de MySQL + MongoDB

---

## 🎯 Tecnologías Clave

- **bcrypt**: Passwords hasheados con salt
- **Redis TTL**: Sesiones expiran automáticamente
- **Aggregation Pipeline**: Procesa millones de documentos (MongoDB)
- **Stored Procedures**: Integridad en cuenta corriente (MySQL)
- **RBAC**: Control de acceso por roles (cliente/técnico/admin)
- **Cola FIFO**: Procesamiento asíncrono (Redis)

---

## 📊 Números del Sistema

- **10 sensores** en 5 países
- **7,200 mediciones** de prueba (30 días)
- **7 tipos de procesos** disponibles
- **3 roles** de usuario
- **3 bases de datos** integradas

---

## 💡 Puntos Fuertes

1. **Persistencia políglota real** - Cada BD hace lo que mejor sabe
2. **Escalable** - MongoDB puede manejar millones de mediciones
3. **Seguro** - bcrypt, sesiones con TTL, RBAC completo
4. **Automatizado** - Facturación al completar procesos
5. **Robusto** - Transacciones ACID, manejo de errores, rollback

---

## 🎬 Para la Demo

**Mostrar:**
1. Registro + Login → bcrypt + Redis
2. Solicitar proceso → Cola en Redis
3. Ejecutar proceso → Aggregation Pipeline (MongoDB)
4. Ver resultado → Integración MySQL + MongoDB
5. Factura generada → Stored Procedure (MySQL)

**Tiempo:** 8-10 minutos
