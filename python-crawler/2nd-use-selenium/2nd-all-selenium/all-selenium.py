"""
全部替换为selenium
"""

import re
import time
import urllib
import random
import warnings
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data_process.static_data import Clinical_Stage_info, Positive_Result, Orthologs_species, Cancers
from data_process.static_data import KEGG_pathways_raw

Cancer_pattern = '|'.join(Cancers)

warnings.filterwarnings('ignore')


def parse_ncbi_kegg(target):
    driver = webdriver.Chrome()

    NCBI_search_url = "https://www.ncbi.nlm.nih.gov/search/all/?term={}".format(target)
    driver.get(NCBI_search_url)

    NCBI_link = driver.find_element(by=By.XPATH, value='//*[@id="feat_gene_title"]').get_attribute('href')
    driver.get(NCBI_link)

    sleep = random.random() * 2 + 3
    time.sleep(sleep)

    KEGG_url = driver.find_element(by=By.XPATH, value='//a[text() = "KEGG"]').get_attribute('href')
    driver.get(KEGG_url)
    try:
        kegg_text = driver.find_element(by=By.XPATH,
                                        value='//span[text() = "Pathway"]/parent::th/following-sibling::td').text

        kegg = {}
        KEGG_LIST = kegg_text.split("\n")
        for i in range(len(KEGG_LIST)):
            KEGG_path = KEGG_LIST[i].split('   ')
            kegg[KEGG_path[0]] = KEGG_path[1]

        copath = pd.DataFrame.from_dict(kegg, orient='index').reset_index()
        copath.columns = ['hsa', 'Homo sapiens']
        # print(copath)
    except:
        copath = pd.DataFrame()

    return copath


def parse_coxpres(target):
    driver = webdriver.Chrome()
    base_url = 'https://coxpresdb.jp/kwsearch/?stype=any&kword='
    query_url = base_url + urllib.parse.quote(target)
    driver.get(query_url)
    results = driver.find_element(By.XPATH, '// *[ @ id = "coK"]')

    h2_list = results.find_elements(By.CSS_SELECTOR, 'h2')
    div_list = results.find_elements(By.CSS_SELECTOR, 'div')
    dict = {}
    for i in range(len(h2_list)):
        if h2_list[i].text == 'Human gene search':
            tr_list = div_list[i].find_elements(By.TAG_NAME, 'tr')
            for j in range(len(tr_list)):

                if j > 0:
                    gene = tr_list[j].find_elements(By.TAG_NAME, 'td')[1].text
                    if target.lower() == gene.lower():
                        copres_url = tr_list[j].find_element(By.TAG_NAME, 'a').get_attribute('href')
                        driver.get(copres_url)
                        dict = {}

                        for i in range(1, 51):
                            path = '//*[@id="coex_list"]/tr[' + str(i) + ']/td[2]/a'
                            gene_cell = driver.find_element(By.XPATH, path).text

                            if len(gene_cell) == 0:
                                break
                            else:
                                dict[i] = gene_cell

                if len(dict) > 0:
                    break
            break

    coxpres = pd.DataFrame([dict]).T.reset_index()
    coxpres.columns = ['ID', 'Gene']
    # print(coxpres)
    return coxpres


def parse_ncbi_Orthologs(target_gene):
    driver = webdriver.Chrome()

    NCBI_search_url = "https://www.ncbi.nlm.nih.gov/search/all/?term={}".format(target_gene)
    driver.get(NCBI_search_url)

    NCBI_link = driver.find_element(by=By.XPATH, value='//*[@id="feat_gene_title"]').get_attribute('href')
    driver.get(NCBI_link)

    genecontext_xpath = '// *[ @ id = "genomic-context"]'
    genecontext_locator = (By.XPATH, genecontext_xpath)
    WebDriverWait(driver, 30, 1).until(EC.visibility_of_element_located(genecontext_locator))
    try:
        Synonyms = driver.find_element(by=By.XPATH, value='//dt[text()="Also known as"]/following-sibling::dd').text

    except:
        Synonyms = ''

    print('Pass Synonyms')

    try:
        summary_raw = driver.find_element(by=By.XPATH, value='//dt[text()="Summary"]/following-sibling::dd').text
        Summary = re.sub('\[(\w*\s*)*,\s\w*\s*\d*\]$', '', summary_raw)
    except:
        Summary = ''
    print('Pass Summary')

    Orthologs_link = driver.find_element(by=By.XPATH,
                                         value='//dt[text()="Orthologs"]/following-sibling::dd/a[text()="all"]').get_attribute(
        'href')
    try:
        Location = driver.find_element(by=By.XPATH, value='//dt[text()="Location: "]/following-sibling::dd/span').text
    except:
        Location = ''
    print('Pass Location')

    try:
        geno_table = driver.find_element(by=By.XPATH, value='//*[@id="ui-ncbigrid-11"]').find_elements(by=By.TAG_NAME,
                                                                                                       value='tr')

        for i in range(1, len(geno_table)):
            geno_table_row = re.sub('\s', ',', geno_table[i].text)

            geno_table_row_list = geno_table_row.split(',')
            for j in range(len(geno_table_row_list)):
                if geno_table_row_list[j] == 'current':
                    Assembly = geno_table_row_list[j + 1]
                    print('Pass Assembly')
                    Location_cor_raw = re.search('\(\d+..\d+(.\w*)*\)', re.sub('\s', '', geno_table[i].text)).group()
                    Location_cor = re.sub(',', ', ', Location_cor_raw)
                    print('Pass Location_cor')
    except:
        Assembly = ''
        print('Pass Assembly')
        Location_cor = ''
        print('Pass Location_cor')

        # print('Synonyms:', Synonyms)
        # print('Summary:', Summary)
        # print('Location:', Location)
        # print('Assembly:', Assembly)
        # print('Location_cor:', Location_cor)
        # print('Orthologs_link:', Orthologs_link)

    return (Synonyms, Location, Summary, Assembly, Location_cor, Orthologs_link)


def parse_Orthologs_fig(Orthologs_link, o_species=Orthologs_species):
    driver_path = (r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')  # 驱动位置
    out_path = r'D:\git\GCDashboard_dev\gcdashboard\auto_report\downloads'  # 是你想指定的路径
    prefs = {'profile.default_content_settings.popups': 0,
             'download.default_directory': out_path}  # 设置下载文件存放路径，这里要写绝对路径
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(executable_path=driver_path, options=options)

    driver.get(Orthologs_link)
    genes_table = driver.find_element(by=By.XPATH, value='//*[@id="DataTables_Table_0"]').find_elements(by=By.TAG_NAME,
                                                                                                        value='tr')
    row_num = 0
    Orthologs_species = o_species
    Orthologs_species_itr = Orthologs_species.copy()

    species_dict = {}
    Organism_list = []
    species_list = []
    # tmp_list = []
    # tmp_species = []
    # tmp_dict = {}
    monkey = 0
    mouse = 0

    for row in genes_table[1:]:
        row_num += 1
        SPECIES = row.find_elements(by=By.TAG_NAME, value='td')[1].find_elements(by=By.TAG_NAME, value='span')
        if len(SPECIES) != 0:

            species = row.find_elements(by=By.TAG_NAME, value='td')[1].find_elements(by=By.TAG_NAME, value='span')[
                0].text
            Orthologs_species_str = '|'.join(Orthologs_species_itr)
            re_result = re.search(Orthologs_species_str, species)  # 匹配不上时返回None
            # print(re_result)

            if re_result != None:

                re_result_str = re.search(Orthologs_species_str, species).group()
                Organism = \
                    row.find_elements(by=By.TAG_NAME, value='td')[1].find_elements(by=By.TAG_NAME, value='label')[
                        0].text

                # print(re_result_str, Organism)

                if Organism in ('Macaca mulatta', 'Macaca fascicularis'):
                    row.find_elements(by=By.TAG_NAME, value='td')[0].click()
                    # print(species,Organism)
                    species_list.append(species)
                    Organism_list.append(Organism)
                    # print(species_list, Organism_list)

                    monkey = + 1

                    Orthologs_species_itr.remove(re_result_str) if monkey == 1 else Orthologs_species_itr
                    print('Monkey{0}: {1}'.format(monkey, Organism), Orthologs_species_itr)
                elif Organism == 'Mus musculus':
                    row.find_elements(by=By.TAG_NAME, value='td')[0].click()
                    # print(species,Organism)
                    species_list.append(species)
                    Organism_list.append(Organism)
                    # print(species_list, Organism_list)
                    mouse = + 1
                    Orthologs_species_itr.remove(re_result_str)
                    print('Mouse{0}: {1}'.format(mouse, Organism), Orthologs_species_itr)
                else:

                    if (re_result_str == 'mouse'):
                        tmp_mouse = row.find_elements(by=By.TAG_NAME, value='td')[0]
                        tmp_mouse_species = species
                        tmp_mouse_Organism = Organism

                    elif (re_result_str == 'monkey'):
                        tmp_monkey = row.find_elements(by=By.TAG_NAME, value='td')[0]
                        tmp_monkey_species = species
                        tmp_monkey_Organism = Organism

                    else:
                        row.find_elements(by=By.TAG_NAME, value='td')[0].click()
                        species_list.append(species)
                        Organism_list.append(Organism)
                    Orthologs_species_itr.remove(re_result_str)

                print(species, Orthologs_species_itr)

                if (len(Orthologs_species_itr) == 0):
                    break

    if (monkey == 0) & ('monkey' not in Orthologs_species_itr):
        tmp_monkey.click()
        species_list.append(tmp_monkey_species)
        Organism_list.append(tmp_monkey_Organism)

    if (mouse == 0) & ('mouse' not in Orthologs_species_itr):
        tmp_mouse.click()
        species_list.append(tmp_mouse_species)
        Organism_list.append(tmp_mouse_Organism)

    # 生成拉丁名和俗名对照
    for i in range(len(species_list)):
        species_dict[Organism_list[i]] = species_list[i]
    # print('123+',i)
    species_df = pd.DataFrame.from_dict(species_dict, orient='index').reset_index()
    species_df.columns = ['Organism', 'Species']

    protine_alignment = driver.find_element(by=By.XPATH, value='//*[@id="add-to-cart"]/following-sibling::button')
    driver.execute_script("arguments[0].click()", protine_alignment)

    align_link = driver.find_element(by=By.XPATH,
                                     value='//*[@id="add-to-cart"]/following-sibling::div[1]/descendant::a').get_attribute(
        'href')
    time.sleep(2)

    driver.get(align_link)

    print('已勾选完并跳转至Align界面')

    driver.find_element(by=By.XPATH, value='//img[@alt="Align"]').click()
    btn_xpath = '//div[@id="graphView"]//span[text()="Download"]/ancestor::a'
    btn_locator = (By.XPATH, btn_xpath)
    WebDriverWait(driver, 30, 1).until(EC.visibility_of_element_located(btn_locator))
    driver.find_element(by=By.XPATH, value=btn_xpath).click()
    time.sleep(3)
    driver.find_element(by=By.XPATH, value='//span[text()="Printer-Friendly PDF/SVG"]/ancestor::a').click()
    time.sleep(3)
    driver.find_element(by=By.XPATH, value='//span[text()="Cancel"]/ancestor::a/preceding-sibling::a[1]').click()
    time.sleep(7)
    print('Align 图片已下载')

    return (species_df)


# def diseases_sum(dict):
#     sum = 0
#     pattern = re.compile(Cancer_pattern, re.I)
#     for disease in dict:
#         if sum > 2:
#             return True
#         res = re.search(pattern, disease)
#         if res:
#             sum += 1
#     return False


def parse_diseases(target):
    driver = webdriver.Chrome()
    base_url = 'https://www.malacards.org/search/results/'
    query_url = base_url + urllib.parse.quote(target)
    driver.get(query_url)
    name_score = {}
    pattern = re.compile(Cancer_pattern, re.I)
    i = 0
    sum = 0
    tr_list = driver.find_elements(by=By.XPATH, value='//table[@class="search-results"]//tr')

    try:
        for i in range(2, len(tr_list), 2):

            score = driver.find_element(by=By.XPATH,
                                        value='//table[@class="search-results"]//tr[{}]/td[7]'.format(i)).text
            name = driver.find_element(by=By.XPATH,
                                       value='//table[@class="search-results"]//tr[{}]/td[5]/a'.format(i)).text
            res = re.search(pattern, name)

            if res != None:
                sum += 1

            if (float(score) > 10) | (res != None):
                name_score[name] = score

            if (float(score) < 10) & (sum > 2):
                break
            # # todo 重复判断
            # if float(score) < 10:
            #     if diseases_sum(name_score):
            #         name_score.pop(name)
            #         break
            #     else:
            #         continue
        driver.quit()
        result_df = pd.DataFrame.from_dict(name_score, orient='index').reset_index()
        result_df.columns = ['Name', 'Score']
        return result_df
    except Exception as e:
        driver.quit()
        print(e)
        raise


def parse_uniprot(target):
    time.sleep(5)
    driver_path = (r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')  # 驱动位置
    out_path = r'D:\git\GCDashboard_dev\gcdashboard\auto_report\downloads'  # 是你想指定的路径
    prefs = {'profile.default_content_settings.popups': 0,
             'download.default_directory': out_path}  # 设置下载文件存放路径，这里要写绝对路径
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(executable_path=driver_path, options=options)

    print('link to uniport')
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
            target_id = driver.find_element(by=By.XPATH,
                                            value='//table[@id="results"]/tbody/tr[{}]/td[2]/a'.format(index)).text

            uniport_url = driver.find_element(by=By.XPATH,
                                              value='//table[@id="results"]/tbody/tr[{}]/td[2]/a'.format(index))
            driver.execute_script("arguments[0].click()", uniport_url)
            time.sleep(2)
            break
    try:
        p_list = driver.find_elements(by=By.XPATH, value='//*[@id="function"]//p')
        function_str = ''
        for p in p_list:
            if p.text != '':
                function_str += (p.text + '\n')
        function_str = re.sub(r'\\n$', '', function_str)
    except:
        function_str
    print('Pass Protein function')

    # Subcellular location
    # 该部分位于shadow-root下 用JS path定位
    try:
        js_path = 'return document.querySelector("#sib-swissbiopics-sl-uniprot").shadowRoot'
        shadow = driver.execute_script(js_path)

        h6_list = shadow.find_elements(By.CSS_SELECTOR, 'li > h6')
        ul_list = shadow.find_elements(By.CSS_SELECTOR, 'li > h6 + ul')

        location_dict = {}
        h6_title_list = []
        subcell_name_list = []
        # ul_list.append('a')
        if len(h6_list) == len(ul_list):
            for h6, ul in zip(h6_list, ul_list):
                h6_content = h6.text
                h6_title_list.append(h6_content)

                a_list = ul.find_elements(By.CSS_SELECTOR, 'li > a[class="subcell_name"]')
                a_list_content = []
                for a in a_list:
                    a_content = a.text
                    a_list_content.append(a_content)
                subcell_name_list.append(a_list_content)
        else:
            raise RuntimeError('Subcellular location  部分h6与ul长度不一致')

        for i in range(len(h6_title_list)):
            location_dict[h6_title_list[i]] = subcell_name_list[i]
    except:
        location_dict = {}
    print('Pass Subcellular location')

    h4_list = driver.find_elements(by=By.TAG_NAME, value='h4')
    for h4 in h4_list:
        if h4.text == 'Topology':
            Topology_tab_tr_list = driver.find_elements(By.XPATH,
                                                        '//h4[text() = "Topology"]//following-sibling::table/tbody/tr')
            # h4_list = driver.find_elements(by=By.TAG_NAME, value='h4')
            col_name = []
            row_content = []
            for i in range(len(Topology_tab_tr_list)):
                if i == 0:
                    # driver.find_elements(By.XPATH, '//h4[text() = "Topology"]//following-sibling::table/tbody/tr[1]')
                    col_name_list = Topology_tab_tr_list[i].find_elements(By.TAG_NAME, 'th')
                    for j in range(3):
                        col_name_text = col_name_list[j].text
                        col_name.append(re.sub('\n\w', '', col_name_text))
                else:
                    tab_content_list = Topology_tab_tr_list[i].find_elements(By.TAG_NAME, 'td')
                    cell_content = []
                    for j in range(3):
                        if j == 1:
                            cell = tab_content_list[j].find_element(By.TAG_NAME, 'a').text
                        else:
                            cell = tab_content_list[j].find_element(By.TAG_NAME, 'span').text
                        # print(cell)
                        cell_content.append(re.sub('\n\w|i$', '', cell))
                    row_content.append(cell_content)

            Topology_tab = pd.DataFrame(row_content, columns=col_name)

            break
        else:
            Topology_tab = 'No Topology'
    print('Pass Topology')

    # Structure
    try:
        btn_xpath = '//button[@title="Screenshot / State Snapshot"]'
        btn_locator = (By.XPATH, btn_xpath)
        WebDriverWait(driver, 120, 1).until(EC.visibility_of_element_located(btn_locator))
        time.sleep(5)
        driver.find_element(by=By.XPATH, value=btn_xpath).click()
        time.sleep(8)
        driver.find_element(by=By.XPATH, value='//button[text()="Copy"]/following-sibling::button').click()
        time.sleep(5)
        print('structure图片已下载')
        source_tab = driver.find_elements(by=By.TAG_NAME, value='protvista-datatable')[0]

        source_identifier = {}
        strong_list = source_tab.find_elements(by=By.TAG_NAME, value='strong')

        source_list = []
        identifier_list = []
        for strong in strong_list:
            source_list.append(strong.text)
            td = strong.find_elements(by=By.XPATH, value='parent::*/following-sibling::td[1]')[0]
            identifier_list.append(td.text)

        for i in range(len(source_list)):
            source_identifier[identifier_list[i]] = source_list[i]
        structure_df = pd.DataFrame.from_dict(source_identifier, orient='index').reset_index()
        structure_df.columns = ['Value', 'Key']



    except Exception as e:
        driver.quit()
        print(e)
        raise
    print('get structure')
    # Domain Keywords
    keywords_list = []
    try:
        a_list = driver.find_elements(by=By.XPATH,
                                      value='//span[text()="Keywords - Domain"]/parent::*/following-sibling::span/a')
        for a in a_list:
            keywords_list.append(a.text)
    except:
        pass

    print('Pass Domain Keywords')

    driver.quit()
    return target_id, function_str, location_dict, Topology_tab, structure_df, keywords_list,


def get_ncbi_kegg(copath):
    if copath.empty:
        copath_tab = 'No data'
    else:
        copath_raw = pd.merge(copath, KEGG_pathways_raw, left_on='hsa', right_on='ID', how='inner')
        copath_tab = copath_raw[['ID', 'Description']]
    return copath_tab


def get_coxpres(coxpres):
    if coxpres.empty:
        coxpres_tab = 'No data'
    else:
        coxpres_raw = pd.merge(coxpres, Clinical_Stage_info, on='Gene', how='left')
        coxpres_tab = coxpres_raw[
            ['ID', 'Gene', 'Cancer_target_highest-level-stage', 'Non-cancer_target_highest-level-stage']]
        coxpres_tab.columns = ['ID', 'Gene', 'CancerDT', 'Non-CancerDT']
        coxpres_tab['CancerDT_count'] = np.where((coxpres_tab['CancerDT'].isin(Positive_Result)), 1, 0)
        coxpres_tab['Non-CancerDT_count'] = np.where(coxpres_tab['Non-CancerDT'].isin(Positive_Result), 1, 0)
        coxpres_tab['Gene_count'] = np.where(
            (coxpres_tab['Non-CancerDT'].isin(Positive_Result)) | (coxpres_tab['CancerDT'].isin(Positive_Result)), 1, 0)
    return coxpres_tab
