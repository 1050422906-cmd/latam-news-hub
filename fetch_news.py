import requests
import json
import os
from deep_translator import GoogleTranslator

API_KEY = os.getenv('NEWSDATA_API_KEY')
# 增加国家，确保覆盖面
COUNTRIES = "ar,br,cl,co,mx,pe"

def translate_text(text):
    if not text or len(text) < 3:
        return ""
    try:
        # 强制指定从西班牙语翻译到中文
        return GoogleTranslator(source='es', target='zh-CN').translate(text)
    except Exception as e:
        print(f"翻译出错，保留原文: {e}")
        return text

def fetch_latam_news():
    if not API_KEY:
        print("错误：未设置 NEWSDATA_API_KEY")
        return

    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={COUNTRIES}&language=es"
    
    print("正在连接 API...")
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if data.get('status') == "success":
            results = data.get('results', [])
            print(f"成功抓取 {len(results)} 条新闻，开始翻译处理...")
            
            for item in results:
                # 核心：必须创建这两个新字段
                item['title_zh'] = translate_text(item.get('title', ''))
                
                desc = item.get('description', '')
                if desc:
                    # 摘要太长容易导致翻译超时，只取前 200 字
                    item['description_zh'] = translate_text(desc[:200])
                else:
                    item['description_zh'] = ""
                
                print(f"完成翻译: {item['title_zh'][:10]}...")

            with open('latest_news.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print("文件已保存！")
        else:
            print(f"API 报错: {data}")
    except Exception as e:
        print(f"脚本运行致命错误: {e}")

if __name__ == "__main__":
    fetch_latam_news()
