"""八层短线策略。

数据供应商适配器必须提供盘中快照及其时间戳；缺少任何核心字段时由调用方安全停机，
绝不以盘后或模拟数据冒充 14:35 实时选股结果。
"""
from dataclasses import dataclass, field


@dataclass
class Candidate:
    code: str; name: str; sector: str; change_pct: float; turnover_pct: float
    volume_ratio: float; amount: float; total_mv: float; amplitude_pct: float
    pe_ttm: float; unlock_days: int; is_st: bool; delisting: bool
    macd_cross: bool; kdj_cross: bool; pattern: bool; institutional_buy: bool
    net_inflow_today_rank: int; net_inflow_5d_rank: int; sector_rank: int
    high_change_pct: float; close_change_pct: float; limit_up_20d: bool
    return_5d_pct: float; late_net_buy: bool; hit_limit_then_fell: bool; amount_vs_yday: float
    reasons: list[str] = field(default_factory=list)


def market_gate(indexes_above_ma20: bool, advance_decline_ratio: float) -> tuple[int, str]:
    if indexes_above_ma20 and advance_decline_ratio > 2: return 10, "可操作"
    if not indexes_above_ma20 and advance_decline_ratio < 1: return 0, "空仓"
    return 6, "谨慎"


def hard_buyable(x: Candidate) -> bool:
    return (2 <= x.change_pct <= 7 and 3 <= x.turnover_pct <= 25 and x.volume_ratio > 1
            and x.amount > 50_000_000 and x.total_mv > 5_000_000_000 and x.amplitude_pct > 2)


def score(x: Candidate, hot_sectors: set[str]) -> dict | None:
    if x.is_st or x.delisting or x.unlock_days <= 90 or not (5_000_000_000 <= x.total_mv <= 200_000_000_000) or not (0 < x.pe_ttm < 100): return None
    if x.sector not in hot_sectors or not hard_buyable(x): return None
    quality = 15 if x.total_mv <= 20_000_000_000 else 10
    technical = min(25, 6 * sum([x.macd_cross, x.kdj_cross, x.pattern, x.institutional_buy]))
    fund = max(0, 20 - min(x.net_inflow_today_rank, 10) - min(x.net_inflow_5d_rank, 10))
    premium = 0
    premium += 5 if x.high_change_pct and x.close_change_pct / x.high_change_pct >= .9 else 1
    premium += 4 if x.sector_rank <= 3 else 1
    premium += 3 if x.limit_up_20d else 0
    premium += 2 if x.return_5d_pct < 15 else (-2 if x.return_5d_pct > 25 else 0)
    if x.late_net_buy and x.sector_rank <= 3: premium += 1
    if 3 <= x.change_pct <= 5 and x.volume_ratio > 2 and x.net_inflow_today_rank <= 10: premium += 1
    if x.hit_limit_then_fell: premium -= 3
    if x.amount_vs_yday < .7: premium -= 2
    return {"code": x.code, "name": x.name, "score": round(quality + technical + fund + max(0, min(15, premium)), 2), "reasons": x.reasons}
