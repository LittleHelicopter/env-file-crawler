import os
import re
import time

import requests
from urllib.parse import urlparse

from utils.file_utils import sanitize_filename


def download_file(url: str, save_path: str, headers: dict = None) -> None:
    """
    从指定 URL 下载非 HTML 文件，并根据 URL 或 Content-Type 确定文件扩展名后保存。
    :param url: 文件的 URL 地址
    :param save_path: 目标存储路径（可以是目录或完整文件路径）
    :param headers: 可选的请求头
    """
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # 获取 Content-Type
        content_type = response.headers.get("Content-Type", "").split(";")[0].strip()

        # 跳过 HTML 文件
        if 'text/html' in content_type:
            print(f"URL {url} 是 HTML 文件，跳过下载。")
            return

        # 根据 Content-Type 获取正确的扩展名
        correct_ext = get_other_file_extension_from_content_type(content_type)

        # 根据 URL 路径生成文件名
        parts = re.split(r'[\\/]', url)
        filename = parts[-1] or (parts[-2] if len(parts) > 1 else "index")

        filename = sanitize_filename(filename)
        filename += f"{int(time.time())}.{correct_ext}"
        print(filename)

        # # 如果没有扩展名且 Content-Type 可以解析，则补充扩展名
        # if not os.path.splitext(filename)[1] and correct_ext:
        #     filename += f"{int(time.time())}.{correct_ext}"
        # print(filename)


        # 如果 save_path 是目录，则拼接文件名
        if os.path.isdir(save_path) or save_path.endswith("/"):
            save_path = os.path.join(save_path, filename)

        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 保存文件
        with open(save_path, 'wb') as f:
            f.write(response.content)

        print(f"下载成功: {save_path}")
    except requests.exceptions.Timeout:
        print(f"下载超时: {url}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误 {response.status_code}: {url} - {e}")
    except requests.exceptions.ConnectionError:
        print(f"网络连接错误: {url}")
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {url} - {e}")



def get_other_file_extension_from_content_type(content_type: str) -> str:
    """
    根据 Content-Type 返回对应的文件扩展名。
    
    :param content_type: 文件的 Content-Type（MIME 类型）
    :return: 对应的文件扩展名，若未找到则返回 None
    """
    content_type_to_extension = {
        # 常见 Office 文件
        # 'application/pdf': 'pdf', # PDF 文件不在此处处理
        'application/msword': 'doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/vnd.ms-excel': 'xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
        'application/zip': 'zip',
        'application/x-zip-compressed': 'zip',
        'text/plain': 'txt',
        'application/vnd.ms-powerpoint': 'ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',

        # 常见文本文件
        # 'text/html': 'html', # HTML 文件不在此处处理
        'text/css': 'css',
        'text/javascript': 'js',
        'text/xml': 'xml',
        'text/csv': 'csv',
        'text/markdown': 'md',
        'text/tab-separated-values': 'tsv',

        # 常见图像文件
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'image/svg+xml': 'svg',
        'image/webp': 'webp',
        'image/bmp': 'bmp',
        'image/tiff': 'tiff',
        'image/x-icon': 'ico',

        # 常见音频文件
        'audio/mpeg': 'mp3',
        'audio/wav': 'wav',
        'audio/ogg': 'ogg',
        'audio/webm': 'webm',
        'audio/flac': 'flac',
        'audio/aac': 'aac',
        'audio/mp4': 'm4a',

        # 常见视频文件
        'video/mp4': 'mp4',
        'video/webm': 'webm',
        'video/ogg': 'ogv',
        'video/x-matroska': 'mkv',
        'video/avi': 'avi',
        'video/quicktime': 'mov',
        'video/x-msvideo': 'avi',
        'video/x-flv': 'flv',

        # 常见字体文件
        'font/woff': 'woff',
        'font/woff2': 'woff2',
        'font/ttf': 'ttf',
        'font/otf': 'otf',
        'application/vnd.ms-fontobject': 'eot',

        # 压缩文件
        'application/x-gzip': 'gz',
        'application/x-tar': 'tar',
        'application/x-rar-compressed': 'rar',
        'application/x-7z-compressed': '7z',
        'application/x-iso9660-image': 'iso',

        # 自定义及其他
        'application/x-shockwave-flash': 'swf',
        'application/epub+zip': 'epub',
        'application/x-msdownload': 'exe',
        'application/x-www-form-urlencoded': 'url',
        'application/vnd.api+json': 'json',
    }

    return content_type_to_extension.get(content_type.split(';')[0].strip())  # 忽略附加参数
