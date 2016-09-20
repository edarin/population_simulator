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
    