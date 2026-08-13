# Tushare 接入

在 GitHub 仓库的 Settings → Secrets and variables → Actions 添加 `TUSHARE_TOKEN`。不要把 Token 提交到代码仓库或发送到聊天。

上线前需要用当前账户实际调用确认：交易日历、日线/分钟线、指数、实时行情、资金流、板块、解禁、估值和涨停相关字段。免费或低积分账户不一定拥有八层策略需要的盘中实时和资金字段；任何一项不足，任务会阻断而不会发布推荐。
