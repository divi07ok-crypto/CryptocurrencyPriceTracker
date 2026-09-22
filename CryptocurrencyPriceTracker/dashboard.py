import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
from crypto_tracker import scrape_crypto_data

# --------------------------------------------------
# Page Settings
# --------------------------------------------------
st.set_page_config(
    page_title="Cryptocurrency Price Tracker",
    page_icon="₿",
    layout="wide"
)

st.title("₿ Cryptocurrency Price Tracker")
st.write("Real-time cryptocurrency monitoring dashboard")


# --------------------------------------------------
# Refresh Data Button
# --------------------------------------------------
if st.button("🔄 Refresh Data", type="primary"):

    with st.spinner("Fetching latest cryptocurrency prices..."):

        new_data = scrape_crypto_data()

    if new_data is not None:

        st.success("✅ Latest data collected and database updated!")

        st.rerun()

    else:

        st.error("❌ Unable to collect cryptocurrency data.")


# --------------------------------------------------
# Read Data From SQLite Database
# --------------------------------------------------
try:

    connection = sqlite3.connect("crypto.db")

    df = pd.read_sql_query(
        """
        SELECT
            timestamp AS Timestamp,
            coin_name AS "Coin Name",
            symbol AS Symbol,
            price AS Price,
            change_24h AS "24h Change",
            market_cap AS "Market Cap"
        FROM crypto_prices
        ORDER BY id DESC
        """,
        connection
    )

    connection.close()


    # --------------------------------------------------
    # Check Data
    # --------------------------------------------------
    if df.empty:

        st.warning("⚠️ No cryptocurrency data available.")

        st.info("Click 'Refresh Data' to collect data.")


    else:

        # --------------------------------------------------
        # Latest Timestamp
        # --------------------------------------------------
        latest_timestamp = df["Timestamp"].iloc[0]

        st.info(
            f"🕒 Last Updated: {latest_timestamp}"
        )


        # --------------------------------------------------
        # Get Latest 10 Cryptocurrencies
        # --------------------------------------------------
        latest_data = df.head(10).copy()


        # --------------------------------------------------
        # Convert Price to Numeric
        # --------------------------------------------------
        latest_data["Price Numeric"] = (
            latest_data["Price"]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
        )

        latest_data["Price Numeric"] = pd.to_numeric(
            latest_data["Price Numeric"],
            errors="coerce"
        )


        # --------------------------------------------------
        # Convert 24h Change to Numeric
        # --------------------------------------------------
        latest_data["Change Numeric"] = (
            latest_data["24h Change"]
            .astype(str)
            .str.replace("%", "", regex=False)
        )

        latest_data["Change Numeric"] = pd.to_numeric(
            latest_data["Change Numeric"],
            errors="coerce"
        )


        # --------------------------------------------------
        # Market Overview
        # --------------------------------------------------
        st.subheader("📈 Market Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🪙 Cryptocurrencies",
            len(latest_data)
        )

        highest_price = latest_data["Price Numeric"].max()

        col2.metric(
            "💰 Highest Price",
            f"${highest_price:,.2f}"
        )

        highest_change = latest_data["Change Numeric"].max()

        col3.metric(
            "🚀 Highest 24h Change",
            f"{highest_change:.2f}%"
        )


        # --------------------------------------------------
        # Top 10 Cryptocurrencies
        # --------------------------------------------------
        st.subheader("📊 Top 10 Cryptocurrencies")

        display_df = latest_data[
            [
                "Coin Name",
                "Symbol",
                "Price",
                "24h Change",
                "Market Cap"
            ]
        ]


        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )


        # --------------------------------------------------
        # DOWNLOAD EXCEL
        # --------------------------------------------------
        st.subheader("📥 Download Data")

        excel_buffer = BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            display_df.to_excel(
                writer,
                index=False,
                sheet_name="Crypto Prices"
            )

        excel_buffer.seek(0)

        st.download_button(
            label="📥 Download Excel",
            data=excel_buffer.getvalue(),
            file_name="crypto_prices.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel"
        )


        # --------------------------------------------------
        # Price Comparison Chart
        # --------------------------------------------------
        st.subheader("💰 Cryptocurrency Price Comparison")

        price_chart = latest_data[
            ["Coin Name", "Price Numeric"]
        ].set_index("Coin Name")

        st.bar_chart(
            price_chart,
            width="stretch"
        )


        # --------------------------------------------------
        # 24h Change Chart
        # --------------------------------------------------
        st.subheader("📈 24h Percentage Change")

        change_chart = latest_data[
            ["Coin Name", "Change Numeric"]
        ].set_index("Coin Name")

        st.bar_chart(
            change_chart,
            width="stretch"
        )


        # --------------------------------------------------
        # Cryptocurrency Filters
        # --------------------------------------------------
        st.subheader("🔎 Cryptocurrency Filters")


        # --------------------------------------------------
        # Price Filter
        # --------------------------------------------------
        st.write("💰 Price Filter")

        price_limit = st.number_input(
            "Show cryptocurrencies with price greater than ($)",
            min_value=0.0,
            value=1000.0,
            step=100.0
        )

        price_filtered = latest_data[
            latest_data["Price Numeric"] > price_limit
        ]

        if not price_filtered.empty:

            st.dataframe(
                price_filtered[
                    [
                        "Coin Name",
                        "Symbol",
                        "Price",
                        "24h Change",
                        "Market Cap"
                    ]
                ],
                width="stretch",
                hide_index=True
            )

        else:

            st.warning(
                "No cryptocurrency found above this price."
            )


        # --------------------------------------------------
        # 24h Change Filter
        # --------------------------------------------------
        st.write("📈 24h Change Filter")

        change_limit = st.number_input(
            "Show cryptocurrencies with 24h change greater than (%)",
            min_value=0.0,
            value=5.0,
            step=1.0
        )

        change_filtered = latest_data[
            latest_data["Change Numeric"] > change_limit
        ]

        if not change_filtered.empty:

            st.dataframe(
                change_filtered[
                    [
                        "Coin Name",
                        "Symbol",
                        "Price",
                        "24h Change",
                        "Market Cap"
                    ]
                ],
                width="stretch",
                hide_index=True
            )

        else:

            st.warning(
                "No cryptocurrency found above this 24h change."
            )


        # --------------------------------------------------
        # Database Information
        # --------------------------------------------------
        st.subheader("🗄️ Database Information")

        connection = sqlite3.connect("crypto.db")

        total_records = pd.read_sql_query(
            "SELECT COUNT(*) AS count FROM crypto_prices",
            connection
        )["count"].iloc[0]

        connection.close()

        st.write(
            f"📌 Total records stored in database: **{total_records}**"
        )

        st.write(
            "📁 Database: **crypto.db**"
        )

        st.write(
            "📋 Table: **crypto_prices**"
        )


# --------------------------------------------------
# Error Handling
# --------------------------------------------------
except Exception as e:

    st.error(
        f"❌ Error loading database: {e}"
    )

    st.info(
        "Click 'Refresh Data' to collect data."
    )