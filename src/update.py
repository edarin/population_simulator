# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 11:54:17 2016

@author: edarin
"""

import pandas as pd


def check_tirage(population_simulee, reference, groupby):
    ''' 
        - population_simulee est la population que l'on veut tester
        - colname est la variable simulée que l'on étudie
        - reference est un dataframe contenant les variable effectif et effectif_ref
            ainsi que les colonne servant au groupby.
        retourn ratio avec effectif_genere, effectif_reference et le ratio des deux
    '''
    population = population_simulee
    reference_activite = reference
    
    
    ratio_des_effectifs = pd.DataFrame(population_simulee.groupby(groupby).size()).reset_index()
    ratio_des_effectifs.rename(columns={0: 'effectif_genere'}, inplace=True)
    
    ratio = ratio_des_effectifs.merge(reference_activite, on=groupby, how='outer',
                                      indicator='_merge')
    assert sum(ratio['_merge'] == 'left') == 0
    ratio['effectif_genere'].fillna(0, inplace=True)
    
    sample_size = len(population)
    population_size = reference['effectif_ref'].sum()
    ratio['effectif_theorique'] = round((ratio['effectif_ref'] * (sample_size / population_size))).astype(int)
        
    
    ratio['ratio'] = ratio['effectif_genere']/ratio['effectif_theorique']

    print(ratio.describe())
    return ratio

