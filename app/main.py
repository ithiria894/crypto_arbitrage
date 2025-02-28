#main.py
# 导入 FastAPI 框架，用于创建 API 应用
from fastapi import FastAPI, Depends, HTTPException
# 导入 SQLAlchemy 的 Session 类，用于数据库会话
from sqlalchemy.orm import Session
# 导入 typing 模块中的 List 类型，用于类型提示（例如返回多个用户时使用列表）
from typing import List

# 导入我们自己编写的 CRUD 操作、数据验证（schemas）以及数据模型（models）
from app import crud, schemas, models
# 导入数据库会话创建函数和数据库引擎，get_db 用于获取数据库会话
from app.database import SessionLocal, engine, get_db

# 让 SQLAlchemy 根据 models.py 中定义的所有模型创建对应的数据库表
# 电脑在做什么：检查 models.Base.metadata 中定义的所有模型，
# 并在数据库中创建对应的表（如果表不存在的话）
models.Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用实例
app = FastAPI()


# --------------------- 用户相关 API --------------------- #
#@app.post("/users/")：这是 FastAPI 的路由装饰器，它将这个 create_new_user 函数绑定到 /users/ 这个 POST 请求的路径上。
# 也就是说，当客户端向这个路径发送一个 POST 请求时，这个函数就会被调用。
# response_model=schemas.User：指定返回响应的格式为 schemas.User，
# 也就是说，API 会返回一个符合 schemas.User 格式的数据对象，
# FastAPI 会自动将 Python 对象转换为 JSON 格式返回给前端。
# def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db))：这是定义的视图函数，它接受两个参数：
# user: schemas.UserCreate：通过请求体传入的用户数据，FastAPI 会自动验证这些数据是否符合 schemas.UserCreate 的格式。
# db: Session = Depends(get_db)：db 是一个数据库会话对象，Depends(get_db) 表示 FastAPI 会自动调用 get_db 函数，
# 获取一个数据库会话对象 db，用于执行数据库操作。
# user: schemas.UserCreate:
# user is a parameter (or variable), and schemas.UserCreate is its data type, 
# indicating that user should be of type schemas.UserCreate.
# schemas.UserCreate is a Pydantic model that defines the structure of the data required to create a new user, such as fields like username, password, and email.
# db: Session = Depends(get_db):
# db is a parameter with the data type Session, which represents a database session object.
# Session is a class from SQLAlchemy used for performing database operations, such as queries and inserts.
# Depends(get_db) is a mechanism in FastAPI that automatically calls the get_db function to provide a database session and assigns it to the db parameter.
# In Python, the syntax xx: yy is known as type annotation. It is used to specify the data type of a variable, parameter, or return value.
# def add(a: int, b: int) -> int:

@app.post("/users/", response_model=schemas.User)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    API route for creating a new user
    """
    db_user = crud.create_user(db, user)  
    return db_user  

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):

    db_user = crud.get_user(db, user_id)  # 电脑查询数据库，找到第一个匹配的用户
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    获取多个用户信息，支持分页（Pagination）
    - skip=0 表示從第一條數據開始
    - skip=10 表示跳過前 10 條數據，從第 11 條數據開始。
    - 例如，limit=10 表示每次最多返回 10 条记录。
    - 所以如果你请求 /users?skip=10&limit=10，你会得到第 11 到第 20 条用户数据。
    - 例子：read_users(skip=0, limit=10)，它只会返回 从第 1 条到第 10 条数据
    - 第二次请求 /users?skip=10&limit=10 会返回 第 11 到第 20 条数据。（用loop）
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.delete("/users/{user_id}", response_model=schemas.User)
def remove_user(user_id: int, db: Session = Depends(get_db)):
    """
    删除用户的 API 路由
    """
    db_user = crud.delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# --------------------- 币对相关 API --------------------- #

@app.post("/currency_pairs/", response_model=schemas.CurrencyPair)
def create_new_currency_pair(currency_pair: schemas.CurrencyPairCreate, db: Session = Depends(get_db)):
    """
    创建币对记录的 API 路由
    - 接收币对数据（例如 "BTCUSDT"），数据格式必须符合 schemas.CurrencyPairCreate
    """
    db_currency_pair = crud.create_currency_pair(db, currency_pair)
    return db_currency_pair

@app.get("/currency_pairs/{pair}", response_model=schemas.CurrencyPair)
def read_currency_pair(pair: str, db: Session = Depends(get_db)):
    """
    根据币对名称获取币对记录的 API 路由
    """
    db_currency_pair = crud.get_currency_pair(db, pair)
    if not db_currency_pair:
        raise HTTPException(status_code=404, detail="Currency pair not found")
    return db_currency_pair

@app.get("/currency_pairs/", response_model=List[schemas.CurrencyPair])
def read_all_currency_pairs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pairs = crud.get_all_currency_pairs(db)
    return pairs

@app.delete("/currency_pairs/{pair}", response_model=schemas.CurrencyPair)
def remove_currency_pair(pair: str, db: Session = Depends(get_db)):
    """
    删除币对记录的 API 路由
    - 电脑通过币对名称查询到对应记录，然后删除并提交事务
    - 返回删除后的币对数据
    """
    db_currency_pair = crud.delete_currency_pair(db, pair)
    if not db_currency_pair:
        raise HTTPException(status_code=404, detail="Currency pair not found")
    return db_currency_pair


# --------------------- 用户币对选择（UserCurrencyPair）相关 API --------------------- #

@app.post("/user_currency_pairs/{user_id}", response_model=schemas.UserCurrencyPair)
def create_new_user_currency_pair(user_id: int, user_currency_pair: schemas.UserCurrencyPairCreate, db: Session = Depends(get_db)):
    """
    创建用户币对选择记录的 API 路由
    - 参数 user_id 来自 URL，标识哪个用户
    - post必须符合 schemas.UserCurrencyPairCreate 格式
    """
    db_ucp = crud.create_user_currency_pair(db, user_currency_pair, user_id)
    return db_ucp

@app.get("/user_currency_pairs/{user_id}", response_model=List[schemas.UserCurrencyPair])
def read_user_currency_pairs(user_id: int, db: Session = Depends(get_db)):
    """
    获取某个用户所有币对选择记录的 API 路由
    """
    db_ucps = crud.get_user_currency_pairs(db, user_id)
    return db_ucps

@app.put("/user_currency_pairs/{user_id}/{currency_pair_id}")
def update_exchanges(user_id: int, currency_pair_id: int, update_data: schemas.UserCurrencyPairUpdate, db: Session = Depends(get_db)):
    updated_record = crud.update_user_currency_pair(
        db=db,
        user_id=user_id,
        currency_pair_id=currency_pair_id,
        update_data=update_data  # 传递整个更新数据
    )
    if not updated_record:
        raise HTTPException(status_code=404, detail="Record not found")
    return updated_record


@app.delete("/user_currency_pairs/{user_id}/{currency_pair_id}", response_model=schemas.UserCurrencyPair)
def delete_user_currency_pair_endpoint(user_id: int, currency_pair_id: int, db: Session = Depends(get_db)):
    """
    删除用户币对选择记录的 API 路由
    """
    deleted_ucp = crud.delete_user_currency_pair(db, user_id, currency_pair_id)
    if not deleted_ucp:
        raise HTTPException(status_code=404, detail="UserCurrencyPair not found")
    return deleted_ucp

@app.get("/users/telegram/{telegram_id}", response_model=schemas.User)
def read_user_by_telegram_id(telegram_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram_id(db, telegram_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/currency_pairs/id/{currency_pair_id}", response_model=schemas.CurrencyPair)
def read_currency_pair_by_id(currency_pair_id: int, db: Session = Depends(get_db)):
    db_pair = crud.get_currency_pair_by_id(db, currency_pair_id)
    if not db_pair:
        raise HTTPException(status_code=404, detail="Currency pair not found")
    return db_pair

# get_user_currency_pairs_with_details

@app.get("/user_currency_pairs/{user_id}/with_details", response_model=List[schemas.UserCurrencyPairDetail])
def read_user_currency_pairs_with_details(user_id: int, db: Session = Depends(get_db)):
    """ 获取用户监控列表（包含详细币对信息） """
    pairs = crud.get_user_currency_pairs_with_details(db, user_id)
    return [{"pair": p.pair, "exchanges": p.selected_exchanges} for p in pairs]

#get available pairs
@app.get("/currency_pairs/", response_model=List[schemas.CurrencyPair])
def read_currency_pairs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_currency_pairs(db, skip=skip, limit=limit)