import requests
import json
import os
import urllib.parse

API_KEY = os.getenv('NEWSDATA_API_KEY')
COUNTRIES = "ar,br,cl,co,mx"

def google_translate(text):
    """使用免 Key 接口直接翻译"""
    if not text: return ""
    try:
        # 使用 Google 翻译的免费接口镜像
        base_url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "zh-CN",
            "dt": "t",
            "q": text
        }
        response = requests.get(base_url, params=params, timeout=10)
        # 解析返回的奇怪 JSON 格式
        result = response.json()
        translated_text = "".join([sentence[0] for sentence in result[0]])
        return translated_text
    except Exception as e:
        print(f"翻译稍后重试: {e}")
        return ""

def fetch_latam_news():
    if not API_KEY:
        print("错误: 缺少 API_KEY")
        return

    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={COUNTRIES}&language=es,pt"
    
    try:
        print("第一步: 抓取新闻原文...")
        res = requests.get(url, timeout=20)
        data = res.json()
        
        if data.get('status') == "success":
            news_list = data.get('results', [])
            print(f"第二步: 成功获取 {len(news_list)} 条新闻，开始翻译成中文...")
            
            for item in news_list:
                # 翻译标题
                item['title_zh'] = google_translate(item.get('title', ''))
                # 翻译摘要
                desc = item.get('description', '')
                item['description_zh'] = google_translate(desc[:300]) if desc else ""
                
                print(f"✅ 翻译成功: {item['title_zh'][:15]}")

            with open('latest_news.json', 'w', encoding='utf-8') as f:
                json.dump(news_list, f, ensure_ascii=False, indent=4)
            print("第三步: 任务完成，数据已存入 latest_news.json")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    fetch_latam_news()
