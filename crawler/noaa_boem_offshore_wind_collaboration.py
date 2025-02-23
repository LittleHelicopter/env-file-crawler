

"""只下载一层link"""
import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# 从 utils 文件夹导入自定义的函数
from utils.file_utils import sanitize_filename
from utils.pdf_utils import download_pdf, is_pdf
from utils.snapshot_utils import is_html, download_html
from utils.other_file_utils import get_other_file_extension_from_content_type, download_file
from utils.web_utils import remove_header_footer

# 定义页面的基本 URL 和请求头
base_url = 'https://www.noaa.gov/news-release/noaa-and-boem-announce-interagency-collaboration-to-advance-offshore-wind-energy'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}


# 发送请求并获取页面内容
response = requests.get(base_url, headers=headers)

# 使用 BeautifulSoup 解析 HTML 内容
soup = remove_header_footer(BeautifulSoup(response.text, 'html.parser'))

# 提取页面上所有的链接，选择包含 "href" 属性的链接
links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]

# 定义保存文件的基本文件夹路径
base_save_folder = r"../data/noaa_boem_offshore_wind_collaboration/"


# 分别定义保存 HTML、PDF 和其他文件的文件夹路径
html_folder = os.path.join(base_save_folder, "html")
pdf_folder = os.path.join(base_save_folder, "pdf")
other_files_folder = os.path.join(base_save_folder, "other_files")

# 如果文件夹不存在，则创建它们
os.makedirs(html_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(other_files_folder, exist_ok=True)

# 下载当前页面 HTML 文件到指定文件夹
download_html(base_url, html_folder, headers)

# 循环遍历每个链接，判断它是否是 PDF 文件或其他类型文件
for link in links:
    try:
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
