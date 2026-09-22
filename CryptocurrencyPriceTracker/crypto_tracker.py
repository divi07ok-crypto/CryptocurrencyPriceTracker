import sqlite3
import os
import time
from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def save_to_database(df):
    """Save scraped cryptocurrency data into SQLite database."""

    connection = sqlite3.connect("crypto.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crypto_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            coin_name TEXT,
            symbol TEXT,
            price TEXT,
            change_24h TEXT,
            market_cap TEXT
        )
    """)

    for _, row in df.iterrows():

        cursor.execute("""
            INSERT INTO crypto_prices
            (timestamp, coin_name, symbol, price, change_24h, market_cap)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row["Timestamp"],
            row["Coin Name"],
            row["Symbol"],
            row["Price"],
            row["24h Change"],
            row["Market Cap"]
        ))

    connection.commit()
    connection.close()

    print("Database updated successfully!")
    print("Database: crypto.db")
    print("Table: crypto_prices")


def scrape_crypto_data():

    print("Starting cryptocurrency data collection...")

    # Chrome settings
    options = webdriver.ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1920,1080")

    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-renderer-backgrounding")

    # Start Chrome
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:

        driver.set_page_load_timeout(60)

        print("Opening CoinMarketCap...")

        driver.get("https://coinmarketcap.com/")

        time.sleep(8)

        print("CoinMarketCap opened successfully!")

        # Find table rows
        rows = driver.find_elements(
            By.XPATH,
            "//table/tbody/tr"
        )

        print("Total rows found:", len(rows))

        crypto_data = []

        # Extract Top 10
        for row in rows:

            try:

                columns = row.find_elements(
                    By.TAG_NAME,
                    "td"
                )

                if len(columns) >= 8:

                    name_text = columns[2].text

                    # Skip CoinMarketCap Index
                    if "CoinMarketCap 20 Index" in name_text:
                        continue

                    name_parts = name_text.split("\n")

                    coin_name = name_parts[0]

                    symbol = (
                        name_parts[1]
                        if len(name_parts) > 1
                        else ""
                    )

                    price = columns[3].text

                    change_24h = columns[5].text

                    market_cap = columns[7].text

                    crypto_data.append({
                        "Rank": len(crypto_data) + 1,
                        "Coin Name": coin_name,
                        "Symbol": symbol,
                        "Price": price,
                        "24h Change": change_24h,
                        "Market Cap": market_cap
                    })

                    if len(crypto_data) == 10:
                        break

            except Exception as e:

                print("Error reading row:", e)

        # Check data
        if len(crypto_data) == 0:

            print("No cryptocurrency data found.")

            return None

        # Create DataFrame
        df = pd.DataFrame(crypto_data)

        # Timestamp
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        df.insert(
            0,
            "Timestamp",
            timestamp
        )

        # ------------------------------------------------
        # SAVE TO CSV
        # ------------------------------------------------

        csv_file = "crypto_prices_history.csv"

        file_exists = os.path.exists(csv_file)

        df.to_csv(
            csv_file,
            mode="a",
            header=not file_exists,
            index=False
        )

        print()
        print("CSV updated successfully!")
        print("File:", csv_file)

        # ------------------------------------------------
        # SAVE TO SQLITE DATABASE
        # ------------------------------------------------

        save_to_database(df)

        # ------------------------------------------------
        # DISPLAY TOP 10
        # ------------------------------------------------

        print()
        print("Top 10 Cryptocurrencies")
        print("=" * 70)

        for coin in crypto_data:

            print(
                f"{coin['Rank']}. "
                f"{coin['Coin Name']} "
                f"({coin['Symbol']}) | "
                f"Price: {coin['Price']} | "
                f"24h: {coin['24h Change']} | "
                f"Market Cap: {coin['Market Cap']}"
            )

        print()
        print("Timestamp:", timestamp)

        # ------------------------------------------------
        # PRICE FILTER
        # ------------------------------------------------

        df["Price Numeric"] = (
            df["Price"]
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
        )

        df["Price Numeric"] = pd.to_numeric(
            df["Price Numeric"],
            errors="coerce"
        )

        price_limit = 1000

        price_filtered = df[
            df["Price Numeric"] > price_limit
        ]

        print()
        print("PRICE FILTER")
        print("-" * 50)

        print(
            f"Cryptocurrencies with price > "
            f"${price_limit}:"
        )

        for _, coin in price_filtered.iterrows():

            print(
                f"{coin['Coin Name']} "
                f"({coin['Symbol']}) - "
                f"{coin['Price']}"
            )

        # ------------------------------------------------
        # 24H CHANGE FILTER
        # ------------------------------------------------

        df["Change Numeric"] = (
            df["24h Change"]
            .str.replace("%", "", regex=False)
        )

        df["Change Numeric"] = pd.to_numeric(
            df["Change Numeric"],
            errors="coerce"
        )

        change_limit = 5

        change_filtered = df[
            df["Change Numeric"] > change_limit
        ]

        print()
        print("24H CHANGE FILTER")
        print("-" * 50)

        print(
            f"Cryptocurrencies with 24h "
            f"change > {change_limit}%:"
        )

        for _, coin in change_filtered.iterrows():

            print(
                f"{coin['Coin Name']} "
                f"({coin['Symbol']}) - "
                f"{coin['24h Change']}"
            )

        print()
        print("Historical data saved successfully!")
        print("Database and CSV updated successfully!")

        return df

    except Exception as e:

        print()
        print("ERROR while collecting data:")
        print(e)

        return None

    finally:

        driver.quit()

        print()
        print(
            "Cryptocurrency Price Tracker Completed!"
        )


# ------------------------------------------------
# PROGRAM START
# ------------------------------------------------

if __name__ == "__main__":

    scrape_crypto_data()