# A 股研究选股系统（免费研究版）

这是一个盘后研究用途的静态选股网站。它不提供实时行情或投资建议。

## 运行方式

```bash
python -m services.selector.run --as-of 2026-08-13
python -m http.server 8000 -d apps/site
```

打开 `http://localhost:8000`。首次运行使用仓库内的演示快照，以便完整验证策略、网站和部署流程。

## 云端运行

GitHub Actions 在工作日 15:40（北京时间）运行，先执行交易日校验，再生成结果并发布 GitHub Pages。它不依赖个人电脑。详见 [部署说明](docs/deployment.md)。

生产前需要把 `MARKET_DATA_URL` 配置为经许可、允许服务器端访问及保存的盘后数据文件地址；任务会校验数据日期和字段完整性。免费源没有 SLA，因此系统会在数据未就绪时重试并告警，而不会发布错误结果。
