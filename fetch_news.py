import requests
import json
import os
import time
from deep_translator import GoogleTranslator

API_KEY = os.getenv('NEWSDATA_API_KEY')
COUNTRIES = "ar,br,cl,co,mx,pe"

def translate_safe(text, field_name="内容"):
    if not text or len(str(text).strip()) < 3:
        return ""
    
    # 尝试最多 3 次翻译，防止网络波动
    for attempt in range(3):
        try:
            # 强制指定从西班牙语(es)翻译到中文(zh-CN)
            translated = GoogleTranslator(source='es', target='zh-CN').translate(text)
            return translated
        except Exception as e:
            print(f"第 {attempt + 1} 次翻译{field_name}失败: {e}")
            time.sleep(1) # 等待一秒重试
    return f"（翻译暂不可用）{text}"

def fetch_latam_news():
    if not API_KEY:
        print("错误：未找到 NEWSDATA_API_KEY")
        return

    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={COUNTRIES}&language=es"
    
    try:
        print("正在获取新闻数据...")
        response = requests.get(url, timeout=20)
        data = response.json()
        
        if data.get('status') == "success":
            raw_results = data.get('results', [])
            processed_results = []
            
            print(f"开始翻译 {len(raw_results)} 条新闻，请稍候...")
            
            for item in raw_results:
                title = item.get('title', '')
                print(f"正在处理: {title[:20]}...")
                
                # 写入中文翻译字段
                item['title_zh'] = translate_safe(title, "标题")
                
                desc = item.get('description', '')
                if desc:
                    # 截取前 300 字，提高翻译成功率
                    item['description_zh'] = translate_safe(desc[:300], "摘要")
                else:
                    item['description_zh'] = "查看原文了解更多详情"
                
                processed_results.append(item)

            with open('latest_news.json', 'w', encoding='utf-8') as f:
                json.dump(processed_results, f, ensure_ascii=False, indent=4)
            print("latest_news.json 已成功保存双语内容")
        else:
            print(f"API 返回错误: {data}")
            
    except Exception as e:
        print(f"脚本运行出错: {e}")

if __name__ == "__main__":
    fetch_latam_news()
