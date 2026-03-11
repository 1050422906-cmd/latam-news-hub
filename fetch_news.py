import requests
import json
import os
import time
from deep_translator import MyMemoryTranslator

API_KEY = os.getenv('NEWSDATA_API_KEY')
COUNTRIES = "ar,br,cl,co,mx,pe"

def translate_text(text):
    if not text or len(str(text).strip()) < 3:
        return ""
    try:
        # 换用 MyMemory 引擎，对 GitHub Actions 更友好
        return MyMemoryTranslator(source='es', target='zh-CN').translate(text)
    except Exception as e:
        print(f"翻译环节出错: {e}")
        return text # 失败则返回原文

def fetch_latam_news():
    if not API_KEY:
        print("错误：Secret 中未找到 NEWSDATA_API_KEY")
        return

    # 抓取西班牙语新闻
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={COUNTRIES}&language=es"
    
    try:
        print("1. 正在获取 NewsData 原文...")
        response = requests.get(url, timeout=20)
        data = response.json()
        
        if data.get('status') == "success":
            raw_results = data.get('results', [])
            processed_results = []
            
            print(f"2. 开始翻译处理（共 {len(raw_results)} 条）...")
            
            for item in raw_results:
                # 显式创建中文标题字段
                item['title_zh'] = translate_text(item.get('title', ''))
                
                # 翻译摘要
                desc = item.get('description', '')
                item['description_zh'] = translate_text(desc[:200]) if desc else "查看原文了解详情"
                
                processed_results.append(item)
                print(f"✅ 已翻译: {item['title_zh'][:15]}...")
                # 稍微停顿一下，避免请求过快
                time.sleep(0.5)

            # 3. 保存文件
            with open('latest_news.json', 'w', encoding='utf-8') as f:
                json.dump(processed_results, f, ensure_ascii=False, indent=4)
            print("3. 双语数据已成功保存到 latest_news.json")
        else:
            print(f"API 返回错误状态: {data}")
            
    except Exception as e:
        print(f"运行发生致命错误: {e}")

if __name__ == "__main__":
    fetch_latam_news()
