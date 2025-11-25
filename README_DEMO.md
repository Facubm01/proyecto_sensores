# 📚 Índice de Documentación para la Demostración

## 🎯 Propósito
Esta carpeta contiene **toda la documentación** necesaria para demostrar el Sistema de Gestión de Sensores al profesor.

---

## 📁 Documentos Disponibles

### 1. **GUIA_DEMOSTRACION.md** 📖
**Para:** Seguir durante la demostración en vivo

**Contiene:**
- Flujo completo paso a paso (usuario + admin)
- Datos correctos e incorrectos
- Script de 10 minutos sugerido
- Comandos útiles
- Preguntas frecuentes del profesor

**Cuándo usar:** ABIERTO durante la demo como referencia

---

### 2. **VERIFICACION_PRE_DEMO.md** ✅
**Para:** Verificar que todo funcione ANTES de mostrar

**Contiene:**
- Checklist de verificación
- Comandos para probar MySQL/MongoDB/Redis
- Test rápido del programa (3 min)
- Troubleshooting de problemas comunes
- Cómo limpiar datos de pruebas anteriores

**Cuándo usar:** 30 minutos ANTES de la demostración

---

### 3. **ARQUITECTURA_VISUAL.md** 🏗️
**Para:** Explicar el diseño del sistema

**Contiene:**
- Diagramas ASCII de la arquitectura
- Distribución de datos (MySQL/MongoDB/Redis)
- Flujo de un proceso completo
- Sistema de autenticación
- Sistema de facturación
- Aggregation Pipeline explicado
- Ventajas de persistencia políglota

**Cuándo usar:** Si el profesor pregunta por la arquitectura

---

### 4. **CASOS_PRUEBA.md** 🧪
**Para:** Casos de prueba específicos con detalles técnicos

**Contiene:**
- 7 casos exitosos (datos correctos)
- 10 casos de error (validaciones)
- Entrada/Salida esperada para cada caso
- Explicaciones técnicas detalladas
- Queries SQL/MongoDB para verificar

**Cuándo usar:** Durante la demo para saber exactamente qué probar

---

### 5. **guia_estudio.md** 📚
**Para:** Estudiar el código en profundidad

**Contiene:**
- Resumen completo del proyecto
- Arquitectura de persistencia políglota
- Modelo de datos de las 3 BDs
- Explicación de cada módulo
- Flujos de uso completos
- Preguntas de repaso
- Consejos de estudio

**Cuándo usar:** Para prepararte ANTES de la evaluación

---

## 🚀 Plan de Acción

### 📅 Un Día Antes
1. ✅ Leer **guia_estudio.md** completa
2. ✅ Revisar **ARQUITECTURA_VISUAL.md**
3. ✅ Practicar explicación de persistencia políglota

### ⏰ 30 Minutos Antes
1. ✅ Ejecutar **VERIFICACION_PRE_DEMO.md**
2. ✅ Verificar que Docker esté corriendo
3. ✅ Hacer test rápido del programa
4. ✅ Abrir **GUIA_DEMOSTRACION.md** en otra ventana

### 🎬 Durante la Demo
1. ✅ Seguir **GUIA_DEMOSTRACION.md** paso a paso
2. ✅ Usar **CASOS_PRUEBA.md** para detalles técnicos
3. ✅ Si pregunta arquitectura → **ARQUITECTURA_VISUAL.md**

---

## 🎯 Flujo de Demostración Recomendado (10 minutos)

### Minutos 0-2: Introducción
```bash
# Mostrar Docker
docker ps

# Mostrar estructura del proyecto  
ls -la
```

Explicar brevemente:
- 3 bases de datos (persistencia políglota)
- Arquitectura de servicios
- CLI con menús dinámicos

---

### Minutos 2-4: Registro y Login
```
1. Registrar usuario nuevo
2. Login exitoso
3. Mostrar menú dinámico según rol
```

**Punto clave:** Explicar bcrypt + sesiones en Redis

---

### Minutos 4-6: Solicitar Proceso
```
1. Cargar saldo ($500)
2. Ver procesos disponibles
3. Solicitar proceso con datos correctos
4. Verificar que queda pendiente
```

**Punto clave:** Explicar cola FIFO en Redis

---

### Minutos 6-8: Ejecutar Proceso (Admin)
```
1. Logout → Login como admin
2. Ejecutar proceso pendiente
3. Mostrar resultado de aggregation
```

**Punto clave:** Explicar:
- Aggregation Pipeline de MongoDB
- Procesamiento de millones de mediciones
- Facturación automática

---

### Minutos 8-9: Ver Resultado
```
1. Logout → Login como usuario
2. Ver solicitud completada
3. Ver resultado detallado
4. Ver factura generada
```

**Punto clave:** Integración MySQL + MongoDB

---

### Minutos 9-10: Validaciones
```
1. Email duplicado (error)
2. Contraseña incorrecta (error)
3. Formato de fecha (error)
```

**Punto clave:** Validaciones en múltiples capas

---

## 💡 Respuestas a Preguntas Típicas

### "¿Por qué 3 bases de datos?"

**Respuesta:**
> "Persistencia políglota - cada BD optimizada para su propósito:
> - **MySQL**: Transacciones ACID para datos críticos (usuarios, facturas)
> - **MongoDB**: Escalabilidad para millones de mediciones (time-series)
> - **Redis**: Performance para sesiones temporales y cola de procesos"

---

### "¿Cómo garantizan la consistencia?"

**Respuesta:**
> "Múltiples mecanismos:
> - Transacciones ACID en MySQL con rollback automático
> - Stored Procedures para operaciones críticas
> - IDs de referencia entre bases de datos
> - Validaciones en capa de servicios
> - Estados de error persistidos si algo falla"

---

### "¿Qué pasa si falla la ejecución?"

**Respuesta:**
> "Manejo robusto de errores:
> - Try-catch en todos los niveles
> - Estado se marca como 'error' en MySQL
> - NO se genera factura si hay error
> - Usuario ve mensaje descriptivo
> - Admin puede reintentar o investigar"

---

### "¿Cómo escala el sistema?"

**Respuesta:**
> "Diseño preparado para escalar:
> - **MongoDB**: Sharding horizontal para mediciones
> - **MySQL**: Read replicas para consultas
> - **Redis**: Cluster para alta disponibilidad
> - **Aplicación**: Stateless (sesión en Redis) → múltiples instancias"

---

## 🎓 Conceptos Clave a Mencionar

### Durante Registro/Login:
- ✅ bcrypt con salt automático
- ✅ Sesiones con TTL en Redis
- ✅ UUID único por sesión

### Durante Solicitud:
- ✅ Cola FIFO en Redis (lpush/rpop)
- ✅ Parámetros JSON en MySQL
- ✅ Estados del proceso

### Durante Ejecución:
- ✅ Aggregation Pipeline ($match, $group)
- ✅ Procesamiento de big data
- ✅ Stored Procedures

### Durante Facturación:
- ✅ Generación automática
- ✅ Transacciones ACID
- ✅ Débito/Crédito en cuenta

---

## 📊 Datos Técnicos del Sistema

```
┌─────────────────────────────────────────────┐
│ Métricas del Sistema                        │
├─────────────────────────────────────────────┤
│ Bases de datos:           3                 │
│ Módulos de servicios:     8                 │
│ Tipos de procesos:        7                 │
│ Roles de usuario:         3                 │
│ TTL de sesión:            3600s (1h)        │
│ Vencimiento factura:      30 días           │
│ Algoritmo hash:           bcrypt            │
│ Session ID:               UUID v4           │
│ Cola:                     FIFO (Redis List) │
│ Aggregation:              MongoDB Pipeline  │
└─────────────────────────────────────────────┘
```

---

## ✅ Checklist Final

Antes de la demo, verificar:

- [ ] Docker containers corriendo (3/3)
- [ ] MySQL accesible (puerto 3307)
- [ ] MongoDB accesible (puerto 27017)
- [ ] Redis accesible (puerto 6379)
- [ ] Tabla `procesos` tiene datos
- [ ] Usuario admin existe
- [ ] Colección `mediciones` tiene datos
- [ ] Programa ejecuta sin errores
- [ ] Documentos abiertos:
  - [ ] GUIA_DEMOSTRACION.md
  - [ ] CASOS_PRUEBA.md
- [ ] Terminal listo en directorio del proyecto
- [ ] Entorno virtual activado

---

## 🎬 Comando para Iniciar

```bash
cd /Users/facundobustamante/proyecto_sensores
source venv/bin/activate
python main.py
```

---

## 📞 Si Algo Sale Mal

### Restart completo:
```bash
# Parar todo
docker-compose down

# Limpiar volúmenes (CUIDADO: borra datos)
docker-compose down -v

# Iniciar de nuevo
docker-compose up -d

# Esperar 30 segundos
sleep 30

# Verificar
docker ps
python main.py
```

---

¡Todo listo para una demostración exitosa! 🚀🎯

**Recuerda:**
- Habla con confianza
- Explica el "por qué" de las decisiones
- Muestra errores también (demuestra robustez)
- Usa ejemplos concretos de big data
- Menciona escalabilidad

¡Mucha suerte! 💪
