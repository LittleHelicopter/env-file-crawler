import os
import requests
import re
import hashlib

from utils.file_utils import sanitize_filename

# 定义文件夹路径
base_folder = f'../data/eta_publications_lbl_other'

# 创建文件夹，如果不存在的话
if not os.path.exists(base_folder):
    os.makedirs(base_folder)

# 定义 PDF 文件的链接列表
pdf_links = [
    "https://eta-publications.lbl.gov/sites/default/files/osw_value_es_final.pdf",
    "https://eta-publications.lbl.gov/sites/default/files/lbnl-1005717.pdf",
    "https://eta-publications.lbl.gov/sites/default/files/lbnl-5793e-ppt.pdf",
    "https://eta-publications.lbl.gov/sites/default/files/lbnl-5793e.pdf",
    "https://crd.lbl.gov/assets/pubs_presos/fullbreezereport.pdf",
    "https://crd.lbl.gov/assets/pubs_presos/danehyreport.pdf",
    "https://eta-publications.lbl.gov/sites/default/files/berkeley_lab_2022.10.06-_miso_interconnection_costs.pdf",
    "https://eta-publications.lbl.gov/sites/default/files/report-46766.pdf"
]

# 处理 URL 转换为合法文件名

# 下载并保存 PDF 文件
def download_pdf_files_for_these_pages(url):
    try:
        # 发送请求获取文件内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        # 生成合法的文件名
        file_name = sanitize_filename(url)

        # 定义保存路径
        save_path = os.path.join(base_folder, file_name)

        # 将文件保存到本地
        with open(save_path, 'wb') as file:
            file.write(response.content)

        print(f"文件已保存：{save_path}")
    except requests.exceptions.RequestException as e:
        print(f"下载失败：{url}，错误信息：{e}")

# 下载所有 PDF 文件
for url in pdf_links:
    download_pdf_files_for_these_pages(url)

print("所有文件下载完成！")
