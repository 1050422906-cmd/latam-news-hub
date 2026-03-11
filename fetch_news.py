import requests
import json
import os
import time

# 配置
API_KEY = os.getenv('NEWSDATA_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
COUNTRIES = "ar,br,cl,co,mx"

def ai_translate(text, country_code):
    """使用 Gemini Pro 进行深度语义翻译"""
    if not text or len(str(text)) < 10:
        return text
    
    # 根据国家代码提示 AI 语种，确保精准度
    lang_context = "葡萄牙语" if country_code == 'br' else "西班牙语"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    prompt = f"""你是一位精通拉美区域研究的资深翻译。请将以下{lang_context}新闻内容翻译成地道、专业的中文。
    要求：
    1. 术语准确（如政治派系、政府机构名）。
    2. 语气中立，符合学术规范。
    3. 仅返回翻译后的文本，不要有任何解释。
    
    内容如下：
    {text}"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4} # 降低随机性，确保严谨
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()
        translated = result['candidates'][0]['content']['parts'][0]['text'].strip()
        return translated
    except Exception as e:
        print(f"AI 翻译异常: {e}")
        return "" # 失败则留空，网页会显示原文

def get_news_batch(countries):
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={countries}&language=es,pt"
    try:
        res = requests.get(url, timeout=20)
        return res.json().get('results', []) if res.json().get('status') == "success" else []
    except: return []

def fetch_latam_news():
    print("🚀 启动 AI 赋能的拉美新闻抓取系统...")
    
    batch1 = get_news_batch("ar,br")
    time.sleep(1)
    batch2 = get_news_batch("cl,co,mx")
    all_news = batch1 + batch2
    
    if not all_news: return

    for item in all_news:
        c_code = (item.get('country') or ['mx'])[0].lower()
        
        # 翻译标题
        item['title_zh'] = ai_translate(item.get('title', ''), c_code)
        
        # 翻译摘要
        desc = item.get('description', '')
        if desc:
            item['description_zh'] = ai_translate(desc[:400], c_code)
        
        print(f"✅ [{c_code}] AI 翻译完成: {item.get('title_zh', '')[:12]}...")
        time.sleep(2) # Gemini 免费层级有频率限制，每分钟建议不超过 15 次请求

    # 保存
    with open('latest_news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)
    
    # 存档
    if not os.path.exists('history'): os.makedirs('history')
    from datetime import datetime
    date_str = datetime.now().strftime('%Y-%m-%d')
    with open(f'history/{date_str}.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)
    
    print("📊 数据归档与 AI 翻译全部完成。")

if __name__ == "__main__":
    fetch_latam_news()
