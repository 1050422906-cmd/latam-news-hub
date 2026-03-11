import requests
import json
import os
import time
from datetime import datetime

# 核心配置
API_KEY = os.getenv('NEWSDATA_API_KEY')
DEEPL_KEY = os.getenv('DEEPL_AUTH_KEY')
COUNTRIES = "ar,br,cl,co,mx"

def translate_text(text):
    """双引擎翻译：优先 DeepL，Google 兜底"""
    if not text or len(str(text)) < 5:
        return ""
    
    # 1. 尝试使用 DeepL
    if DEEPL_KEY:
        try:
            deepl_url = "https://api-free.deepl.com/v2/translate"
            payload = {
                "auth_key": DEEPL_KEY,
                "text": text,
                "target_lang": "ZH"
            }
            res = requests.post(deepl_url, data=payload, timeout=10)
            if res.status_code == 200:
                return res.json()['translations'][0]['text']
        except Exception as e:
            print(f"DeepL 接口调用跳过，改用 Google: {e}")

    # 2. Google 翻译镜像兜底 (无需 Key)
    try:
        google_url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "auto", "tl": "zh-CN", "dt": "t", "q": text}
        response = requests.get(google_url, params=params, timeout=5)
        return "".join([s[0] for s in response.json()[0]])
    except:
        return ""

def get_news_batch(countries):
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={countries}&language=es,pt"
    try:
        res = requests.get(url, timeout=20)
        return res.json().get('results', []) if res.json().get('status') == "success" else []
    except: return []

def fetch_latam_news():
    print("🚀 启动 DeepL 高级翻译系统...")
    # 分两批抓取确保覆盖 5 国
    all_news = get_news_batch("ar,br") + get_news_batch("cl,co,mx")
    
    if not all_news:
        print("未抓取到新闻")
        return

    for item in all_news:
        # 翻译标题
        item['title_zh'] = translate_text(item.get('title', ''))
        # 翻译摘要 (截取前 300 字节省 DeepL 额度)
        desc = item.get('description', '')
        item['description_zh'] = translate_text(desc[:300]) if desc else "查看原文了解更多详情"
        
        c_code = (item.get('country') or ['未知'])[0].upper()
        print(f"✅ [{c_code}] DeepL 翻译完成")
        time.sleep(0.2) # DeepL API 响应极快，无需长时间等待

    # 保存最新数据
    with open('latest_news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)

    # 存档与更新目录
    if not os.path.exists('history'): os.makedirs('history')
    date_str = datetime.now().strftime('%Y-%m-%d')
    with open(f'history/{date_str}.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)

    # 更新 catalog.json (用于网页下拉菜单)
    files = [f.replace('.json', '') for f in os.listdir('history') if f.endswith('.json') and f != 'catalog.json']
    files.sort(reverse=True)
    with open('history/catalog.json', 'w', encoding='utf-8') as f:
        json.dump(files, f, ensure_ascii=False, indent=4)

    print(f"✨ 所有任务圆满完成！今日简报已存至 history/{date_str}.json")

if __name__ == "__main__":
    fetch_latam_news()
