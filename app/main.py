#main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, models
from app.database import SessionLocal, engine, get_db
# from fastapi.lifespan import LifespanContext


models.Base.metadata.create_all(bind=engine)
app = FastAPI()



# --------------------- User-related API --------------------- #


@app.post("/users/", response_model=schemas.User)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    API route for creating a new user
    """
    db_user = crud.create_user(db, user)  
    return db_user  

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)  
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve multiple user information, supports pagination
    - skip=0 means start from the first data
    - skip=10 means skip the first 10 data, start from the 11th data.
    - For example, limit=10 means return up to 10 records each time.
    - So if you request /users?skip=10&limit=10, you will get the 11th to 20th user data.
    - Example: read_users(skip=0, limit=10), it will only return data from the 1st to the 10th
    - The second request /users?skip=10&limit=10 will return data from the 11th to the 20th. (using loop)
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.delete("/users/{user_id}", response_model=schemas.User)
def remove_user(user_id: int, db: Session = Depends(get_db)):
    """
    API route for deleting a user
    """
    db_user = crud.delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user



# --------------------- Currency Pair-related API --------------------- #

@app.post("/currency_pairs/", response_model=schemas.CurrencyPair)
def create_new_currency_pair(currency_pair: schemas.CurrencyPairCreate, db: Session = Depends(get_db)):
    """
    API route for creating a currency pair record
    - Receives currency pair data (e.g., "BTCUSDT"), data format must conform to schemas.CurrencyPairCreate
    """
    db_currency_pair = crud.create_currency_pair(db, currency_pair)
    return db_currency_pair

@app.get("/currency_pairs/{pair}", response_model=schemas.CurrencyPair)
def read_currency_pair(pair: str, db: Session = Depends(get_db)):
    """
    API route for retrieving a currency pair record by name
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
    API route for deleting a currency pair record
    - Computer queries the corresponding record by currency pair name, then deletes and commits the transaction
    - Returns the deleted currency pair data
    """
    db_currency_pair = crud.delete_currency_pair(db, pair)
    if not db_currency_pair:
        raise HTTPException(status_code=404, detail="Currency pair not found")
    return db_currency_pair



# --------------------- User Currency Pair Selection (UserCurrencyPair) related API --------------------- #

@app.post("/user_currency_pairs/{user_id}", response_model=schemas.UserCurrencyPair)
def create_new_user_currency_pair(user_id: int, user_currency_pair: schemas.UserCurrencyPairCreate, db: Session = Depends(get_db)):
    """
    API route for creating a user currency pair selection record
    - Parameter user_id comes from the URL, identifying which user
    - post must conform to schemas.UserCurrencyPairCreate format
    """
    db_ucp = crud.create_user_currency_pair(db, user_currency_pair, user_id)
    return db_ucp

@app.get("/user_currency_pairs/{user_id}", response_model=List[schemas.UserCurrencyPair])
def read_user_currency_pairs(user_id: int, db: Session = Depends(get_db)):
    """
    API route for retrieving all currency pair selection records of a user
    """
    db_ucps = crud.get_user_currency_pairs(db, user_id)
    return db_ucps

@app.put("/user_currency_pairs/{user_id}/{currency_pair_id}")
def update_exchanges(user_id: int, currency_pair_id: int, update_data: schemas.UserCurrencyPairUpdate, db: Session = Depends(get_db)):
    updated_record = crud.update_user_currency_pair(
        db=db,
        user_id=user_id,
        currency_pair_id=currency_pair_id,
        update_data=update_data  # Pass the entire update data
    )
    if not updated_record:
        raise HTTPException(status_code=404, detail="Record not found")
    return updated_record


@app.delete("/user_currency_pairs/{user_id}/{currency_pair_id}", response_model=schemas.UserCurrencyPair)
def delete_user_currency_pair_endpoint(user_id: int, currency_pair_id: int, db: Session = Depends(get_db)):
    """
    API route for deleting a user currency pair selection record
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
    """
    Retrieve user's monitoring list (including detailed currency pair information)
    """
    pairs = crud.get_user_currency_pairs_with_details(db, user_id)
    return [{"pair": p.pair, "exchanges": p.selected_exchanges} for p in pairs]

#get available pairs
@app.get("/currency_pairs/", response_model=List[schemas.CurrencyPair])
def read_currency_pairs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_currency_pairs(db, skip=skip, limit=limit)

@app.on_event("startup")
async def startup_event():
    default_pairs = ["BTCUSDT", "ETHUSDT", "SNEKUSDT"]
    for pair in default_pairs:
        try:
            crud.create_currency_pair(SessionLocal(), schemas.CurrencyPairCreate(pair=pair))
        except HTTPException as e:
            if e.status_code != 422:  # Ignore if pair already exists
                raise