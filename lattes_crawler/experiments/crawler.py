# -*- coding: utf8 -*-

'''
Created on 31/12/2014

@author: Jonathas Magalhães
'''

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'lattes_crawler.settings'

from lattes_crawler.crawler                 import lattes
from lattes_crawler.apps.research.models    import Research

from xml.dom import minidom


def get_collab(research): 
    parsedxml           = minidom.parseString(research.lattes_information.encode('utf8'))
    curriculo_lattes    = parsedxml.getElementsByTagName("curriculo_lattes")[0]
    pesquisador         = curriculo_lattes.getElementsByTagName("pesquisador")[0]
    colaboradores       = pesquisador.getElementsByTagName("colaboradores")
    if colaboradores == []:
        return 
    else:
        idcolaboradorlist   = colaboradores[0].getElementsByTagName("id_lattes_colaborador")
    
    col_list = [x.firstChild.nodeValue for x in idcolaboradorlist ]
    return col_list
    
def save_attributes(lattes_id):
    try:
        research = Research.objects.get(lattes_id = lattes_id)
        if not research.is_saved():
            research.lattes_information = lattes.get_cv_lattes(lattes_id)
            research.save()
    except:
        research            = Research()
        research.lattes_id  = lattes_id
        research.save()
    return research

def save_lattes(research):
    research = save_attributes(research.lattes_id) 
    
    if research.lattes_information is not None:
        collaborators = get_collab(research)
        if collaborators is not None:
            for col in collaborators:
                research_col            = save_attributes(col)
                research.collaborators.add(research_col)
                research.save()
        
def walk_lattes(lattes_id_seed):
    save_attributes(lattes_id_seed)
    while True:
        researches = Research.objects.filter(lattes_information = None)
        
        if not researches:
            return
        for research in researches:
            save_lattes(research)

def test():
    researches = Research.objects.all()
    for research in researches:
        print research.lattes_information

def test2():
    research = Research.objects.get(id = 1)
    collaborators = get_collab(research)
    print collaborators
        
def main():
    seeds = ["8951598251334162", "5760364940162939", "6935433850568144", "7337100011232657", "3697034512999386", 
             "4671683163069536", "3198452549472216", "6322106621770962", "2127559774805521", "9348556938029052", 
             "5192472683408995", "9747151229532463", "8053391833089941", "0590320684933608", "5787113463718492",
             "7151033935149782"]
    for seed in seeds:
        walk_lattes(lattes_id_seed = seed)

if __name__ == '__main__':
    main()