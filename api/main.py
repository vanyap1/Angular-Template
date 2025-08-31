# Start  - uvicorn main:app --host 0.0.0.0 --reload
# http://192.168.1.151:8000/docs#/
# run to debug "uvicorn main:app --host 0.0.0.0 --port 4200 --reload"

from fastapi import FastAPI, Query, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import urllib.parse
from sqlalchemy.orm import Session
from sql import SessionLocal, LdbLocalSession, Base, Recipe, Drink, Ingredient, User, Machine, Switch, WaterHeaterSchedule, Device, DeviceData, DevsMeasurementUnit
from pydantic import BaseModel
from uuid import uuid4
import hashlib
from typing import List, Optional
import socket
import json
from sqlalchemy import func

openapi_tags = [
    {
        "name": "Switches",
        "description": "Операції для керування вимикачами: перегляд, додавання, зміна стану, видалення."
    },
    {
        "name": "Sensors",
        "description": "Операції для роботи з сенсорами: отримання, оновлення, історія вимірювань."
    },
    {
        "name": "WaterHeater",
        "description": "Операції для роботи з водонагрівачами: отримання, додавання, редагування."
    },
    {
        "name": "UserManagement",
        "description": "Операції для керування користувачами: реєстрація, редагування, видалення, зміна пароля."
    },
     {
        "name": "RealTimeServerApi",
        "description": "Операції для роботи з реальним часом: отримання даних, підписка на події."
    },
     {
        "name": "Machines",
        "description": "Операції для роботи з машинами: отримання, додавання, редагування."
    },
     {
        "name": "Drinks",
        "description": "Операції для роботи з напоями: отримання, додавання, редагування."
    },
    {
        "name": "Recipes",
        "description": "Операції для роботи з рецептами: отримання, додавання інгредієнтів до рецептів."
    },
    {
        "name": "Ingredients",
        "description": "Операції для роботи з інгредієнтами: отримання, додавання, редагування."
    }
   
]



app = FastAPI(openapi_tags=openapi_tags)
appHost = '/tmp/appServer'
gpioUserKey = "key"
sensorUserKey = "key"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency
def get_db_ldb():
    db = LdbLocalSession()
    try:
        yield db
    finally:
        db.close()





# Модель для відповіді з токеном
class Token(BaseModel):
    access_token: str
    token_type: str

# Модель для відповіді з користувачем без токену
class UserResponse(BaseModel):
    id: int
    login: str
    user_level: int
    user_group: str

    class Config:
        from_attributes = True

# Функція для перевірки користувача
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.login == username).first()
    if user and user.password_hash == hashlib.sha256(password.encode()).hexdigest():
        return user
    return None

# Endpoint для отримання токену
@app.post("/token", response_model=Token, tags=["UserManagement"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(form_data)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = str(uuid4())
    user.token = token  # Зберігаємо токен у базі даних
    db.commit()
    return {"access_token": token, "token_type": "bearer"}

# Функція для перевірки токену
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Функція для перевірки рівня доступу
def check_user_level(user: User, required_level: int):
    if user.user_level > required_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

@app.get("/current_user_info/", tags=["UserManagement"])
async def get_current_user_info(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"login": user.login, "last_login": user.last_login}

@app.get("/param/", tags=["UserManagement"])
async def items(id: str = Query(...), current_user: User = Depends(get_current_user)) -> str:
    check_user_level(current_user, 1)  # Перевірка рівня доступу
    decoded_id = urllib.parse.unquote(id)  # Декодуємо параметр id
    print(decoded_id)
    return decoded_id


# Отримати список користувачів
@app.get("/users/", tags=["UserManagement"])
async def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    users = db.query(User.id, User.login, User.user_level, User.user_group).all()
    return [{"id": user.id, "login": user.login, "user_level": user.user_level, "user_group": user.user_group} for user in users]

# Оновити користувача за ID
@app.put("/userEdit/{user_id}", tags=["UserManagement"])
async def update_user(user_id: int, login: str, password: str, user_level: int, user_group: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.login = login
    user.password_hash = hashlib.sha256(password.encode()).hexdigest()
    user.user_level = user_level
    user.user_group = user_group
    db.commit()
    return "ok: user updated"

# Додати нового користувача
@app.post("/userAdd/", tags=["UserManagement"])
async def add_user(login: str, password: str, user_level: int, user_group: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    
    # Перевірка, чи користувач вже існує
    existing_user = db.query(User).filter(User.login == login).first()
    print(existing_user)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    
    token = str(uuid4())
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    new_user = User(login=login, password_hash=password_hash, user_level=user_level, user_group=user_group, token=token)
    print(new_user)
    db.add(new_user)
    db.commit()
    return new_user

# Функція для оновлення пароля користувача адміністратором
@app.put("/admin/update_password/", tags=["UserManagement"])
async def admin_update_password(login: str, new_password: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)  # Перевірка рівня доступу адміністратора
    user = db.query(User).filter(User.login == login).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    db.commit()
    return {"status": "ok", "message": "Password updated successfully"}

# Функція для самостійної зміни пароля користувачем
@app.put("/user/change_password/", tags=["UserManagement"])
async def change_password(old_password: str, new_password: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = current_user
    if user.password_hash != hashlib.sha256(old_password.encode()).hexdigest():
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    user.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    db.commit()
    return {"status": "ok", "message": "Password changed successfully"}

@app.delete("/userDel/{user_id}", tags=["UserManagement"])
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1) 
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"status": "ok", "message": "User deleted successfully"}




# Отримати список всіх сенсорів
@app.get("/sensors/", tags=["Sensors"])
async def get_sensors(db: Session = Depends(get_db_ldb)):
    sensors = db.query(Device).all()
    return {"ok": [
        {"mac": s.mac, "name": s.name, "description": s.description, "battery_voltage": s.battery_voltage, "input_state": s.input_state, "output_state": s.output_state, "last_seen_at": s.last_seen_at}
        for s in sensors
    ]}
# Модель для створення/оновлення сенсора
class SensorCreateUpdateRequest(BaseModel):
    mac: str
    name: str
    description: str
    battery_voltage: float
    input_state: int
    output_state: int
    fw_url: str
    userKey: str

# Отримати повний рядок сенсора по MAC
@app.get("/sensor/{mac}/full/", tags=["Sensors"])
async def get_sensor_full(mac: str, db: Session = Depends(get_db_ldb)):
    device = db.query(Device).filter(Device.mac == mac).first()
    if not device:
        return {"err": "Sensor not found"}
    result = {
        "id": device.id,
        "mac": device.mac,
        "name": device.name,
        "description": device.description,
        "battery_voltage": device.battery_voltage,
        "input_state": device.input_state,
        "output_state": device.output_state,
        "fw_url": device.fw_url,
        "created_at": device.created_at,
        "updated_at": device.updated_at,
        "last_seen_at": device.last_seen_at,
        "fw_url": device.fw_url
    }
    return {"ok": result}

# Створити новий сенсор
@app.post("/sensor/create/", tags=["Sensors"])
async def create_sensor(req: SensorCreateUpdateRequest, db: Session = Depends(get_db_ldb)):
    if not req.userKey or req.userKey != sensorUserKey:
        return {"err": "Forbidden: Invalid user key"}
    existing = db.query(Device).filter(Device.mac == req.mac).first()
    if existing:
        return {"err": "Sensor with this MAC already exists"}
    device = Device(
        mac=req.mac,
        name=req.name,
        description=req.description,
        battery_voltage=req.battery_voltage,
        input_state=req.input_state,
        output_state=req.output_state,
        fw_url=req.fw_url,
        last_seen_at=func.now()
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return {"ok": {"id": device.id}}

# Оновити всі дані сенсора по MAC
class SensorCreateUpdateRequest(BaseModel):
    """
    Модель для оновлення даних сенсора.
    Всі поля необов'язкові, оновлюється лише те, що передано.
    - name: назва сенсора (str)
    - description: опис сенсора (str)
    - battery_voltage: напруга батареї (float)
    - input_state: стан входів (int)
    - output_state: стан виходів (int)
    - fw_url: посилання на прошивку (str)
    - units: масив одиниць вимірювання для каналів (List[str], до 8)
    - channel_names: масив назв каналів (List[str], до 8)
    - userKey: ключ автентифікації сенсора (str, обов'язковий)
    """
    name: Optional[str] = None
    userKey: str
    description: Optional[str] = None
    battery_voltage: Optional[float] = None
    input_state: Optional[int] = None
    output_state: Optional[int] = None
    fw_url: Optional[str] = None
    units: Optional[List[str]] = None
    channel_names: Optional[List[str]] = None
    

    class Config:
        json_schema_extra = {
            "example": {
                "name": "BoilerRoom-01",
                "userKey": "key",
                "description": "Модуль котельні",
                "battery_voltage": 4.15,
                "input_state": 0,
                "output_state": 0,
                "fw_url": "http://example.com/fw.bin",
                "units": ["A", "V", "W", "°C", "°F", "L", "kg", "m"],
                "channel_names": ["Current", "Voltage", "Power", "Temp", "Humidity", "Flow", "Weight", "Distance"]
                
            }
        }
@app.put("/sensor/{mac}/update_full/", tags=["Sensors"])
async def update_sensor_full(mac: str, req: SensorCreateUpdateRequest, db: Session = Depends(get_db_ldb)):
    if not req.userKey or req.userKey != sensorUserKey:
        return {"err": "Forbidden: Invalid user key"}
    device = db.query(Device).filter(Device.mac == mac).first()
    if not device:
        return {"err": "Sensor not found"}

    # Оновлюємо тільки ті поля, які присутні в запиті
    if hasattr(req, "name") and req.name is not None:
        device.name = req.name
    if hasattr(req, "description") and req.description is not None:
        device.description = req.description
    if hasattr(req, "battery_voltage") and req.battery_voltage is not None:
        device.battery_voltage = req.battery_voltage
    if hasattr(req, "input_state") and req.input_state is not None:
        device.input_state = req.input_state
    if hasattr(req, "output_state") and req.output_state is not None:
        device.output_state = req.output_state
    if hasattr(req, "fw_url") and req.fw_url is not None:
        device.fw_url = req.fw_url

    device.updated_at = func.now()
    device.last_seen_at = func.now()

    # Оновлення юнітів та їх опису, якщо передані
    if hasattr(req, "units") and req.units is not None:
        for i, unit in enumerate(req.units):
            channel_number = i + 1
            unit_row = db.query(DevsMeasurementUnit).filter(
                DevsMeasurementUnit.device_id == device.id,
                DevsMeasurementUnit.channel_number == channel_number
            ).first()
            if unit_row and unit != "":
                unit_row.unit = unit

    if hasattr(req, "channel_names") and req.channel_names is not None:
        for i, name in enumerate(req.channel_names):
            channel_number = i + 1
            unit_row = db.query(DevsMeasurementUnit).filter(
                DevsMeasurementUnit.device_id == device.id,
                DevsMeasurementUnit.channel_number == channel_number
            ).first()
            if unit_row and name != "":
                unit_row.channel_name = name

    db.commit()
    return {"ok": "Sensor updated"}

# Додати дані від сенсора (оновити сенсор і записати вимірювання)
# Приймає: mac (str), battery_voltage (float), input_state (int), output_state (int), channels (List[float]), userKey (str)
# Повертає: JSON з ключем "ok" та станом виходів, або "err" з описом помилки.

from typing import List, Optional

class SensorDataRequest(BaseModel):
    mac: str
    battery_voltage: float
    input_state: int
    output_state: int
    channels: List[float]
    units: Optional[List[str]] = None
    userKey: str

    class Config:
        json_schema_extra = {
            "example": {
                "mac": "AA:BB:CC:DD:AA:01",
                "battery_voltage": 12.3,
                "input_state": 912,
                "output_state": 512,
                "channels": [1, 2, 3, 4, 5, 6, 7, 8],
                "units": ["A", "V", "W", "°C", "°F", "L", "kg", "m"],
                "userKey": "key"
            }
        }

@app.post("/sensor/data/", tags=["Sensors"])
async def add_sensor_data(
    req: SensorDataRequest,
    db: Session = Depends(get_db_ldb)
):
    if not req.userKey or req.userKey != sensorUserKey:
        return {"err": "Forbidden: Invalid user key"}
    # Знайти або створити сенсор
    device = db.query(Device).filter(Device.mac == req.mac).first()
    is_new = False
    if not device:
        device = Device(
            mac=req.mac,
            name="Auto-Device",
            description="Автоматично створений",
            battery_voltage=req.battery_voltage,
            input_state=req.input_state,
            output_state=req.output_state,
            last_seen_at=func.now()
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        is_new = True
    else:
        device.battery_voltage = req.battery_voltage
        device.input_state = req.input_state
        device.output_state = req.output_state
        device.last_seen_at = func.now()
        db.commit()
    # Додати вимірювання
    data = DeviceData(
        device_id=device.id,
        channel1=req.channels[0] if len(req.channels) > 0 else None,
        channel2=req.channels[1] if len(req.channels) > 1 else None,
        channel3=req.channels[2] if len(req.channels) > 2 else None,
        channel4=req.channels[3] if len(req.channels) > 3 else None,
        channel5=req.channels[4] if len(req.channels) > 4 else None,
        channel6=req.channels[5] if len(req.channels) > 5 else None,
        channel7=req.channels[6] if len(req.channels) > 6 else None,
        channel8=req.channels[7] if len(req.channels) > 7 else None,
    )
    db.add(data)
    db.commit()

    # Додати юніти, якщо це новий сенсор і units передано
    if is_new and req.units is not None:
        for i in range(1, 9):
            unit = req.units[i-1] if len(req.units) >= i else ""
            unit_exists = db.query(DevsMeasurementUnit).filter(
                DevsMeasurementUnit.device_id == device.id,
                DevsMeasurementUnit.channel_number == i
            ).first()
            if not unit_exists:
                db.add(DevsMeasurementUnit(
                    device_id=device.id,
                    channel_number=i,
                    unit=unit,
                    channel_name=f"Channel {i}"
                ))
        db.commit()

    return {"ok": {"output_state": device.output_state}}

# Отримати дані сенсора по маку (останній запис)
@app.get("/sensor/{mac}/last/", tags=["Sensors"])
async def get_sensor_last(mac: str, db: Session = Depends(get_db_ldb)):
    device = db.query(Device).filter(Device.mac == mac).first()
    if not device:
        return {"err": "Sensor not found"}
    last_data = db.query(DeviceData).filter(DeviceData.device_id == device.id).order_by(DeviceData.recorded_at.desc()).first()
    
    # Отримати юніти та назви каналів
    units = [None] * 8
    names = [None] * 8
    unit_rows = db.query(DevsMeasurementUnit).filter(DevsMeasurementUnit.device_id == device.id).order_by(DevsMeasurementUnit.channel_number).all()
    for unit_row in unit_rows:
        idx = unit_row.channel_number - 1
        if 0 <= idx < 8:
            units[idx] = unit_row.unit
            names[idx] = unit_row.channel_name

    header = {
        "mac": device.mac,
        "name": device.name,
        "description": device.description,
        "battery_voltage": device.battery_voltage,
        "input_state": device.input_state,
        "output_state": device.output_state,
        "last_seen_at": device.last_seen_at,
        "unit": units,
        "channel_name": names
    }
    body = {
        "recorded_at": last_data.recorded_at if last_data else None,
        "channels": [getattr(last_data, f"channel{i+1}") if last_data else None for i in range(8)]
        
    }
    return {"ok": {"header": header, "body": body}}

# Отримати дані сенсора по маку за період часу
# Приймає: mac (str), start (str), end (str)
# Повертає: JSON з "header" (інфо про сенсор) і "rows" (масив вимірювань)
@app.get("/sensor/{mac}/history/", tags=["Sensors"])
async def get_sensor_history(mac: str, start: str, end: str, db: Session = Depends(get_db_ldb)):
    device = db.query(Device).filter(Device.mac == mac).first()
    if not device:
        return {"err": "Sensor not found"}
    
    
    data = db.query(DeviceData).filter(
        DeviceData.device_id == device.id,
        DeviceData.recorded_at >= start,
        DeviceData.recorded_at <= end
    ).order_by(DeviceData.recorded_at).all()
    
    # Отримати юніти та назви каналів
    units = [None] * 8
    names = [None] * 8
    unit_rows = db.query(DevsMeasurementUnit).filter(DevsMeasurementUnit.device_id == device.id).order_by(DevsMeasurementUnit.channel_number).all()
    for unit_row in unit_rows:
        idx = unit_row.channel_number - 1
        if 0 <= idx < 8:
            units[idx] = unit_row.unit
            names[idx] = unit_row.channel_name

    header = {
        "mac": device.mac,
        "name": device.name,
        "description": device.description,
        "battery_voltage": device.battery_voltage,
        "input_state": device.input_state,
        "output_state": device.output_state,
        "fw_url": getattr(device, "fw_url", None),
        "last_seen_at": device.last_seen_at,
        "unit": units,
        "channel_name": names
    }
    rows = [
        {
            "recorded_at": d.recorded_at,
            "channel1": d.channel1,
            "channel2": d.channel2,
            "channel3": d.channel3,
            "channel4": d.channel4,
            "channel5": d.channel5,
            "channel6": d.channel6,
            "channel7": d.channel7,
            "channel8": d.channel8
        }
        for d in data
    ]
    return {"ok": {"header": header, "rows": rows}}

# Оновити дані сенсора по маку (назва, опис, стани)
@app.put("/sensor/{mac}/update/", tags=["Sensors"])
async def update_sensor_info(mac: str, name: str, description: str, input_state: int, output_state: int, battery_voltage: float, userKey: str, db: Session = Depends(get_db_ldb)):
    if not userKey or userKey != sensorUserKey:
        return {"err": "Forbidden: Invalid user key"}
    device = db.query(Device).filter(Device.mac == mac).first()
    if not device:
        return {"err": "Sensor not found"}
    device.name = name
    device.description = description
    device.input_state = input_state
    device.output_state = output_state
    device.battery_voltage = battery_voltage
    device.updated_at = func.now()
    db.commit()
    return {"ok": "Sensor updated"}

# Видалити сенсор та всі його дані по MAC
# Приймає: mac (str), userKey (str)
# Повертає: JSON з ключем "ok" або "err"
@app.delete("/sensor/{mac}/delete/", tags=["Sensors"])
async def delete_sensor(mac: str, userKey: str, db: Session = Depends(get_db_ldb)):
    if not userKey or userKey != sensorUserKey:
        return {"err": "Forbidden: Invalid user key"}
    device = db.query(Device).filter(Device.mac == mac).first()
    if not device:
        return {"err": "Sensor not found"}
    try:
        # Видалення всіх вимірювань
        db.query(DeviceData).filter(DeviceData.device_id == device.id).delete()
        # Видалення всіх юнітів
        db.query(DevsMeasurementUnit).filter(DevsMeasurementUnit.device_id == device.id).delete()
        # Видалення самого сенсора
        db.delete(device)
        db.commit()
        return {"ok": f"Sensor {mac} and all its data deleted"}
    except Exception as e:
        return {"err": str(e)}




# Отримати всі рядки з таблиці WaterHeaterSchedule.
# Приймає: нічого.
# Повертає: JSON з ключем "ok" та списком розкладів, або "err" з описом помилки.
@app.get("/water_heater_schedule/", tags=["WaterHeater"])
async def get_water_heater_schedule(db: Session = Depends(get_db_ldb)):
    try:
        schedules = db.query(WaterHeaterSchedule).all()
        result = [
            {
                "id": s.id,
                "day_name": s.day_name,
                "start_time": str(s.start_time),
                "stop_time": str(s.stop_time),
                "enabled": s.enabled,
                "last_modified": s.last_modified,
                "modified_by": s.modified_by,
                "comment": s.comment
            }
            for s in schedules
        ]
        return {"ok": result}
    except Exception as e:
        return {"err": str(e)}

# Оновити один рядок розкладу за його id.
# Приймає: id (int) — ідентифікатор, start_time (str), stop_time (str), enabled (bool), userKey (str) — ключ користувача.
# Повертає: JSON з ключем "ok" та повідомленням, або "err" з описом помилки.
@app.put("/water_heater_schedule/{id}", tags=["WaterHeater"])
async def update_water_heater_schedule(
    id: int,
    start_time: str,
    stop_time: str,
    enabled: bool,
    userKey: str,
    db: Session = Depends(get_db_ldb)
):
    if not userKey or userKey != gpioUserKey:
        return {"err": "Forbidden: Invalid user key"}
    schedule = db.query(WaterHeaterSchedule).filter(WaterHeaterSchedule.id == id).first()
    if not schedule:
        return {"err": "Schedule not found"}
    try:
        schedule.start_time = start_time
        schedule.stop_time = stop_time
        schedule.enabled = enabled
        schedule.modified_by = "byWebUser"
        db.commit()
        return {"ok": f"Schedule {id} updated"}
    except Exception as e:
        return {"err": str(e)}





# Отримати список всіх вимикачів.
# Приймає: нічого.
# Повертає: JSON з ключем "ok" та списком вимикачів, або "err" з описом помилки.
@app.get("/getSwitches/", tags=["Switches"])
async def getSwitches(db: Session = Depends(get_db_ldb)):
    try:
        switches = db.query(Switch).all()
        result = [{"id": s.id, "switch_name": s.switch_name, "state": s.state, "enabled": s.enabled, "state_changed_at": s.state_changed_at, "changed_by": s.changed_by, "description": s.description} for s in switches]
        return {"ok": result}
    except Exception as e:
        return {"err": str(e)}

# Встановити стан вимикача за його ID.
# Приймає: switch_id (int) — ID вимикача, state (bool) — новий стан, userKey (str) — ключ користувача.
# Повертає: JSON з ключем "ok" та повідомленням, або "err" з описом помилки.
@app.get("/setSwitchById/", tags=["Switches"])
async def setSwitchById(switch_id: int, state: bool, userKey: str, db: Session = Depends(get_db_ldb)):
    if not userKey or userKey != gpioUserKey:
        return {"err": "Forbidden: Invalid user key"}
    switch = db.query(Switch).filter(Switch.id == switch_id).first()
    if not switch:
        return {"err": "Switch not found"}
    try:
        switch.state = state
        switch.changed_by = userKey
        db.commit()
        return {"ok": f"Switch {switch_id} set to {'on' if state else 'off'}"}
    except Exception as e:
        return {"err": str(e)}

# Додати новий вимикач.
# Приймає: switch_name (str) — назва вимикача, initialState (bool) — початковий стан, description (str) — опис, userKey (str) — ключ користувача.
# Повертає: JSON з ключем "ok" та повідомленням, або "err" з описом помилки.
@app.post("/addSwitch/", tags=["Switches"])
async def addSwitch(switch_name: str, initialState: bool, enabled: bool, description: str, userKey: str, db: Session = Depends(get_db_ldb)):
    if not userKey or userKey != gpioUserKey:
        return {"err": "Forbidden: Invalid user key"}
    try:
        new_switch = Switch(switch_name=switch_name, state=initialState, enabled=enabled, changed_by=userKey, description=description)
        db.add(new_switch)
        db.commit()
        return {"ok": f"Switch {switch_name} added with state {'on' if initialState else 'off'} and enabled {enabled}"}
    except Exception as e:
        return {"err": str(e)}

# Отримати інформацію про вимикач за його ID.
# Приймає: switch_id (int) — ID вимикача.
# Повертає: JSON з ключем "ok" та деталями вимикача, або "err" з описом помилки.
@app.get("/getSwitchesById/", tags=["Switches"])
async def getSwitchesById(switch_id: int, db: Session = Depends(get_db_ldb)):
    switch = db.query(Switch).filter(Switch.id == switch_id).first()
    if not switch:
        return {"err": "Switch not found"}
    try:
        result = {"id": switch.id, "switch_name": switch.switch_name, "state": switch.state, "enabled": switch.enabled, "state_changed_at": switch.state_changed_at, "changed_by": switch.changed_by, "description": switch.description}
        return {"ok": result}
    except Exception as e:
        return {"err": str(e)}

# Отримати інформацію про вимикач за його назвою.
# Приймає: switch_name (str) — назва вимикача.
# Повертає: JSON з ключем "ok" та деталями вимикача, або "err" з описом помилки.
@app.get("/getSwitchesByName/", tags=["Switches"])
async def getSwitchesByName(switch_name: str, db: Session = Depends(get_db_ldb)):
    switch = db.query(Switch).filter(Switch.switch_name == switch_name).first()
    if not switch:
        return {"err": "Switch not found"}
    try:
        result = {"id": switch.id, "switch_name": switch.switch_name, "state": switch.state, "enabled": switch.enabled, "state_changed_at": switch.state_changed_at, "changed_by": switch.changed_by, "description": switch.description}
        return {"ok": result}
    except Exception as e:
        return {"err": str(e)}

# Видалити вимикач за його ID.
# Приймає: switch_id (int) — ID вимикача, userKey (str) — ключ користувача.
# Повертає: JSON з ключем "ok" та повідомленням, або "err" з описом помилки.
@app.delete("/removeSwitchById/", tags=["Switches"])
async def removeSwitchById(switch_id: int, userKey: str, db: Session = Depends(get_db_ldb)):
    if not userKey or userKey != gpioUserKey:
        return {"err": "Forbidden: Invalid user key"}
    switch = db.query(Switch).filter(Switch.id == switch_id).first()
    if not switch:
        return {"err": "Switch not found"}
    try:
        db.delete(switch)
        db.commit()
        return {"ok": f"Switch {switch_id} removed"}
    except Exception as e:
        return




@app.get("/getParam/", tags=["RealTimeServerApi"])
async def getServerParam(param: str = None):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(appHost)
            
            req = {"type": "get", "param": param}
            s.sendall(json.dumps(req).encode())
            #s.sendall(b'{}')
            data = s.recv(1048576)
            values = json.loads(data.decode())
            print(values)
        return values
    except socket.error as e:
        return {"error": "Socket connection failed", "details": str(e)}

@app.get("/getPowerMeter/", tags=["RealTimeServerApi"])
async def getServerParam():
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(appHost)
            req = {"type": "get", "param": "MainPowerMeterData"}
            s.sendall(json.dumps(req).encode())
            #s.sendall(b'{}')
            data = s.recv(1048576)
            values = json.loads(data.decode())
            print(values)
        return values
    except socket.error as e:
        return {"error": "Socket connection failed", "details": str(e)}


@app.get("/setParam/", tags=["RealTimeServerApi"])
async def setServerParam(param: str = None, value: str = None):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(appHost)
            req = {"type": "set", "param": param, "value": value}
            s.sendall(json.dumps(req).encode())
            #s.sendall(b'{}')
            data = s.recv(1024)
            values = json.loads(data.decode())
            print(values)
        return values
    except socket.error as e:
        return {"error": "Socket connection failed", "details": str(e)}
    



#Machine related endpoints

# Отримати список машин
@app.get("/machines/", tags=["Machines"])
async def get_machines(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    machines = db.query(Machine).all()
    return machines

# Оновити машину за ID
@app.put("/machines/{machine_id}", tags=["Machines"])
async def update_machine(machine_id: int, alias: str, location: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    machine.alias = alias
    machine.location = location
    db.commit()
    return machine

# Додати нову машину
@app.post("/machines/", tags=["Machines"])
async def add_machine(alias: str, location: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    new_machine = Machine(alias=alias, location=location)
    db.add(new_machine)
    db.commit()
    return new_machine


# Функція для додавання нового напою
@app.post("/addDrink/", tags=["Drinks"])
async def add_drink(machine_id: int, name: str, image: str, description: str, price: float, available: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)  # Перевірка рівня доступу

    # Додаємо новий напій
    new_drink = Drink(
        machine_id=machine_id,
        name=name,
        image=image,
        description=description,
        price=price,
        available=available
    )
    db.add(new_drink)
    db.commit()
    return {"status": "ok", "drink_id": new_drink.id}

@app.get("/drinks/", tags=["Drinks"])
async def get_drinks(machine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)  # Перевірка рівня доступу
    drinks = db.query(Drink).filter(Drink.machine_id == machine_id).all()
    return [{"id": drink.id, "name": drink.name, "image": drink.image, "description": drink.description, "price": drink.price, "available": drink.available} for drink in drinks]





#drink related endpoints

# Отримати список напоїв
@app.get("/drinks/", tags=["Drinks"])
async def get_drinks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    drinks = db.query(Drink).all()
    return drinks

# Отримати список напоїв для машини за ID
@app.get("/machines/{machine_id}/drinks/", tags=["Drinks"])
async def get_drinks_for_machine(machine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    drinks = db.query(Drink).filter(Drink.machine_id == machine_id).all()
    return drinks

# Оновити напій за ID
@app.put("/drinks/{drink_id}", tags=["Drinks"])
async def update_drink(drink_id: int, name: str, image: str, description: str, price: float, available: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    drink = db.query(Drink).filter(Drink.id == drink_id).first()
    if not drink:
        raise HTTPException(status_code=404, detail="Drink not found")
    drink.name = name
    drink.image = image
    drink.description = description
    drink.price = price
    drink.available = available
    db.commit()
    return drink

# Додати новий напій
@app.post("/drinks/", tags=["Drinks"])
async def add_drink(machine_id: int, name: str, image: str, description: str, price: float, available: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    new_drink = Drink(machine_id=machine_id, name=name, image=image, description=description, price=price, available=available)
    db.add(new_drink)
    db.commit()
    return new_drink



@app.get("/recipes/", tags=["Recipes"])
async def get_recipes(machine_id: int, drink_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)  # Перевірка рівня доступу
    results = db.query(Recipe, Drink.name.label('drink'), Ingredient.name.label('ingredient'), Recipe.amount) \
                .join(Drink, Recipe.drink_id == Drink.id) \
                .join(Ingredient, Recipe.ingredient_id == Ingredient.id) \
                .filter(Recipe.machine_id == machine_id, Drink.id == drink_id) \
                .order_by(Recipe.step_index) \
                .all()
    return [{"drink": result.drink, "ingredient": result.ingredient, "amount": result.amount} for result in results]

@app.get("/addRecipesIngradient/", tags=["Recipes"])
async def add_recipes_ingradient(machine_id: int, drink_id: int, ingredient_id: int, ingredient_amount: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)  # Перевірка рівня доступу

    # Додаємо інгредієнт до рецепту
    new_recipe = Recipe(
        machine_id=machine_id,
        drink_id=drink_id,
        ingredient_id=ingredient_id,
        step_index=0,  # Можливо, потрібно визначити логіку для step_index
        amount=ingredient_amount
    )
    db.add(new_recipe)
    db.commit()
    return {"status": "ok"}



#ingredient related endpoints

# Отримати список інгредієнтів
@app.get("/ingredients/", tags=["Ingredients"])
async def get_ingredients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    ingredients = db.query(Ingredient).all()
    return ingredients

# Оновити інгредієнт за ID
@app.put("/ingredients/{ingredient_id}", tags=["Ingredients"])
async def update_ingredient(ingredient_id: int, name: str, stock: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ingredient.name = name
    ingredient.stock = stock
    db.commit()
    return ingredient

# Додати новий інгредієнт
@app.post("/ingredients/", tags=["Ingredients"])
async def add_ingredient(machine_id: int, name: str, stock: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    new_ingredient = Ingredient(machine_id=machine_id, name=name, stock=stock)
    db.add(new_ingredient)
    db.commit()
    return new_ingredient

#User related endpoints

