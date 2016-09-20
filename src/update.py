# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 11:54:17 2016

@author: edarin
"""

import pandas as pd


def check_tirage(population_simulee, reference,sample_size, groupby):
    ''' 
        - population_simulee est la population que l'on veut tester
        - colname est la variable simulée que l'on étudie
        - reference est un dataframe contenant les variable effectif (effectifs de la variable d'intérêt)
            et effectif_ref ainsi que les colonne servant au groupby.
        retourn ratio avec effectif_genere, effectif_reference et le ratio des deux
    '''
       
    ratio_des_effectifs = pd.DataFrame(population_simulee.groupby(groupby).size()).reset_index()
    ratio_des_effectifs.rename(columns={0: 'effectif_genere'}, inplace=True)
    
    ratio = ratio_des_effectifs.merge(reference, on=groupby, how='inner')
    ratio['effectif_genere'].fillna(0, inplace=True)
    
    population_size = reference['effectif_ref'].sum()
    ratio['effectif_theorique'] = round((ratio['effectif'] * (sample_size / population_size))).astype(int)
        
    
    ratio['ratio'] = ratio['effectif_genere']/ratio['effectif_theorique']

    return ratio

