from __future__ import annotations

import argparse
import json
import logging
import shutil
from datetime import date, datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from services.selector.calendar import is_trading_day
from services.selector.providers.multisource_public import MultiSourceUnavailable, fetch_candidates

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "apps" / "site"
DATA = SITE / "data"
BACKUPS = ROOT / "runtime" / "backups"
SHANGHAI = ZoneInfo("Asia/Shanghai")


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
    try:
        snapshot, selections = fetch_candidates()
    except MultiSourceUnavailable as exc:
        publish_blocked(day, str(exc))
        logging.warning("multi-source unavailable: %s", exc)
        return
    publish_partial(day, snapshot, selections)


def publish_blocked(day: date, message: str, snapshot: dict | None = None) -> None:
    payload = {
        "asOf": day.isoformat(),
        "updatedAt": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
        "status": "blocked",
        "mode": "免费多源公开数据研究版",
        "strategy": {"version": "eight-layer-v1", "description": "八层策略；关键实时字段不全时不发布推荐。"},
        "source": "免费多源公开数据",
        "message": message,
        "marketSnapshot": snapshot,
        "results": [],
    }
    output = DATA / "latest.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    history = DATA / "history.json"
    records = json.loads(history.read_text(encoding="utf-8")) if history.exists() else []
    records = [r for r in records if r.get("asOf") != day.isoformat()]
    records.insert(0, {"asOf": day.isoformat(), "count": 0, "strategyVersion": "eight-layer-v1", "status": "blocked"})
    history.write_text(json.dumps(records[:365], ensure_ascii=False, indent=2), encoding="utf-8")
    BACKUPS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output, BACKUPS / f"selection-{day.isoformat()}.json")
    write_status(day, "blocked", message)

def publish_partial(day: date, snapshot: dict, selections: list[dict]) -> None:
    payload={"asOf":day.isoformat(),"updatedAt":datetime.now(SHANGHAI).isoformat(timespec="seconds"),"status":"partial","mode":"免费多源公开数据研究版","strategy":{"version":"multi-source-basic-v1","description":"已验证基础行情与流动性过滤；板块持续性、资金流、解禁与技术共振待数据可用后纳入。"},"source":"、".join(snapshot["sources"]),"message":"已生成基础多源候选；不是完整八层策略结果。","marketSnapshot":snapshot,"results":selections}
    output=DATA/"latest.json"; output.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    history=DATA/"history.json"; records=json.loads(history.read_text(encoding="utf-8")) if history.exists() else []; records=[r for r in records if r.get("asOf")!=day.isoformat()]; records.insert(0,{"asOf":day.isoformat(),"count":len(selections),"strategyVersion":"multi-source-basic-v1","status":"partial"}); history.write_text(json.dumps(records[:365],ensure_ascii=False,indent=2),encoding="utf-8")
    write_status(day,"partial",f"基础多源候选：{len(selections)} 只")


def write_status(day: date, status: str, message: str) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "status.json").write_text(json.dumps({"asOf": day.isoformat(), "status": status, "message": message}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
