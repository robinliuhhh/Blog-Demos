import parse
from datetime import datetime


def start(target):
    start_DT = datetime.now()
    copath = parse.parse_ncbi_kegg(target)
    copath_tab = parse.get_ncbi_kegg(copath)
    print('----------Co-pathway----------')
    print(copath_tab)

    coxpres = parse.parse_coxpres(target)
    coxpres_tab = parse.get_coxpres(coxpres)
    print('--------Co-expression---------')
    print(coxpres_tab)

    diseases = parse.parse_diseases(target)
    print('-----Associated diseases------')
    print(diseases)

    uniprot = parse.parse_uniprot(target)
    print('-------target_id--------')
    print(uniprot[0])
    print('-------Protein function-------')
    print(uniprot[1])
    print('-----Subcellular location-----')
    print(uniprot[2])
    print('-------Topology--------')
    print(uniprot[3])
    print('----------Structure-----------')
    print(uniprot[4])
    print('-------Domain Keywords--------')
    print(uniprot[5])

    NCBI = parse.parse_ncbi_Orthologs(target)
    print('-------Synonyms-------')
    print(NCBI[0])
    print('-------Location-------')
    print(NCBI[1])
    print('-------Summary-------')
    print(NCBI[2])
    print('-------Assembly-------')
    print(NCBI[3])
    print('-------Location_cor-------')
    print(NCBI[4])
    print('-------Orthologs_link-------')
    print(NCBI[5])
    print('-------Align_species-------')
    species_dict = parse.parse_Orthologs_fig(NCBI[5])
    print(species_dict)
    # parse.parse_Orthologs_fig(target)
    end_DT = datetime.now()

    print('爬虫时长：{} s'.format((end_DT - start_DT).microseconds / 10000))

    return NCBI, uniprot, copath, diseases, coxpres_tab, copath_tab, species_dict


if __name__ == '__main__':
    URL = 'https://www.ncbi.nlm.nih.gov/gene/7057/ortholog/'
    target = 'npr1'
    scrp_results = start(target)
    # Synonyms = scrp_results[0][0]
    # print(Synonyms)
