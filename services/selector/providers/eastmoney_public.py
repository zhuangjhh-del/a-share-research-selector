"""Best-effort public research feed via AKShare/Eastmoney.

This is not an Eastmoney Choice API.  It has no contract, SLA, or redistribution
right, so only derived research output is published and source failures block runs.
"""
from __future__ import annotations

from datetime import datetime
from time import sleep


class PublicFeedUnavailable(RuntimeError):
    pass


def fetch_market_snapshot() -> dict:
    # Public sources are often transiently rate-limited. Retry here rather than
    # publishing an upstream exception to the website.
    quotes = indices = None
    for attempt in range(4):
        try:
            import akshare as ak
            quotes = ak.stock_zh_a_spot_em()
            indices = ak.stock_zh_index_spot_em(symbol="沪深重要指数")
            break
        except Exception:
            if attempt == 3:
                raise PublicFeedUnavailable("东方财富公开数据暂时无法连接；已自动重试 4 次")
            sleep(2 ** attempt)
    required = {"代码", "名称", "最新价", "涨跌幅", "成交额", "量比", "换手率", "总市值", "市盈率-动态", "振幅"}
    missing = required - set(quotes.columns)
    if missing or quotes.empty:
        raise PublicFeedUnavailable(f"行情字段不足：{','.join(sorted(missing)) or '空快照'}")
    advancing = int((quotes["涨跌幅"] > 0).sum())
    declining = int((quotes["涨跌幅"] < 0).sum())
    return {
        "capturedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "stockCount": int(len(quotes)),
        "advancing": advancing,
        "declining": declining,
        "advanceDeclineRatio": round(advancing / max(declining, 1), 3),
        "indicesAvailable": int(len(indices)),
        "feed": "东方财富公开数据（AKShare）",
        # Full scoring is deliberately blocked until MA20, board persistence, unlock,
        # technical pattern, and fund-flow data are all supplied by a compliant source.
        "missingForEightLayer": ["三大指数 MA20", "板块连续活跃度", "未来90日解禁", "MACD/KDJ/形态", "主力5日及当日净流入", "14:00-14:40资金流", "近20日涨停"],
    }
