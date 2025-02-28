import pytest
import time
from fastapi.testclient import TestClient
from app.main import app  # Import FastAPI application from main.py
from app.database import get_db, SessionLocal  # Import database-related functions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

# Set up test database (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Test-specific database file
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db function to use test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

# Prepare database before tests start
@pytest.fixture(scope="module")
def setup_database():
    from app import models
    models.Base.metadata.create_all(bind=engine)  # Create tables
    yield
    models.Base.metadata.drop_all(bind=engine)  # Clean up after tests

def clear_database():
    from app import models
    with engine.connect() as connection:
        for table in reversed(models.Base.metadata.sorted_tables):
            connection.execute(table.delete())
        connection.commit()

@pytest.fixture(autouse=True)
def cleanup_database(setup_database):
    yield
    clear_database() #after every test clean the db

# Test user creation-----------------------------------------------------------------
def test_create_user():
    # Simulate POST request to create a new user
    unique_telegram_id= f"123456789_{time.time()}"
    user={"telegram_id": unique_telegram_id, "username": "testuser"}

    response = client.post("/users/",json=user)
    
    # Check if response status code is 200 (success)
    assert response.status_code == 200
    
    # Check if response content contains expected data
    data = response.json()
    assert data["telegram_id"] == user["telegram_id"]
    assert data["username"] == user["username"]
    assert "id" in data  # Ensure user ID is returned
    assert "currency_pairs" in data  # Ensure returned data contains currency_pairs field
    assert data["currency_pairs"] == []  # New user's currency_pairs should be empty

# Test Mark-----------------------------------------------------------------
@pytest.mark.parametrize("telegram_id, username, status", [
    (f"111_{time.time()}", "user1", 200),  # Normal
    (f"111_{time.time()}", "user1", 200),  # Normal
    ("", "user2", 422),                    # Empty telegram_id
    ("", "user2", 422),                    # Empty telegram_id
    (f"222_{time.time()}", "", 200),       # Empty username
    (f"222_{time.time()}", "", 200),       # Empty username
])

def test_create_user_validation(telegram_id, username, status):
    response = client.post("/users/", json={"telegram_id": telegram_id, "username": username})
    assert response.status_code == status

# Test Repeated telegram id-------------------------------------------------------
def test_create_duplicate_telegram_id():

    telegram_id = f"dup_{time.time()}"
    client.post("/users/", json={"telegram_id": telegram_id, "username": "user1"})
    response = client.post("/users/", json={"telegram_id": telegram_id, "username": "user2"})
    assert response.status_code == 422  # Assume uniqueness violation returns 422

# Test user retrieval-----------------------------------------------------------------
def test_read_user():
    # First create a user
    unique_telegram_id= f"123456789_{time.time()}"
    user={"telegram_id": unique_telegram_id, "username": "testuser"}
    create_response = client.post("/users/",json=user)
    user_id = create_response.json()["id"]

    # Retrieve user by ID
    read_response = client.get(f"/users/{user_id}")
    
    # Check response
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["telegram_id"] == user["telegram_id"]
    assert data["username"] == user["username"]
    assert data["id"] == user_id
    assert data["currency_pairs"] == []  # Confirm new user's currency_pairs is empty

# Test non-existent user-----------------------------------------------------------------
def test_read_user_not_found():
    # Test non-existent user ID
    response = client.get("/users/9999")
    assert response.status_code == 404 #Error code returned by read_user() in main.py
    assert response.json()["detail"] == "User not found" #Error message returned by read_user() in main.py

# Test read users (pagination)-----------------------------------------------------------------
def test_read_users_pagination():
    for i in range(5):
        client.post("/users/", json={"telegram_id": f"pag{i}", "username": f"user{i}"})

    response = client.get("/users/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["telegram_id"] == "pag2"

# Test remove user-----------------------------------------------------------------
def test_remove_user():
    
    # First create a user
    unique_telegram_id= f"123456789_{time.time()}"
    user={"telegram_id": unique_telegram_id, "username": "testuser"}

    create_response = client.post("/users/",json=user)
    user_id = create_response.json()["id"]

    #Delete User by id
    delete_response = client.delete(f"/users/{user_id}")

    #Check response
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["telegram_id"] == user["telegram_id"]
    assert data["username"] == user["username"]
    assert data["id"] == user_id

    #check get the same user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found" #Error returned by read_user() in main.py

# Test remove not exist user-----------------------------------------------------------------
def test_not_exit_user():
    #Delete User by id
    user_id=999
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 404

# # ========== Currency Pair-related Tests ========== #

#Create a new CurrencyPair in the database and return the JSON data of the newly created CurrencyPair
@pytest.fixture
def currency_pair():
    response = client.post("/currency_pairs/", json={"pair": f"BTCUSDT_{time.time()}"})
    return response.json()
                                                         
# Test create pair -----------------------------------------------------------------
def test_create_currency_pair():
    
    pair="ETHUSDT"
    response = client.post("/currency_pairs/", json={"pair": pair})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["pair"]==pair

# Test Repeated Pair-----------------------------------------------------------------
def test_create_duplicate_pair():

    pair = "SNEKUSDT"
    client.post("/currency_pairs/", json={"pair": pair})
    response = client.post("/users/", json={"pair": pair})
    assert response.status_code == 422  # Assume uniqueness violation returns 422

# Test read pair-----------------------------------------------------------------
def test_read_currency_pair(currency_pair):
    pair = currency_pair["pair"] #create currency pair using fixture
    response = client.get(f"/currency_pairs/{pair}")
    assert response.status_code == 200
    assert response.json()["pair"] == pair

# Test delete pair-----------------------------------------------------------------
def test_delete_currency_pair(currency_pair):
    pair =currency_pair["pair"]
    response = client.delete(f"/currency_pairs/{pair}")
    assert response.status_code == 200
    assert client.get(f"/currency_pairs/{pair}").status_code == 404

# Test delete not exist pair----------------------------------------------
def test_delete_not_exit_pair():
    pair="AAABBB"
    response = client.delete(f"/currency_pairs/{pair}")
    assert response.status_code == 404

# # ---- User Currency Pair Selection Tests ---- #

@pytest.fixture
def create_user():
    response = client.post("/users/", json={"telegram_id": f"user_{time.time()}", "username": "testuser"})
    return response.json()

def test_create_user_currency_pair(create_user, currency_pair):
    user_id = create_user["id"]
    response = client.post(
        f"/user_currency_pairs/{user_id}",
        json={"currency_pair_id": currency_pair["id"], "selected_exchanges": "Binance,Kraken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["currency_pair_id"] == currency_pair["id"]
    assert data["selected_exchanges"] == "Binance,Kraken"

def test_update_user_currency_pair(create_user):
    user_id = create_user["id"]
    currency_pair_id=1
    client.post(
        f"/user_currency_pairs/{user_id}",
        json={"currency_pair_id": currency_pair_id, "selected_exchanges": "Binance"}
    )
    response = client.put(
        f"/user_currency_pairs/{user_id}/{currency_pair_id}",
        json={"exchange_to_add": "Kraken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Binance" in data["selected_exchanges"]
    assert "Kraken" in data["selected_exchanges"]

def test_delete_user_currency_pair(create_user):
    user_id = create_user["id"]
    currency_pair_id =1
    client.post(
        f"/user_currency_pairs/{user_id}",
        json={"currency_pair_id": currency_pair_id, "selected_exchanges": "Binance"}
    )
    response = client.delete(f"/user_currency_pairs/{user_id}/{currency_pair_id}")
    assert response.status_code == 200

# ---- Advanced Tests ---- #

def test_read_user_mock():
    with patch("app.crud.get_user", return_value={"id": 1, "telegram_id": "mocked", "username": "mock", "currency_pairs": []}):
        response = client.get("/users/1")
        
        assert response.status_code == 200
        
        assert response.json()["telegram_id"] == "mocked"

