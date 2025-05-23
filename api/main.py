# Start  - uvicorn main:app --host 0.0.0.0 --reload
# http://192.168.1.151:8000/docs#/
#

from fastapi import FastAPI, Query, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import urllib.parse
from sqlalchemy.orm import Session
from sql import SessionLocal, Base, Recipe, Drink, Ingredient, User, Machine
from pydantic import BaseModel
from uuid import uuid4
import hashlib
from typing import List

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
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
        orm_mode = True

# Функція для перевірки користувача
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.login == username).first()
    if user and user.password_hash == hashlib.sha256(password.encode()).hexdigest():
        return user
    return None

# Endpoint для отримання токену
@app.post("/token", response_model=Token)
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

@app.get("/current_user_info/")
async def get_current_user_info(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"login": user.login, "last_login": user.last_login}

@app.get("/param/")
async def items(id: str = Query(...), current_user: User = Depends(get_current_user)) -> str:
    check_user_level(current_user, 1)  # Перевірка рівня доступу
    decoded_id = urllib.parse.unquote(id)  # Декодуємо параметр id
    print(decoded_id)
    return decoded_id

@app.get("/recipes/")
async def get_recipes(machine_id: int, drink_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)  # Перевірка рівня доступу
    results = db.query(Recipe, Drink.name.label('drink'), Ingredient.name.label('ingredient'), Recipe.amount) \
                .join(Drink, Recipe.drink_id == Drink.id) \
                .join(Ingredient, Recipe.ingredient_id == Ingredient.id) \
                .filter(Recipe.machine_id == machine_id, Drink.id == drink_id) \
                .order_by(Recipe.step_index) \
                .all()
    return [{"drink": result.drink, "ingredient": result.ingredient, "amount": result.amount} for result in results]

@app.get("/addRecipesIngradient/")
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

# Функція для додавання нового напою
@app.post("/addDrink/")
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

@app.get("/drinks/")
async def get_drinks(machine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)  # Перевірка рівня доступу
    drinks = db.query(Drink).filter(Drink.machine_id == machine_id).all()
    return [{"id": drink.id, "name": drink.name, "image": drink.image, "description": drink.description, "price": drink.price, "available": drink.available} for drink in drinks]



#Machine related endpoints

# Отримати список машин
@app.get("/machines/")
async def get_machines(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    machines = db.query(Machine).all()
    return machines

# Оновити машину за ID
@app.put("/machines/{machine_id}")
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
@app.post("/machines/")
async def add_machine(alias: str, location: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    new_machine = Machine(alias=alias, location=location)
    db.add(new_machine)
    db.commit()
    return new_machine

#drink related endpoints

# Отримати список напоїв
@app.get("/drinks/")
async def get_drinks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    drinks = db.query(Drink).all()
    return drinks

# Отримати список напоїв для машини за ID
@app.get("/machines/{machine_id}/drinks/")
async def get_drinks_for_machine(machine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    drinks = db.query(Drink).filter(Drink.machine_id == machine_id).all()
    return drinks

# Оновити напій за ID
@app.put("/drinks/{drink_id}")
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
@app.post("/drinks/")
async def add_drink(machine_id: int, name: str, image: str, description: str, price: float, available: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    new_drink = Drink(machine_id=machine_id, name=name, image=image, description=description, price=price, available=available)
    db.add(new_drink)
    db.commit()
    return new_drink

#ingredient related endpoints

# Отримати список інгредієнтів
@app.get("/ingredients/")
async def get_ingredients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    ingredients = db.query(Ingredient).all()
    return ingredients

# Оновити інгредієнт за ID
@app.put("/ingredients/{ingredient_id}")
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
@app.post("/ingredients/")
async def add_ingredient(machine_id: int, name: str, stock: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    new_ingredient = Ingredient(machine_id=machine_id, name=name, stock=stock)
    db.add(new_ingredient)
    db.commit()
    return new_ingredient

#User related endpoints

# Отримати список користувачів
@app.get("/users/")
async def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)
    users = db.query(User.id, User.login, User.user_level, User.user_group).all()
    return [{"id": user.id, "login": user.login, "user_level": user.user_level, "user_group": user.user_group} for user in users]

# Оновити користувача за ID
@app.put("/userEdit/{user_id}")
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
@app.post("/userAdd/")
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
@app.put("/admin/update_password/")
async def admin_update_password(login: str, new_password: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1)  # Перевірка рівня доступу адміністратора
    user = db.query(User).filter(User.login == login).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    db.commit()
    return {"status": "ok", "message": "Password updated successfully"}

# Функція для самостійної зміни пароля користувачем
@app.put("/user/change_password/")
async def change_password(old_password: str, new_password: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = current_user
    if user.password_hash != hashlib.sha256(old_password.encode()).hexdigest():
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    user.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    db.commit()
    return {"status": "ok", "message": "Password changed successfully"}

@app.delete("/userDel/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_user_level(current_user, 1) 
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"status": "ok", "message": "User deleted successfully"}