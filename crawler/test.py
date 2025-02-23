from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from utils.web_utils import get_links_from_specific_div, get_links_from_specific_div_dynamic

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://emp.lbl.gov",  # 如果有的话，添加 Referrer
    "Origin": "https://emp.lbl.gov"    # 如果需要
}


def get_doi_link(url, headers):
    """
    从指定网页下获取 DOI 的链接，并跟踪重定向

    参数:
    - url: 网页的 URL。
    - headers: 请求头。

    返回:
    - 最终的 DOI 网页链接
    """
    try:
        # 发送请求获取网页内容，允许重定向
        response = requests.get(url, headers=headers, allow_redirects=True)
        response.raise_for_status()  # 检查请求是否成功


        # 使用 BeautifulSoup 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 定位到包含 DOI 的 <h3> 标签
        h3_tag = soup.find('h3', text='DOI')

        if h3_tag:
            # 查找其后的 <a> 标签并获取 DOI 链接
            a_tag = h3_tag.find_next('a', href=True)
            if a_tag:
                doi_link = a_tag['href']
                # 如果链接是相对路径，合成成绝对路径
                doi_link = urljoin(url, doi_link)
                return doi_link
            else:
                print("未找到 DOI 链接的 <a> 标签。")
        else:
            print("未找到包含 DOI 的 <h3> 标签。")
    except requests.exceptions.RequestException as e:
        print(f"请求过程中发生错误: {e}")


# 示例用法
link = "https://emp.lbl.gov/news/international-perspectives-social-acceptance"

doi_link = get_doi_link(link, headers)
print(f"doi:{doi_link}")
doi_pdf_url = get_links_from_specific_div(doi_link,
                                          "btn-multi-block mb-1",
                                          header=headers)

print(doi_pdf_url)

