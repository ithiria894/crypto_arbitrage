#models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    """ User table, stores customer information """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String)
    

    # Get user's currency pair selections through associated objects (associated objects store exchange selections for each currency pair)
    currency_pairs = relationship("UserCurrencyPair", back_populates="user")


class CurrencyPair(Base):
    """ Currency pair table, stores currency pair information """
    __tablename__ = "currency_pairs"

    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String, unique=True)  # e.g., "BTCUSDT"
    

    # Get users who follow this currency pair through associated objects
    users = relationship("UserCurrencyPair", back_populates="currency_pair")


class UserCurrencyPair(Base):
    """
    Association table, used to store the currency pairs selected by users and the exchange selections for those pairs
    Each record represents a user's exchange list selection for a currency pair
    """
    __tablename__ = "user_currency_pairs"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    currency_pair_id = Column(Integer, ForeignKey("currency_pairs.id"), primary_key=True)

    # User's selected exchanges for the currency pair, comma-separated string, e.g., "Binance, Kraken, Coinbase"
    selected_exchanges = Column(String)


    # Establish bidirectional relationship
    user = relationship("User", back_populates="currency_pairs")
    currency_pair = relationship("CurrencyPair", back_populates="users")



# You might ask: 🤔 Why add relationship when UserCurrencyPair already has ForeignKey?
# 📌 ForeignKey only tells SQLAlchemy which table and column this field is related to (just an ID).
# 📌 relationship allows SQLAlchemy to automatically query the complete object of the related table!

# user = db.query(User).filter(User.id == 1).first()
# for line in user.currency_pairs:
#     print(line.currency_pair.pair, line.selected_exchanges)
