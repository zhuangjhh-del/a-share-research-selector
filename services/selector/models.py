from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class StockBar:
    code: str
    name: str
    close: float
    volume: float
    amount: float
    ma5: float
    ma20: float
    listed_days: int
    is_st: bool
    is_suspended: bool


@dataclass(frozen=True)
class Selection:
    code: str
    name: str
    score: float
    reasons: list[str]

    def to_dict(self) -> dict:
        return asdict(self)
