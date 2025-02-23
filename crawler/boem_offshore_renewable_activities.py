"""
计划更改爬取目标：state activities
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # 使用 webdriver-manager 自动安装和管理 ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def scrape_state_links(url):
    driver = initialize_driver()

    try:
        driver.get(url)

        # 等待页面加载完成
        wait = WebDriverWait(driver, 30)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

        # 等待地图加载完成（确保地图元素已加载）
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".esri-ui.calcite-mode-light")))

        # 找到所有可以点击的州（假设它们是地图上的区域，使用 CSS Selector 选择它们）
        # 你需要根据实际页面的 HTML 结构来修改选择器
        state_elements = driver.find_elements(By.CSS_SELECTOR, ".esri-ui.calcite-mode-light a")

        # 存储所有的链接
        state_links = []

        for state in state_elements:
            # 模拟点击每个州
            state.click()

            # 等待新页面加载
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

            # 抓取该州的链接（假设在点击后会显示该州的相关链接，调整选择器根据实际情况）
            try:
                # 假设链接存在某个已加载的元素内
                state_link = driver.find_element(By.CSS_SELECTOR, "a[state-detail-link]").get_attribute("href")
                if state_link:
                    state_links.append(state_link)
            except Exception as e:
                print(f"Error retrieving link for state: {e}")

            # 返回上一页
            driver.back()
            time.sleep(2)  # 给页面一些时间返回并加载内容

        return state_links

    finally:
        driver.quit()


def save_links_to_file(links, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")


# URL 你需要爬取的页面
url = "https://www.boem.gov/renewable-energy/offshore-renewable-activities"
links = scrape_state_links(url)

# 保存到文件
save_folder = "../data/boem_state_links/"
save_path = os.path.join(save_folder, "state_links.txt")
# save_links_to_file(links, save_path)

print(f"已保存 {len(links)} 个州链接到 {save_path}")
