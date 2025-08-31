use ldb;

CREATE TABLE water_heater_schedule (
    id TINYINT UNSIGNED PRIMARY KEY,          -- 0 = всі дні, 1=Пн, ... 7=Нд
    day_name VARCHAR(16) NOT NULL,            -- Назва дня тижня
    start_time TIME NOT NULL,                 -- Час старту
    stop_time TIME NOT NULL,                  -- Час стопу
    enabled BOOLEAN NOT NULL DEFAULT 1,       -- Чи активний графік
    last_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
                                             ON UPDATE CURRENT_TIMESTAMP, -- Час останнього редагування
    modified_by VARCHAR(32) NOT NULL DEFAULT 'system', -- Хто редагував
    comment VARCHAR(128) DEFAULT NULL         -- Коментар
);


-- Глобальний графік (всі дні)
INSERT INTO water_heater_schedule 
(id, day_name, start_time, stop_time, enabled, comment)
VALUES
(0, 'Щодня', '04:00', '05:30', 1, 'Щоденний ранковий підігрів');

-- Індивідуальні графіки для кожного дня
INSERT INTO water_heater_schedule 
(id, day_name, start_time, stop_time, enabled, comment)
VALUES
(1, 'Понеділок', '14:28', '22:10', 1, 'Стандартний денний графік'),
(2, 'Вівторок', '14:28', '22:10', 1, 'Стандартний денний графік'),
(3, 'Середа', '14:28', '22:10', 1, 'Стандартний денний графік'),
(4, 'Четвер', '14:28', '22:10', 1, 'Стандартний денний графік'),
(5, 'Пʼятниця', '14:28', '22:10', 1, 'Стандартний денний графік'),
(6, 'Субота', '14:28', '22:10', 1, 'Стандартний денний графік'),
(7, 'Неділя', '14:28', '22:10', 1, 'Стандартний денний графік');