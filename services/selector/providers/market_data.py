from __future__ import annotations

import csv
import io
import os
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from services.selector.models import StockBar

REQUIRED_COLUMNS = {"code", "name", "close", "volume", "amount", "ma5", "ma20", "listed_days", "is_st", "is_suspended"}


class MarketDataError(RuntimeError):
    pass


def load_daily_snapshot(as_of: str) -> list[StockBar]:
    """读取已获许可的盘后 CSV；未配置时读取演示数据。

    MARKET_DATA_URL 可为 HTTPS URL，CSV 必须是当日完整快照且包含 REQUIRED_COLUMNS。
    本模块故意不内置任何网页抓取或未授权的免费行情接口。
    """
    url = os.getenv("MARKET_DATA_URL")
    if url:
        try:
            with urlopen(url.format(as_of=as_of), timeout=30) as response:
                content = response.read().decode("utf-8")
        except (URLError, OSError) as exc:
            raise MarketDataError(f"数据源不可用: {exc}") from exc
    else:
        content = Path("data/demo_snapshot.csv").read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
        raise MarketDataError("数据快照字段不完整")
    result = []
    for row in reader:
        try:
            result.append(StockBar(
                code=row["code"], name=row["name"], close=float(row["close"]),
                volume=float(row["volume"]), amount=float(row["amount"]),
                ma5=float(row["ma5"]), ma20=float(row["ma20"]),
                listed_days=int(row["listed_days"]), is_st=row["is_st"].lower() == "true",
                is_suspended=row["is_suspended"].lower() == "true",
            ))
        except (TypeError, ValueError, KeyError) as exc:
            raise MarketDataError(f"数据行无效: {row}") from exc
    if not result:
        raise MarketDataError("数据快照为空")
    return result
