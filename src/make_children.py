# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 10:28:55 2016

@author: edarin
"""
import pandas as pd
import numpy as np

from tools import (distance_to_reference, get_proba, get_classes_age,
    ajout_effectif_reference,
    from_unique_value_reference_to_standard_reference)

def generate_Children(reference_typefam, population_menage):
    
    reference_typefam = reference_typefam[reference_typefam['type_fam'] != 'Total']
    reference_typefam['effectif'] *= 1000
    reference_typefam.loc[reference_typefam['type_fam'] == 'Couples', 'effectif'] *= 2
    reference_typefam['proba'] = reference_typefam.effectif / reference_typefam.effectif_ref

# -> penser à générer l'effectif de réfeérence depuis le script et non à la mano

    population_enfant = population_menage.copy()
    population_enfant['type_fam'] = ''
    
    population_enfant.loc[population_enfant['statut_marital'] == 1, 'type_fam'] = 'Couples'
    
    for sexe in ['femme', 'homme']:
        population_enfant.loc[(population_enfant['statut_marital'] != 1) & (population_enfant['sexe'] == sexe), 'type_fam'] = '{0} solo'.format(sexe)
    
    population_enfant = population_enfant.merge(reference_typefam, how='inner', on='type_fam')
    
    
    population_enfant['enfant'] = np.random.binomial(1, population_enfant['proba'])
    population_enfant['enfant'] = population_enfant['enfant'].astype(bool)
    population_test = population_enfant
    test_enfant = distance_to_reference(
                        population_simulee = population_test[population_test['enfant'] == True], 
                        reference = reference_typefam, 
                        sample_size = len(population_test),
                        groupby = 'type_fam',
                         )
    print ("Test effectifs simulés pour le nbr de ménages ayant des enfants :")
    print(test_enfant['ratio'].describe())
    
    return population_enfant[['type_fam', 'enfant']]
    
def add_Children(reference_enfant, population_menage):
    reference_enfant = pd.melt(reference_enfant, id_vars=['type_fam'], 
                           var_name = 'nb_enf', value_name = 'effectif' )
    
    reference_enfant['proba'] = reference_enfant.groupby('type_fam')['effectif'].apply(lambda x: x/sum(x))
    
    reference_enfant.set_index('type_fam', inplace = True)
    
    
    population_enfant = population_menage.copy()
    population_enfant['nb_enf'] = 0
    
    for type_fam in ['Couples', 'homme solo', 'femme solo']:
        condition = (population_enfant['enfant'] == True) & (population_enfant['type_fam'] == type_fam)
        nb_menage = len(population_enfant.loc[condition, 'nb_enf'])
        population_enfant.loc[condition, 'nb_enf'] = np.random.choice(np.arange(1,5), nb_menage, p=reference_enfant.loc[type_fam, 'proba'])
    
    print("Équivalent du taux de fécondité :")
    print(population_enfant.loc[(population_enfant.enfant == True), 'nb_enf'].mean())

    return population_enfant['nb_enf']

















