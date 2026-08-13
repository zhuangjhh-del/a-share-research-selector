"""Best-effort multi-source public research feed (no credentials)."""
from __future__ import annotations
from datetime import datetime

class MultiSourceUnavailable(RuntimeError): pass

def _pick(frame, *names):
    for name in names:
        if name in frame.columns: return name
    return None

def fetch_candidates() -> tuple[dict, list[dict]]:
    try:
        import akshare as ak
    except Exception as exc: raise MultiSourceUnavailable("免费数据组件未安装") from exc
    sources=[]; quotes=None
    required_names=("代码","名称","涨跌幅","成交额","换手率","总市值","最高","最低","最新价")
    for source, call in [("新浪财经", ak.stock_zh_a_spot)]:
        try:
            candidate=call()
            if candidate is not None and not candidate.empty and all(_pick(candidate, n) for n in required_names):
                quotes=candidate; sources.append(source); break
        except Exception: continue
    if quotes is None or quotes.empty:
        # Independent fallback: Tonghuashun public capital-flow table.
        try:
            funds=ak.stock_fund_flow_individual(symbol="即时")
            import pandas as pd
            funds["涨跌幅"]=pd.to_numeric(funds["涨跌幅"].astype(str).str.replace("%",""),errors="coerce")
            funds["换手率"]=pd.to_numeric(funds["换手率"].astype(str).str.replace("%",""),errors="coerce")
            funds["成交额"]=pd.to_numeric(funds["成交额"].astype(str).str.replace("亿","e8").str.replace("万","e4"),errors="coerce")
            f=funds[(~funds["股票简称"].astype(str).str.contains("ST|退",na=False)) & funds["涨跌幅"].between(2,7) & funds["换手率"].between(3,25) & (funds["成交额"]>50_000_000)]
            results=[]
            for _,r in f.head(5).iterrows(): results.append({"code":str(r["股票代码"]).zfill(6),"name":str(r["股票简称"]),"score":round(float(r["涨跌幅"])*5+float(r["换手率"])/2,2),"reasons":["同花顺公开资金流","涨幅 2%-7%","换手率 3%-25%","成交额大于 5000 万"]})
            return {"capturedAt":datetime.now().astimezone().isoformat(timespec="seconds"),"sources":["同花顺公开资金流"],"stockCount":int(len(funds)),"candidateCount":len(results),"coverage":"基础行情、换手率、成交额与资金流"},results
        except Exception as exc: raise MultiSourceUnavailable("新浪行情与同花顺公开资金流均暂时不可用") from exc
    code=_pick(quotes,"代码"); name=_pick(quotes,"名称"); change=_pick(quotes,"涨跌幅"); amount=_pick(quotes,"成交额"); turnover=_pick(quotes,"换手率"); mv=_pick(quotes,"总市值"); high=_pick(quotes,"最高"); low=_pick(quotes,"最低"); price=_pick(quotes,"最新价")
    needed=[code,name,change,amount,turnover,mv,high,low,price]
    if any(x is None for x in needed): raise MultiSourceUnavailable("公开行情缺少基础筛选字段")
    q=quotes.copy()
    for c in [change,amount,turnover,mv,high,low,price]: q[c]=__import__('pandas').to_numeric(q[c],errors='coerce')
    q=q[(~q[name].astype(str).str.contains("ST|退",na=False)) & q[change].between(2,7) & q[turnover].between(3,25) & (q[amount]>50_000_000) & (q[mv]>5_000_000_000)]
    q=q[((q[high]-q[low])/q[price]*100)>2].dropna(subset=[code])
    results=[]
    for _,r in q.assign(_score=q[change]*4+q[turnover]/2+(q[amount]/1e9).clip(upper=10)).sort_values("_score",ascending=False).head(5).iterrows():
        results.append({"code":str(r[code]).zfill(6),"name":str(r[name]),"score":round(float(r['_score']),2),"reasons":["涨幅 2%-7%","换手率 3%-25%","成交额大于 5000 万","市值大于 50 亿","振幅大于 2%"]})
    snap={"capturedAt":datetime.now().astimezone().isoformat(timespec="seconds"),"sources":sources,"stockCount":int(len(quotes)),"candidateCount":len(results),"coverage":"基础行情与流动性过滤"}
    return snap,results
