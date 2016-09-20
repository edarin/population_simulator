# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 11:54:17 2016

@author: edarin
"""

import pandas as pd


def check_tirage(population_simulee, reference,sample_size, groupby,
                 nb_modalite=1):
    ''' 
        - population_simulee est la population que l'on veut tester
        - colname est la variable simulée que l'on étudie
        - reference est un dataframe contenant les variable effectif (effectifs de la variable d'intérêt)
            et effectif_ref ainsi que les colonne servant au groupby.
        - lorsque l'on a décomposé la population en plusieurs modalités
        on a plusieurs lignes faisant référence à la même population.
        A ce moment, là on prévoit que l'effectif total de la population est
        multiplié par nb_modalite.
        # TODO: automatiser le compte du nombre de modalité (peut-être en
            ajoutant le nom de la variable d'intérêt dans les paramètres)
        
        retourn ratio avec effectif_genere, effectif_reference et le ratio des deux
    '''
       
    assert isinstance(nb_modalite, int)
    ratio_des_effectifs = pd.DataFrame(population_simulee.groupby(groupby).size()).reset_index()
    ratio_des_effectifs.rename(columns={0: 'effectif_genere'}, inplace=True)
    
    ratio = ratio_des_effectifs.merge(reference, on=groupby, how='inner')
    ratio['effectif_genere'].fillna(0, inplace=True)
    
    population_size = reference['effectif_ref'].sum()/nb_modalite
    ratio['effectif_theorique'] = round((ratio['effectif'] * (sample_size / population_size))).astype(int)
        
    
    ratio['ratio'] = ratio['effectif_genere']/ratio['effectif_theorique']

    return ratio

