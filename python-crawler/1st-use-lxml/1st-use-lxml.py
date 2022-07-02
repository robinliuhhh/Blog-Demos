"""
最初的版本 能跑就行
"""

import time
import urllib
import random
import datetime
import requests
import warnings
import numpy as np
import pandas as pd
from lxml import etree
from data_process.static_data import Clinical_Stage_info
from data_process.static_data import KEGG_pathways_raw

warnings.filterwarnings('ignore')

coxpresdb_url = 'https://coxpresdb.jp'


def start(target):
    coxpres_base_url = 'https://coxpresdb.jp/kwsearch/?stype=any&kword='
    coxpres_query_url = coxpres_base_url + urllib.parse.quote(target)
    start = datetime.datetime.now()
    print('Co-expression requests start:', start)
    coxpres_selector = start_requests(coxpres_query_url)
    coxpres = parse_coxpres(coxpres_selector)
    coxpres_tab = get_coxpres_tab(coxpres)
    print('Co-expression requests cost: ', datetime.datetime.now() - start)

    sleep = random.random() * 6 + 3
    print('sleep {} s next requests -> Co-pathway'.format(round(sleep, 2)))
    time.sleep(sleep)

    ncbi_base_url = 'https://www.ncbi.nlm.nih.gov/gene/?term='
    ncbi_query_url = ncbi_base_url + target
    start = datetime.datetime.now()
    print('Co-pathway requests start:', start)
    ncbi_selector = start_requests(ncbi_query_url)
    copath = parse_copathway(ncbi_selector)
    copath_tab = get_copath_tab(copath)
    print('Co-pathway requests cost: ', datetime.datetime.now() - start)

    return coxpres_tab, copath_tab


def start_requests(url):
    kv = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.16 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cookie": "__yjs_duid=1_bb4356a2f0f96e1660429464725a94221622518116225; BIDUPSID=4AAB5EB2C9739B7313829BB01F5E2EFD; PSTM=1623295653; BAIDUID=4AAB5EB2C9739B73B05E5DDA093E2D46:FG=1; H_PS_PSSID=33802_34222_31253_34226_34004_34113_34107_34134_26350_34093; BD_UPN=123253; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; BD_CK_SAM=1; rsv_jmp_slow=1625802293555; BAIDUID_BFESS=B7FB41707F9642CC47C6D60BEDF4C6CC:FG=1; ab_sr=1.0.1_YTljZjMwMDk5OWRhNDNjMzgwNWMwN2JmZTQ2NjhjZGNkNWFkNDY3NGUwMDI2YTExZjg3MjkzZjE0ZGJjNWNkN2FkZjZlYjNhOGQ3Mjc0N2IwNDk0ZTNlYWU2YmUyNjFiMWYzMDJkYmU2NTkzZDFkMmI3OWViNjFiNjA5ZTI5MWI3N2RlMDhlZWE3ZjllMGE1YzFlYWVkNzZjY2IxODQxYQ==; PSINO=5; H_PS_645EC=39e7kxid%2B3qQFj90u9mJYLlj4IKrxTzUAzDXsgPZ3s8pipOwK%2B%2FAUgQYqwF5iN4; BA_HECTOR=248l010n8k0k818gd61gefpck0q"
    }
    proxies = {"http": None, "https": None}
    try:
        response = requests.get(url, headers=kv, proxies=proxies)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        html = response.content
        selector = etree.HTML(html)
        return selector
    except Exception as e:
        print(e)


def parse_coxpres(selector):
    human_gene = selector.xpath('//*[@id="coK"]/h2[1]/a/text()')
    if human_gene[0] != ' Human gene search ':
        print('No match for Human gene')
        return pd.DataFrame()
    coxpres_href = selector.xpath('//div[@class="table_padding"][1]//td/a/@href')
    coxpres_url = coxpresdb_url + coxpres_href[0]

    sleep = random.random() * 2 + 3
    # print('sleep {} s then go to Human gene Coexpressed gene list link'.format(round(sleep, 2)))
    time.sleep(sleep)

    parse_selector = start_requests(coxpres_url)
    print('parsing 50 Coexpressed Genes')
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


def parse_copathway(selector):
    ncbi_href = selector.xpath('//a[@id="feat_gene_title"]/@href')
    if len(ncbi_href) == 0:
        print('No match for Homo sapiens')
        return pd.DataFrame()

    sleep = random.random() * 2 + 3
    # print('sleep {} s then go to Homo sapiens link'.format(round(sleep, 2)))
    time.sleep(sleep)

    kegg_selector = start_requests(ncbi_href[0])
    kegg_href = kegg_selector.xpath('//div[@class="portlet dis-links-to-other-res brieflink"]/div[2]/ul/li/a/@href')
    kegg_text = kegg_selector.xpath('//div[@class="portlet dis-links-to-other-res brieflink"]/div[2]/ul/li/a/text()')
    kegg = {}
    for i in range(len(kegg_text)):
        kegg[kegg_text[i]] = kegg_href[i]
    # kegg = dict(zip(kegg_text, kegg_href))

    sleep = random.random() * 3 + 3
    # print('sleep {} s then go to KEGG link'.format(round(sleep, 2)))
    time.sleep(sleep)

    parse_selector = start_requests(kegg['KEGG'])
    print('parsing pathway list')
    hsa_path = '//td[@class="fr1"]//tr[6]//a/text()'
    hsa = parse_selector.xpath(hsa_path)
    human_path = '//td[@class="fr1"]//tr[6]//td[2]/text()'
    human = parse_selector.xpath(human_path)
    dict = {"hsa": hsa, "Homo sapiens": human}
    copath = pd.DataFrame(dict)
    return copath


def get_coxpres_tab(coxpres):
    if coxpres.empty:
        return 'No data'
    print('generating coxpres_tab')
    coxpres_raw = pd.merge(coxpres, Clinical_Stage_info, on='Gene', how='left')
    coxpres_tab = coxpres_raw[
        ['ID', 'Gene', 'Cancer_target_highest-level-stage', 'Non-cancer_target_highest-level-stage']]
    coxpres_tab.columns = ['ID', 'Gene', 'CancerDT', 'Non-CancerDT']
    coxpres_tab['CancerDT_count'] = np.where((coxpres_tab['CancerDT'] == 'Launched'), 1, 0)
    coxpres_tab['Non-CancerDT_count'] = np.where(coxpres_tab['Non-CancerDT'] == 'Launched', 1, 0)
    return coxpres_tab


def get_copath_tab(copath):
    if copath.empty:
        return 'No data'
    print('generating copath_tab')
    copath_raw = pd.merge(copath, KEGG_pathways_raw, left_on='hsa', right_on='ID', how='inner')
    copath_tab = copath_raw[['ID', 'Description']]
    return copath_tab


if __name__ == '__main__':
    target = 'CD276'
    start(target)
