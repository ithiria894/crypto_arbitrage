#schemas.py
from pydantic import BaseModel,field_validator,Field
from typing import List, Optional



class UserCurrencyPairBase(BaseModel): #for check type
    currency_pair_id: int
    selected_exchanges: str  # 存储用户选择的交易所，逗号分隔的字符串

class UserCurrencyPairCreate(UserCurrencyPairBase): #for check type when create data(post)
    pass


class UserCurrencyPair(UserCurrencyPairBase): #for check type when get data(get)
    user_id: int

    class Config:
        orm_mode = True
    # 使 Pydantic 可以通过 ORM 模型访问数据
    # 為了讓 Pydantic 的模型可以兼容 SQLAlchemy ORM，
    # 讓 FastAPI 在返回查詢結果時，能夠 自動轉換 SQLAlchemy 的對象為 Pydantic 的 dict。


class UserCurrencyPairUpdate(BaseModel):
    new_exchanges: Optional[str] = None          # 如果传入，则直接替换整个字符串
    exchange_to_remove: Optional[str] = None       # 如果传入，则移除指定的交易所
    exchange_to_add: Optional[str] = None          # 如果传入，则添加指定的交易所

    # class Config:
    #     orm_mode = True #no need btc not for get


##########################################################################################################
#pydantic的功能：如果要求int但使用者發送 "12345"（字串），Pydantic 會自動轉換成 12345（整數）
class UserBase(BaseModel): 
    telegram_id: str= Field(...) #must be provided
    # telegram_id: str = Field(..., min_length=5, max_length=20, description="User's Telegram ID")
    username: str = "default_user"  # 設定預設值
    # username: str = Field(..., min_length=3, max_length=30, example="JohnDoe")

    # class Config: 
    #     orm_mode = True UserBase 
    # UserBase 不需要 orm_mode = True，因為它不會直接用來返回 SQLAlchemy 物件。

    #property: 有時候你可能不想在資料庫中存儲某個欄位，而是動態計算出來
    @property #你可以直接 user.username_uppercase 來獲取大寫的 username，而不需要存儲額外的欄位。
    def username_uppercase(self):
        return self.username.upper()

    @field_validator("telegram_id")
    # @field_validator("telegram_id","username") If username cannot be empty
    def not_empty(cls, v):
        if not v or v.strip() == "":
            #not v：如果 v 為 None 或空字符串，這條條件會成立。
            raise ValueError("Field cannot be empty")
        return v

class UserCreate(UserBase):#for check type when create data(post)
    pass


class User(UserBase):#for check type when get data(get)，so need to add id
    id: int
    currency_pairs: List[UserCurrencyPair]  # 与该用户相关的所有币对选择的列表

    class Config:
        orm_mode = True
"""
舉例當我們從 API 查詢用戶 /users/123456，API 可能會返回這樣的 JSON:
{
    "id": 1,
    "telegram_id": "123456",
    "username": "test_user",
    "currency_pairs": []
}
這個 JSON 就符合 User 的定義。
"""
##########################################################################################################
# get_user_currency_pairs_with_details

class UserCurrencyPairDetail(BaseModel):
    """ 用于返回用户监控列表的详细信息 """
    pair: str          # 币对名称（如 BTCUSDT）
    exchanges: str     # 用户选择的交易所列表（逗号分隔）

    class Config:
        orm_mode = True

##########################################################################################################

class CurrencyPairBase(BaseModel):
    pair: str  # 例如 "BTCUSDT"

    @field_validator("pair")
    def not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Field cannot be empty")
        return v

class CurrencyPairCreate(CurrencyPairBase):
    pass


class CurrencyPair(CurrencyPairBase):
    id: int
    users: List[UserCurrencyPair]  # 与该币对相关的所有用户的列表

    class Config:
        orm_mode = True

##########################################################################################
