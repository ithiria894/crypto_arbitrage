# Crypto Arbitrage FastAPI Application

This application is a FastAPI-based service designed to manage users and their selected cryptocurrency pairs for arbitrage opportunities. It includes a Telegram bot for user interaction and real-time monitoring of price differences across multiple exchanges.

## Project Motivation

This project was inspired by the observation of price discrepancies for cryptocurrencies across different exchanges. These price differences create arbitrage opportunities - the ability to profit by simultaneously buying an asset on one exchange where the price is lower and selling it on another exchange where the price is higher.

Having more capital allows traders to:
- Take advantage of larger arbitrage opportunities
- Offset fixed costs like fees more effectively
- Generate meaningful returns even from smaller price differences
- Have more flexibility in position sizing

![Trump Arbitrage Example](trump.png)
For example:
- Exchange A might list TRUMPUSDT at $16
- While Exchange B lists it at $17.07
- This $1.07 difference represents a 6.69% price gap. Trading with 5000 USDT could yield approximately 334.50 USDT in potential profit (before fees)


## Profit Potential Scales with Capital

The potential profit from arbitrage trading increases proportionally with the amount of capital deployed:

Example with TRUMPUSDT price difference of 6.69%:
- Trading with 5,000 USDT → ~334.50 USDT profit
- Trading with 10,000 USDT → ~669 USDT profit  
- Trading with 50,000 USDT → ~3,345 USDT profit
- Trading with 100,000 USDT → ~6,690 USDT profit

*Note: These are theoretical maximum profits before considering:
- Trading fees
- Transfer fees between exchanges
- Slippage
- Available liquidity
- Network congestion
- Other execution risks




The application helps users:
1. Monitor these price differences in real-time
2. Track multiple currency pairs across selected exchanges
3. Get notifications when significant arbitrage opportunities arise
4. Make more informed trading decisions

By automating the monitoring process and providing instant notifications through Telegram, traders can quickly identify and act on profitable arbitrage opportunities that might otherwise be missed through manual observation.


## Features

- **User Management**: Create, read, update, and delete user accounts.
- **Currency Pair Management**: Add, view, and remove cryptocurrency pairs.
- **User Currency Pair Selection**: Users can select currency pairs and specify exchanges to monitor.
- **Real-time Monitoring**: Check real-time prices and calculate arbitrage opportunities.
- **Telegram Bot Integration**: Interact with the application via a Telegram bot.

## Getting Started

### Prerequisites

- Python 3.7+
- FastAPI
- SQLAlchemy
- SQLite (or another database of your choice)
- Telegram Bot Token

### Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory.
   - Add your Telegram Bot Token:
     ```
     TELEGRAM_BOT_TOKEN=your_telegram_bot_token
     ```

4. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API**:
   - Open your browser and go to `http://localhost:8000/docs` to view the interactive API documentation.

## API Endpoints

### User Endpoints

- **Create User**: `POST /users/`
- **Get User by ID**: `GET /users/{user_id}`
- **Get All Users**: `GET /users/`
- **Delete User**: `DELETE /users/{user_id}`

### Currency Pair Endpoints

- **Create Currency Pair**: `POST /currency_pairs/`
- **Get Currency Pair by Name**: `GET /currency_pairs/{pair}`
- **Get All Currency Pairs**: `GET /currency_pairs/`
- **Delete Currency Pair**: `DELETE /currency_pairs/{pair}`

### User Currency Pair Endpoints

- **Create User Currency Pair**: `POST /user_currency_pairs/{user_id}`
- **Get User Currency Pairs**: `GET /user_currency_pairs/{user_id}`
- **Update Exchanges for User Currency Pair**: `PUT /user_currency_pairs/{user_id}/{currency_pair_id}`
- **Delete User Currency Pair**: `DELETE /user_currency_pairs/{user_id}/{currency_pair_id}`

## Telegram Bot Commands

- **/start**: Create a new account or welcome back an existing user.
- **/add_pair**: Add a currency pair to monitor.
- **/list_pairs**: View your watchlist.
- **/remove_pair**: Remove a currency pair from your watchlist.
- **/add_exchange**: Add an exchange to monitor.
- **/remove_exchange**: Remove an exchange from monitoring.
- **/list_available_pairs**: View all available currency pairs.
- **/list_on_time**: List real-time arbitrage opportunities.
- **/delete_me**: Delete your account and stop monitoring.
- **/help**: Show all commands.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

This project is licensed under the MIT License.