from pydantic import BaseModel
from typing import List, Optional

class UserCurrencyPairBase(BaseModel): #for check type
    currency_pair_id: int
    selected_exchanges: str  # 存储用户选择的交易所，逗号分隔的字符串

    class Config:
        orm_mode = True  # 使 Pydantic 可以通过 ORM 模型访问数据


class UserCurrencyPairCreate(UserCurrencyPairBase): #for check type when create data(post)
    pass


class UserCurrencyPair(UserCurrencyPairBase): #for check type when get data(get)
    user_id: int

    class Config:
        orm_mode = True

class UserCurrencyPairUpdate(BaseModel):
    new_exchanges: Optional[str] = None          # 如果传入，则直接替换整个字符串
    exchange_to_remove: Optional[str] = None       # 如果传入，则移除指定的交易所
    exchange_to_add: Optional[str] = None          # 如果传入，则添加指定的交易所

    class Config:
        orm_mode = True

##########################################################################################################

class CurrencyPairBase(BaseModel):
    pair: str  # 例如 "BTCUSDT"

    class Config:
        orm_mode = True


class CurrencyPairCreate(CurrencyPairBase):
    pass


class CurrencyPair(CurrencyPairBase):
    id: int
    users: List[UserCurrencyPair]  # 与该币对相关的所有用户的列表

    class Config:
        orm_mode = True

##########################################################################################################
class UserBase(BaseModel):
    telegram_id: str
    username: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    currency_pairs: List[UserCurrencyPair]  # 与该用户相关的所有币对选择的列表

    class Config:
        orm_mode = True


# get_user_currency_pairs_with_details

class UserCurrencyPairDetail(BaseModel):
    """ 用于返回用户监控列表的详细信息 """
    pair: str          # 币对名称（如 BTCUSDT）
    exchanges: str     # 用户选择的交易所列表（逗号分隔）

    class Config:
        orm_mode = True