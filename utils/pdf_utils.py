import os
import re
import time

import requests


def is_pdf(content_type, link=""):
    """
    判断 Content-Type 是否为 PDF 文件类型。
    
    :param link: 也可以通过link追加判断
    :param content_type: 文件的 Content-Type（MIME 类型）
    :return: 如果是 PDF 类型，则返回 True，否则返回 False
    """
    return 'application/pdf' in content_type or link.lower().endswith(".pdf")


def download_pdf(url: str, headers: dict, download_folder: str):
    """
    下载 PDF 文件并保存到指定文件夹。
    
    :param url: 目标 URL
    :param headers: 请求头
    :param download_folder: 保存 PDF 文件的文件夹路径
    """
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果请求失败，会抛出异常
        
        # 判断 Content-Type 是否为 PDF
        content_type = response.headers.get('Content-Type', '')
        if is_pdf(content_type):
            # 生成保存文件的路径

            parts = re.split(r'[\\/]', url)  # 兼容 '/' 和 '\'
            file_name = parts[-1] or (parts[-2] if len(parts) > 1 else "index.pdf")  # 选取有效的文件名
            file_name += f"{int(time.time())}.pdf"

            # 如果目录不存在，创建目录
            os.makedirs(download_folder, exist_ok=True)
            file_path = os.path.join(download_folder, file_name)
            
            # 保存 PDF 内容到文件
            with open(file_path, 'wb') as file:  # PDF 文件需要以二进制方式写入
                file.write(response.content)
            print(f"PDF 文件已保存: {file_path}")
        else:
            print(f"URL {url} 不是 PDF 文件，跳过下载。")
    
    except requests.exceptions.RequestException as e:
        print(f"下载 PDF 时出错: {e}")