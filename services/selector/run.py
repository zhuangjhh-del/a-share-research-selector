from __future__ import annotations

import argparse
import json
import logging
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

from services.selector.calendar import is_trading_day
from services.selector.providers.market_data import load_daily_snapshot
from services.selector.strategies.demo_strategy import STRATEGY_DESCRIPTION, STRATEGY_VERSION, select

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "apps" / "site"
DATA = SITE / "data"
BACKUPS = ROOT / "runtime" / "backups"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    day = date.fromisoformat(args.as_of)
    DATA.mkdir(parents=True, exist_ok=True)
    if not is_trading_day(day):
        write_status(day, "skipped", "非交易日，不执行盘后选股")
        return
    stocks = load_daily_snapshot(args.as_of)
    selections = select(stocks)
    payload = {
        "asOf": args.as_of,
        "updatedAt": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "status": "success",
        "mode": "免费研究版（盘后数据）",
        "strategy": {"version": STRATEGY_VERSION, "description": STRATEGY_DESCRIPTION},
        "source": "演示快照" if not __import__("os").getenv("MARKET_DATA_URL") else "已配置的获许可盘后数据源",
        "results": [item.to_dict() for item in selections],
    }
    output = DATA / "latest.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    history = DATA / "history.json"
    records = json.loads(history.read_text(encoding="utf-8")) if history.exists() else []
    records = [r for r in records if r.get("asOf") != args.as_of]
    records.insert(0, {"asOf": args.as_of, "count": len(selections), "strategyVersion": STRATEGY_VERSION})
    history.write_text(json.dumps(records[:365], ensure_ascii=False, indent=2), encoding="utf-8")
    BACKUPS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output, BACKUPS / f"selection-{args.as_of}.json")
    write_status(day, "success", f"完成：{len(selections)} 只入选")
    logging.info("completed %s", payload["updatedAt"])


def write_status(day: date, status: str, message: str) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "status.json").write_text(json.dumps({"asOf": day.isoformat(), "status": status, "message": message}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
