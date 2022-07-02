import parse


def start(target):
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
    print('-------Protein function-------')
    print(uniprot[0])
    print('-----Subcellular location-----')
    print(uniprot[1])
    print('----------Structure-----------')
    print(uniprot[2])
    print('-------Domain Keywords--------')
    print(uniprot[3])


if __name__ == '__main__':
    target = 'thbs1'
    start(target)
