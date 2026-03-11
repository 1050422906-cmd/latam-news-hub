import requests
import json
import os
import time

API_KEY = os.getenv('NEWSDATA_API_KEY')

def google_translate(text):
    """直接调用 Google 翻译 API 镜像"""
    if not text or len(str(text)) < 5:
        return ""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "zh-CN",
            "dt": "t",
            "q": text
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        translated = "".join([sentence[0] for sentence in data[0]])
        return translated
    except Exception as e:
        print(f"翻译跳过: {e}")
        return ""

def get_news_batch(countries):
    """抓取指定国家的新闻"""
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
    print("开始分批次抓取拉美五国新闻...")
    
    # 分成两组，确保每组都不会因为达到10条限制而漏掉小国家
    batch1 = get_news_batch("ar,br") # 阿根廷，巴西
    time.sleep(1) # 稍微停顿，尊重API频率
    batch2 = get_news_batch("cl,co,mx") # 智利，哥伦比亚，墨西哥
    
    all_news = batch1 + batch2
    
    if not all_news:
        print("未获取到任何新闻内容。")
        return

    print(f"总计获取 {len(all_news)} 条原始新闻，开始翻译...")

    for item in all_news:
        # 翻译标题
        item['title_zh'] = google_translate(item.get('title', ''))
        # 翻译摘要
        desc = item.get('description', '')
        item['description_zh'] = google_translate(desc[:300]) if desc else "点击查看全文"
        
        c_name = item.get('country', ['未知'])[0]
        print(f"✅ [{c_name}] 翻译完成: {item['title_zh'][:12]}...")
        time.sleep(0.3)

    # 保存合并后的数据
    with open('latest_news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)
    print(f"任务完成！共处理并存档 {len(all_news)} 条双语新闻。")

if __name__ == "__main__":
    fetch_latam_news()
