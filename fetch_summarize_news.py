# Gemini × NHK RSS × JSON出力スクリプト
# → NHK RSSからニュース3件取得 → Gemini APIで要約 → JSON保存

import feedparser
import json
from datetime import datetime
import google.generativeai as genai
import os

# ==== 設定 ==== #
RSS_URL = "https://www.nhk.or.jp/rss/news/cat0.xml"
NEWS_COUNT = 3
API_KEY = os.environ["GOOGLE_API_KEY"]
MODEL_NAME = "models/gemini-2.0-flash"  # 安定動作用チャットモデル推奨

# ==== Gemini 初期化 ==== #
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)
chat = model.start_chat()

# ==== 要約処理 ==== #
def summarize_with_gemini(title, content):
    prompt = f"""
    以下はニュース記事です。

    タイトル: {title}
    本文: {content}

    この内容を小学生にもわかるように、やさしい言葉で短くまとめてください。
    出力形式：
    タイトル: ～
    本文: ～
    """
    response = chat.send_message(prompt)
    result = response.text

    if "タイトル:" in result and "本文:" in result:
        parts = result.split("本文:")
        title_line = parts[0].replace("タイトル:", "").strip()
        content_line = parts[1].strip()
        return title_line, content_line
    else:
        return title, result.strip()

# ==== ニュース取得＆要約 ==== #
def fetch_and_summarize():
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries[:NEWS_COUNT]

    articles = []
    for entry in entries:
        title = entry.title
        content = entry.get("summary", "")
        print(f"要約中: {title}")
        simple_title, simple_content = summarize_with_gemini(title, content)
        articles.append({
            "title": simple_title,
            "content": simple_content
        })

    return articles

# ==== JSON保存 ==== #
def save_to_json(articles):
    today = datetime.now().strftime("%Y%m%d")
    filename = f"news_{today}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"保存完了: {filename}")

# ==== 実行 ==== #
if __name__ == "__main__":
    news = fetch_and_summarize()
    save_to_json(news)
