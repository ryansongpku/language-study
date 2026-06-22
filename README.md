# 每日三句 · 多语言学习 (Daily Three)

一个 iPhone 可用的网页 App (PWA)。每天 3 句中文（1 句简单 + 2 句中等），
每个 tab 是一句话，下面是这句的 4 种语言翻译练习与讲解，
用「中文 → 自己思考翻译 → 看标准翻译 → 看讲解」的方式学习 4 种语言：
Français · 日本語 · ᠮᠣᠩᠭᠣᠯ（传统竖写蒙古文）· Español。

> 想增减语言，改 `generate.py` 顶部的 `LANGUAGES` 列表即可，界面会自动适配。

## 文件
- `index.html` — App 界面（单文件，含全部样式与逻辑）
- `content.json` — 当天内容（句子 + 翻译 + 读音 + 讲解）
- `generate.py` — 调用 Claude API 生成每日 `content.json`
- `generate_icons.py` — 生成 App 图标
- `manifest.json` / `sw.js` — PWA 配置（可“添加到主屏幕”、离线可用）

## 线上地址（已部署）
**https://ryansongpku.github.io/language-study/**

GitHub Actions（`.github/workflows/daily.yml`）每天 **06:00 北京时间**自动在云端运行
`generate.py` 生成当天内容并发布到 GitHub Pages —— 不依赖本地电脑。
API key 存为仓库 secret `ANTHROPIC_API_KEY`（不在代码里）。
也可在仓库 Actions 页面点 “Run workflow” 手动立即刷新。

## 在 iPhone 上用
1. Safari 打开 https://ryansongpku.github.io/language-study/
2. 点分享 → “添加到主屏幕”，即可像原生 App 一样全屏使用（图标是白色“三”字）。

## 本地开发 / 手动生成
1. 在 `.env`（本目录）填入 `ANTHROPIC_API_KEY=sk-ant-...`
2. `python3 generate.py` —— 刷新本地 `content.json`
3. `python3 -m http.server 8123` 后浏览器开 `http://localhost:8123/`

## 说明
- 蒙古语用**传统竖写蒙古文**（回鹘式竖排，列从左到右），翻译下方附拉丁转写 + 西里尔对照，方便认读。
  - 若 iPhone 上蒙古文显示为方框 □，说明系统缺少蒙古文字体；告诉我，我可以打包一个网页字体进去。
