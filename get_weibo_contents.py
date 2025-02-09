import requests
import pandas as pd
import re
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def extract_uid(input_str):
    """从用户输入的网址或UID中提取数字UID"""
    match = re.search(r'(?:uid=|/u/|^)(\d+)', input_str)
    if match:
        return match.group(1)
    else:
        raise ValueError("无法提取UID，请检查输入格式是否为以下之一：\n1. https://weibo.com/u/123456\n2. 123456")

def manual_login_get_cookies():
    """通过手动登录获取cookies"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://weibo.com/login.php")
    
    print("请执行以下操作：")
    print("1. 在浏览器中手动登录微博账号")
    print("2. 登录完成后，在控制台按回车继续")
    input()
    
    # 获取登录后的cookies
    cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
    driver.quit()
    return cookies

def weibo_spider(uid, cookies):
    """微博数据爬取主函数"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Referer': f'https://m.weibo.cn/u/{uid}',
    }
    
    data_list = []
    page = 1
    containerid = f'107603{uid}'
    
    while True:
        url = f'https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}&containerid={containerid}&page={page}'
        
        try:
            response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
            if response.status_code != 200:
                print(f"请求失败，状态码：{response.status_code}")
                break
                
            data = response.json()
            cards = data.get('data', {}).get('cards', [])
            
            if not cards:
                print("没有更多数据，爬取结束")
                break

            for card in cards:
                if card.get('card_type') == 9:  # 仅处理微博卡片
                    mblog = card.get('mblog', {})
                    
                    # 处理时间格式
                    created_at = mblog.get('created_at', '')
                    try:
                        dt = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
                        date = dt.strftime('%Y-%m-%d')
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        date, time_str = '', ''
                    
                    # 处理博文内容
                    text = re.sub(r'<.*?>|回复<a.*?</a>:', '', mblog.get('text', ''))
                    
                    # 获取设备信息
                    source = mblog.get('source', '')
                    device = re.sub(r'^来自', '', source) if source else ''
                    
                    # 构建数据记录
                    data_list.append({
                        '序号': len(data_list) + 1,
                        '日期': date,
                        '时间': time_str,
                        '博文内容': text.strip(),
                        '评论': mblog.get('comments_count', 0),
                        '手机编辑': device
                    })
            
            print(f"已处理第 {page} 页，累计获取 {len(data_list)} 条数据")
            page += 1
            time.sleep(3)  # 增加请求间隔防止被封
            
        except Exception as e:
            print(f"发生错误：{str(e)}")
            break
    
    return data_list

def save_to_excel(data, filename):
    """保存数据到Excel文件"""
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"数据已保存到 {filename}")

if __name__ == "__main__":
    # 获取用户输入并提取UID
    while True:
        try:
            uid_input = input("请输入微博用户主页网址或UID（示例：https://weibo.com/u/123456 或直接输入123456）: ").strip()
            uid = extract_uid(uid_input)
            break
        except ValueError as e:
            print(e)
    
    # 获取cookies
    print("开始获取登录cookies...")
    cookies = manual_login_get_cookies()
    
    # 执行爬取
    print("开始爬取数据...")
    weibo_data = weibo_spider(uid, cookies)
    
    # 保存结果
    if weibo_data:
        save_to_excel(weibo_data, "weibo_posts.xlsx")
    else:
        print("没有获取到数据")