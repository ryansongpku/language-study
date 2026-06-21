# 每日三句 · 多语言学习 (Daily Three)

一个 iPhone 可用的网页 App (PWA)。每天 3 句中文（1 句简单 + 2 句复杂），
用「中文 → 自己思考翻译 → 看标准翻译 → 看讲解」的方式学习 4 种语言：
Français · 日本語 · ᠮᠣᠩᠭᠣᠯ（传统竖写蒙古文）· Español。

> 想增减语言，改 `generate.py` 顶部的 `LANGUAGES` 列表即可，界面会自动适配。

## 文件
- `index.html` — App 界面（单文件，含全部样式与逻辑）
- `content.json` — 当天内容（句子 + 翻译 + 读音 + 讲解）
- `generate.py` — 调用 Claude API 生成每日 `content.json`
- `generate_icons.py` — 生成 App 图标
- `manifest.json` / `sw.js` — PWA 配置（可“添加到主屏幕”、离线可用）

## 启用每日自动生成（需要 API key）
1. 在 `.env`（本目录，或 `../personal-website/.env`）里填入真实的密钥：
   `ANTHROPIC_API_KEY=sk-ant-...`  （目前是占位符 `your_api_key_here`）
2. 运行一次试试：`python3 generate.py` —— 会刷新 `content.json`。
3. 想每天自动跑，可加 cron（例如每天早上 6 点）：
   `0 6 * * * /usr/bin/python3 /Users/yansong/language-study/generate.py`

> 没有 key 也能用：当前 `content.json` 是一份示例内容（界面顶部标有「示例内容」）。

## 在 iPhone 上用
1. 让手机和电脑在同一 Wi-Fi，电脑上跑：
   `cd /Users/yansong/language-study && python3 -m http.server 8123`
2. iPhone Safari 打开 `http://<电脑IP>:8123/`
3. 点分享 → “添加到主屏幕”，即可像原生 App 一样全屏使用。
   （长期使用建议部署到任意静态托管，如 GitHub Pages / Vercel。）

## 说明
- 蒙古语用**传统竖写蒙古文**（回鹘式竖排，列从左到右），翻译下方附拉丁转写 + 西里尔对照，方便认读。
  - 若 iPhone 上蒙古文显示为方框 □，说明系统缺少蒙古文字体；告诉我，我可以打包一个网页字体进去。
