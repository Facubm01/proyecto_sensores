#!/bin/bash
# Script para corregir el encoding UTF-8 en MySQL

echo "🔧 Corrigiendo encoding UTF-8 en MySQL..."

# Conectar a MySQL y actualizar los datos
mysql -h 127.0.0.1 -P 3307 -u admin -padmin123 sensores_db << 'EOF'

-- Configurar charset para la sesión
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Actualizar nombres de ciudades y países con tildes correctas
UPDATE sensores SET ciudad = 'Córdoba' WHERE ciudad = 'Córdoba' OR ciudad LIKE '%rdoba%';
UPDATE sensores SET ciudad = 'São Paulo' WHERE ciudad = 'São Paulo' OR ciudad LIKE '%o Paulo%';
UPDATE sensores SET pais = 'Perú' WHERE pais = 'Perú' OR pais LIKE 'Per%';

-- Verificar cambios
SELECT id, nombre, ciudad, pais FROM sensores ORDER BY pais, ciudad;

EOF

echo "✅ Encoding corregido"
echo ""
echo "Ciudades y países actualizados:"
echo "  • Córdoba (con tilde)"
echo "  • São Paulo (con tilde)"
echo "  • Perú (con tilde)"
