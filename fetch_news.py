import requests
import json
import os

# 1. 从刚才设置的 Secrets 中读取 Key
API_KEY = os.getenv('NEWSDATA_API_KEY')

# 2. 设置你想抓取的拉美国家代码
# ar=阿根廷, br=巴西, cl=智利, co=哥伦比亚, mx=墨西哥, pe=秘鲁
COUNTRIES = "ar,br,cl,co,mx,pe"

def fetch_latam_news():
    # 构建请求地址 (限制为西班牙语es和葡萄牙语pt)
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={COUNTRIES}&language=es,pt"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == "success":
            # 3. 将抓取到的结果保存为最新新闻文件
            with open('latest_news.json', 'w', encoding='utf-8') as f:
                json.dump(data['results'], f, ensure_ascii=False, indent=4)
            print("新闻抓取并保存成功！")
        else:
            print(f"API 报错: {data.get('message')}")
            
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    fetch_latam_news()
