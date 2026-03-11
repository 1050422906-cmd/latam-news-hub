import requests
import json
import os
import time
from datetime import datetime

# 核心配置
API_KEY = os.getenv('NEWSDATA_API_KEY')

def google_translate(text):
    """极速版 Google 翻译镜像接口"""
    if not text or len(str(text)) < 5:
        return ""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",  # 自动识别原文 (西语/葡语)
            "tl": "zh-CN", # 目标语种：中文
            "dt": "t",
            "q": text
        }
        # 移除了长等待，设置 5 秒超时
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        translated = "".join([sentence[0] for sentence in data[0]])
        return translated
    except Exception as e:
        print(f"翻译跳过: {e}")
        return ""

def get_news_batch(countries):
    """分批抓取函数"""
    if not API_KEY: return []
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={countries}&language=es,pt"
    try:
        res = requests.get(url, timeout=20)
        data = res.json()
        if data.get('status') == "success":
            return data.get('results', [])
    except Exception as e:
        print(f"抓取 {countries} 失败: {e}")
    return []

def fetch_latam_news():
    print("🚀 启动极速抓取与翻译系统...")
    
    # 分两组抓取，解决免费版 10 条限制问题
    batch1 = get_news_batch("ar,br")
    time.sleep(0.5) # 极短停顿
    batch2 = get_news_batch("cl,co,mx")
    
    all_news = batch1 + batch2
    
    if not all_news:
        print("未获取到任何数据。")
        return

    print(f"成功获取 {len(all_news)} 条原始新闻，开始极速翻译...")

    for item in all_news:
        # 极速处理翻译
        item['title_zh'] = google_translate(item.get('title', ''))
        
        desc = item.get('description', '')
        if desc:
            item['description_zh'] = google_translate(desc[:300])
        else:
            item['description_zh'] = "点击链接查看全文"
        
        c_code = (item.get('country') or ['未知'])[0].upper()
        print(f"✅ [{c_code}] 处理完成")

    # 1. 保存为最新文件
    with open('latest_news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)

    # 2. 存档历史记录
    if not os.path.exists('history'):
        os.makedirs('history')
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    with open(f'history/{date_str}.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)
        
    print(f"✅ 任务圆满完成！已更新 latest_news.json 并存档至 history/{date_str}.json")

if __name__ == "__main__":
    fetch_latam_news()
