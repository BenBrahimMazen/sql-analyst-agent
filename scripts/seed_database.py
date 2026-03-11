import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
import os

fake = Faker()
random.seed(42)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'finance.db')

STOCKS = [
    ("AAPL", "Apple Inc.", "Technology", 189.50),
    ("MSFT", "Microsoft Corp.", "Technology", 415.20),
    ("GOOGL", "Alphabet Inc.", "Technology", 175.30),
    ("AMZN", "Amazon.com Inc.", "Consumer Discretionary", 185.60),
    ("TSLA", "Tesla Inc.", "Automotive", 177.80),
    ("JPM", "JPMorgan Chase", "Financial", 198.40),
    ("BAC", "Bank of America", "Financial", 38.90),
    ("GS", "Goldman Sachs", "Financial", 462.10),
    ("JNJ", "Johnson & Johnson", "Healthcare", 158.70),
    ("PFE", "Pfizer Inc.", "Healthcare", 28.40),
    ("XOM", "Exxon Mobil", "Energy", 112.30),
    ("CVX", "Chevron Corp.", "Energy", 152.60),
    ("WMT", "Walmart Inc.", "Consumer Staples", 67.80),
    ("MCD", "McDonald's Corp.", "Consumer Staples", 295.40),
    ("NFLX", "Netflix Inc.", "Communication", 628.90),
]

def create_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE NOT NULL,
            company_name TEXT NOT NULL,
            sector TEXT NOT NULL,
            current_price REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price_per_share REAL NOT NULL,
            total_value REAL NOT NULL,
            transaction_date TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            shares_owned INTEGER NOT NULL,
            average_buy_price REAL NOT NULL,
            UNIQUE(user_id, ticker)
        );

        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open_price REAL NOT NULL,
            high_price REAL NOT NULL,
            low_price REAL NOT NULL,
            close_price REAL NOT NULL,
            volume INTEGER NOT NULL,
            UNIQUE(ticker, date)
        );
    """)
    conn.commit()

def seed_stocks(conn):
    conn.executemany(
        "INSERT OR IGNORE INTO stocks (ticker, company_name, sector, current_price) VALUES (?,?,?,?)",
        STOCKS
    )
    conn.commit()
    print(f"✅ Seeded {len(STOCKS)} stocks")

def seed_transactions(conn):
    transactions = []
    today = datetime.today()

    for _ in range(500):
        stock = random.choice(STOCKS)
        ticker, _, _, base_price = stock
        user_id = random.randint(1, 20)
        tx_type = random.choice(["BUY", "SELL"])
        quantity = random.randint(1, 100)
        # Vary price realistically around base price
        price = round(base_price * random.uniform(0.85, 1.15), 2)
        total = round(price * quantity, 2)
        days_ago = random.randint(0, 365)
        date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        transactions.append((user_id, ticker, tx_type, quantity, price, total, date))

    conn.executemany(
        """INSERT INTO transactions
           (user_id, ticker, transaction_type, quantity, price_per_share, total_value, transaction_date)
           VALUES (?,?,?,?,?,?,?)""",
        transactions
    )
    conn.commit()
    print(f"✅ Seeded {len(transactions)} transactions")

def seed_portfolio(conn):
    portfolio = {}
    for user_id in range(1, 21):
        num_stocks = random.randint(2, 8)
        chosen = random.sample(STOCKS, num_stocks)
        for stock in chosen:
            ticker, _, _, base_price = stock
            shares = random.randint(5, 200)
            avg_price = round(base_price * random.uniform(0.80, 1.10), 2)
            key = (user_id, ticker)
            if key not in portfolio:
                portfolio[key] = (user_id, ticker, shares, avg_price)

    conn.executemany(
        """INSERT OR IGNORE INTO portfolio
           (user_id, ticker, shares_owned, average_buy_price)
           VALUES (?,?,?,?)""",
        list(portfolio.values())
    )
    conn.commit()
    print(f"✅ Seeded {len(portfolio)} portfolio entries")

def seed_market_data(conn):
    records = []
    today = datetime.today()

    for ticker, _, _, base_price in STOCKS:
        price = base_price
        for days_ago in range(365, -1, -1):
            date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            change = random.uniform(-0.03, 0.03)
            open_p = round(price, 2)
            close_p = round(price * (1 + change), 2)
            high_p = round(max(open_p, close_p) * random.uniform(1.0, 1.02), 2)
            low_p = round(min(open_p, close_p) * random.uniform(0.98, 1.0), 2)
            volume = random.randint(1_000_000, 50_000_000)
            records.append((ticker, date, open_p, high_p, low_p, close_p, volume))
            price = close_p

    conn.executemany(
        """INSERT OR IGNORE INTO market_data
           (ticker, date, open_price, high_price, low_price, close_price, volume)
           VALUES (?,?,?,?,?,?,?)""",
        records
    )
    conn.commit()
    print(f"✅ Seeded {len(records)} market data records")

if __name__ == "__main__":
    print("🌱 Seeding finance database...")
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    seed_stocks(conn)
    seed_transactions(conn)
    seed_portfolio(conn)
    seed_market_data(conn)
    conn.close()
    print("\n🎉 Database ready at data/finance.db")