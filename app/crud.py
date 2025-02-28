#crud.py
from sqlalchemy.orm import Session
from app import models, schemas  # 直接导入models和schemas
from typing import Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
# ========== 用户相关的 CRUD 操作 ========== #
def create_user(db: Session, user: schemas.UserCreate):
    """ 在数据库中创建一个新用户 """
    db_user = models.User(telegram_id=user.telegram_id, username=user.username)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user) #refresh so db_user can get from the db then to return
    except IntegrityError:
        db.rollback()
        # 如果發生錯誤（例如，資料庫中已經有相同的 telegram_id），
        # rollback() 會撤銷所有已經進行的更改，
        # 使數據庫恢復到執行 commit() 之前的狀態
        raise HTTPException(status_code=422, detail="Telegram ID already exists")
    return db_user

def get_user(db: Session, user_id: int):
    """ 通过 ID 获取用户 """
    return db.query(models.User).filter(models.User.id == user_id).first()  # 只取第一个匹配的用户

def get_users(db: Session, skip: int = 0, limit: int = 10):
    """ 获取多个用户，支持分页 """
    return db.query(models.User).offset(skip).limit(limit).all()

def delete_user(db: Session, user_id: int):
    """ 通过 ID 删除用户 """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)  # 从数据库删除用户
        db.commit()  # 提交事务
    return db_user  # 返回被删除的用户


# ========== 币对相关的 CRUD 操作 ========== #

def create_currency_pair(db: Session, currency_pair: schemas.CurrencyPairCreate):
    """ 在数据库中创建一个新的币对 """
    try:
        db_currency_pair = models.CurrencyPair(pair=currency_pair.pair)
        db.add(db_currency_pair)
        db.commit()
        db.refresh(db_currency_pair)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Pair already exists")
    return db_currency_pair

def get_currency_pair(db: Session, pair: str):
    """ 通过币对名称查找币对 """
    return db.query(models.CurrencyPair).filter(models.CurrencyPair.pair == pair).first()

def get_all_currency_pairs(db: Session):
    """获取所有币对"""
    return db.query(models.CurrencyPair).all()

def delete_currency_pair(db: Session, pair: str):
    """ 通过币对名称删除币对 """
    db_currency_pair = db.query(models.CurrencyPair).filter(models.CurrencyPair.pair == pair).first()
    if db_currency_pair:
        db.delete(db_currency_pair)
        db.commit()
    return db_currency_pair


# ========== 用户币对选择（UserCurrencyPair）相关的 CRUD 操作 ========== #

def create_user_currency_pair(db: Session, user_currency_pair: schemas.UserCurrencyPairCreate, user_id: int):
    """ 用户选择某个币对并指定要监控的交易所 """
    db_user_currency_pair = models.UserCurrencyPair(
        user_id=user_id,
        currency_pair_id=user_currency_pair.currency_pair_id,
        selected_exchanges=user_currency_pair.selected_exchanges
    )
    db.add(db_user_currency_pair)
    db.commit()
    db.refresh(db_user_currency_pair)
    return db_user_currency_pair

def get_user_currency_pairs(db: Session, user_id: int):
    """ 获取用户选择的所有币对 """
    return db.query(models.UserCurrencyPair).filter(models.UserCurrencyPair.user_id == user_id).all()

def update_user_currency_pair(
    db: Session,
    user_id: int,
    currency_pair_id: int,
    update_data: schemas.UserCurrencyPairUpdate  # 接收更新数据
):
    """
    更新用户对于某个币对的交易所选择：
      - 如果 new_exchanges 提供，则直接替换整个字段；
      - 否则可以通过 exchange_to_remove 或 exchange_to_add 更新现有值。
    """
    db_ucp = db.query(models.UserCurrencyPair).filter(
        models.UserCurrencyPair.user_id == user_id,
        models.UserCurrencyPair.currency_pair_id == currency_pair_id
    ).first()

    if not db_ucp:
        return None  # 或抛出异常

    # 如果传入 new_exchanges，则直接替换整个字段
    if update_data.new_exchanges is not None:
        db_ucp.selected_exchanges = update_data.new_exchanges.strip()
    else:
        # 分割当前的交易所字符串为列表
        exchanges = [ex.strip() for ex in db_ucp.selected_exchanges.split(',') if ex.strip()]
        
        # 删除指定的交易所
        if update_data.exchange_to_remove:
            exchanges = [ex for ex in exchanges if ex.lower() != update_data.exchange_to_remove.lower()]
        
        # 添加新的交易所（避免重复）
        if update_data.exchange_to_add and update_data.exchange_to_add.lower() not in [ex.lower() for ex in exchanges]:
            exchanges.append(update_data.exchange_to_add.strip())
        
        # 更新字段：用逗号分隔的字符串
        db_ucp.selected_exchanges = ','.join(exchanges)
    
    db.commit()
    db.refresh(db_ucp)
    return db_ucp


def delete_user_currency_pair(db: Session, user_id: int, currency_pair_id: int):
    """ 删除用户选择的某个币对 """
    db_user_currency_pair = db.query(models.UserCurrencyPair).filter(
        models.UserCurrencyPair.user_id == user_id,
        models.UserCurrencyPair.currency_pair_id == currency_pair_id
    ).first()

    if db_user_currency_pair:
        db.delete(db_user_currency_pair)
        db.commit()
    
    return db_user_currency_pair


def get_user_by_telegram_id(db: Session, telegram_id: str):
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def get_currency_pair_by_id(db: Session, currency_pair_id: int):
    return db.query(models.CurrencyPair).filter(models.CurrencyPair.id == currency_pair_id).first()

# get_user_currency_pairs_with_details

def get_user_currency_pairs_with_details(db: Session, user_id: int):
    """ 获取用户监控列表（包含币对名称） """
    return (
        db.query(
            models.CurrencyPair.pair,                    # 币对名称
            models.UserCurrencyPair.selected_exchanges  # 选择的交易所
        )
        .join(models.UserCurrencyPair, models.CurrencyPair.id == models.UserCurrencyPair.currency_pair_id)
        .filter(models.UserCurrencyPair.user_id == user_id)
        .all()
    )
