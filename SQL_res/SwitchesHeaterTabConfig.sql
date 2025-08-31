SELECT * FROM ldb.switches;


use ldb;

CREATE TABLE switches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    switch_name VARCHAR(32) NOT NULL,       -- Назва вимикача
    state BOOLEAN NOT NULL DEFAULT 0,       -- Стан: 0=вимкнено, 1=увімкнено
    state_changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
                                             -- Час останньої зміни
    changed_by VARCHAR(32) NOT NULL,        -- Хто змінив
    description VARCHAR(64) DEFAULT NULL,   -- Опис вимикача
    UNIQUE (switch_name)                    -- Унікальна назва вимикача
);

INSERT INTO switches (switch_name, state, changed_by, description)
VALUES ('WaterHeaterPower', 0, 'system', 'Живлення бойлера');