import requests
import json
import os

API_KEY = os.getenv('NEWSDATA_API_KEY')
# 这里我们先减少国家数量，测试一下稳定性，只填墨西哥(mx)和阿根廷(ar)
COUNTRIES = "mx,ar"

def fetch_latam_news():
    if not API_KEY:
        print("错误：没有找到 API_KEY，请检查 GitHub Secrets 设置！")
        return

    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={COUNTRIES}&language=es"
    
    print(f"正在请求接口...")
    try:
        response = requests.get(url)
        data = response.json()
        
        # 这一步很关键：把 API 返回的内容打印在 GitHub 的运行日志里
        print(f"API 返回状态: {data.get('status')}")
        
        if data['status'] == "success":
            if not data.get('results'):
                print("警告：API 请求成功，但没有找到任何新闻内容。")
                return
                
            with open('latest_news.json', 'w', encoding='utf-8') as f:
                json.dump(data['results'], f, ensure_ascii=False, indent=4)
            print(f"成功抓取到 {len(data['results'])} 条新闻！")
        else:
            # 如果失败了，打印出具体报错（比如 Key 错误或点数用完）
            print(f"API 返回错误信息: {data.get('results', {}).get('message') or data}")
            
    except Exception as e:
        print(f"程序运行发生致命错误: {e}")

if __name__ == "__main__":
    fetch_latam_news()
