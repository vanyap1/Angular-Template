use ldb;



CREATE TABLE Batteries (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    batId CHAR(16) UNIQUE NOT NULL,
    description VARCHAR(256),
    batCapacity INT
);

CREATE TABLE BatteryData (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    batteryId BIGINT UNSIGNED NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    current DECIMAL(6,2),
    voltage DECIMAL(6,2),
    capacity INT,
    power DECIMAL(8,2),
    energy INT,
    FOREIGN KEY (batteryId) REFERENCES Batteries(id) ON DELETE CASCADE
);

INSERT INTO Batteries (batId, description, batCapacity) VALUES
('BAT000000000001', 'LiFePO4 12V 100Ah', 100),
('BAT000000000002', 'AGM 12V 65Ah', 65),
('BAT000000000003', 'NMC 24V 200Ah', 200);

INSERT INTO BatteryData (batteryId, timestamp, current, voltage, capacity, power, energy) VALUES
(1, '2025-06-09 08:00:00', 12.30, 13.50, 98, 166.05, 120),
(1, '2025-06-09 10:00:00', 11.80, 13.40, 96, 158.12, 145),
(1, '2025-06-09 12:00:00', 10.50, 13.20, 92, 138.60, 180);

-- Для батареї №2
INSERT INTO BatteryData (batteryId, timestamp, current, voltage, capacity, power, energy) VALUES
(2, '2025-06-09 09:00:00', 8.00, 12.60, 60, 100.80, 85),
(2, '2025-06-09 11:00:00', 7.50, 12.50, 58, 93.75, 105),
(2, '2025-06-09 13:00:00', 6.80, 12.40, 55, 84.32, 122);

-- Для батареї №3
INSERT INTO BatteryData (batteryId, current, voltage, capacity, power, energy) VALUES
(3, 20.50, 25.60, 190, 524.80, 210),
(3, 19.00, 25.20, 185, 478.80, 280),
(3, 17.30, 25.00, 180, 432.50, 350);

SELECT bd.*
FROM BatteryData bd
JOIN Batteries b ON bd.batteryId = b.id
WHERE b.batId = 'BAT000000000001'
  AND bd.timestamp >= NOW() - INTERVAL 1 DAY
ORDER BY bd.timestamp;

SELECT *
FROM BatteryData
WHERE batteryId = 3
  AND timestamp >= NOW() - INTERVAL 1 DAY
ORDER BY timestamp;

SELECT 
    bd.*,
    b.batId,
    b.description,
    b.batCapacity
FROM BatteryData bd
JOIN Batteries b ON bd.batteryId = b.id
WHERE bd.batteryId = 3
  AND bd.timestamp >= NOW() - INTERVAL 1 DAY
ORDER BY bd.timestamp;

SELECT * FROM Batteries where id = 1;
