"""https://www.fisheries.noaa.gov/topic/offshore-wind-energy"""
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

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

# 配置日志记录
logging.basicConfig(filename="../logs/noaa_fisher_offshore_wind_energy_crawl_log.txt",  # 日志文件名
                    level=logging.INFO,       # 设置日志级别
                    format='%(asctime)s - %(levelname)s - %(message)s')  # 日志格式

def get_links_from_primary_div(base_url, html_content):
    """
    从页面中去掉header和footer的部分

    :param base_url: 网站的基础 URL。
    :param html_content: 网页的 HTML 内容。
    :return: 从页面中去掉header和footer的部分的内容抓取的list
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    modified_soup = remove_header_footer(soup)

    links = set()
    if modified_soup:  # 如果找到了该 div
        for a_tag in modified_soup .find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(base_url).netloc:  # 确保是同一网站
                links.add(full_url)

    logging.info(f"从页面 {base_url} 提取了 {len(links)} 个链接。")
    return list(links)


def remove_header_footer(soup):
    """
    去掉页面中的 header 和 footer 部分，只保留其余内容。

    :param soup: BeautifulSoup 解析后的 HTML 内容。
    :return: 去掉 header 和 footer 后的 HTML 内容。
    """
    # 删除 header 和 footer
    header = soup.find('header')
    if header:
        header.decompose()  # 删除 header 部分

    footer = soup.find('footer')
    if footer:
        footer.decompose()  # 删除 footer 部分

    # 返回去掉 header 和 footer 后的剩余内容
    return soup


def crawl_website(start_url, save_folder, max_depth=2):
    """
    爬取网站中的 HTML 页面，并下载 PDF 及其他支持的文件格式。

    :param start_url: 网站的起始 URL。
    :param save_folder: 存储网页和文件的文件夹。
    :param max_depth: 最大抓取深度（默认值 2）。
    """

    to_visit = [(start_url, 0)]
    visited = set()
    headers = {"User-Agent": "Mozilla/5.0"}

    # 创建 HTML、PDF 和其他文件的目录
    html_folder = os.path.join(save_folder, "html")
    pdf_folder = os.path.join(save_folder, "pdf")
    other_files_folder = os.path.join(save_folder, "other_files")
    os.makedirs(html_folder, exist_ok=True)
    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(other_files_folder, exist_ok=True)

    download_html(start_url, html_folder, headers)

    while to_visit:
        url, depth = to_visit.pop(0)
        if (url not in visited and depth <= max_depth):
            visited.add(url)
            logging.info(f"访问: {url} (深度: {depth})")

            try:
                response = requests.get(url, headers=headers, stream=True)
                response.raise_for_status()

                content_type = response.headers.get('Content-Type', '')

                # 处理 HTML 页面
                if is_html(content_type):
                    links = get_links_from_primary_div(url, response.text)
                    for link in links:
                        if link not in visited:
                            to_visit.append((link, depth + 1))

                    html_filename = sanitize_filename(url) + ".html"
                    html_file_path = os.path.join(html_folder, html_filename)

                    download_html(url, html_folder, headers)

                    logging.info(f"保存 HTML: {html_file_path}")

                # 处理 PDF 文件
                elif is_pdf(content_type):
                    download_pdf(url, headers, pdf_folder)
                    logging.info(f"下载 PDF: {url}")

                # 处理其他支持的文件类型
                else:
                    file_ext = get_other_file_extension_from_content_type(content_type)
                    if file_ext:
                        try:
                            download_file(url, other_files_folder, headers)
                            logging.info(f"下载 {file_ext} 文件: {url}")
                        except Exception as e:
                            logging.error(f"下载 {file_ext} 失败: {e}")
                    else:
                        logging.warning(f"跳过未知文件类型: {url} ({content_type})")

            except requests.exceptions.RequestException as e:
                logging.error(f"请求失败: {e}")
            except Exception as e:
                logging.error(f"处理 {url} 时发生错误: {e}")

    logging.info(f"抓取完成，共访问 {len(visited)} 个页面。")

def crawl_multiple_websites(start_urls, base_save_folder, max_depth=3):
    """
    遍历多个网站，抓取每个网站的子页面，确保每个网站的页面保存到独立文件夹。

    :param start_urls: 一个包含多个 URL 的列表。
    :param base_save_folder: 所有页面保存的根文件夹。
    :param max_depth: 最大抓取深度（默认值是 3）。
    """
    for start_url in start_urls:
        logging.info(f"开始爬取: {start_url}")
        # 使用 sanitize_filename 来规范化每个 URL 对应的文件夹名称
        parts = re.split(r'[\\/]', start_url)
        folder_name = sanitize_filename(parts[-1] or (parts[-2] if len(parts) > 1 else "index"))
        save_folder = os.path.join(base_save_folder, folder_name)

        # 创建文件夹（如果不存在）
        os.makedirs(save_folder, exist_ok=True)

        # 调用 crawl_website 函数
        crawl_website(start_url, save_folder, max_depth)


# 示例：多个 start_url
start_urls = [
              # 'https://www.fisheries.noaa.gov/topic/offshore-wind-energy/overview',
              'https://www.fisheries.noaa.gov/topic/offshore-wind-energy/assessing-impacts-to-marine-life',
              'https://www.fisheries.noaa.gov/topic/offshore-wind-energy/evaluating-impacts-to-fisheries']

# 指定根保存文件夹路径
base_save_folder = r"../data/noaa_fisher_osw_energy/"

# 调用爬虫函数
crawl_multiple_websites(start_urls, base_save_folder)
