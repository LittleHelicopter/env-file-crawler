import os
import requests

from utils.file_utils import sanitize_filename

# 定义文件夹路径
base_folder = '../data/other_doe_pages'

# 创建文件夹，如果不存在的话
if not os.path.exists(base_folder):
    os.makedirs(base_folder)

# 定义每个年份对应的多个链接
files_by_year = {
    "2012": [
        "https://www1.eere.energy.gov/wind/pdfs/2012_wind_technologies_market_report.pdf"
    ],
    "2013": [
        "https://www.energy.gov/sites/default/files/2014/08/f18/2013%20Wind%20Technologies%20Market%20Report_1.pdf"
    ],
    "2014": [
        "https://www.energy.gov/sites/default/files/2015/08/f25/2014-Wind-Technologies-Market-Report-8.7.pdf"
    ],
    "2015": [
        "https://www.energy.gov/sites/default/files/2016/08/f33/2015-Wind-Technologies-Market-Report-08162016.pdf"
    ],
    "2016": [
        "https://www.energy.gov/sites/prod/files/2017/10/f37/2016_Wind_Technologies_Market_Report_101317.pdf"
    ],
    "2017": [
        "https://www.energy.gov/sites/default/files/2018/08/f54/2017_wind_technologies_market_report_8.15.18.v2.pdf"
    ],
    "2018": [
        "https://www.energy.gov/sites/prod/files/2019/08/f65/2018%20Wind%20Technologies%20Market%20Report%20FINAL.pdf"
    ]
}
def download_pdf_file_for_these_file(url, year):
    try:
        # 发送请求获取文件内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        # 根据年份创建文件夹
        year_folder = os.path.join(base_folder, year)
        if not os.path.exists(year_folder):
            os.makedirs(year_folder)

        # 生成合法的文件名
        file_name = sanitize_filename(url)

        # 定义保存路径
        save_path = os.path.join(year_folder, file_name)

        # 将文件保存到本地
        with open(save_path, 'wb') as file:
            file.write(response.content)

        print(f"文件已保存：{save_path}")
    except requests.exceptions.RequestException as e:
        print(f"下载失败：{url}，错误信息：{e}")

# 下载指定年份的文件
for year, urls in files_by_year.items():
    for url in urls:
        download_pdf_file_for_these_file(url, year)

print("所有文件下载完成！")