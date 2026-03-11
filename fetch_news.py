import requests
import json
import os
import time
from deep_translator import MyMemoryTranslator

# 从 GitHub Secrets 读取 API Key
API_KEY = os.getenv('NEWSDATA_API_KEY')
# 精确控制在 5 个国家：阿根廷, 巴西, 智利, 哥伦比亚, 墨西哥
COUNTRIES = "ar,br,cl,co,mx" 

def translate_text(text):
    """安全翻译函数"""
    if not text or len(str(text).strip()) < 5:
        return ""
    try:
        # 使用 MyMemory 自动识别源语言（西语或葡语）翻译到中文
        translated = MyMemoryTranslator(source='auto', target='zh-CN').translate(text)
        return translated
    except Exception as e:
        print(f"翻译小跳过: {e}")
        return ""

def fetch_latam_news():
    if not API_KEY:
        print("错误：Secret 中未找到 NEWSDATA_API_KEY")
        return

    # 抓取包含西班牙语(es)和葡萄牙语(pt)的新闻
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={COUNTRIES}&language=es,pt"
    
    try:
        print(f"1. 正在获取 {COUNTRIES} 的新闻原文（含西语/葡语）...")
        response = requests.get(url, timeout=20)
        data = response.json()
        
        if data.get('status') == "success":
            raw_results = data.get('results', [])
            processed_results = []
            
            print(f"2. 开始翻译处理（共 {len(raw_results)} 条）...")
            
            for item in raw_results:
                title_orig = item.get('title', '')
                # 执行翻译
                item['title_zh'] = translate_text(title_orig)
                
                desc_orig = item.get('description', '')
                if desc_es:
                    item['description_zh'] = translate_text(desc_orig[:250])
                else:
                    item['description_zh'] = ""
                
                processed_results.append(item)
                # 打印日志查看翻译后的标题
                print(f"✅ 处理完成: {item.get('title_zh', '原文加载')}...")
                # 停顿 0.5 秒防止请求过快被翻译服务器拦截
                time.sleep(0.5)

            # 3. 保存文件
            with open('latest_news.json', 'w', encoding='utf-8') as f:
                json.dump(processed_results, f, ensure_ascii=False, indent=4)
            print("3. 任务完成！双语数据（含巴西）已存入 latest_news.json")
        else:
            print(f"API 报错: {data.get('results', {}).get('message', data)}")
            
    except Exception as e:
        print(f"脚本运行出错: {e}")

if __name__ == "__main__":
    fetch_latam_news()
