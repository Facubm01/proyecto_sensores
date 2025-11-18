-- ============================================
-- SCHEMA MYSQL - DATOS TRANSACCIONALES
-- ============================================

USE sensores_db;

-- Tabla: Usuarios
CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_estado (estado)
) ENGINE=InnoDB;

-- Tabla: Roles
CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    descripcion ENUM('usuario', 'tecnico', 'administrador') UNIQUE NOT NULL
) ENGINE=InnoDB;

-- Tabla: Usuarios_Roles (relación muchos a muchos)
CREATE TABLE usuarios_roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    rol_id INT NOT NULL,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_usuario_rol (usuario_id, rol_id)
) ENGINE=InnoDB;

-- Tabla: Sensores (metadata)
CREATE TABLE sensores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    tipo ENUM('temperatura', 'humedad', 'ambos') DEFAULT 'ambos',
    latitud DECIMAL(10, 8) NOT NULL,
    longitud DECIMAL(11, 8) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    pais VARCHAR(100) NOT NULL,
    estado ENUM('activo', 'inactivo', 'falla') DEFAULT 'activo',
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ciudad (ciudad),
    INDEX idx_pais (pais),
    INDEX idx_estado (estado)
) ENGINE=InnoDB;

-- Tabla: Grupos (para mensajería)
CREATE TABLE grupos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tabla: Grupos_Miembros
CREATE TABLE grupos_miembros (
    id INT PRIMARY KEY AUTO_INCREMENT,
    grupo_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE KEY unique_grupo_usuario (grupo_id, usuario_id)
) ENGINE=InnoDB;

-- Tabla: Procesos (catálogo de servicios)
CREATE TABLE procesos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL,
    costo DECIMAL(10, 2) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    INDEX idx_tipo (tipo),
    INDEX idx_activo (activo)
) ENGINE=InnoDB;

-- Tabla: Solicitudes de Proceso
CREATE TABLE solicitudes_proceso (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    proceso_id INT NOT NULL,
    parametros JSON,
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('pendiente', 'en_proceso', 'completado', 'error') DEFAULT 'pendiente',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (proceso_id) REFERENCES procesos(id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha (fecha_solicitud)
) ENGINE=InnoDB;

-- Tabla: Facturas
CREATE TABLE facturas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    monto_total DECIMAL(10, 2) NOT NULL,
    estado ENUM('pendiente', 'pagada', 'vencida') DEFAULT 'pendiente',
    fecha_vencimiento DATE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario (usuario_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha_emision (fecha_emision)
) ENGINE=InnoDB;

-- Tabla: Detalle de Facturas
CREATE TABLE facturas_detalle (
    id INT PRIMARY KEY AUTO_INCREMENT,
    factura_id INT NOT NULL,
    solicitud_id INT NOT NULL,
    concepto VARCHAR(255) NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE,
    FOREIGN KEY (solicitud_id) REFERENCES solicitudes_proceso(id)
) ENGINE=InnoDB;

-- Tabla: Pagos
CREATE TABLE pagos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    factura_id INT NOT NULL,
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    monto DECIMAL(10, 2) NOT NULL,
    metodo VARCHAR(50) NOT NULL,
    referencia VARCHAR(100),
    FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE,
    INDEX idx_factura (factura_id),
    INDEX idx_fecha (fecha_pago)
) ENGINE=InnoDB;

-- Tabla: Cuenta Corriente
CREATE TABLE cuenta_corriente (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT UNIQUE NOT NULL,
    saldo DECIMAL(10, 2) DEFAULT 0.00,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabla: Movimientos de Cuenta Corriente
CREATE TABLE movimientos_cuenta (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cuenta_id INT NOT NULL,
    tipo ENUM('debito', 'credito') NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    concepto VARCHAR(255) NOT NULL,
    referencia_id INT,
    saldo_anterior DECIMAL(10, 2) NOT NULL,
    saldo_nuevo DECIMAL(10, 2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cuenta_id) REFERENCES cuenta_corriente(id) ON DELETE CASCADE,
    INDEX idx_cuenta (cuenta_id),
    INDEX idx_fecha (fecha)
) ENGINE=InnoDB;

-- ============================================
-- DATOS INICIALES
-- ============================================

-- Insertar roles
INSERT INTO roles (descripcion) VALUES 
    ('usuario'),
    ('tecnico'),
    ('administrador');

-- Insertar usuario administrador
-- Password: admin123 (hashed con bcrypt)
INSERT INTO usuarios (nombre_completo, email, password_hash, estado) VALUES
    ('Administrador Sistema', 'admin@sensores.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oi2xF1A7aUiG', 'activo');

-- Asignar rol administrador
INSERT INTO usuarios_roles (usuario_id, rol_id) VALUES (1, 3);

-- Crear cuenta corriente para admin
INSERT INTO cuenta_corriente (usuario_id, saldo) VALUES (1, 10000.00);

-- Insertar procesos disponibles
INSERT INTO procesos (nombre, descripcion, tipo, costo) VALUES
    ('Informe Temperaturas Máximas/Mínimas', 'Reporte de temperaturas máximas y mínimas por ciudad/país en rango de fechas', 'informe_max_min', 50.00),
    ('Informe Temperaturas Promedio', 'Reporte de temperaturas promedio por ciudad/país mensualizadas o anualizadas', 'informe_promedio', 75.00),
    ('Informe Humedad Máximas/Mínimas', 'Reporte de humedad máxima y mínima por ciudad/país en rango de fechas', 'informe_humedad_max_min', 50.00),
    ('Informe Humedad Promedio', 'Reporte de humedad promedio por ciudad/país mensualizadas o anualizadas', 'informe_humedad_promedio', 75.00),
    ('Generación de Alertas', 'Genera alertas para temperaturas/humedad fuera de rango en zona específica', 'alertas_rango', 100.00),
    ('Consulta en Línea', 'Servicio de consulta en tiempo real de sensores por zona', 'consulta_online', 30.00),
    ('Proceso Periódico Mensual', 'Reporte automático mensual de temperaturas/humedad por zona', 'proceso_periodico_mensual', 200.00);

-- Insertar sensores de ejemplo
INSERT INTO sensores (nombre, codigo, tipo, latitud, longitud, ciudad, pais, estado) VALUES
    ('Sensor Centro Buenos Aires', 'BA-CENTRO-001', 'ambos', -34.60368440, -58.38156300, 'Buenos Aires', 'Argentina', 'activo'),
    ('Sensor Palermo', 'BA-PALERMO-001', 'ambos', -34.57771800, -58.43178800, 'Buenos Aires', 'Argentina', 'activo'),
    ('Sensor Recoleta', 'BA-RECOLETA-001', 'ambos', -34.58822200, -58.39270600, 'Buenos Aires', 'Argentina', 'activo'),
    ('Sensor Cordoba Centro', 'CBA-CENTRO-001', 'ambos', -31.41668900, -64.18333300, 'Córdoba', 'Argentina', 'activo'),
    ('Sensor Rosario Centro', 'ROS-CENTRO-001', 'ambos', -32.94682000, -60.63932000, 'Rosario', 'Argentina', 'activo'),
    ('Sensor Mendoza Centro', 'MDZ-CENTRO-001', 'ambos', -32.88946000, -68.84583000, 'Mendoza', 'Argentina', 'activo'),
    ('Sensor Santiago Centro', 'SCL-CENTRO-001', 'ambos', -33.44889900, -70.66931200, 'Santiago', 'Chile', 'activo'),
    ('Sensor São Paulo Centro', 'SP-CENTRO-001', 'ambos', -23.55052100, -46.63330900, 'São Paulo', 'Brasil', 'activo'),
    ('Sensor Montevideo Centro', 'MVD-CENTRO-001', 'ambos', -34.90328300, -56.18816300, 'Montevideo', 'Uruguay', 'activo'),
    ('Sensor Lima Centro', 'LIM-CENTRO-001', 'ambos', -12.04637400, -77.04279700, 'Lima', 'Perú', 'activo');

-- Crear grupo de técnicos
INSERT INTO grupos (nombre, descripcion) VALUES
    ('Técnicos de Mantenimiento', 'Grupo para coordinación de técnicos de campo');

-- ============================================
-- PROCEDURES Y TRIGGERS
-- ============================================

DELIMITER $$

-- Procedure: Registrar movimiento en cuenta corriente
CREATE PROCEDURE registrar_movimiento(
    IN p_cuenta_id INT,
    IN p_tipo ENUM('debito', 'credito'),
    IN p_monto DECIMAL(10, 2),
    IN p_concepto VARCHAR(255),
    IN p_referencia_id INT
)
BEGIN
    DECLARE v_saldo_anterior DECIMAL(10, 2);
    DECLARE v_saldo_nuevo DECIMAL(10, 2);
    
    -- Obtener saldo actual
    SELECT saldo INTO v_saldo_anterior
    FROM cuenta_corriente
    WHERE id = p_cuenta_id;
    
    -- Calcular nuevo saldo
    IF p_tipo = 'debito' THEN
        SET v_saldo_nuevo = v_saldo_anterior - p_monto;
    ELSE
        SET v_saldo_nuevo = v_saldo_anterior + p_monto;
    END IF;
    
    -- Actualizar saldo
    UPDATE cuenta_corriente
    SET saldo = v_saldo_nuevo
    WHERE id = p_cuenta_id;
    
    -- Registrar movimiento
    INSERT INTO movimientos_cuenta (cuenta_id, tipo, monto, concepto, referencia_id, saldo_anterior, saldo_nuevo)
    VALUES (p_cuenta_id, p_tipo, p_monto, p_concepto, p_referencia_id, v_saldo_anterior, v_saldo_nuevo);
END$$

DELIMITER ;

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista: Solicitudes con detalles
CREATE VIEW v_solicitudes_detalle AS
SELECT 
    s.id,
    s.fecha_solicitud,
    s.estado,
    u.nombre_completo AS usuario,
    u.email,
    p.nombre AS proceso,
    p.tipo,
    p.costo,
    s.parametros
FROM solicitudes_proceso s
JOIN usuarios u ON s.usuario_id = u.id
JOIN procesos p ON s.proceso_id = p.id;

-- Vista: Facturas con detalles
CREATE VIEW v_facturas_detalle AS
SELECT 
    f.id,
    f.fecha_emision,
    f.monto_total,
    f.estado,
    f.fecha_vencimiento,
    u.nombre_completo AS usuario,
    u.email,
    COUNT(fd.id) AS cantidad_items
FROM facturas f
JOIN usuarios u ON f.usuario_id = u.id
LEFT JOIN facturas_detalle fd ON f.id = fd.factura_id
GROUP BY f.id, f.fecha_emision, f.monto_total, f.estado, f.fecha_vencimiento, u.nombre_completo, u.email;

-- Vista: Estado de sensores por país
CREATE VIEW v_sensores_por_pais AS
SELECT 
    pais,
    COUNT(*) AS total_sensores,
    SUM(CASE WHEN estado = 'activo' THEN 1 ELSE 0 END) AS activos,
    SUM(CASE WHEN estado = 'inactivo' THEN 1 ELSE 0 END) AS inactivos,
    SUM(CASE WHEN estado = 'falla' THEN 1 ELSE 0 END) AS con_falla
FROM sensores
GROUP BY pais;

COMMIT;
