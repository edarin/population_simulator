# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 14:33:05 2016

@author: edarin
"""

import pandas as pd


def get_classes_age(tab, age_col, classes):
    ''' ajoute une colonne à tab contenant la classe d'age
        faisant référence aux catégories de la serie classes
    '''
    assert isinstance(classes, pd.Series)
    assert classes.name not in tab.columns
    age = tab[age_col]

    tab[classes.name] = ''
    for classe in classes.unique():
        age_inf = int(classe.split('-')[0])
        age_sup = int(classe.split('-')[1])
        cond_classe = (age >= age_inf) & (age <= age_sup)
        tab.loc[cond_classe, classes.name] = classe
    return tab


def ajout_effectif_reference(tab_init, tab_ref, col_ref, groupby):
    '''
    Ajoute à la table d'intérêt l'effectif de référence
    '''
    assert all(tab_init.groupby(groupby).size() == 1)
    reference = tab_ref.groupby(groupby)[col_ref].sum()
    reference = reference.reset_index()
    output = tab_init.merge(reference, on=groupby, how='left')
    return output


def get_proba(tab, col):
    div = tab[col]/tab[col].sum()
    return div


def distance_to_reference(population_simulee, reference, sample_size, groupby,
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


def from_unique_value_reference_to_standard_reference(tab, col):
    '''
        Lorsque l'on a une table de référence avec la répartition
        d'une sous-population, on construit une table de référence au
        format standard en ajoutant les effectifs complémentaire avec 
        la variable col qui est un booléen True pour l'effectif 
        d'orginie et False pour l'autre
    '''
    tab_other_value = tab.copy()
    tab_other_value['effectif'] = tab_other_value['effectif_ref'] - tab_other_value['effectif']
    tab_other_value['proba_activite'] = tab_other_value['effectif']/tab_other_value['effectif_ref']
    tab['activite'] = True
    tab_other_value['activite'] = False
    tab = pd.concat([tab, tab_other_value])
    return tab