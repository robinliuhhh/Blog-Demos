"""
1.引入selenium
2.抽取公共方法 并把原始文件分成[爬虫逻辑]和[获取结果]两个文件
3.已完成部分还是使用lxml 涉及点击事件则使用selenium
"""

# 'https://coxpresdb.jp' [done]
# Co-expression
#
# 'https://www.ncbi.nlm.nih.gov/gene/?term='
# Co-pathway  KEGG pathways [done]  Synonyms  Genomic location  Target_id  Orthologs  Gene summary
#
# 'https://www.malacards.org/search/results/' [done]
# Associated diseases
#
# 'https://www.uniprot.org/uniprot/?query=' [done] except Subcellular location
# Protein function  Subcellular location  Structure  Domain Keywords
#
# parse返回爬下来的原始数据 get返回处理好的dataframe

import re
import time
import urllib
import random
import requests
import warnings
import numpy as np
import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data_process.static_data import Clinical_Stage_info, Positive_Result
from data_process.static_data import KEGG_pathways_raw

warnings.filterwarnings('ignore')


def start_requests(url):
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.16 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cookie": "__yjs_duid=1_bb4356a2f0f96e1660429464725a94221622518116225; BIDUPSID=4AAB5EB2C9739B7313829BB01F5E2EFD; PSTM=1623295653; BAIDUID=4AAB5EB2C9739B73B05E5DDA093E2D46:FG=1; H_PS_PSSID=33802_34222_31253_34226_34004_34113_34107_34134_26350_34093; BD_UPN=123253; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; BD_CK_SAM=1; rsv_jmp_slow=1625802293555; BAIDUID_BFESS=B7FB41707F9642CC47C6D60BEDF4C6CC:FG=1; ab_sr=1.0.1_YTljZjMwMDk5OWRhNDNjMzgwNWMwN2JmZTQ2NjhjZGNkNWFkNDY3NGUwMDI2YTExZjg3MjkzZjE0ZGJjNWNkN2FkZjZlYjNhOGQ3Mjc0N2IwNDk0ZTNlYWU2YmUyNjFiMWYzMDJkYmU2NTkzZDFkMmI3OWViNjFiNjA5ZTI5MWI3N2RlMDhlZWE3ZjllMGE1YzFlYWVkNzZjY2IxODQxYQ==; PSINO=5; H_PS_645EC=39e7kxid%2B3qQFj90u9mJYLlj4IKrxTzUAzDXsgPZ3s8pipOwK%2B%2FAUgQYqwF5iN4; BA_HECTOR=248l010n8k0k818gd61gefpck0q"
    }
    proxies = {"http": None, "https": None}
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response
    except Exception as e:
        print(e)
        raise


def get_lxml_selector(url):
    response = start_requests(url)
    selector = etree.HTML(response.content)
    return selector


def parse_ncbi_kegg(target):
    base_url = 'https://www.ncbi.nlm.nih.gov/gene/?term='
    query_url = base_url + target
    selector = get_lxml_selector(query_url)
    ncbi_href = selector.xpath('//a[@id="feat_gene_title"]/@href')
    if len(ncbi_href) == 0:
        print('No match for Homo sapiens')
        return pd.DataFrame()

    sleep = random.random() * 2 + 3
    # print('sleep {} s then go to Homo sapiens link'.format(round(sleep, 2)))
    time.sleep(sleep)

    kegg_selector = get_lxml_selector(ncbi_href[0])
    kegg_href = kegg_selector.xpath('//div[@class="portlet dis-links-to-other-res brieflink"]/div[2]/ul/li/a/@href')
    kegg_text = kegg_selector.xpath('//div[@class="portlet dis-links-to-other-res brieflink"]/div[2]/ul/li/a/text()')
    kegg = {}
    for i in range(len(kegg_text)):
        kegg[kegg_text[i]] = kegg_href[i]
    # kegg = dict(zip(kegg_text, kegg_href))

    sleep = random.random() * 3 + 3
    # print('sleep {} s then go to KEGG link'.format(round(sleep, 2)))
    time.sleep(sleep)

    parse_selector = get_lxml_selector(kegg['KEGG'])
    hsa_path = '//span[text()="Pathway"]/parent::*/following-sibling::td//a/text()'
    hsa = parse_selector.xpath(hsa_path)
    human_path = '//span[text()="Pathway"]/parent::*/following-sibling::td//td[2]/text()'
    human = parse_selector.xpath(human_path)
    dict = {"hsa": hsa, "Homo sapiens": human}
    copath = pd.DataFrame(dict)
    return copath


def parse_coxpres(target):
    coxpresdb_url = 'https://coxpresdb.jp'
    base_url = 'https://coxpresdb.jp/kwsearch/?stype=any&kword='
    query_url = base_url + urllib.parse.quote(target)
    selector = get_lxml_selector(query_url)
    human_gene = selector.xpath('//*[@id="coK"]/h2[1]/a/text()')
    if human_gene[0] != ' Human gene search ':
        print('No match for Human gene')
        return pd.DataFrame()
    coxpres_href = selector.xpath('//div[@class="table_padding"][1]//td/a/@href')
    coxpres_url = coxpresdb_url + coxpres_href[0]

    sleep = random.random() * 2 + 3
    # print('sleep {} s then go to Human gene Coexpressed gene list link'.format(round(sleep, 2)))
    time.sleep(sleep)

    parse_selector = get_lxml_selector(coxpres_url)
    dict = {}
    for i in range(1, 51):
        path = '//*[@id="coex_list"]/tr[' + str(i) + ']/td[2]/a/text()'
        gene = parse_selector.xpath(path)
        if len(gene) == 0:
            break
        else:
            gene = [str(g) for g in gene]  # <class 'lxml.etree._ElementUnicodeResult'> -> <class 'str'>
            dict[i] = str(gene[0])
    coxpres = pd.DataFrame([dict]).T.reset_index()
    coxpres.columns = ['ID', 'Gene']
    return coxpres


def diseases_sum(dict):
    sum = 0
    pattern = re.compile(r'cancer|tumor|adenocarcinoma|Carcinoma|neoplasm|adenoma|leukemia|lymphoma|myeloma', re.I)
    for disease in dict:
        if sum > 2:
            return True
        res = re.search(pattern, disease)
        if res:
            sum += 1
    return False


def parse_diseases(target):
    driver = webdriver.Chrome()
    base_url = 'https://www.malacards.org/search/results/'
    query_url = base_url + urllib.parse.quote(target)
    driver.get(query_url)
    name_score = {}
    i = 0
    try:
        while True:
            i += 2
            score = driver.find_element(by=By.XPATH,
                                        value='//table[@class="search-results"]//tr[{}]/td[7]'.format(i)).text
            name = driver.find_element(by=By.XPATH,
                                       value='//table[@class="search-results"]//tr[{}]/td[5]/a'.format(i)).text
            name_score[name] = score
            # todo 重复判断
            if float(score) < 10:
                if diseases_sum(name_score):
                    name_score.pop(name)
                    break
                else:
                    continue
        driver.quit()
        result_df = pd.DataFrame.from_dict(name_score, orient='index').reset_index()
        result_df.columns = ['Name', 'Score']
        return result_df
    except Exception as e:
        driver.quit()
        print(e)
        raise


def parse_uniprot(target):
    driver = webdriver.Chrome()
    base_url = 'https://www.uniprot.org/uniprot/?query='
    query_url = base_url + urllib.parse.quote(target) + '&sort=score'
    driver.get(query_url)
    # Protein function
    tr_list = driver.find_elements(by=By.XPATH, value='//table[@id="results"]/tbody/tr')
    index = 0
    for tr in tr_list:
        index += 1
        find = tr.text.find('Homo sapiens (Human)')
        if find == -1:
            if index == len(tr_list):
                raise ValueError(
                    'No match for Human gene: https://www.uniprot.org/uniprot/?query={}&sort=score'.format(target))
            else:
                continue
        else:
            driver.find_element(by=By.XPATH, value='//table[@id="results"]/tbody/tr[{}]/td[2]/a'.format(index)).click()
            time.sleep(2)
            break
    p_list = driver.find_elements(by=By.XPATH, value='//*[@id="function"]//p')
    function_str = ''
    for p in p_list:
        if p.text != '':
            function_str += (p.text + '\n')
    function_str = re.sub(r'\\n$', '', function_str)

    # Subcellular location
    # 该部分位于shadow-root下 用JS path定位
    # js_path = 'return document.querySelector("#sib-swissbiopics-sl-uniprot").shadowRoot'
    # shadow = driver.execute_script(js_path)
    #
    # h6_list = shadow.find_elements(By.CSS_SELECTOR, 'li > h6')
    # for i in range(len(h6_list)):
    #     h6 = shadow.find_elements(By.CSS_SELECTOR, 'li > h6')[i]
    #     print(h6.text)
    # aa = shadow.find_elements(By.CSS_SELECTOR, 'li > h6')[i].find_elements(By.CSS_SELECTOR,
    #                                                                        '+ ul > li > a[class="subcell_name"]')
    # print(len(aa))
    # shadow.find_elements(By.CSS_SELECTOR, 'li > h6')[i].find_elements(By.XPATH, '//following-sibling::ul')
    # a_list = shadow.find_elements(By.CSS_SELECTOR,
    #                               'li > h6 + ul > li > a[class="subcell_name"]')
    # [@class="subcell_name"]
    # //*[@id="SL0243term"]
    # a_list = shadow.find_elements(By.XPATH,
    #                               '//*[@id="swissBioPicsSlData"]/div/ul/li[2]/ul/li/a')
    #     print(len(a_list))
    #     # .find_elements(By.TAG_NAME, 'a')
    #     for a in a_list:
    #         if a.text != '':
    #             print(a.text)
    location_dict = {}

    # Structure
    try:
        btn_xpath = '//button[@title="Screenshot / State Snapshot"]'
        btn_locator = (By.XPATH, btn_xpath)
        WebDriverWait(driver, 30, 1).until(EC.visibility_of_element_located(btn_locator))
        time.sleep(5)
        driver.find_element(by=By.XPATH, value=btn_xpath).click()
        time.sleep(2)
        driver.find_element(by=By.XPATH, value='//button[text()="Copy"]/following-sibling::button').click()
        source_identifier = {}
        strong_list = driver.find_elements(by=By.XPATH, value='//*[@id="structure"]//strong')
        td_list = driver.find_elements(by=By.XPATH,
                                       value='//*[@id="structure"]//strong/parent::*/following-sibling::td[1]')
        source_list = []
        for strong in strong_list:
            source_list.append(strong.text)
        identifier_list = []
        for td in td_list:
            identifier_list.append(td.text)
        for i in range(len(source_list)):
            source_identifier[identifier_list[i]] = source_list[i]
        structure_df = pd.DataFrame.from_dict(source_identifier, orient='index').reset_index()
        structure_df.columns = ['Value', 'Key']
    except Exception as e:
        driver.quit()
        print(e)
        raise

    # Domain Keywords
    keywords_list = []
    a_list = driver.find_elements(by=By.XPATH,
                                  value='//span[text()="Keywords - Domain"]/parent::*/following-sibling::span/a')
    for a in a_list:
        keywords_list.append(a.text)

    driver.quit()
    return function_str, location_dict, structure_df, keywords_list


def get_ncbi_kegg(copath):
    if copath.empty:
        return 'No data'
    copath_raw = pd.merge(copath, KEGG_pathways_raw, left_on='hsa', right_on='ID', how='inner')
    copath_tab = copath_raw[['ID', 'Description']]
    return copath_tab


def get_coxpres(coxpres):
    if coxpres.empty:
        return 'No data'
    coxpres_raw = pd.merge(coxpres, Clinical_Stage_info, on='Gene', how='left')
    coxpres_tab = coxpres_raw[
        ['ID', 'Gene', 'Cancer_target_highest-level-stage', 'Non-cancer_target_highest-level-stage']]
    coxpres_tab.columns = ['ID', 'Gene', 'CancerDT', 'Non-CancerDT']
    coxpres_tab['CancerDT_count'] = np.where((coxpres_tab['CancerDT'].isin(Positive_Result)), 1, 0)
    coxpres_tab['Non-CancerDT_count'] = np.where(coxpres_tab['Non-CancerDT'].isin(Positive_Result), 1, 0)
    coxpres_tab['Gene_count'] = np.where(
        (coxpres_tab['Non-CancerDT'].isin(Positive_Result)) | (coxpres_tab['CancerDT'].isin(Positive_Result)), 1, 0)
    return coxpres_tab
