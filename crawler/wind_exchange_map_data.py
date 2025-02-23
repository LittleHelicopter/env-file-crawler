"""
https://windexchange.energy.gov/maps-data?per_page=96&page=1
仅抓取两层
"""

import re
import sys

sys.path.append("..")
import requests
import os
import time
from urllib.parse import urljoin, urlparse
from utils.other_file_utils import download_file, get_other_file_extension_from_content_type
from utils.snapshot_utils import download_html, is_html
from utils.file_utils import sanitize_filename, read_urls_from_file
from utils.pdf_utils import download_pdf, is_pdf
from utils.web_utils import remove_header_footer, get_links_from_specific_div, get_links_from_specific_div_dynamic

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

# 配置日志记录
logging.basicConfig(filename="../logs/wind_exchange_map_data.txt",  # 日志文件名
                    level=logging.INFO,  # 设置日志级别
                    format='%(asctime)s - %(levelname)s - %(message)s')  # 日志格式

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

root_save_folder = r"../data/"

start_urls = ["https://windexchange.energy.gov/maps-data?per_page=96&page=1",
              "https://windexchange.energy.gov/maps-data?per_page=96&page=2"]

# 为每个 URL 生成简短的文件名
url_to_filename = {
    "https://windexchange.energy.gov/maps-data?per_page=96&page=1": "wind_exchange_map_data",
    "https://windexchange.energy.gov/maps-data?per_page=96&page=2": "wind_exchange_map_data"
}

visited_urls = set()


# 定义请求的基本操作
def process_first_and_second_layer(base_url, pdf_folder, other_files_folder):
    """处理第一层和第二层页面，抓取 HTML、PDF 和其他文件，并传递 HTML 链接到下一层"""
    if base_url in visited_urls:
        return
    visited_urls.add(base_url)

    try:
        # 获取当前页面的链接
        # start链接页面上的链接
        links = get_links_from_specific_div_dynamic(base_url, "visualizations-list")

        # 下载当前页面的 HTML
        download_html(base_url, html_folder, headers)

        # 循环遍历所有链接并处理
        for link in links:
            try:
                link_response = requests.head(link, headers=headers)
                content_type = link_response.headers.get('Content-Type', '')

                # 如果 Content-Type 是 HTML，则下载 HTML 并传递到下一层
                if is_html(content_type):
                    download_html(link, html_folder, headers)
                    print(f"进入第二层抓取 HTML：{link}")
                    process_second_layer(link, pdf_folder, other_files_folder)

                # 如果是 PDF 文件，则下载 PDF
                elif is_pdf(content_type, link):
                    print(f"下载 PDF 文件：{link}")
                    download_pdf(link, headers, pdf_folder)

                # 对于其他文件类型，下载文件
                else:
                    file_ext = get_other_file_extension_from_content_type(content_type)
                    if file_ext:
                        print(f"下载 {file_ext} 文件：{link}")
                        download_file(link, other_files_folder, headers)
                    else:
                        print(f"跳过未知文件类型：{link}")

            except requests.exceptions.RequestException as e:
                print(f"处理链接 {link} 时发生错误: {e}")

    except requests.exceptions.RequestException as e:
        print(f"访问 {base_url} 时发生错误: {e}")


def process_second_layer(url, pdf_folder, other_files_folder):
    """处理第二层页面，只抓取 PDF 和其他文件，不再下载 HTML"""
    if url in visited_urls:
        return
    visited_urls.add(url)

    try:
        # 获取当前页面的链接
        links = get_links_from_specific_div_dynamic(url)

        for link in links:
            try:
                link_response = requests.head(link, headers=headers)
                content_type = link_response.headers.get('Content-Type', '')

                # 如果是 PDF 文件，则下载 PDF
                if is_pdf(content_type, link):
                    print(f"下载 PDF 文件：{link}")
                    download_pdf(link, headers, pdf_folder)

                elif is_html(content_type):
                    download_html(link, html_folder, headers)
                    print(f"进入第二层抓取 HTML：{link}")

                # 对于其他文件类型，下载文件
                else:
                    file_ext = get_other_file_extension_from_content_type(content_type)
                    if file_ext:
                        print(f"下载 {file_ext} 文件：{link}")
                        download_file(link, other_files_folder, headers)
                    else:
                        print(f"跳过未知文件类型：{link}")


            except requests.exceptions.RequestException as e:
                print(f"检查链接 {link} 时发生错误: {e}")

    except requests.exceptions.RequestException as e:
        print(f"访问 {url} 时发生错误: {e}")


# 主程序逻辑
for base_url in start_urls:
    # 生成文件夹路径
    folder_name = url_to_filename.get(base_url, sanitize_filename(
        base_url.replace('https://', '').replace('www.', '').strip('/')))
    base_save_folder = os.path.join(root_save_folder, folder_name)

    # 定义保存 HTML、PDF 和其他文件的文件夹路径
    html_folder = os.path.join(base_save_folder, "html")
    pdf_folder = os.path.join(base_save_folder, "pdf")
    other_files_folder = os.path.join(base_save_folder, "other_files")

    # 如果文件夹不存在，则创建它们
    os.makedirs(html_folder, exist_ok=True)
    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(other_files_folder, exist_ok=True)

    # 处理第一层和第二层
    process_first_and_second_layer(base_url, pdf_folder, other_files_folder)

    # 处理第三层，只抓取 PDF 和其他文件
    process_second_layer(base_url, pdf_folder, other_files_folder)
