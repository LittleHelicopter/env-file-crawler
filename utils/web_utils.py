import warnings

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def remove_header_footer(soup):
    """
    去掉页面中的 header 和 footer 部分，只保留其余内容。

    :param soup: BeautifulSoup 解析后的 HTML 内容。
    :return: soup, 去掉 header 和 footer 后的 HTML 内容。
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



def get_links_from_specific_div(base_url, div_class=None, header=None):
    """
    从指定 class 的 <div> 中提取链接。如果 div_class 为空，则提取所有 <div> 内的链接。
    header和footer一定会被去掉
    静态加载

    :param base_url: 目标网页的 URL。
    :param div_class: 目标 <div> 的 class 名称，默认为 None 表示不限制 class。
    :return: 目标 <div> 内部的所有链接列表。
    """
    warnings.warn(
        "This function is deprecated and will be removed in the future. "
        "Use get_links_from_specific_div_dynamic() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    try:
        response = requests.get(base_url, timeout=10, headers=header)
        response.raise_for_status()  # 确保请求成功
        base_url = response.url
        print(f"final_url {base_url}")
    except requests.RequestException as e:
        logging.error(f"请求失败: {e}")
        return []

    soup = remove_header_footer(BeautifulSoup(response.text, 'html.parser'))

    links = set()
    target_divs = soup.find_all(attrs={"class": div_class}) if div_class else soup.find_all('div')

    for div in target_divs:
        for a_tag in div.find_all('a', href=True):
            full_url = urljoin(base_url, a_tag['href'])
            # if urlparse(full_url).netloc == urlparse(base_url).netloc:  # 确保是同一网站
            links.add(full_url)

    logging.info(f"从 {base_url} 提取了 {len(links)} 个链接（div_class={div_class}）。")
    return list(links)


def get_links_from_specific_div_dynamic(base_url, div_class=None, time=5, header=None):
    """
    从指定 class 的 <div> 中提取链接。通过 Selenium 处理动态加载的网页内容。

    :param base_url: 目标网页的 URL。
    :param div_class: 目标 <div> 的 class 名称，默认为 None 表示不限制 class。
    :param driver_path: 浏览器驱动的路径，默认为 'chromedriver'。
    :return: 目标 <div> 内部的所有链接列表。
    """
    # 设置 Selenium 驱动程序
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
    driver = webdriver.Chrome(options=options)

    try:
        # 打开网页
        driver.get(base_url)

        # 等待直到页面加载完成，目标 div 存在
        if div_class:
            WebDriverWait(driver, timeout=time).until(
                EC.presence_of_element_located((By.CLASS_NAME, div_class))
            )
        else:
            WebDriverWait(driver, timeout=time).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
            )

        # 获取页面源代码并解析
        soup = remove_header_footer(BeautifulSoup(driver.page_source, 'html.parser'))

        # 提取目标 div 中的所有链接
        links = set()
        if div_class:
            target_divs = soup.find_all(attrs={"class": div_class})
        else:
            target_divs = soup.find_all('div')

        for div in target_divs:
            for a_tag in div.find_all('a', href=True):
                full_url = urljoin(base_url, a_tag['href'])
                links.add(full_url)

        logging.info(f"从 {base_url} 提取了 {len(links)} 个链接（div_class={div_class}）。")
        return list(links)
    except Exception as e:
        logging.error(f"爬取过程中发生错误: {e}")
        return []
    finally:
        # 关闭浏览器
        driver.quit()



