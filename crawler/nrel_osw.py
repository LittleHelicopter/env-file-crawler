"""
主页面为"https://www.nrel.gov/wind/offshore-wind.html"
主页面中的以下页面中的七个链接
    "https://www.nrel.gov/wind/atlantic-offshore-wind-transmission-study.html",
    "https://www.nrel.gov/wind/gulf-of-mexico-offshore-wind-transmission.html",
    "https://www.nrel.gov/news/press/2019/nrel-selected-for-series-of-offshore-wind-turbine-research-projects.html",
    "https://www.nrel.gov/wind/offshore-supply-chain-road-map.html",
    "https://www.nrel.gov/wind/west-coast-ports.html",
    "https://www.nrel.gov/wind/offshore-resource.html",
    "https://www.nrel.gov/wind/offshore-workforce.html",
    "https://www.nrel.gov/wind/offshore-market-assessment.html",
    "https://windexchange.energy.gov/offshore-workforce-safety-training",
    "https://www.pnnl.gov/projects/west-coast-offshore-wind-transmission-study",
    "https://www.nrel.gov/news/program/2020/scientific-collaboration-buoys-offshore-wind.html",
    "https://www.nrel.gov/wind/floating-offshore-array-design.html"
"""

import os
import time

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# 从 utils 文件夹导入自定义的函数
from utils.file_utils import sanitize_filename
from utils.pdf_utils import download_pdf, is_pdf
from utils.snapshot_utils import is_html, download_html
from utils.other_file_utils import get_other_file_extension_from_content_type, download_file
from utils.web_utils import remove_header_footer

# 定义请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

# 这里是包含多个起始 URL 的列表
start_urls = [
    "https://www.nrel.gov/wind/atlantic-offshore-wind-transmission-study.html",
    "https://www.nrel.gov/wind/gulf-of-mexico-offshore-wind-transmission.html",
    "https://www.nrel.gov/news/press/2019/nrel-selected-for-series-of-offshore-wind-turbine-research-projects.html",
    "https://www.nrel.gov/wind/offshore-supply-chain-road-map.html",
    "https://www.nrel.gov/wind/west-coast-ports.html",
    "https://www.nrel.gov/wind/offshore-resource.html",
    "https://www.nrel.gov/wind/offshore-workforce.html",
    "https://www.nrel.gov/wind/offshore-market-assessment.html",
    "https://windexchange.energy.gov/offshore-workforce-safety-training",
    "https://www.pnnl.gov/projects/west-coast-offshore-wind-transmission-study",
    "https://www.nrel.gov/news/program/2020/scientific-collaboration-buoys-offshore-wind.html",
    "https://www.nrel.gov/wind/floating-offshore-array-design.html"
]

# 为每个 URL 生成简短的文件名
url_to_filename = {
    "https://www.nrel.gov/wind/atlantic-offshore-wind-transmission-study.html": "atlantic-offshore-transmission",
    "https://www.nrel.gov/wind/gulf-of-mexico-offshore-wind-transmission.html": "gulf-mexico-offshore-transmission",
    "https://www.nrel.gov/news/press/2019/nrel-selected-for-series-of-offshore-wind-turbine-research-projects.html": "offshore-wind-turbine-research",
    "https://www.nrel.gov/wind/offshore-supply-chain-road-map.html": "offshore-supply-chain-roadmap",
    "https://www.nrel.gov/wind/west-coast-ports.html": "west-coast-ports",
    "https://www.nrel.gov/wind/offshore-resource.html": "offshore-resource",
    "https://www.nrel.gov/wind/offshore-workforce.html": "offshore-workforce",
    "https://www.nrel.gov/wind/offshore-market-assessment.html": "offshore-market-assessment",
    "https://windexchange.energy.gov/offshore-workforce-safety-training": "offshore-workforce-safety",
    "https://www.pnnl.gov/projects/west-coast-offshore-wind-transmission-study": "west-coast-transmission",
    "https://www.nrel.gov/news/program/2020/scientific-collaboration-buoys-offshore-wind.html": "scientific-buoys-offshore",
    "https://www.nrel.gov/wind/floating-offshore-array-design.html": "floating-offshore-array"
}

# 定义根保存文件夹路径
root_save_folder = r"../data/nrel_osw/"

# 定义请求的基本操作
for base_url in start_urls:
    # 获取每个 URL 对应的简短文件名
    folder_name = url_to_filename.get(base_url, sanitize_filename(base_url.replace('https://', '').replace('www.', '').strip('/')))
    base_save_folder = os.path.join(root_save_folder, folder_name)

    # 分别定义保存 HTML、PDF 和其他文件的文件夹路径
    html_folder = os.path.join(base_save_folder, "html")
    pdf_folder = os.path.join(base_save_folder, "pdf")
    other_files_folder = os.path.join(base_save_folder, "other_files")

    # 如果文件夹不存在，则创建它们
    os.makedirs(html_folder, exist_ok=True)
    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(other_files_folder, exist_ok=True)

    try:
        # 发送请求并获取页面内容

        response = requests.get(base_url, headers=headers)

        # 使用 BeautifulSoup 解析 HTML 内容
        soup = remove_header_footer(BeautifulSoup(response.text, 'html.parser'))

        # 提取页面上所有的链接，选择包含 "href" 属性的链接
        links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]

        # 下载当前页面 HTML 文件到指定文件夹
        download_html(base_url, html_folder, headers)

        # 循环遍历每个链接，判断它是否是 PDF 文件或其他类型文件
        for link in links:
            try:
                time.sleep(2)
                # 发送 HEAD 请求获取文件头部信息，检查 Content-Type
                link_response = requests.head(link, headers=headers)
                content_type = link_response.headers.get('Content-Type', '')
                print(link)

                # 如果 Content-Type 表示这是 HTML 文件
                if is_html(content_type):
                    print("正在下载当前页面")
                    download_html(link, html_folder, headers)

                # 如果 Content-Type 表示这是 PDF 文件
                elif is_pdf(content_type):
                    print("下载 pdf 文件中...")
                    download_pdf(link, headers, pdf_folder)

                # 对于其他类型的文件，根据 Content-Type 获取正确的扩展名
                else:
                    # 获取正确的扩展名
                    file_ext = get_other_file_extension_from_content_type(content_type)

                    if file_ext:
                        try:
                            # 下载其他类型文件
                            download_file(link, other_files_folder, headers)
                            print(f"下载 {file_ext} 文件: {link}")
                        except Exception as e:
                            # 捕获下载文件的异常
                            print(f"下载 {file_ext} 文件失败: {e}")
                    else:
                        # 如果无法识别文件类型，跳过该文件
                        print(f"跳过未知文件类型: {link} ({content_type})")

            except requests.exceptions.RequestException as e:
                # 处理请求时的异常
                print(f"检查链接 {link} 时发生错误: {e}")

    except requests.exceptions.RequestException as e:
        # 处理访问 base_url 时的异常
        print(f"访问 {base_url} 时发生错误: {e}")
