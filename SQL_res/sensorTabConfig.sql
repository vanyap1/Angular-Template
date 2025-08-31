use ldb;

-- Таблиця пристроїв
CREATE TABLE devices (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    mac CHAR(17) NOT NULL,                      -- MAC-адреса
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
               ON UPDATE CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP NULL DEFAULT NULL,   -- останній контакт

    input_state  SMALLINT UNSIGNED NOT NULL DEFAULT 0,  -- 16 біт входи
    output_state SMALLINT UNSIGNED NOT NULL DEFAULT 0,  -- 16 біт виходи
    battery_voltage DECIMAL(4,2) DEFAULT NULL,  -- напруга, напр. 4.25
    name VARCHAR(32) NOT NULL,
    description VARCHAR(64) DEFAULT NULL,

    CONSTRAINT uq_devices_mac UNIQUE (mac)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Таблиця даних (по 8 каналів в одному рядку)
CREATE TABLE device_data (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    device_id INT UNSIGNED NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    channel1 DECIMAL(8,2) DEFAULT NULL,
    channel2 DECIMAL(8,2) DEFAULT NULL,
    channel3 DECIMAL(8,2) DEFAULT NULL,
    channel4 DECIMAL(8,2) DEFAULT NULL,
    channel5 DECIMAL(8,2) DEFAULT NULL,
    channel6 DECIMAL(8,2) DEFAULT NULL,
    channel7 DECIMAL(8,2) DEFAULT NULL,
    channel8 DECIMAL(8,2) DEFAULT NULL,

    CONSTRAINT fk_device_data_device
        FOREIGN KEY (device_id) REFERENCES devices(id)
        ON DELETE CASCADE,

    INDEX idx_device_time (device_id, recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


INSERT INTO devices (mac, created_at, updated_at, last_seen_at,
                     input_state, output_state, battery_voltage,
                     name, description)
VALUES
('AA:BB:CC:DD:EE:01', NOW(), NOW(), NOW(), 0, 0, 4.15, 'BoilerRoom-01', 'Модуль котельні'),
('AA:BB:CC:DD:EE:02', NOW(), NOW(), NOW(), 3, 1, 3.98, 'LivingRoom-01', 'Кімнатний датчик'),
('AA:BB:CC:DD:EE:03', NOW(), NOW(), NOW(), 0, 0, 4.22, 'Outdoor-01', 'Вуличний модуль');

-- Дані від BoilerRoom-01
INSERT INTO device_data (device_id, recorded_at, channel1, channel2, channel3)
VALUES
(1, NOW(), 23.45, 45.20, 1012.80),
(1, NOW(), 23.80, 44.90, 1013.00);

-- Дані від LivingRoom-01
INSERT INTO device_data (device_id, recorded_at, channel1, channel3)
VALUES
(2, NOW(), 22.10, 650.00),
(2, NOW(), 22.35, 670.00);

-- Дані від Outdoor-01
INSERT INTO device_data (device_id, recorded_at, channel1, channel4)
VALUES
(3, NOW(), 18.55, 1013.25),
(3, NOW(), 18.10, 1012.90);


-- якщо пристрою з таким MAC ще нема → створюємо
INSERT INTO devices (mac, created_at, updated_at, last_seen_at,
                     input_state, output_state, battery_voltage,
                     name, description)
VALUES
('AA:BB:CC:DD:EE:99', NOW(), NOW(), NOW(), 0, 0, 4.10, 'Auto-Device', 'створено автоматично')
ON DUPLICATE KEY UPDATE
    last_seen_at = VALUES(last_seen_at),
    battery_voltage = VALUES(battery_voltage),
    input_state = VALUES(input_state),
    output_state = VALUES(output_state),
    updated_at = NOW();
    
    
    
SELECT *
FROM devices;

SELECT *
FROM devices
WHERE id = 1;

SELECT dd.*
FROM device_data dd
WHERE dd.device_id = 1
  AND dd.recorded_at BETWEEN '2025-08-19 22:00:00' AND '2025-08-19 23:00:00'
ORDER BY dd.recorded_at;

SELECT dd.*
FROM device_data dd
JOIN devices d ON dd.device_id = d.id
WHERE d.mac = 'AA:BB:CC:DD:EE:01'
  AND dd.recorded_at BETWEEN '2025-08-01 00:00:00' AND '2025-08-20 23:59:59'
ORDER BY dd.recorded_at;

-- крок 1. створити/оновити сенсор
INSERT INTO devices (mac, last_seen_at, battery_voltage, input_state, output_state, name, description)
VALUES ('AA:BB:CC:DD:EE:99', NOW(), 4.05, 2, 1, 'Auto-Device', 'Автоматично створений')
ON DUPLICATE KEY UPDATE
    last_seen_at = VALUES(last_seen_at),
    battery_voltage = VALUES(battery_voltage),
    input_state = VALUES(input_state),
    output_state = VALUES(output_state),
    updated_at = NOW();

-- крок 2. вставити дані (використавши id знайденого/створеного сенсора)
INSERT INTO device_data (device_id, recorded_at, channel1, channel2, channel3, channel4)
VALUES (
    (SELECT id FROM devices WHERE mac = 'AA:BB:CC:DD:EE:99'),
    NOW(),
    23.45, 45.10, 1012.80, NULL
);

SELECT dd.*
FROM device_data dd
JOIN devices d ON dd.device_id = d.id
WHERE d.mac = 'AA:BB:CC:DD:EE:01'
ORDER BY dd.recorded_at DESC
LIMIT 1;

UPDATE devices
SET battery_voltage = 4.12,
    input_state = 5,
    output_state = 2,
    last_seen_at = NOW(),
    updated_at = NOW()
WHERE id = 2;

UPDATE devices
SET battery_voltage = 3.95,
    input_state = 1,
    output_state = 0,
    last_seen_at = NOW(),
    updated_at = NOW()
WHERE mac = 'AA:BB:CC:DD:EE:02';


CREATE TABLE devsMeasurementUnits (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    device_id INT UNSIGNED NOT NULL,
    channel_number TINYINT UNSIGNED NOT NULL, -- від 1 до 8
    unit VARCHAR(16) NOT NULL,                -- напр. "°C", "V", "A", "%"
    channel_name VARCHAR(32) DEFAULT NULL,    -- опціонально: "Температура", "Напруга" і т.д.

    CONSTRAINT fk_measurement_units_device
        FOREIGN KEY (device_id) REFERENCES devices(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_device_channel UNIQUE (device_id, channel_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Для пристрою 7 (id = 7)
INSERT INTO devsMeasurementUnits (device_id, channel_number, unit, channel_name) VALUES
(7, 1, '°C', 'Температура датчика 1'),
(7, 2, '°C', 'Температура датчика 2'),
(7, 3, '%', 'Вологість'),
(7, 4, 'V', 'Напруга живлення'),
(7, 5, '°C', 'Температура корпусу'),
(7, 6, '%', 'Вологість корпусу'),
(7, 7, 'V', 'Вхідна напруга'),
(7, 8, 'V', 'Вихідна напруга');

-- Для пристрою 8 (id = 8)
INSERT INTO devsMeasurementUnits (device_id, channel_number, unit, channel_name) VALUES
(8, 1, 'A', 'Струм фаза 1'),
(8, 2, 'A', 'Струм фаза 2'),
(8, 3, 'A', 'Струм фаза 3'),
(8, 4, 'V', 'Напруга L1-N'),
(8, 5, 'V', 'Напруга L2-N'),
(8, 6, 'V', 'Напруга L3-N'),
(8, 7, 'W', 'Потужність активна'),
(8, 8, 'W', 'Потужність реактивна');
