import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from trading_strategy import (
    calculate_moving_averages,
    get_stock_data,
    identify_golden_cross,
    implement_strategy,
)

st.set_page_config(page_title="MSFT Strategy Dashboard", layout="wide")


def load_strategy_data():
    data = get_stock_data("MSFT")
    data = calculate_moving_averages(data)
    data = identify_golden_cross(data)
    positions = implement_strategy(data)
    return data, positions


def render_chart(data, positions):
    st.title("Price Chart")
    st.caption("Whole period view of MSFT close price, 50-day MA, 200-day MA, plus buy/sell markers.")

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(data.index, data["Close"], label="Close Price", color="navy", linewidth=2)
    ax.plot(data.index, data["MA50"], label="Short-term MA (50)", color="orange", linewidth=1.8)
    ax.plot(data.index, data["MA200"], label="Long-term MA (200)", color="green", linewidth=1.8)

    if not positions.empty:
        buy_dates = positions["BuyDate"]
        sell_dates = positions["SellDate"]
        buy_prices = positions["BuyPrice"]
        sell_prices = positions["SellPrice"]

        ax.scatter(buy_dates, buy_prices, color="green", s=70, marker="o", label="Buy")
        ax.scatter(sell_dates, sell_prices, color="red", s=70, marker="x", label="Sell")

    ax.set_title("MSFT Price and Moving Averages")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    st.pyplot(fig)


def render_statistics(positions):
    st.title("Overall Trade Statistics")

    if positions.empty:
        st.info("No trading signals were generated for this strategy on the selected dataset.")
        return

    total_trades = len(positions)
    win_trades = int((positions["ProfitPct"] > 0).sum())
    loss_trades = total_trades - win_trades
    win_rate = (win_trades / total_trades) * 100 if total_trades else 0
    avg_profit = positions["ProfitPct"].mean()
    avg_holding = positions["HoldingDays"].mean()
    target_reached = int((positions["SellReason"] == "Target reached").sum())
    max_period = int((positions["SellReason"] == "Max holding period").sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", total_trades)
    col2.metric("Winning Trades", win_trades)
    col3.metric("Losing Trades", loss_trades)
    col4.metric("Win Rate", f"{win_rate:.2f}%")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Average Profit", f"{avg_profit:.2f}%")
    col6.metric("Average Holding Days", f"{avg_holding:.1f}")
    col7.metric("Target Reached", target_reached)
    col8.metric("Max Period Exits", max_period)

    st.subheader("Trade Summary Table")
    summary = pd.DataFrame(
        {
            "Metric": [
                "Total Trades",
                "Winning Trades",
                "Losing Trades",
                "Win Rate (%)",
                "Average Profit (%)",
                "Average Holding Days",
                "Target Reached",
                "Max Holding Period Exit",
            ],
            "Value": [
                total_trades,
                win_trades,
                loss_trades,
                round(win_rate, 2),
                round(avg_profit, 2),
                round(avg_holding, 2),
                target_reached,
                max_period,
            ],
        }
    )
    st.dataframe(summary, use_container_width=True)


def render_trades(positions):
    st.title("Detailed Trades")

    if positions.empty:
        st.info("No detailed trades available for the selected strategy.")
        return

    display = positions.copy()
    display["BuyDate"] = display["BuyDate"].dt.strftime("%Y-%m-%d")
    display["SellDate"] = display["SellDate"].dt.strftime("%Y-%m-%d")
    display["BuyPrice"] = display["BuyPrice"].round(2)
    display["SellPrice"] = display["SellPrice"].round(2)
    display["ProfitPct"] = display["ProfitPct"].round(2)
    st.dataframe(display, use_container_width=True)


page = st.sidebar.radio("Navigation", ["Price Chart", "Trade Statistics", "Detailed Trades"])

data, positions = load_strategy_data()

if page == "Price Chart":
    render_chart(data, positions)
elif page == "Trade Statistics":
    render_statistics(positions)
else:
    render_trades(positions)
