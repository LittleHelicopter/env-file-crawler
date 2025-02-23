import os

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from utils.file_utils import sanitize_filename
from utils.other_file_utils import get_other_file_extension_from_content_type, download_file
from utils.pdf_utils import is_pdf, download_pdf
from utils.snapshot_utils import is_html, download_html


# **等待文件下载完成**
import os
import time

START = time.time()
def wait_for_new_file(current_files, directory, timeout=360):
    start_time = time.time()

    while time.time() - start_time < timeout:
        new_files = set(os.listdir(directory))

        # 计算新增的文件
        added_files = new_files - current_files

        # 如果有新增文件，输出增加的文件名，并返回 True
        if added_files:
            for file in added_files:
                print(f"新增文件: {file}")
            return True

        # 更新当前文件集合
        current_files = new_files

        time.sleep(1)

    print("下载超时，没有检测到新文件。")
    return False


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

from_date = "01/01/2025"  # 开始日期，格式为 mm/dd/YYYY
# end_date = "12/31/2023"
keyword = "offshore wind"  # 在这里替换成你想搜索的关键词

root_save_folder = r"../data/ferc_elibrary/"
folder_name = sanitize_filename(from_date)
base_save_folder = os.path.abspath(os.path.join(root_save_folder, folder_name))

os.makedirs(base_save_folder, exist_ok=True)





chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": base_save_folder,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://elibrary.ferc.gov/eLibrary/search')
time.sleep(3)  # 等待页面加载

# 输入开始日期
date_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "mat-input-8"))
)

# 使用 JavaScript 清空日期输入框
driver.execute_script("arguments[0].value = '';", date_input)  # 清空内容
date_input.send_keys(from_date)  # 输入新的日期
date_input.send_keys(Keys.TAB)  # 切换焦点以触发验证
print(f"已输入开始日期：{from_date}")


time.sleep(3)  # 等待日期过滤结果加载


# # 输入结束日期
# date_input = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.ID, "mat-input-0"))
# )
#
# # 使用 JavaScript 清空日期输入框
# driver.execute_script("arguments[0].value = '';", date_input)  # 清空内容
# date_input.send_keys(end_date)  # 输入新的日期
# date_input.send_keys(Keys.TAB)  # 切换焦点以触发验证
# print(f"已输入开始日期：{end_date}")
#
#
# time.sleep(3)  # 等待日期过滤结果加载


# 输入关键词
search_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "mat-input-1"))
)
search_input.clear()  # 清除输入框
search_input.send_keys(keyword)
search_input.send_keys(Keys.RETURN)  # 模拟回车
print(f"已输入关键词：{keyword}")

# time.sleep(20)  # 等待搜索结果加载

# 点击 "下一页" 按钮并提取 href
while True:
    try:
        # 等待页面加载
        time.sleep(20)

        # 提取 tbody 内的所有 <a> 标签的 href 属性
        links = driver.find_elements(By.XPATH, "//tbody//a")

        # 输出每个链接的 href 属性
        for link in links:

            class_attr = link.get_attribute("class")
            opacity = link.value_of_css_property("opacity")  # 获取透明度
            link = link.get_attribute("href")

            # 判断是否是无效链接
            if (
                    link is None or
                    "/filelist?accession_Number=" in link or
                    "/docinfo?accession_Number=" in link or
                    link.endswith("optimized=false") or
                    "disabled" in class_attr or  # class 包含 'disabled'
                    float(opacity) < 0.5  # 透明度太低（通常是灰色）
            ):
                continue

            print(f'正在下载：{link}')
            try:
                link_response = requests.head(link, headers=headers)
                content_type = link_response.headers.get('Content-Type', '')

                # 如果是 PDF 文件，则下载 PDF
                if is_pdf(content_type, link):
                    print(f"下载 PDF 文件：{link}")
                    download_pdf(link, headers, base_save_folder)

                elif is_html(content_type):
                    print(f"打开html：{link}")
                    try:

                        current_files = set(os.listdir(base_save_folder))
                        # **打开链接**
                        driver.execute_script("window.open(arguments[0]);", link)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)  # 等待新页面加载，触发自动下载

                        # **等待文件下载**
                        wait_for_new_file(current_files, base_save_folder)

                        # **关闭下载页面，返回主页面**
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                    except requests.exceptions.RequestException as e:
                        print(f"访问 {link} 时发生错误: {e}")
                    print(f"进入第二层抓取 HTML：{link}")

                # 对于其他文件类型，下载文件
                else:
                    file_ext = get_other_file_extension_from_content_type(content_type)
                    if file_ext:
                        print(f"下载 {file_ext} 文件：{link}")
                        download_file(link, base_save_folder, headers)
                    else:
                        print(f"跳过未知文件类型：{link}")

            except requests.exceptions.RequestException as e:
                print(f"检查链接 {link} 时发生错误: {e}")

        # 等待下一页内容加载
        time.sleep(2)

        # 定位并点击下一页按钮
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next page']"))
        )
        next_button.click()
        print("已点击下一页")

    except Exception as e:
        print("没有下一页了", e)
        break

# 关闭浏览器
driver.quit()

END = time.time()

elapsed_time = END - START  # 计算运行时间

print(f"代码运行时间: {elapsed_time:.6f} 秒")