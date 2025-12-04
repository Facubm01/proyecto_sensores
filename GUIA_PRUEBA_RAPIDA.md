# 🚀 Guía Rápida para Probar el Programa

## ✅ Estado Actual

- ✅ Docker Desktop corriendo
- ✅ Contenedores iniciados (MySQL, MongoDB, Redis)
- ✅ Dependencias instaladas
- ✅ Programa listo para ejecutar

---

## 📋 Pasos para Probar

### 1. **Abrir una Terminal/PowerShell**

Abre PowerShell o CMD en el directorio del proyecto:
```powershell
cd C:\Users\Levy\Desktop\proyecto_sensores
```

### 2. **Verificar que los contenedores estén corriendo**

```powershell
docker ps
```

Deberías ver 3 contenedores:
- `sensores_mysql`
- `sensores_mongodb`
- `sensores_redis`

Si no están corriendo:
```powershell
docker-compose up -d
```

### 3. **Ejecutar el programa**

```powershell
python main.py
```

---

## 🎯 Qué Probar

### **Funcionalidades Nuevas Implementadas:**

1. **Dashboard** (Opción 1 en menú principal)
   - Ver estadísticas del usuario
   - Gráficos de solicitudes
   - Estadísticas financieras

2. **Notificaciones** (Opción 6 en menú principal)
   - Ver notificaciones cuando se complete un proceso
   - Contador de no leídas en el menú

3. **Exportar Resultados**
   - Ver detalle de una solicitud completada
   - Opción "Exportar resultado (JSON)" o "Exportar resultado (CSV)"
   - Archivos se guardan en `exports/`

4. **Visualización de Datos**
   - Ver detalle de solicitud completada
   - Opción "Visualizar gráfico"
   - Gráficos ASCII en la terminal

5. **Sistema de Logging**
   - Los logs se guardan automáticamente en `logs/`
   - Un archivo por día: `sistema_YYYYMMDD.log`

---

## 🔍 Flujo de Prueba Recomendado

### **Paso 1: Registro/Login**
1. Registrar un nuevo usuario
2. O iniciar sesión si ya tienes uno

### **Paso 2: Explorar Dashboard**
1. Menú principal → Opción 1 (Dashboard)
2. Ver estadísticas generales
3. Explorar diferentes secciones

### **Paso 3: Solicitar un Proceso**
1. Menú principal → Opción 2 (Gestión de Procesos)
2. Solicitar nuevo proceso
3. Elegir un proceso disponible
4. Completar parámetros

### **Paso 4: Ejecutar Proceso (como Admin)**
1. Cerrar sesión
2. Iniciar sesión como administrador
3. Menú principal → Opción 9 (Ejecutar Procesos Pendientes)
4. Ejecutar el proceso pendiente

### **Paso 5: Ver Notificación**
1. Cerrar sesión como admin
2. Iniciar sesión como usuario normal
3. Verás que hay notificaciones (contador en menú)
4. Menú principal → Opción 6 (Notificaciones)
5. Ver la notificación del proceso completado

### **Paso 6: Exportar y Visualizar**
1. Menú principal → Opción 3 (Ver Mis Solicitudes)
2. Ver solicitudes completadas
3. Ver detalle de una solicitud
4. Probar exportar (JSON/CSV)
5. Probar visualización de gráficos

---

## 📁 Archivos Generados

Durante el uso, se crearán automáticamente:

- `exports/` - Archivos exportados (JSON/CSV)
- `logs/` - Logs del sistema

---

## ⚠️ Notas Importantes

1. **Encoding en Windows**: El programa ahora maneja UTF-8 correctamente
2. **Primera ejecución**: Puede tardar un poco en inicializar las bases de datos
3. **Datos de prueba**: Si no hay datos, algunas funciones mostrarán mensajes informativos

---

## 🐛 Si Algo No Funciona

### **Error de conexión a bases de datos:**
```powershell
# Verificar contenedores
docker ps

# Reiniciar contenedores
docker-compose restart
```

### **Error de encoding:**
- El programa ya está configurado para UTF-8
- Si persiste, ejecuta: `chcp 65001` antes de `python main.py`

### **Dependencias faltantes:**
```powershell
pip install -r requirements.txt
```

---

## 🎉 ¡Listo para Probar!

Ejecuta `python main.py` y explora todas las nuevas funcionalidades implementadas.


