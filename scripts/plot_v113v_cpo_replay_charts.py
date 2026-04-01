from __future__ import annotations

import json
from pathlib import Path

import matplotlib.dates as mdates
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
import pandas as pd
import requests


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"
FEED_PATH = REPO_ROOT / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
OUTPUT_DIR = REPO_ROOT / "reports" / "analysis"
ETF_PROXY_SYMBOL = "sh515050"
ETF_PROXY_NAME = "5G通信ETF(515050)"


def load_payload() -> dict:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def to_frames(payload: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    day_df = pd.DataFrame(payload["replay_day_rows"]).copy()
    order_df = pd.DataFrame(payload["executed_order_rows"]).copy()
    day_df["trade_date"] = pd.to_datetime(day_df["trade_date"])
    if not order_df.empty:
        order_df["trade_date"] = pd.to_datetime(order_df["trade_date"])
    return day_df, order_df


def load_feed_frame() -> pd.DataFrame:
    feed_df = pd.read_csv(FEED_PATH)
    feed_df["symbol"] = feed_df["symbol"].astype(str).str.zfill(6)
    feed_df["trade_date"] = pd.to_datetime(feed_df["trade_date"])
    feed_df["day_return"] = feed_df["close"] / feed_df["pre_close"] - 1.0
    feed_df["market_cap_proxy"] = (feed_df["turnover"] * 20.0).clip(lower=4_000_000_000.0)
    return feed_df


def load_etf_proxy_frame() -> pd.DataFrame:
    response = requests.get(
        "https://quotes.sina.cn/cn/api/openapi.php/CN_MarketDataService.getKLineData",
        params={"symbol": ETF_PROXY_SYMBOL, "scale": "240", "ma": "no", "datalen": "1023"},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("result", {}).get("data", [])
    etf_df = pd.DataFrame(rows).copy()
    etf_df["trade_date"] = pd.to_datetime(etf_df["day"])
    etf_df["close"] = etf_df["close"].astype(float)
    return etf_df[["trade_date", "close"]]


def style_time_axis(ax) -> None:
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


def save_equity_curve(day_df: pd.DataFrame, order_df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(day_df["trade_date"], day_df["equity_after_close"], color="#124559", linewidth=2.2, label="Equity")
    ax.plot(day_df["trade_date"], day_df["cash_after_close"], color="#598392", linewidth=1.6, label="Cash")

    if not order_df.empty:
        merged = order_df.merge(
            day_df[["trade_date", "equity_after_close"]],
            on="trade_date",
            how="left",
        )
        color_map = {"open": "#2a9d8f", "add": "#1d3557", "reduce": "#e9c46a", "close": "#e76f51"}
        for action_mode, action_rows in merged.groupby("action_mode"):
            ax.scatter(
                action_rows["trade_date"],
                action_rows["equity_after_close"],
                s=55,
                alpha=0.95,
                color=color_map.get(action_mode, "#6c757d"),
                label=action_mode,
                zorder=5,
            )

    ax.set_title("CPO Full-Board Replay: Equity Curve")
    ax.set_ylabel("Account Value")
    ax.grid(alpha=0.25)
    style_time_axis(ax)
    ax.legend(ncols=3, frameon=False)
    fig.tight_layout()
    output_path = OUTPUT_DIR / "v113v_cpo_equity_curve.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output_path


def save_exposure_breadth(day_df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={"hspace": 0.18})

    axes[0].plot(day_df["trade_date"], day_df["gross_exposure_after_close"], color="#7f5539", linewidth=2)
    axes[0].set_title("Gross Exposure After Close")
    axes[0].set_ylabel("Exposure")
    axes[0].grid(alpha=0.25)

    breadth = day_df["board_context"].apply(lambda x: x["breadth"])
    avg_return = day_df["board_context"].apply(lambda x: x["avg_return"])
    axes[1].bar(day_df["trade_date"], breadth, color="#6a994e", width=2.0, alpha=0.75, label="Breadth")
    axes[1].plot(day_df["trade_date"], avg_return, color="#bc4749", linewidth=1.4, label="Avg Return")
    axes[1].axhline(0.0, color="#333333", linewidth=0.8)
    axes[1].set_title("Board Breadth And Average Return")
    axes[1].set_ylabel("Breadth / Return")
    axes[1].grid(alpha=0.22)
    axes[1].legend(frameon=False)
    style_time_axis(axes[1])

    fig.tight_layout()
    output_path = OUTPUT_DIR / "v113v_cpo_exposure_breadth.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output_path


def save_turnover_orders(day_df: pd.DataFrame, order_df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={"hspace": 0.18})

    axes[0].bar(day_df["trade_date"], day_df["day_turnover_notional"], color="#457b9d", width=2.0)
    axes[0].set_title("Daily Turnover Notional")
    axes[0].set_ylabel("Turnover")
    axes[0].grid(alpha=0.22)

    if order_df.empty:
        order_counts = pd.Series(0, index=day_df["trade_date"])
    else:
        order_counts = order_df.groupby("trade_date").size().reindex(day_df["trade_date"], fill_value=0)
    episode_counts = day_df.set_index("trade_date")["episode_count"]
    axes[1].bar(day_df["trade_date"], order_counts.values, color="#f4a261", width=2.0, label="Executed Orders")
    axes[1].plot(day_df["trade_date"], episode_counts.values, color="#264653", linewidth=1.5, label="Episode Count")
    axes[1].set_title("Orders Vs Episode Days")
    axes[1].set_ylabel("Count")
    axes[1].grid(alpha=0.22)
    axes[1].legend(frameon=False)
    style_time_axis(axes[1])

    fig.tight_layout()
    output_path = OUTPUT_DIR / "v113v_cpo_turnover_orders.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output_path


def save_trade_timeline(order_df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 5))
    if not order_df.empty:
        symbols = list(dict.fromkeys(order_df["symbol"].tolist()))
        symbol_to_y = {symbol: idx for idx, symbol in enumerate(symbols)}
        color_map = {"open": "#2a9d8f", "add": "#1d3557", "reduce": "#e9c46a", "close": "#e76f51"}
        for action_mode, action_rows in order_df.groupby("action_mode"):
            ax.scatter(
                action_rows["trade_date"],
                action_rows["symbol"].map(symbol_to_y),
                s=110,
                alpha=0.95,
                color=color_map.get(action_mode, "#6c757d"),
                label=action_mode,
            )
        ax.set_yticks(list(symbol_to_y.values()))
        ax.set_yticklabels(list(symbol_to_y.keys()))
    ax.set_title("Trade Timeline By Symbol")
    ax.set_ylabel("Symbol")
    ax.grid(alpha=0.22)
    style_time_axis(ax)
    ax.legend(frameon=False, ncols=4)
    fig.tight_layout()
    output_path = OUTPUT_DIR / "v113v_cpo_trade_timeline.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output_path


def build_holding_state_frame(day_df: pd.DataFrame, order_df: pd.DataFrame) -> pd.DataFrame:
    symbol_alias = {
        "300308": "300308",
        "300502": "300502",
        "300757": "300757",
        "688498": "688498",
    }
    qty_by_symbol: dict[str, int] = {}
    state_rows: list[dict[str, object]] = []

    order_map: dict[pd.Timestamp, list[dict[str, object]]] = {}
    if not order_df.empty:
        for row in order_df.to_dict("records"):
            order_map.setdefault(row["trade_date"], []).append(row)

    for row in day_df.to_dict("records"):
        trade_date = row["trade_date"]
        for order in order_map.get(trade_date, []):
            symbol = str(order["symbol"])
            quantity = int(order["quantity"])
            if str(order["action"]) == "buy":
                qty_by_symbol[symbol] = qty_by_symbol.get(symbol, 0) + quantity
            elif str(order["action"]) == "sell":
                qty_by_symbol[symbol] = max(0, qty_by_symbol.get(symbol, 0) - quantity)
                if qty_by_symbol[symbol] == 0:
                    qty_by_symbol.pop(symbol, None)

        active_symbols = [symbol_alias.get(symbol, symbol) for symbol in sorted(qty_by_symbol)]
        holding_label = "flat" if not active_symbols else " + ".join(active_symbols)
        state_rows.append(
            {
                "trade_date": trade_date,
                "holding_label": holding_label,
                "holding_count": len(active_symbols),
            }
        )

    return pd.DataFrame(state_rows)


def save_equity_curve_by_holding_state(day_df: pd.DataFrame, order_df: pd.DataFrame) -> Path:
    state_df = build_holding_state_frame(day_df, order_df)
    merged = day_df.merge(state_df, on="trade_date", how="left")
    merged["equity_norm"] = merged["equity_after_close"] / float(merged["equity_after_close"].iloc[0])

    x = mdates.date2num(merged["trade_date"])
    y = merged["equity_norm"].to_numpy()
    points = list(zip(x, y))
    segments = [[points[i], points[i + 1]] for i in range(len(points) - 1)]
    segment_labels = merged["holding_label"].iloc[:-1].tolist()

    unique_labels = list(dict.fromkeys(merged["holding_label"].tolist()))
    cmap = plt.get_cmap("tab20")
    color_map = {label: cmap(idx % 20) for idx, label in enumerate(unique_labels)}
    colors = [color_map[label] for label in segment_labels]

    fig, ax = plt.subplots(figsize=(15, 7))
    lc = LineCollection(segments, colors=colors, linewidths=2.6, alpha=0.95)
    ax.add_collection(lc)
    ax.autoscale()

    segment_start = 0
    labels = merged["holding_label"].tolist()
    for idx in range(1, len(labels) + 1):
        if idx == len(labels) or labels[idx] != labels[segment_start]:
            seg = merged.iloc[segment_start:idx]
            mid_idx = segment_start + (len(seg) // 2)
            mid_x = merged.iloc[mid_idx]["trade_date"]
            mid_y = merged.iloc[mid_idx]["equity_norm"]
            ax.text(
                mid_x,
                mid_y,
                labels[segment_start],
                fontsize=8,
                color=color_map[labels[segment_start]],
                ha="center",
                va="bottom",
                bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": color_map[labels[segment_start]], "alpha": 0.72},
            )
            segment_start = idx

    ax.set_title("CPO Replay Equity Curve Colored By Holding State")
    ax.set_ylabel("Normalized Equity")
    ax.grid(alpha=0.22)
    style_time_axis(ax)

    legend_handles = []
    for label in unique_labels:
        handle = plt.Line2D([0], [0], color=color_map[label], lw=3, label=label)
        legend_handles.append(handle)
    ax.legend(handles=legend_handles, frameon=False, ncols=3, loc="upper left")

    fig.tight_layout()
    output_path = OUTPUT_DIR / "v113v_cpo_equity_curve_by_holding_state.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output_path


def save_equity_vs_board_curve(day_df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))

    equity_norm = day_df["equity_after_close"] / float(day_df["equity_after_close"].iloc[0])
    board_avg_return = day_df["board_context"].apply(lambda x: x["avg_return"])
    board_curve = (1.0 + board_avg_return).cumprod()

    ax.plot(day_df["trade_date"], equity_norm, color="#124559", linewidth=2.2, label="Strategy Equity")
    ax.plot(day_df["trade_date"], board_curve, color="#bc4749", linewidth=2.0, label="CPO Equal-Weight Board")

    ax.set_title("Strategy Vs CPO Board Curve")
    ax.set_ylabel("Normalized Curve")
    ax.grid(alpha=0.25)
    style_time_axis(ax)
    ax.legend(frameon=False)
    fig.tight_layout()
    output_path = OUTPUT_DIR / "v113v_cpo_equity_vs_board_curve.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output_path


def save_equity_vs_board_proxy_mcap_curve(day_df: pd.DataFrame, feed_df: pd.DataFrame) -> Path:
    weighted = (
        feed_df.groupby("trade_date")
        .apply(
            lambda grp: pd.Series(
                {
                    "proxy_weighted_return": (
                        (grp["day_return"] * grp["market_cap_proxy"]).sum() / grp["market_cap_proxy"].sum()
                    )
                    if grp["market_cap_proxy"].sum() > 0
                    else 0.0
                }
            )
        )
        .reset_index()
    )

    merged = day_df.merge(weighted, on="trade_date", how="left")
    merged["proxy_weighted_return"] = merged["proxy_weighted_return"].fillna(0.0)

    strategy_curve = merged["equity_after_close"] / float(merged["equity_after_close"].iloc[0])
    board_proxy_curve = (1.0 + merged["proxy_weighted_return"]).cumprod()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(merged["trade_date"], strategy_curve, color="#124559", linewidth=2.2, label="Strategy Equity")
    ax.plot(
        merged["trade_date"],
        board_proxy_curve,
        color="#8d0801",
        linewidth=2.0,
        label="CPO Proxy Market-Cap Weighted",
    )

    ax.set_title("Strategy Vs CPO Proxy Market-Cap Weighted Curve")
    ax.set_ylabel("Normalized Curve")
    ax.grid(alpha=0.25)
    style_time_axis(ax)
    ax.legend(frameon=False)
    fig.tight_layout()
    output_path = OUTPUT_DIR / "v113v_cpo_equity_vs_board_proxy_mcap_curve.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output_path


def save_equity_vs_etf_proxy_curve(day_df: pd.DataFrame, etf_df: pd.DataFrame) -> Path:
    merged = day_df.merge(etf_df, on="trade_date", how="left")
    merged["close"] = merged["close"].ffill()

    strategy_curve = merged["equity_after_close"] / float(merged["equity_after_close"].iloc[0])
    etf_curve = merged["close"] / float(merged["close"].iloc[0])

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(merged["trade_date"], strategy_curve, color="#124559", linewidth=2.2, label="Strategy Equity")
    ax.plot(merged["trade_date"], etf_curve, color="#2a9d8f", linewidth=2.0, label=ETF_PROXY_NAME)

    ax.set_title("Strategy Vs ETF Proxy Curve")
    ax.set_ylabel("Normalized Curve")
    ax.grid(alpha=0.25)
    style_time_axis(ax)
    ax.legend(frameon=False)
    fig.tight_layout()
    output_path = OUTPUT_DIR / "v113v_cpo_equity_vs_etf_proxy_curve.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output_path


def build_position_history(day_df: pd.DataFrame, order_df: pd.DataFrame) -> dict[pd.Timestamp, dict[str, int]]:
    qty_by_symbol: dict[str, int] = {}
    position_history: dict[pd.Timestamp, dict[str, int]] = {}

    order_map: dict[pd.Timestamp, list[dict[str, object]]] = {}
    if not order_df.empty:
        for row in order_df.to_dict("records"):
            order_map.setdefault(row["trade_date"], []).append(row)

    for trade_date in day_df["trade_date"]:
        for order in order_map.get(trade_date, []):
            symbol = str(order["symbol"])
            quantity = int(order["quantity"])
            if str(order["action"]) == "buy":
                qty_by_symbol[symbol] = qty_by_symbol.get(symbol, 0) + quantity
            elif str(order["action"]) == "sell":
                new_qty = max(0, qty_by_symbol.get(symbol, 0) - quantity)
                if new_qty <= 0:
                    qty_by_symbol.pop(symbol, None)
                else:
                    qty_by_symbol[symbol] = new_qty
        position_history[trade_date] = dict(qty_by_symbol)

    return position_history


def save_full_invested_curve(day_df: pd.DataFrame, order_df: pd.DataFrame, feed_df: pd.DataFrame) -> Path:
    feed_close = (
        feed_df[["trade_date", "symbol", "close"]]
        .drop_duplicates(subset=["trade_date", "symbol"])
        .set_index(["trade_date", "symbol"])["close"]
    )
    position_history = build_position_history(day_df, order_df)

    full_invested_curve = [1.0]
    trade_dates = day_df["trade_date"].tolist()

    for idx in range(1, len(trade_dates)):
        prev_date = trade_dates[idx - 1]
        curr_date = trade_dates[idx]
        prev_positions = position_history.get(prev_date, {})

        if not prev_positions:
            full_invested_curve.append(full_invested_curve[-1])
            continue

        prev_values: dict[str, float] = {}
        for symbol, qty in prev_positions.items():
            try:
                prev_close = float(feed_close.loc[(prev_date, symbol)])
            except KeyError:
                continue
            prev_values[symbol] = qty * prev_close

        total_prev_value = sum(prev_values.values())
        if total_prev_value <= 0:
            full_invested_curve.append(full_invested_curve[-1])
            continue

        weighted_return = 0.0
        for symbol, prev_value in prev_values.items():
            try:
                prev_close = float(feed_close.loc[(prev_date, symbol)])
                curr_close = float(feed_close.loc[(curr_date, symbol)])
            except KeyError:
                continue
            if prev_close <= 0:
                continue
            symbol_return = curr_close / prev_close - 1.0
            weighted_return += (prev_value / total_prev_value) * symbol_return

        full_invested_curve.append(full_invested_curve[-1] * (1.0 + weighted_return))

    actual_curve = day_df["equity_after_close"] / float(day_df["equity_after_close"].iloc[0])
    full_invested_series = pd.Series(full_invested_curve, index=day_df["trade_date"])

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(day_df["trade_date"], actual_curve, color="#124559", linewidth=2.2, label="Actual Equity")
    ax.plot(
        day_df["trade_date"],
        full_invested_series.values,
        color="#d62828",
        linewidth=2.2,
        label="Full-Invested Same-Holdings Curve",
    )

    ax.set_title("CPO Replay: Remove Cash Drag With Full-Invested Same-Holdings Curve")
    ax.set_ylabel("Normalized Curve")
    ax.grid(alpha=0.25)
    style_time_axis(ax)
    ax.legend(frameon=False)
    fig.tight_layout()
    output_path = OUTPUT_DIR / "v113v_cpo_full_invested_same_holdings_curve.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main() -> None:
    payload = load_payload()
    day_df, order_df = to_frames(payload)
    feed_df = load_feed_frame()
    etf_df = load_etf_proxy_frame()
    paths = [
        save_equity_curve(day_df, order_df),
        save_equity_curve_by_holding_state(day_df, order_df),
        save_full_invested_curve(day_df, order_df, feed_df),
        save_equity_vs_board_curve(day_df),
        save_equity_vs_board_proxy_mcap_curve(day_df, feed_df),
        save_equity_vs_etf_proxy_curve(day_df, etf_df),
        save_exposure_breadth(day_df),
        save_turnover_orders(day_df, order_df),
        save_trade_timeline(order_df),
    ]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
