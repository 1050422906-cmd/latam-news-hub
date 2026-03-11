import requests
import json
import os
import time
from deep_translator import MyMemoryTranslator

API_KEY = os.getenv('NEWSDATA_API_KEY')
COUNTRIES = "ar,br,cl,co,mx"

def translate_safe(text, lang='es'):
    """针对不同国家强制指定源语言"""
    if not text or len(str(text)) < 5:
        return ""
    # 巴西用 pt (葡萄牙语)，其他用 es (西班牙语)
    source_lang = 'pt' if lang == 'br' else 'es'
    try:
        return MyMemoryTranslator(source=source_lang, target='zh-CN').translate(text)
    except Exception as e:
        print(f"翻译跳过: {e}")
        return ""

def fetch_latam_news():
    if not API_KEY:
        print("错误: 未找到 API_KEY")
        return

    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={COUNTRIES}&language=es,pt"
    
    try:
        print(f"正在抓取原文...")
        res = requests.get(url, timeout=30)
        data = res.json()
        
        if data.get('status') == "success":
            raw_news = data.get('results', [])
            print(f"抓取成功，开始强制语种翻译...")
            
            for item in raw_news:
                # 获取该条新闻所属国家
                c_code = item.get('country', ['mx'])[0] 
                
                # 执行翻译
                item['title_zh'] = translate_safe(item.get('title', ''), c_code)
                item['description_zh'] = translate_safe(item.get('description', '')[:300], c_code)
                
                # 打印日志以便我们确认
                print(f"✅ [{c_code}] 翻译结果: {item['title_zh'][:15]}")
                time.sleep(1) 
            
            with open('latest_news.json', 'w', encoding='utf-8') as f:
                json.dump(raw_news, f, ensure_ascii=False, indent=4)
            print("数据处理完毕。")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    fetch_latam_news()
