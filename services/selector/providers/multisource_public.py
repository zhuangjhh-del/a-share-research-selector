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
    for source, call in [("新浪财经", ak.stock_zh_a_spot), ("东方财富", ak.stock_zh_a_spot_em)]:
        try:
            quotes=call(); sources.append(source)
            if quotes is not None and not quotes.empty: break
        except Exception: continue
    if quotes is None or quotes.empty: raise MultiSourceUnavailable("新浪与东方财富公开行情均暂时不可用")
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
