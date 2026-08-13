from __future__ import annotations

from datetime import date


# 兜底清单：每年开年通过交易所公布的休市安排更新；仅用于拒绝显然非交易日。
# 在线正式数据源接入后，TradingCalendarProvider 应改为该供应商的交易日历。
KNOWN_CLOSED_DAYS = {
    date(2026, 1, 1), date(2026, 1, 2),
    date(2026, 2, 16), date(2026, 2, 17), date(2026, 2, 18),
    date(2026, 2, 19), date(2026, 2, 20), date(2026, 2, 23),
}


def is_trading_day(day: date) -> bool:
    return day.weekday() < 5 and day not in KNOWN_CLOSED_DAYS
