import os
import requests
import re
import hashlib

from utils.file_utils import sanitize_filename
from utils.snapshot_utils import download_html

# 定义文件夹路径
base_folder = f'../data/lbl_news'
# 定义请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

# 创建文件夹，如果不存在的话
if not os.path.exists(base_folder):
    os.makedirs(base_folder)

# 定义 PDF 文件的链接列表
urls = [
    "https://newscenter.lbl.gov/2023/06/01/reducing-the-cost-of-floating-offshore-wind/",
    "https://newscenter.lbl.gov/2024/08/21/report-highlights-advancements-in-wind-technology-and-supply-chains/",
    "https://newscenter.lbl.gov/2023/08/24/report-highlights-technology-advancement-and-value-of-wind-energy-2/",
    "https://newscenter.lbl.gov/2021/08/30/technology-advancement-and-value-of-wind-energy/",
    "https://newscenter.lbl.gov/2021/04/15/experts-predictions-for-future-wind-energy-costs-drop-significantly/",
    "https://newscenter.lbl.gov/2016/09/13/experts-anticipate-significant-continued-reductions-wind-energy-costs/",
    "https://newscenter.lbl.gov/2010/08/04/new-study-sheds-light-on-u-s-wind-power-market/",
    "https://newscenter.lbl.gov/2020/03/30/using-fiber-optics-to-advance-safe-and-renewable-energy/",
    "https://newscenter.lbl.gov/2017/02/15/catch-extreme-waves-with-higher-resolution-modeling/"
]



# 下载所有snapshot
for url in urls:
    download_html(url, base_folder, headers)

print("所有文件下载完成！")
