#crud.py
from sqlalchemy.orm import Session
from app import models, schemas  
from typing import Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

def create_user(db: Session, user: schemas.UserCreate):
    """ Create a new user in the database """
    db_user = models.User(telegram_id=user.telegram_id, username=user.username)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user) #refresh so db_user can get from the db then to return
    except IntegrityError:
        db.rollback()

        raise HTTPException(status_code=422, detail="Telegram ID already exists")
    return db_user

def get_user(db: Session, user_id: int):
    """ Get user by ID """
    return db.query(models.User).filter(models.User.id == user_id).first()  

def get_users(db: Session, skip: int = 0, limit: int = 10):
    """ Get multiple users, supports pagination """
    return db.query(models.User).offset(skip).limit(limit).all()

def delete_user(db: Session, user_id: int):
    """ Delete user by ID """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)  
        db.commit()  
    return db_user  


# ========== Currency Pair-related CRUD Operations ========== #

def create_currency_pair(db: Session, currency_pair: schemas.CurrencyPairCreate):
    """ Create a new currency pair in the database """
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
    """ Find currency pair by name """
    return db.query(models.CurrencyPair).filter(models.CurrencyPair.pair == pair).first()

def get_all_currency_pairs(db: Session):
    """ Get all currency pairs """
    return db.query(models.CurrencyPair).all()

def delete_currency_pair(db: Session, pair: str):
    """ Delete currency pair by name """
    db_currency_pair = db.query(models.CurrencyPair).filter(models.CurrencyPair.pair == pair).first()
    if db_currency_pair:
        db.delete(db_currency_pair)
        db.commit()
    return db_currency_pair


# ========== User Currency Pair Selection (UserCurrencyPair) related CRUD Operations ========== #

def create_user_currency_pair(db: Session, user_currency_pair: schemas.UserCurrencyPairCreate, user_id: int):
    """ User selects a currency pair and specifies exchanges to monitor """
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
    """ Get all currency pairs selected by the user """
    return db.query(models.UserCurrencyPair).filter(models.UserCurrencyPair.user_id == user_id).all()

def update_user_currency_pair(
    db: Session,
    user_id: int,
    currency_pair_id: int,
    update_data: schemas.UserCurrencyPairUpdate  # Receive update data
):
    """
    Update user's exchange selection for a currency pair:
      - If new_exchanges is provided, directly replace the entire field;
      - Otherwise, update existing values through exchange_to_remove or exchange_to_add.
    """
    db_ucp = db.query(models.UserCurrencyPair).filter(
        models.UserCurrencyPair.user_id == user_id,
        models.UserCurrencyPair.currency_pair_id == currency_pair_id
    ).first()

    if not db_ucp:
        return None  # or raise an exception

    # If new_exchanges is provided, directly replace the entire field
    if update_data.new_exchanges is not None:
        db_ucp.selected_exchanges = update_data.new_exchanges.strip()
    else:
        # Split the current exchange string into a list
        exchanges = [ex.strip() for ex in db_ucp.selected_exchanges.split(',') if ex.strip()]
        
        # Remove the specified exchange
        if update_data.exchange_to_remove:
            exchanges = [ex for ex in exchanges if ex.lower() != update_data.exchange_to_remove.lower()]
        
        # Add new exchange (avoid duplicates)
        if update_data.exchange_to_add and update_data.exchange_to_add.lower() not in [ex.lower() for ex in exchanges]:
            exchanges.append(update_data.exchange_to_add.strip())
        
        # Update field: comma-separated string
        db_ucp.selected_exchanges = ','.join(exchanges)
    
    db.commit()
    db.refresh(db_ucp)
    return db_ucp


def delete_user_currency_pair(db: Session, user_id: int, currency_pair_id: int):
    """ Delete a user's selected currency pair """
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
    """ Get user's monitoring list (including currency pair names) """
    return (
        db.query(
            models.CurrencyPair.pair,                    # Currency pair name
            models.UserCurrencyPair.selected_exchanges  # Selected exchanges
        )
        .join(models.UserCurrencyPair, models.CurrencyPair.id == models.UserCurrencyPair.currency_pair_id)
        .filter(models.UserCurrencyPair.user_id == user_id)
        .all()
    )
