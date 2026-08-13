"""Tushare 生产数据适配器。

Token 仅从环境变量 TUSHARE_TOKEN 读取。不同账户积分/订阅对应的接口权限不同，
因此必须在运行时校验字段与数据时间戳，权限不足时安全阻断。
"""
from __future__ import annotations

import os


class TushareNotConfigured(RuntimeError):
    pass


def fetch_tushare_snapshot() -> dict:
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        raise TushareNotConfigured("Tushare Token 尚未配置")
    try:
        import tushare as ts
        pro = ts.pro_api(token)
        # Access check only. The exact real-time fields depend on the account's
        # purchased permissions and must be mapped after a successful test call.
        calendar = pro.trade_cal(exchange="SSE", is_open="1", limit=1)
    except Exception as exc:
        # Safe diagnostic only: exception class, never token or request headers.
        raise TushareNotConfigured(f"Tushare 基础接口调用失败（{type(exc).__name__}）") from exc
    if calendar is None or calendar.empty:
        raise TushareNotConfigured("Tushare 未返回有效交易日历数据")
    return {
        "capturedAt": None,
        "provider": "Tushare",
        "permissionCheck": "passed",
        "missingForEightLayer": [
            "盘中三大指数及 MA20", "全市场涨跌停与涨跌家数", "板块持续活跃度",
            "实时量比/换手率", "当日及5日主力资金", "14:00-14:40资金流", "解禁与涨停基因",
        ],
    }
