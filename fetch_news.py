import requests
import json
import os
import time
from deep_translator import MyMemoryTranslator

# 1. 基础配置
API_KEY = os.getenv('NEWSDATA_API_KEY')
# 严格遵守 5 个国家限制：阿根廷, 巴西, 智利, 哥伦比亚, 墨西哥
COUNTRIES = "ar,br,cl,co,mx" 

def translate_text(text):
    """翻译核心函数，带容错机制"""
    if not text or len(str(text).strip()) < 5:
        return ""
    try:
        # MyMemory 自动识别西语/葡语并转为中文
        return MyMemoryTranslator(source='auto', target='zh-CN').translate(text)
    except Exception as e:
        print(f"翻译接口暂不可用: {e}")
        return ""

def fetch_latam_news():
    if not API_KEY:
        print("错误：未检测到 API Key，请检查 GitHub Secrets 设置")
        return

    # 2. 抓取原文
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={COUNTRIES}&language=es,pt"
    
    try:
        print(f"正在抓取 {COUNTRIES} 的最新新闻...")
        response = requests.get(url, timeout=20)
        data = response.json()
        
        if data.get('status') == "success":
            results = data.get('results', [])
            print(f"抓取成功，共 {len(results)} 条，开始进行中文翻译...")
            
            for item in results:
                # 获取原文内容
                orig_title = item.get('title', '')
                orig_desc = item.get('description', '')

                # --- 核心翻译逻辑 (已修正变量名) ---
                item['title_zh'] = translate_text(orig_title)
                
                if orig_desc:
                    # 截取前250字防止翻译超时
                    item['description_zh'] = translate_text(orig_desc[:250])
                else:
                    item['description_zh'] = "点击原文链接查看详细报道"
                
                print(f"✅ 成功翻译：{item['title_zh'][:15]}...")
                time.sleep(0.5) # 避开频率限制

            # 3. 写入文件
            with open('latest_news.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print("数据处理完毕，latest_news.json 已存回仓库。")
            
        else:
            print(f"API 报错：{data}")
            
    except Exception as e:
        print(f"发生致命错误：{e}")

if __name__ == "__main__":
    fetch_latam_news()
