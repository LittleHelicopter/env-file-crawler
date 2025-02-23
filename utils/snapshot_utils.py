import os
import re
import time

import requests
from urllib.parse import urljoin, urlparse
from utils.file_utils import sanitize_filename

def is_html(content_type: str) -> bool:
    """
    判断 Content-Type 是否为 HTML 类型。
    
    :param content_type: 文件的 Content-Type（MIME 类型）
    :return: 如果是 HTML 类型，则返回 True，否则返回 False
    """
    return 'text/html' in content_type.lower()


def download_html(url, download_folder, headers=None):
    """
    下载 HTML 文件并保存到指定文件夹。
    
    :param url: 目标 URL
    :param headers: 请求头
    :param download_folder: 保存 HTML 文件的文件夹路径
    """
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果请求失败，会抛出异常
        
        # 判断 Content-Type 是否为 HTML
        content_type = response.headers.get('Content-Type', '')
        if is_html(content_type):
            # 生成保存文件的路径
            parts = re.split(r'[\\/]', url)  # 兼容 '/' 和 '\'
            file_name = parts[-1] or (parts[-2] if len(parts) > 1 else "index.html")  # 选取有效的文件名
            file_name += f"{int(time.time())}.html"
            
            # 如果目录不存在，创建目录
            os.makedirs(download_folder, exist_ok=True)
            file_name = sanitize_filename(file_name)
            print("filename" + file_name)
            file_path = os.path.join(download_folder, file_name)
            file_path = os.path.normpath(file_path)
            print("filepath" + file_path)
            
            # 保存 HTML 内容到文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"HTML 文件已保存: {file_path}")
        else:
            print(f"URL {url} 不是 HTML 文件，跳过下载。")
    
    except requests.exceptions.RequestException as e:
        print(f"下载 HTML 时出错: {e}")

# TODO


def generate_valid_filename(url):
    """
    生成合法的文件名。
    
    :param url: 要从中生成文件名的URL。
    :return: 合法的文件名，基于URL。
    """
    path = url.replace(base_url, '').strip('/')
    if not path:
        return 'index.html'  # 如果路径为空，则使用默认文件名
    # 替换非法字符为下划线
    path = path.replace('/', '_').replace('?', '_').replace(':', '_')
    return path + '.html'


def save_html_snapshot(url, html_content):
    """
    保存HTML页面内容快照到本地文件。

    :param url: 当前页面的URL。
    :param html_content: 网页的HTML内容。
    :return: 无
    """
    try:
        file_name = generate_valid_filename(url)  # 生成有效的文件名
        file_path = os.path.join(html_folder_path, file_name)  # 拼接文件路径
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html_content)  # 保存HTML内容
        print(f'保存HTML快照: {file_path}')
    except OSError as e:
        print(f"保存HTML快照出错: {e}")


def log_failed_url(url):
    """
    记录无法访问的URL到日志文件中。

    :param url: 无法访问的URL。
    :return: 无
    """
    try:
        with open(error_log_path, 'a') as log_file:
            log_file.write(f"{url}\n")
        print(f"Logged failed URL: {url}")
    except OSError as e:
        print(f"写入日志文件时出错: {e}")


def crawl_pdfs(url, save_directory, headers):
    """
    遍历当前页面并下载PDF文件。

    :param url: 当前页面的URL。
    :param save_directory: 保存下载的PDF文件的目录。
    :param headers: 请求头信息。
    :return: 无
    """
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type')
        if 'application/pdf' in content_type:
            # 如果是PDF文件，下载并保存
            pdf_url = urljoin(url, urlparse(url).path)
            pdf_name = os.path.basename(pdf_url)
            pdf_save_path = os.path.join(save_directory, pdf_name)
            download_file(pdf_url, pdf_save_path, headers)

    except requests.exceptions.RequestException as e:
        print(f"下载PDF文件时出错: {e}")