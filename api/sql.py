from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, Boolean, ForeignKey, TIMESTAMP, SmallInteger, Time, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "mysql+pymysql://vanya:1234@localhost/machineDb"
LDB_URL = "mysql+pymysql://vanya:1234@localhost/ldb"

engine = create_engine(DATABASE_URL)
ldb_engine = create_engine(LDB_URL)

LdbLocalSession = sessionmaker(autocommit=False, autoflush=False, bind=ldb_engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class WaterHeaterSchedule(Base):
    __tablename__ = 'water_heater_schedule'
    id = Column(SmallInteger, primary_key=True, autoincrement=False)  # 0=всі дні, 1=Пн,...7=Нд
    day_name = Column(String(16), nullable=False)
    start_time = Column(Time, nullable=False)
    stop_time = Column(Time, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    last_modified = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    modified_by = Column(String(32), nullable=False, default='system')
    comment = Column(String(128), nullable=True)

class Device(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mac = Column(String(17), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    last_seen_at = Column(TIMESTAMP, nullable=True)
    input_state = Column(SmallInteger, nullable=False, default=0)
    output_state = Column(SmallInteger, nullable=False, default=0)
    battery_voltage = Column(DECIMAL(4,2), nullable=True)
    name = Column(String(32), nullable=False)
    description = Column(String(64), nullable=True)
    fw_url = Column(String(255), nullable=False, default='')

class DeviceData(Base):
    __tablename__ = 'device_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    recorded_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    channel1 = Column(DECIMAL(8,2), nullable=True)
    channel2 = Column(DECIMAL(8,2), nullable=True)
    channel3 = Column(DECIMAL(8,2), nullable=True)
    channel4 = Column(DECIMAL(8,2), nullable=True)
    channel5 = Column(DECIMAL(8,2), nullable=True)
    channel6 = Column(DECIMAL(8,2), nullable=True)
    channel7 = Column(DECIMAL(8,2), nullable=True)
    channel8 = Column(DECIMAL(8,2), nullable=True)

class DevsMeasurementUnit(Base):
    __tablename__ = 'devsMeasurementUnits'
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    channel_number = Column(SmallInteger, nullable=False)  # від 1 до 8
    unit = Column(String(16), nullable=False)              # напр. "°C", "V", "A", "%"
    channel_name = Column(String(32), nullable=True)       # напр. "Температура", "Напруга"
    # Унікальність пари device_id + channel_number забезпечується на рівні БД

    device = relationship("Device")

    
class Switch(Base):
    __tablename__ = 'switches'
    id = Column(Integer, primary_key=True, autoincrement=True)
    switch_name = Column(String(32), nullable=False, unique=True)
    state = Column(Boolean, nullable=False, default=False)
    enabled = Column(Boolean, nullable=False, default=True)
    state_changed_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    changed_by = Column(String(32), nullable=False)
    description = Column(String(64))

class Machine(Base):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(String(255), nullable=False)
    location = Column(String(512), nullable=False)

class Drink(Base):
    __tablename__ = 'drinks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey('machines.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    image = Column(String(255))
    description = Column(String(512))
    price = Column(DECIMAL(10, 2), nullable=False)
    available = Column(Boolean, default=True)
    machine = relationship("Machine")

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey('machines.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    stock = Column(DECIMAL(10, 2), nullable=False, default=0)
    machine = relationship("Machine")

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey('machines.id', ondelete='CASCADE'), nullable=False)
    drink_id = Column(Integer, ForeignKey('drinks.id', ondelete='CASCADE'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id', ondelete='CASCADE'), nullable=False)
    step_index = Column(Integer, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    machine = relationship("Machine")
    drink = relationship("Drink")
    ingredient = relationship("Ingredient")

class UserLevel(Base):
    __tablename__ = 'user_levels'
    level = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=False)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    user_level = Column(Integer, nullable=False)
    last_login = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    user_group = Column(String(50), nullable=False)
    token = Column(String(36), nullable=False)
# Create all tables
Base.metadata.create_all(bind=engine)
