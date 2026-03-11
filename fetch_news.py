import requests
import json
import os
# 导入翻译库
try:
    from deep_translator import GoogleTranslator
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "deep-translator"])
    from deep_translator import GoogleTranslator

API_KEY = os.getenv('NEWSDATA_API_KEY')
# 指定拉美重点国家
COUNTRIES = "ar,br,cl,co,mx,pe"

def translate_text(text):
    if not text: return ""
    try:
        # 将西语/葡语翻译为中文
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except Exception as e:
        print(f"翻译出错: {e}")
        return text

def fetch_latam_news():
    if not API_KEY:
        print("错误：未找到 API_KEY")
        return

    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={COUNTRIES}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == "success":
            results = data.get('results', [])
            for item in results:
                print(f"正在处理: {item.get('title')[:20]}...")
                # 新增：保存中文标题和简介
                item['title_zh'] = translate_text(item.get('title'))
                item['description_zh'] = translate_text(item.get('description'))
            
            with open('latest_news.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print("双语数据抓取成功！")
    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    fetch_latam_news()
