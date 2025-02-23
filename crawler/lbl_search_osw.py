"""
可以不动态加载，下载doi的pdf的时候
"""

import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

from utils.file_utils import save_url_to_file
from utils.other_file_utils import get_other_file_extension_from_content_type, download_file
from utils.pdf_utils import is_pdf, download_pdf
from utils.snapshot_utils import download_html, is_html
from utils.web_utils import get_links_from_specific_div_dynamic, remove_header_footer, get_links_from_specific_div


def get_doi_link(url, headers):
    """
    从指定网页下获取 DOI 的链接

    参数:
    - url: 网页的 URL。
    - headers: 请求头。

    返回:
    - DOI 网页链接
    """
    try:
        # 发送请求获取网页内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
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



url = "https://search.lbl.gov/?q=offshore+wind#gsc.tab=0&gsc.q=offshore%20wind&gsc.sort=&gsc.page=1"


base_url = "https://search.lbl.gov/?q=offshore+wind#gsc.tab=0&gsc.q=offshore%20wind&gsc.sort="

page_urls = [f"{base_url}&gsc.page={page}" for page in range(1, 11)]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

# ================================
# 获取所有需要处理的链接
# ================================

"""

# 打印构造的 URL 列表
print(page_urls)

# 存放所有查询结果link的list
links = []
links.extend(page_urls)
for page_url in page_urls:
    links.extend(get_links_from_specific_div_dynamic(page_url, "gsc-expansionArea"))

# 打印链接
print(links)
print(len(links))
"""


# ================================
# 起始页处理与文件夹建立
# ================================


# 发送请求并获取页面内容
response = requests.get(base_url, headers=headers)

# 使用 BeautifulSoup 解析 HTML 内容
soup = remove_header_footer(BeautifulSoup(response.text, 'html.parser'))

# 提取页面上所有的链接，选择包含 "href" 属性的链接
links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]

# 定义保存文件的基本文件夹路径
base_save_folder = r"../data/lbl_search_osw/"

# 分别定义保存 HTML、PDF 和其他文件的文件夹路径
html_folder = os.path.join(base_save_folder, "html")
pdf_folder = os.path.join(base_save_folder, "pdf")
other_files_folder = os.path.join(base_save_folder, "other_files")

# 如果文件夹不存在，则创建它们
os.makedirs(html_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(other_files_folder, exist_ok=True)

# 下载当前页面 HTML 文件到指定文件夹
download_html(base_url, html_folder, headers)


# ================================
# 依次处理获取的每个链接
# ================================

links = ['https://eesa.lbl.gov/2025/01/21/advancing-floating-offshore-wind-technology-with-fiber-optic/', 'https://emp.lbl.gov/news/international-perspectives-social-acceptance', 'https://emp.lbl.gov/webinar/international-perspectives-social', 'https://emp.lbl.gov/publications/estimating-value-offshore-wind-along', 'https://energygeosciences.lbl.gov/research/focus-areas/floating-offshore-wind/', 'https://emp.lbl.gov/webinar/estimating-value-offshore-wind-along', 'https://eta-publications.lbl.gov/sites/default/files/osw_value_es_final.pdf', 'https://emp.lbl.gov/news/new-study-finds-market-value-offshore-wind', 'https://emp.lbl.gov/accelerating-offshore-wind-development-coastal-provinces-china', 'https://emp.lbl.gov/news/future-wind-energy-part-2-cost-reductions', 'https://energyanalysis.lbl.gov/publications/forecasting-wind-energy-costs-and', 'https://newscenter.lbl.gov/2023/06/01/reducing-the-cost-of-floating-offshore-wind/', 'https://emp.lbl.gov/sites/default/files/2024-05/China_OSW_2024_FINAL.pdf', 'https://eta-publications.lbl.gov/sites/default/files/offshore_wind_value_final.pdf', 'https://newscenter.lbl.gov/2021/04/15/experts-predictions-for-future-wind-energy-costs-drop-significantly/', 'https://emp.lbl.gov/publications/wind-power-costs-driven-innovation', 'https://newscenter.lbl.gov/2016/09/13/experts-anticipate-significant-continued-reductions-wind-energy-costs/', 'https://emp.lbl.gov/news/are-we-underestimating-potential-wind-energy', 'https://emp.lbl.gov/news/wind-power-costs-reduced-dramatically', 'https://emp.lbl.gov/news/experts-anticipate-larger-turbines', 'https://newscenter.lbl.gov/2022/08/16/report-highlights-technology-advancement-and-value-of-wind-energy/', 'https://eta-publications.lbl.gov/sites/default/files/lbnl-1005717.pdf', 'https://emp.lbl.gov/publications/expert-perspectives-wind-plant-future', 'https://eta-publications.lbl.gov/sites/default/files/expert_survey_factsheet.pdf', 'https://eta.lbl.gov/news/wind-energy-benefits-outweigh-costs', 'https://emp.lbl.gov/news/new-collaborative-nrellbnl-report', 'https://newscenter.lbl.gov/2024/08/21/report-highlights-advancements-in-wind-technology-and-supply-chains/', 'https://newscenter.lbl.gov/2020/03/30/using-fiber-optics-to-advance-safe-and-renewable-energy/', 'https://eta-publications.lbl.gov/sites/default/files/nyiso_interconnection_costs_vfinal.pdf', 'https://emp.lbl.gov/publications/land-based-wind-market-report-2022', 'https://emp.lbl.gov/publications/forecasts-land-based-wind-deployment', 'https://eta-publications.lbl.gov/sites/default/files/lbnl-5559e.pdf', 'https://emp.lbl.gov/publications/2015-cost-wind-energy-review', 'https://eta.lbl.gov/publications/land-based-wind-market-report-2021', 'https://emp.lbl.gov/News?field_tags_tid=379&page=11', 'https://emp.lbl.gov/sites/default/files/2024-09/Land-Based%20Wind%20Market%20Report_2024%20Edition_Presentation.pdf', 'https://eta-publications.lbl.gov/sites/default/files/webinar_slides_pdf.pdf', 'https://emp.lbl.gov/webinars?page=14', 'https://emp.lbl.gov/news/new-report-shows-technology-advancement-and', 'https://emp.lbl.gov/sites/default/files/news/future_of_wind_energy_iii.pdf', 'https://energyanalysis.lbl.gov/publications/land-based-wind-market-report-2021', 'https://eta-publications.lbl.gov/sites/default/files/wiser_natureenergy_article_resubmission2_clean.pdf', 'https://eesa.lbl.gov/news/all-news/', 'https://eesa.lbl.gov/news/', 'https://eta-publications.lbl.gov/sites/default/files/wind_plant_future_factsheet.pdf', 'https://eta-publications.lbl.gov/sites/default/files/wind_lcoe_elicitation_ne_pre-print_april2021.pdf', 'https://emp.lbl.gov/news/new-data-products-berkeley-lab-summarize', 'https://emp.lbl.gov/webinar/expert-elicitation-survey-predicts-37-49', 'https://emp.lbl.gov/news/webinar-us-interconnection-costs', 'https://emp.lbl.gov/news/are-we-understating-potential-and', 'https://www2.lbl.gov/mfea/assets/docs/posters/11_Industry.pdf', 'https://eesa.lbl.gov/', 'https://emp.lbl.gov/sites/default/files/2024-04/Queued%20Up%202024%20Edition%20-%20Webinar%20Version.pdf', 'https://emp.lbl.gov/maps-projects-region-state-and-county', 'https://energyanalysis.lbl.gov/publications/expert-elicitation-survey-future-wind', 'https://emp.lbl.gov/webinars?tag_42=21&page=2', 'http://eta-publications.lbl.gov/sites/default/files/iea_wind_future_cost_survey_oct_2015_final.pdf', 'https://emp.lbl.gov/news/grid-connection-requests-grow-40-2022-clean', 'https://eta-publications.lbl.gov/sites/default/files/scaling_turbines.pdf', 'https://energyanalysis.lbl.gov/publications/iea-wind-tcp-task-26-wind-technology', 'https://eta.lbl.gov/news/tech-advancement-and-value-wind', 'https://emp.lbl.gov/sites/default/files/2024-04/Queued%20Up%202024%20Edition_1.pdf', 'https://emp.lbl.gov/sites/default/files/emp-files/land-based_wind_market_report_2023_edition_final.pdf', 'https://ses.lbl.gov/publications/land-based-wind-market-report-2021', 'https://energygeosciences.lbl.gov/profile/ywu3/', 'https://elements.lbl.gov/all-news/page/126/', 'https://eta.lbl.gov/publications/2015-cost-wind-energy-review', 'https://energyanalysis.lbl.gov/news/tech-advancement-and-value-wind', 'http://eta-publications.lbl.gov/sites/default/files/presentation-lbnl-2829e.pdf', 'https://climatesciences.lbl.gov/profile/ywu3/', 'https://emp.lbl.gov/news/record-amounts-zero-carbon-electricity', 'https://energygeosciences.lbl.gov/', 'https://eta-publications.lbl.gov/sites/default/files/iso-ne_interconnection_costs_vfinal.pdf', 'https://energygeosciences.lbl.gov/profile/linqingluo/', 'https://newscenter.lbl.gov/2023/08/24/report-highlights-technology-advancement-and-value-of-wind-energy-2/', 'https://elements.lbl.gov/all-news/page/127/', 'https://emp.lbl.gov/publications/us-renewables-portfolio-standards-0', 'https://ei-spark.lbl.gov/generation/onshore-wind/turb/strat/', 'https://emp.lbl.gov/publications/2035-japan-report-plummeting-costs', 'https://elements.lbl.gov/all-news/page/115/', 'https://emp.lbl.gov/news?page=9', 'https://eta-publications.lbl.gov/sites/default/files/iea_wind_expert_survey_full_presentation.pdf.pdf', 'https://energygeosciences.lbl.gov/research/focus-areas/', 'https://emp.lbl.gov/news?page=12', 'https://eta-publications.lbl.gov/sites/default/files/land-based_wind_market_report_2024_edition_executive_summary.pdf', 'https://eta-publications.lbl.gov/sites/default/files/korean_power_system_challenges_and_opportunities.pdf', 'https://emp.lbl.gov/news/grid-connection-backlog-grows-30-2023-dominated-requests-solar-wind-and-energy-storage', 'https://www.nersc.gov/assets/Uploads/NUGcall_ERF.pdf', 'https://eta-publications.lbl.gov/sites/default/files/uswtdb_v7_0_052324_memo.pdf', 'https://emp.lbl.gov/publications/2009-wind-technologies-market-report', 'https://eta-publications.lbl.gov/research-areas/renewable-energy?page=1', 'https://emp.lbl.gov/search?page=13', 'https://emp.lbl.gov/sites/default/files/queued_up_2022_04-06-2023.pdf', 'https://energyanalysis.lbl.gov/publications?order=riendhfdc&s=year&o=desc&page=35', 'https://eta-publications.lbl.gov/sites/default/files/2024-12/wind_industry_survey.pdf', 'https://elements.lbl.gov/news/doe-accepting-proposals-for-earthshot-research-centers/', 'https://ei-spark.lbl.gov/generation/onshore-wind/project/info/', 'https://eta-publications.lbl.gov/sites/default/files/lbnl_wind_lcoe_survey_full_data_april2021.xlsx', 'https://emp.lbl.gov/sites/default/files/emp-files/lbnl_webinar_strongly_annoyed-_031218_-_final.pdf', 'https://eta-publications.lbl.gov/sites/default/files/2015_nrel_cost_of_wind_energy_review_lbnl.pdf']


headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    # "Referer": "https://emp.lbl.gov",  # 如果有的话，添加 Referrer
    # "Origin": "https://emp.lbl.gov"    # 如果需要
}



# 循环遍历每个链接，判断它是否是可下载文件或html
# 用来存储发生 403 错误的链接
forbidden_links = []

for link in links:
    try:
        # 发送 HEAD 请求获取文件头部信息，检查 Content-Type
        link_response = requests.head(link, headers=headers)

        # 检查是否为 403 错误
        if link_response.status_code == 403:
            forbidden_links.append(link)
            print(f"访问被拒绝 (403): {link}")
            continue  # 跳过此链接的处理

        content_type = link_response.headers.get('Content-Type', '')
        print(link)


        # 如果 Content-Type 表示这是 PDF 文件
        if is_pdf(content_type):
            print("下载 pdf 文件中...")
            download_pdf(link, headers, pdf_folder)
        # 如果 Content-Type 表示这是 HTML 文件
        elif is_html(content_type):
            print("正在下载当前页面")
            download_html(link, html_folder, headers)

            # 在这个页面上继续爬取

            # 1. 如果这个网页上有doi号的论文，仅下载这篇论文
            doi_link = get_doi_link(link, headers)
            if doi_link:
                doi_pdf_url = get_links_from_specific_div(doi_link, "btn-multi-block mb-1", header=headers)
                print(doi_pdf_url)
                if is_pdf(content_type):
                    download_pdf(link, headers, pdf_folder)
            # 2. 如果没有doi号论文
            else:
                sublinks = get_links_from_specific_div(link)
                for sublink in sublinks:
                    # 如果 Content-Type 表示这是 PDF 文件
                    if is_pdf(content_type):
                        print("下载 pdf 文件中...")
                        download_pdf(sublink, headers, pdf_folder)
                    elif is_html(content_type):
                        print("正在下载当前页面")
                        download_html(sublink, html_folder, headers)

                    else:
                        # 获取正确的扩展名
                        file_ext = get_other_file_extension_from_content_type(content_type)

                        if file_ext:
                            try:
                                # 下载其他类型文件
                                download_file(sublink, other_files_folder, headers)
                                print(f"下载 {file_ext} 文件: {link}")
                            except Exception as e:
                                # 捕获下载文件的异常
                                print(f"下载 {file_ext} 文件失败: {e}")
                        else:
                            # 如果无法识别文件类型，跳过该文件
                            print(f"跳过未知文件类型: {sublink} ({content_type})")

        # 对于其他类型的文件，根据 Content-Type 获取正确的扩展名
        else:
            # 获取正确的扩展名
            file_ext = get_other_file_extension_from_content_type(content_type)

            if file_ext:
                try:
                    # 下载其他类型文件
                    # download_file(link, other_files_folder, headers)
                    print(f"下载 {file_ext} 文件: {link}")
                except Exception as e:
                    # 捕获下载文件的异常
                    print(f"下载 {file_ext} 文件失败: {e}")
            else:
                # 如果无法识别文件类型，跳过该文件
                print(f"跳过未知文件类型: {link} ({content_type})")

    except requests.exceptions.RequestException as e:
        # 处理请求时的异常
        print(f"检查链接 {link} 时发生错误: {e}")

# 输出被拒绝的链接
if forbidden_links:
    print("\n以下链接因403错误被拒绝访问：")
    for link in forbidden_links:
        print(link)

save_url_to_file(base_save_folder, forbidden_links, mode='w')

