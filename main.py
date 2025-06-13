import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

# キーワード一覧
KEYWORDS = [
    "Claude Code",
    "Vibe Cording",
    "Obsidian",
    "Azure Open AI",
    "Copilot"
]

# 出力フォルダ
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日付
today = datetime.now().strftime("%Y-%m-%d")

# 出力ファイル名
csv_filename = os.path.join(OUTPUT_DIR, f"articles_{today}.csv")
md_filename = os.path.join(OUTPUT_DIR, f"articles_{today}.md")

# 結果格納リスト
results = []

def match_keywords(text):
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def scrape_qiita():
    print("Scraping Qiita...")
    for keyword in KEYWORDS:
        url = f"https://qiita.com/search?q={keyword.replace(' ', '+')}"
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            articles = soup.select("div.searchResult_item")
            for article in articles:
                title_tag = article.select_one("h2.searchResult_itemTitle a")
                if title_tag:
                    title = title_tag.text.strip()
                    link = title_tag["href"]
                    if match_keywords(title):
                        results.append(["Qiita", keyword, title, f"https://qiita.com{link}"])
        except Exception as e:
            print(f"Error scraping Qiita for keyword '{keyword}': {e}")

def scrape_zenn():
    print("Scraping Zenn...")
    url = "https://zenn.dev/"
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.select("article a")
        for a in articles:
            title = a.text.strip()
            link = a.get("href")
            if match_keywords(title) and link:
                results.append(["Zenn", "N/A", title, f"https://zenn.dev{link}"])
    except Exception as e:
        print(f"Error scraping Zenn: {e}")

def scrape_note():
    print("Scraping Note...")
    url = "https://note.com/"
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.select("a")
        for a in articles:
            title = a.text.strip()
            link = a.get("href")
            if match_keywords(title) and link and link.startswith("/"):
                results.append(["Note", "N/A", title, f"https://note.com{link}"])
    except Exception as e:
        print(f"Error scraping Note: {e}")

# 実行
scrape_qiita()
scrape_zenn()
scrape_note()

# CSV保存
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Source", "Keyword", "Title", "URL"])
    writer.writerows(results)

# Markdown保存
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(f"# Articles Collected on {today}\n\n")
    for source, keyword, title, url in results:
        f.write(f"- **[{source}]** {title}\n")

print(f"Saved {len(results)} articles to {csv_filename} and {md_filename}")
