# 部署说明（免费研究版）

## 范围和限制

本项目只在收盘后生成研究结果，默认北京时间 15:40 触发；不会使用或展示实时行情。GitHub Actions 与 GitHub Pages 都在云端运行，不依赖个人电脑。GitHub 的计划任务是尽力调度，偶尔会延迟；因此页面更新时间以任务实际完成时间为准，而非承诺的精确 15:40。

免费数据没有可保证的 SLA。本项目以“数据延迟或失败时不发布”为原则，连续重试三次，最终失败使工作流失败并保留 Actions 日志。可在 GitHub 仓库 Settings → Notifications 配置失败邮件；需要企业微信时，后续可添加一个由 `WECHAT_WEBHOOK` 密钥保护的通知步骤。

## 发布步骤

1. 新建一个私有 GitHub 仓库并推送本项目。
2. 在仓库 Settings → Pages 中选择 **GitHub Actions** 作为部署来源。
3. 在 Settings → Actions → General 中允许工作流读写仓库内容。
4. 可选：在 Settings → Secrets and variables → Actions 添加 `MARKET_DATA_URL`。该 URL 应为你已确认有权使用、保存的盘后 CSV；可包含 `{as_of}` 占位符。
5. 在 Actions 页面手动运行 `Daily post-market research` 验证网站部署。
6. 首周检查每次工作流日志、`apps/site/data/status.json` 和结果日期。

## 数据文件契约

CSV 需要包含：`code,name,close,volume,amount,ma5,ma20,listed_days,is_st,is_suspended`。实际接入时，数据源适配器负责把原始数据转换为这个内部格式。不要将未获得云端使用或保存授权的网页接口接入本项目。

## 数据备份与恢复

每次任务在运行目录创建 JSON 快照；云端生产更推荐将 `selection-YYYY-MM-DD.json` 上传至私有对象存储（例如 S3/COS），并给存储桶配置版本控制和生命周期策略。GitHub 仓库保留发布数据版本，可用 Git 历史恢复页面结果。
