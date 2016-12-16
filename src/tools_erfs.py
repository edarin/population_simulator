import pandas as pd
import numpy as np
import json

def open_json(file):
    try:
        with open(file, 'r') as fp:
            return json.load(fp)
    except Exception as e:
        print('Failed to load from graph ' + repr(e))
        return {}
        
def get_individu(table):
    
    '''
    Table utilisee : output/erfs_fpr_2012.h5
    Fait les merge necessaire pour creer table individu
    '''

    erfs = pd.HDFStore(table)
    emploi_ind = erfs['/fpr_irf12e12t4']
    revenu_ind = erfs['/fpr_indiv_2012_retropole']
    individu = emploi_ind.merge(revenu_ind, on= ['noindiv', 'noi', 'ident12'], how='inner')
    individu = individu[(individu.naia != 1854) & (individu.naia != 0)]
    return individu

def get_individu_simplified(table):
    '''
    Selection des colonnes d'interet
    '''
    individu = table[['acteu6', 'naia', 'chpub', 'matri', 'dip', 'age', 'nbenf18', 'nbenf18m', 
                    'nbenf3', 'nbenf6','noi', 'retrai', 'revent','noindiv',
                    'sexe', 'statut', 'typmen15', 'rag_i', 'ric_i', 'rnc_i', 'chomage_i',
                    'pens_alim_recue_i', 'retraites_i', 'salaires_i', 'wprm', 'maahe']]
    return individu

def get_menage(table):
    '''
    Table utilisee : output/erfs_fpr_2012.h5
    Fait les merge necessaire pour creer table menage
    '''
    erfs = pd.HDFStore(table)
    emploi_men = erfs['/fpr_mrf12e12t4']
    revenu_men = erfs['/fpr_menage_2012_retropole']
    menage = revenu_men.merge(emploi_men, on= ['ident12'])
    assert menage.isnull().values.any() == False
    return menage

def get_salaire(table, groupby):
    '''
    Recuperer le salaire en fonction du groupby
    '''
    salaire = table.groupby(groupby).salaires_i
    return salaire

def get_weights(table, groupby):
    '''
    Recuperer les poids en fonction du groupby
    '''
    weights = table.groupby(groupby).wprm
    return weights

