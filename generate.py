#!/usr/bin/env python3
"""
Daily multilingual sentence generator for the 语言学习 (language-study) PWA.

Generates 3 Chinese sentences (1 simple + 2 complex) and, for each, the standard
translation, pronunciation, and a Chinese-language explanation (生字 / 语法 / 为什么
这样翻译最好) in 7 target languages: English, French, Japanese, Mongolian (Cyrillic),
Spanish, Tibetan, Thai.

Run manually or via cron / scheduled task:
  0 6 * * * /usr/bin/python3 /Users/yansong/language-study/generate.py

Requires ANTHROPIC_API_KEY in the environment or in a .env file next to this script
(or in ../personal-website/.env, which is also checked).

Output: content.json  — read by index.html.
"""

import json
import os
import sys
import random
import time
import datetime
from pathlib import Path

import anthropic

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
CONTENT_JSON = SCRIPT_DIR / "content.json"
MODEL        = "claude-sonnet-4-6"

# Target languages. `pron` = label for the pronunciation/romanization field
# (None for Latin-script languages where no transliteration is needed).
LANGUAGES = [
    {"code": "fr", "name": "French",             "native": "Français",  "pron": None},
    {"code": "ja", "name": "Japanese",           "native": "日本語",     "pron": "罗马音 (romaji)"},
    {"code": "mn", "name": "Mongolian written in TRADITIONAL Mongolian script (classical vertical script, Unicode range U+1800–U+18AF) — NOT Cyrillic", "native": "ᠮᠣᠩᠭᠣᠯ", "pron": "拉丁转写 + 西里尔对照"},
    {"code": "es", "name": "Spanish",            "native": "Español",   "pron": None},
]

# A pool of everyday themes so daily sentences stay varied.
THEMES = [
    "日常生活与家庭", "工作与学习", "旅行与交通", "饮食与烹饪", "天气与季节",
    "健康与运动", "购物与金钱", "友情与社交", "科技与互联网", "情感与心理",
    "自然与环境", "文化与节日", "时间与计划", "梦想与目标", "新闻与社会",
]

# ── Load API key from .env (this dir, then ../personal-website) ────────────────
def load_env():
    for env_file in (SCRIPT_DIR / ".env",
                     SCRIPT_DIR.parent / "personal-website" / ".env"):
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    sys.exit("ERROR: ANTHROPIC_API_KEY not set. Add it to .env or export it before running.")

client = anthropic.Anthropic(api_key=API_KEY)


# ── Helpers ────────────────────────────────────────────────────────────────────
def call_tool(prompt: str, tool_name: str, schema: dict,
              max_tokens: int = 2048, retries: int = 2) -> dict:
    """Get structured output via tool-use. The SDK returns a validated dict,
    so there is no fragile text-JSON parsing (quotes/newlines can't break it)."""
    tool = {"name": tool_name, "description": "Return the structured result.",
            "input_schema": schema}
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                tools=[tool],
                tool_choice={"type": "tool", "name": tool_name},
                messages=[{"role": "user", "content": prompt}],
            )
            for block in resp.content:
                if block.type == "tool_use":
                    return block.input
            raise ValueError("no tool_use block in response")
        except (anthropic.APIError, ValueError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise last_err


def generate_sentences(theme_a: str, theme_b: str) -> list:
    """Generate the 3 Chinese sentences: 1 simple, 2 complex."""
    prompt = f"""你是一位中文母语老师，帮一位中文母语者通过翻译练习来学外语。
请生成 3 个**地道、自然**的中文句子，用于翻译练习：

- 第 1 句：**简单**。短句，常用词汇，适合初学者（约 6–12 字）。
- 第 2 句：**中等**。日常句子，可含一个从句或连接词（如因为/虽然/的时候），稍长一点（约 12–20 字）。
- 第 3 句：**中等**。另一个日常场景，难度与第 2 句相当（约 12–20 字）。

要求：
- 三句话主题各不相同，可参考主题：「{theme_a}」「{theme_b}」，也可自由发挥。
- 句子要像真人说话/写作，避免教科书式生硬例句，避免老套（如"今天天气很好"）。
- **不要难句**：不要成语堆砌、不要过于书面或抽象的表达，保持自然口语化。
- 不要使用任何特定人名、不要涉及敏感内容。

请按顺序返回 3 个句子：第 1 个 level 为 simple，第 2、3 个 level 为 medium。"""
    schema = {
        "type": "object",
        "properties": {
            "sentences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "level": {"type": "string", "enum": ["simple", "medium"]},
                        "zh": {"type": "string"},
                    },
                    "required": ["level", "zh"],
                },
            }
        },
        "required": ["sentences"],
    }
    data = call_tool(prompt, "submit_sentences", schema, max_tokens=1024)
    sents = data["sentences"]
    # The model occasionally returns the array as a JSON-encoded string; recover it.
    if isinstance(sents, str):
        sents = json.loads(sents)
    norm = []
    for i, s in enumerate(sents):
        if isinstance(s, str):
            s = json.loads(s)
        norm.append({"level": s.get("level", "simple" if i == 0 else "medium"), "zh": s["zh"]})
    return norm


# Per-language special instructions for non-Latin / tricky scripts.
SCRIPT_NOTES = {
    "mn": "用**传统竖写蒙古文**（回鹘式蒙古文，Unicode U+1800–U+18AF），不要用西里尔字母；pron 给拉丁转写并附西里尔对照，方便认读。",
    "bo": "用**藏文**书写（拉萨方言）；pron 给拉萨音或威利转写。",
    "ja": "正常使用汉字+假名；pron 给罗马音。",
    "th": "用泰文书写；pron 给 RTGS 罗马音。",
}


def translate_one(zh: str, level: str, L: dict) -> dict:
    """Translate one Chinese sentence into a single target language with explanation."""
    pron_note = (f'"pron"：给 {L["pron"]}（帮助发音的读音/转写）'
                 if L["pron"] else
                 '"pron"：填 null（拉丁字母语言，无需注音）')
    script_note = SCRIPT_NOTES.get(L["code"], "")
    script_line = f"\n特别注意：{script_note}" if script_note else ""

    prompt = f"""你是一位精通{L["name"]}的翻译与语言教学专家，正在帮一位中文母语者学习。
请把下面这个中文句子（难度：{level}）翻译成 {L["name"]}，并给出讲解。

中文句子：「{zh}」

要求：
- "text"：标准、地道的{L["name"]}翻译。
- {pron_note}
- "explanation"：一个**含 3 个字符串**的数组，全部用**简体中文**讲解：
  第 1 条以「①生字：」开头，列出 2–4 个关键词并给词义；
  第 2 条以「②语法：」开头，讲清结构、时态、语序等关键语法点；
  第 3 条以「③为什么这样翻最自然：」开头，点出与中文的差异或地道之处。
  讲解要具体、对学习者有用，不要空泛。{script_line}"""

    schema = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": f"{L['name']} 的标准翻译"},
            "pron": {"type": ["string", "null"], "description": "读音/转写，无则为 null"},
            "explanation": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3 条中文讲解：①生字 ②语法 ③为什么这样翻最自然",
            },
        },
        "required": ["text", "explanation"],
    }
    # Traditional Mongolian is very token-heavy (script + Latin + Cyrillic + 讲解),
    # so it needs a much larger budget to avoid truncated tool output.
    mt = 4096 if L["code"] == "mn" else 2200
    data = call_tool(prompt, "submit_translation", schema, max_tokens=mt)
    exp = data.get("explanation", "")
    # The model sometimes returns the array as a JSON-encoded string; recover it.
    if isinstance(exp, str):
        s = exp.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    exp = parsed
            except json.JSONDecodeError:
                pass
    if isinstance(exp, list):
        exp = "\n".join(str(x).strip() for x in exp if str(x).strip())
    text = data.get("text", "")
    if not text or not exp:
        raise ValueError("empty text/explanation")
    return {"text": text, "pron": data.get("pron"), "explanation": exp}


def translate_sentence(zh: str, level: str) -> dict:
    """For one Chinese sentence, produce all 7-language breakdowns (one call each)."""
    out = {}
    for L in LANGUAGES:
        result = None
        for attempt in range(2):
            try:
                result = translate_one(zh, level, L)
                break
            except Exception as e:
                print(f"      WARNING: {L['code']} attempt {attempt+1} failed: {e}")
                time.sleep(1.0)
        out[L["code"]] = result or {"text": "(生成失败，请重试)", "pron": None, "explanation": ""}
        time.sleep(0.2)
    return out


# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    today = datetime.date.today().isoformat()
    print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] Generating sentences for {today}…")

    themes = random.sample(THEMES, 2)
    sentences = generate_sentences(themes[0], themes[1])
    print(f"  → {len(sentences)} sentences:")
    for s in sentences:
        print(f"     [{s['level']}] {s['zh']}")

    out_sentences = []
    for i, s in enumerate(sentences, 1):
        print(f"  [{i}/{len(sentences)}] translating into {len(LANGUAGES)} languages…")
        translations = translate_sentence(s["zh"], s["level"])
        out_sentences.append({
            "level": s["level"],
            "zh": s["zh"],
            "translations": translations,
        })

    output = {
        "date": today,
        "languages": [
            {"code": L["code"], "native": L["native"]} for L in LANGUAGES
        ],
        "sentences": out_sentences,
    }
    CONTENT_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"  ✓ Saved {CONTENT_JSON}")


if __name__ == "__main__":
    main()
