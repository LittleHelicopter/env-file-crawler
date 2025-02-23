
import sys
sys.path.append("..")
import requests
import os
import time
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from utils.snapshot_utils import download_html, is_html
from utils.file_utils import sanitize_filename, read_urls_from_file

from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_links_from_primary_div(base_url, html_content):
    """
    从页面中 `<div class="l-page__primary">` 部分提取所有链接。

    :param base_url: 网站的基础 URL。
    :param html_content: 网页的 HTML 内容。
    :return: 在 `<div class="l-page__primary">` 中的所有有效链接列表。
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    primary_div = soup.find('div', class_='node__content l-grid')  # 获取指定的 div

    links = set()
    if primary_div:  # 如果找到了该 div
        for a_tag in primary_div.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(base_url).netloc:  # 确保是同一网站
                links.add(full_url)

    return list(links)


def crawl_website(start_url, save_folder, max_depth=2):
    """
    遍历下载网站中的所有子页面，限制抓取深度，且确保仅抓取 HTML 页面，且仅从 <div class="l-page__primary"> 提取链接。

    :param start_url: 网站的首页 URL。
    :param save_folder: 存储网页的文件夹。
    :param max_depth: 最大抓取深度（默认值是 2）。
    """
    to_visit = [(start_url, 0)]  # 初始化待访问的链接队列，队列中的元素包含链接和当前深度
    visited = set()  # 用于存储已访问的链接
    headers = {"User-Agent": "Mozilla/5.0"}  # 设置请求头

    while to_visit:
        url, depth = to_visit.pop(0)
        if (url not in visited
                and depth <= max_depth):    # 如果不想限制深度只需要去掉这个
            visited.add(url)
            print(f"访问: {url} (深度: {depth})")

            try:
                # 发送请求并获取页面
                response = requests.get(url, headers=headers)
                response.raise_for_status()

                # 使用 is_html 判断页面是否为 HTML
                if is_html(response.headers.get('Content-Type', '')):
                    # 获取页面中 `<div class="l-page__primary">` 中的所有链接
                    links = get_links_from_primary_div(url, response.text)  # 从指定 div 提取链接
                    for link in links:
                        if link not in visited:
                            to_visit.append((link, depth + 1))  # 加一层深度

                    print(f"保存快照: {save_folder}")
                    download_html(url, save_folder, headers)
                else:
                    print(f"跳过非HTML页面: {url}")

            except requests.exceptions.RequestException as e:
                print(f"请求失败: {e}")

    print(f"抓取完成，共抓取 {len(visited)} 个页面。")




def crawl_multiple_websites(start_urls, base_save_folder, max_depth=2):
    """
    遍历多个网站，抓取每个网站的子页面，确保每个网站的页面保存到独立文件夹。

    :param start_urls: 一个包含多个 URL 的列表。
    :param base_save_folder: 所有页面保存的根文件夹。
    :param max_depth: 最大抓取深度（默认值是 3）。
    """
    for start_url in start_urls:
        print(start_url)
        # 使用 sanitize_filename 来规范化每个 URL 对应的文件夹名称
        folder_name = sanitize_filename(start_url.replace('https://', '').replace('www.', '').strip('/'))
        save_folder = os.path.join(base_save_folder, folder_name)

        # 创建文件夹（如果不存在）
        os.makedirs(save_folder, exist_ok=True)

        # 调用 crawl_website 函数
        print(f"开始爬取: {start_url}")
        crawl_website(start_url, save_folder, max_depth)


# 示例：多个 start_url
start_urls = read_urls_from_file(r"../data/links_to_scrape/boem_snapshot_links.txt")
#     [
#     "https://www.boem.gov/renewable-energy/rules-development-and-interim-policy",
#     # "https://www.boem.gov/about-boem/procurement-business-opportunities"
# ]

# 指定根保存文件夹路径
base_save_folder = r"../data/snapshots/boem"

# 调用爬虫函数
crawl_multiple_websites(start_urls, base_save_folder)

# # 示例用法
# start_url = "https://www.boem.gov/renewable-energy/rules-development-and-interim-policy"
# save_folder = "data/snapshots/boem/rules-development-and-interim-policy"  # 保存文件夹路径
# crawl_website(start_url, save_folder)


# 示例用法
# url = "https://www.boem.gov/renewable-energy/state-activities/coastal-virginia-offshore-wind-project-cvow-research-project"
# save_folder = "test"  # 你可以修改保存目录
# save_filename = "cvow_snapshot.html"
# save_path = os.path.join(save_folder, save_filename)

# download_html(url, save_path)
