from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "mysql+pymysql://vanya:1234@localhost/machineDb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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