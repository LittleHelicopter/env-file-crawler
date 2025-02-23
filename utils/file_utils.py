import hashlib
import os
import json
import csv
import pickle
import re


def sanitize_filename(url: str, max_length: int = 150) -> str:
    """
    处理 URL 转换为合法文件名：
    - 替换非法字符
    - 限制最大长度
    - 避免 Windows 不支持的字符
    """
    # 只保留字母、数字、横线和下划线
    sanitized = re.sub(r'[<>:"/\\|?*\[\]&=]', '_', url)

    # 限制最大长度，防止路径过长
    if len(sanitized) > max_length:
        hash_suffix = hashlib.md5(url.encode()).hexdigest()[:8]  # 添加哈希防止重复
        sanitized = sanitized[:max_length - 9] + "_" + hash_suffix  # 确保不超出长度

    return sanitized

def save_file(file_path, content, mode='w'):
    """
    将内容保存到文本文件。
    
    :param file_path: 文件路径
    :param content: 要写入文件的内容
    :param mode: 文件打开模式，默认是 'w'（写入模式）
    """
    try:
        with open(file_path, mode, encoding='utf-8') as file:
            file.write(content)
        print(f"文件已成功保存: {file_path}")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")


def save_url_to_file(file_path, links, mode='w'):
    try:
        with open(file_path, mode, encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")
        print(f"已保存 {len(links)} 个链接到 {file_path}")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")


def read_file(file_path, mode='r'):
    """
    从文本文件读取内容。
    
    :param file_path: 文件路径
    :param mode: 文件打开模式，默认是 'r'（读取模式）
    :return: 文件内容（字符串）
    """
    try:
        with open(file_path, mode, encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


def read_urls_from_file(file_path, mode='r'):
    """
    从文本文件中逐行读取 URLs，并返回一个列表。

    :param file_path: 文件路径
    :param mode: 文件打开模式，默认是 'r'（读取模式）
    :return: URL 列表
    """
    try:
        with open(file_path, mode, encoding='utf-8') as file:
            # 逐行读取文件，并返回 URL 列表
            urls = file.read().splitlines()
        return urls
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return []

def save_binary_file(file_path, content):
    """
    保存二进制文件。
    
    :param file_path: 文件路径
    :param content: 二进制内容
    """
    try:
        with open(file_path, 'wb') as file:
            file.write(content)
        print(f"文件已成功保存为二进制格式: {file_path}")
    except Exception as e:
        print(f"保存二进制文件时发生错误: {e}")

def read_binary_file(file_path):
    """
    读取二进制文件。
    
    :param file_path: 文件路径
    :return: 文件内容（字节）
    """
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"读取二进制文件时发生错误: {e}")
        return None

def save_json(file_path, data):
    """
    将数据保存为 JSON 文件。
    
    :param file_path: 文件路径
    :param data: 要保存的数据（通常为字典或列表）
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"JSON 文件已保存: {file_path}")
    except Exception as e:
        print(f"保存 JSON 文件时发生错误: {e}")

def read_json(file_path):
    """
    读取 JSON 文件并返回数据。
    
    :param file_path: 文件路径
    :return: 解析后的 JSON 数据（字典或列表）
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"读取 JSON 文件时发生错误: {e}")
        return None

def save_csv(file_path, data, fieldnames=None):
    """
    将数据保存为 CSV 文件。
    
    :param file_path: 文件路径
    :param data: 数据，通常为列表的列表或字典的列表
    :param fieldnames: 字段名（如果是字典数据），可选
    """
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames) if isinstance(data, list) and isinstance(data[0], dict) else csv.writer(file)
            if isinstance(data, list) and isinstance(data[0], dict):
                writer.writeheader()
            writer.writerows(data)
        print(f"CSV 文件已保存: {file_path}")
    except Exception as e:
        print(f"保存 CSV 文件时发生错误: {e}")

def read_csv(file_path):
    """
    读取 CSV 文件并返回数据。
    
    :param file_path: 文件路径
    :return: CSV 数据，列表的列表或字典的列表
    """
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = list(reader)
        return data
    except Exception as e:
        print(f"读取 CSV 文件时发生错误: {e}")
        return None

def save_pickle(file_path, data):
    """
    将数据保存为 pickle 文件。
    
    :param file_path: 文件路径
    :param data: 要保存的数据
    """
    try:
        with open(file_path, 'wb') as file:
            pickle.dump(data, file)
        print(f"Pickle 文件已保存: {file_path}")
    except Exception as e:
        print(f"保存 Pickle 文件时发生错误: {e}")

def read_pickle(file_path):
    """
    从 pickle 文件读取数据。
    
    :param file_path: 文件路径
    :return: 解析后的数据
    """
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        return data
    except Exception as e:
        print(f"读取 Pickle 文件时发生错误: {e}")
        return None
