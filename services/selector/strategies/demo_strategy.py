from services.selector.models import Selection, StockBar

STRATEGY_VERSION = "demo-v1"
STRATEGY_DESCRIPTION = "排除 ST、停牌和上市不足 60 日标的；要求 5 日均线高于 20 日均线、收盘价高于 5 日均线、成交额不少于 1 亿元。"


def select(stocks: list[StockBar]) -> list[Selection]:
    selected = []
    for stock in stocks:
        if stock.is_st or stock.is_suspended or stock.listed_days < 60 or stock.amount < 100_000_000:
            continue
        if stock.ma5 <= stock.ma20 or stock.close <= stock.ma5:
            continue
        score = round((stock.ma5 / stock.ma20 - 1) * 1000 + min(stock.amount / 1_000_000_000, 10), 2)
        selected.append(Selection(stock.code, stock.name, score, ["MA5 高于 MA20", "收盘价高于 MA5", "成交额不少于 1 亿元"]))
    return sorted(selected, key=lambda x: x.score, reverse=True)
