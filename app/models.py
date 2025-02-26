from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    """ 用户表，存储客户信息 """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String)
    
    # 通过关联对象获取用户的币对选择（关联对象中存储了每个币对的交易所选择）
    currency_pairs = relationship("UserCurrencyPair", back_populates="user")


class CurrencyPair(Base):
    """ 币对表，存储币对信息 """
    __tablename__ = "currency_pairs"

    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String, unique=True)  # 例如 "BTCUSDT"
    
    # 通过关联对象获取关注这个币对的用户
    users = relationship("UserCurrencyPair", back_populates="currency_pair")


class UserCurrencyPair(Base):
    """
    关联表，用来存储用户选择的币对及该币对的交易所选择
    每个记录表示一个用户对一个币对选择的交易所列表
    """
    __tablename__ = "user_currency_pairs"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    currency_pair_id = Column(Integer, ForeignKey("currency_pairs.id"), primary_key=True)
    # 用户对该币对选择的交易所，逗号分隔的字符串，如 "Binance, Kraken, Coinbase"
    selected_exchanges = Column(String)

    # 建立双向关系
    user = relationship("User", back_populates="currency_pairs")
    currency_pair = relationship("CurrencyPair", back_populates="users")
