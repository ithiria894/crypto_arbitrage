#schemas.py
from pydantic import BaseModel,field_validator,Field
from typing import List, Optional



class UserCurrencyPairBase(BaseModel): # for checking type
    currency_pair_id: int
    selected_exchanges: str  # Stores the exchanges selected by the user, comma-separated string

class UserCurrencyPairCreate(UserCurrencyPairBase): # for checking type when creating data (post)
    pass


class UserCurrencyPair(UserCurrencyPairBase): # for checking type when getting data (get)
    user_id: int

    class Config:
        orm_mode = True
    # Allows Pydantic to access data through ORM models
    # To make Pydantic models compatible with SQLAlchemy ORM,
    # so that FastAPI can automatically convert SQLAlchemy objects to Pydantic dicts when returning query results.


class UserCurrencyPairUpdate(BaseModel):
    new_exchanges: Optional[str] = None          # If provided, directly replace the entire string
    exchange_to_remove: Optional[str] = None     # If provided, remove the specified exchange
    exchange_to_add: Optional[str] = None        # If provided, add the specified exchange

    # class Config:
    #     orm_mode = True # no need because not for get


##########################################################################################################
# Pydantic's feature: If an int is required but the user sends "12345" (string), Pydantic will automatically convert it to 12345 (integer)
class UserBase(BaseModel): 
    telegram_id: str= Field(...) # must be provided
    # telegram_id: str = Field(..., min_length=5, max_length=20, description="User's Telegram ID")
    username: str = "default_user"  # Set default value
    # username: str = Field(..., min_length=3, max_length=30, example="JohnDoe")

    # class Config: 
    #     orm_mode = True UserBase 
    # UserBase does not need orm_mode = True because it will not be directly used to return SQLAlchemy objects.

    # property: Sometimes you may not want to store a field in the database, but calculate it dynamically
    @property # You can directly use user.username_uppercase to get the uppercase username without storing an extra field.
    def username_uppercase(self):
        return self.username.upper()

    @field_validator("telegram_id")
    # @field_validator("telegram_id","username") If username cannot be empty
    def not_empty(cls, v):
        if not v or v.strip() == "":
            # not v: If v is None or an empty string, this condition will be true.
            raise ValueError("Field cannot be empty")
        return v

class UserCreate(UserBase): # for checking type when creating data (post)
    pass


class User(UserBase): # for checking type when getting data (get), so need to add id
    id: int
    currency_pairs: List[UserCurrencyPair]  # List of all currency pair selections related to the user

    class Config:
        orm_mode = True

"""
Example: When we query a user from the API /users/123456, the API might return a JSON like this:
{
    "id": 1,
    "telegram_id": "123456",
    "username": "test_user",
    "currency_pairs": []
}
This JSON matches the definition of User.
"""
##########################################################################################################
# get_user_currency_pairs_with_details

class UserCurrencyPairDetail(BaseModel):
    """ Used to return detailed information of the user's monitoring list """
    pair: str          # Currency pair name (e.g., BTCUSDT)
    exchanges: str     # List of exchanges selected by the user (comma-separated)

    class Config:
        orm_mode = True

##########################################################################################################

class CurrencyPairBase(BaseModel):
    pair: str  # e.g., "BTCUSDT"

    @field_validator("pair")
    def not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Field cannot be empty")
        return v

class CurrencyPairCreate(CurrencyPairBase):
    pass


class CurrencyPair(CurrencyPairBase):
    id: int
    users: List[UserCurrencyPair]  # List of all users related to the currency pair

    class Config:
        orm_mode = True

##########################################################################################
