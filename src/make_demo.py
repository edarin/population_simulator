# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 15:21:02 2016

@author: edarin
"""
import pandas as pd
import numpy as np
from generation import generate_population

from tools import (distance_to_reference, get_proba, get_classes_age,
    ajout_effectif_reference,
    from_unique_value_reference_to_standard_reference)
"""

S'occupe de générer une population à partir d'inputs
de description de la population

- L'input (marges dans les programmes) est une 
Series de la librairie pandas. 

Son index reprend les colonnes qui seront imputées

"""
from numpy.testing import assert_almost_equal
from pandas import Series, DataFrame


def complete_input(incomplete_marges):
    # est-ce utile ? 
    complete_marges = incomplete_marges
    return complete_marges
    

def check_input_format(marges):
    ''' réalise des tests sur le format utilisé pour la
        génération de la table
    '''
    assert isinstance(marges, Series)
    assert all(0 <= marges)
    assert all(marges <= 1)
    assert_almost_equal(marges.sum(), 1)
    return True



def generate_population(marges, size):
    ''' 
        retourne une population ayant les caractèristiques
        marquées dans l'objet marges.
        - marges
        - size est la taille en nombre de ligne de la 
            population génrée.
        Note importante : 
            La taille obtenue n'est pas exactement size.
            On part du principe que la taille est là pour 
            controler à peu près le temps de calcul mais 
            la taille exacte n'est pas très importante
    '''
    check_input_format(marges)
    size_group = marges*size
    size_group = size_group.round().astype(int)
    def _check_size(vecteur, taille):
        # TODO: should be an option
        return abs(vecteur.sum()/taille - 1) < 0.05
    
    def resize(marges, size):
        # TODO: faire un appel recursif ?
        # TODO: ça doit se trouver sur internet
        pass
    

    if not _check_size(size_group, size):
        resize(marges, size)
    
    nb_to_generate = size_group[size_group > 0]
#    population_values = nb_to_generate.values.repeat(nb_to_generate).index
    population = nb_to_generate.repeat(nb_to_generate)
    population = population.reset_index().iloc[:,:-1]
    return population


if __name__ == '__main__':
    import pandas as pd
    reference = pd.read_csv("data/demographie/pop_age_sexe_2016.csv")
    del reference['total']
    marges = reference.set_index('age_revolu').unstack()
    marges.index.names = ['sexe', 'age']
    marges /= marges.sum()
    generate_population(marges, 1000)

def generate_SexeAge(effectifs_age_sexe, sample_size_target):
    """    
    Sexe et Age
    # Issu de données INSEE 2016
    # Champ : France y compris Mayotte.
    # Source : Insee, estimations de population (résultats provisoires arrêtés à fin 2015).
    # À noter : âge = 100 correspond à 100 et plus
    """
    del effectifs_age_sexe['total']
    
    effectifs_age_sexe = pd.melt(effectifs_age_sexe, id_vars=['age'],
                                 value_vars=['femme', 'homme'], var_name ='sexe',
                                 value_name='effectif_ref')
    
    nbr_population_totale = effectifs_age_sexe['effectif_ref'].sum()
    marges = get_proba(effectifs_age_sexe.set_index(['sexe', 'age']), 'effectif_ref')
    
    population = generate_population(marges, sample_size_target)
    sample_size = len(population)
    # just a trick to use distance_to_reference
    effectifs_age_sexe['effectif'] = effectifs_age_sexe['effectif_ref']
    test_age_sexe = distance_to_reference(population, effectifs_age_sexe, sample_size, ['age','sexe'])
    del effectifs_age_sexe['effectif']
    print ("Test du ratio pour âge et sexe :")
    print(test_age_sexe['ratio'].describe())
    print ("Test du MSE pour âge et sexe :")
    print(test_age_sexe['mse'].mean())
       
    return population, effectifs_age_sexe

def generate_Handicap(reference_handicap, reference_handicap_jeune, population, effectifs_age_sexe, sample_size):
    """
    population_handicapée :
    Champ : population âgée de 15 à 64 ans en France métropolitaine vivant en ménage ordinaire (collectivités exclues).
    Source : Dares, enquête complémentaire à l'enquête Emploi 2007.
    http://www.insee.fr/fr/themes/document.asp?ref_id=T11F037
    Limite : pas d'handicapés au-dessus de 64 ans

    population handicapée jeune : NATTEF06244.xls
    Table issue du mode de scolarisation -> création artificielle de la catégorie sexe
    - Champ : France.
    - Source : Depp.
    - 2014-2015

    """  
    reference_handicap['homme'] *= reference_handicap.iloc[4,1]/100
    reference_handicap['femme'] *= reference_handicap.iloc[4,2]/100
    reference_handicap = reference_handicap.drop(reference_handicap.index[4])                        
    
    # Ajout jeune handicap      
    reference_handicap_jeune['femme'] = reference_handicap_jeune['effectif'] / 2
    reference_handicap_jeune['homme'] = reference_handicap_jeune['effectif'] / 2
    del reference_handicap_jeune['effectif']
    
    reference_handicap = pd.concat([reference_handicap_jeune, reference_handicap])
                                    
    classes_age_handicap = reference_handicap['classe_age_handicap'].str.replace(' ans', '')
    classes_age_handicap = classes_age_handicap.str.replace(' à ', '-')
    reference_handicap['classe_age_handicap'] = classes_age_handicap
    
    reference_handicap = pd.melt(reference_handicap, id_vars=['classe_age_handicap'],
                                 value_vars=['femme', 'homme'], var_name = 'sexe',
                                 value_name='effectif')
    
    ##### reference_handicap : création de la colonne proba_handicap    
    effectifs_age_sexe = get_classes_age(effectifs_age_sexe,
                                         'age',
                                         classes_age_handicap)
    
    reference_handicap = ajout_effectif_reference(reference_handicap,
                                                  effectifs_age_sexe,
                                                  'effectif_ref',
                                                  ['sexe', 'classe_age_handicap'])
                                           
    reference_handicap['proba_handicap'] = reference_handicap['effectif']/reference_handicap['effectif_ref']
    
    population_handicap = population.copy()
    population_handicap = get_classes_age(population_handicap, 'age', classes_age_handicap)
    population_handicap = population_handicap.merge(reference_handicap, on=['classe_age_handicap', 'sexe'], how='outer')
    # Pas d'infos concernant les handicapés de plus de 64 ans
    population_handicap['proba_handicap'].fillna(0, inplace=True)
    population_handicap['handicap'] = np.random.binomial(1, population_handicap['proba_handicap'])
    population_handicap['handicap'] = population_handicap['handicap'].astype(bool)
    
    # Ajout des effectifs des non actifs
    reference_handicap = from_unique_value_reference_to_standard_reference(
        reference_handicap,
        'handicap')
    #### Vérifier que le tirage se rapproche de la réalité
    test_handicap = distance_to_reference(population_handicap, reference_handicap, sample_size,
                         ['sexe', 'classe_age_handicap', 'handicap'],
                         nb_modalite=2)
    print ("Test du ratio pour handicap :")
    print(test_handicap['ratio'].describe())
    print ("Test du MSE pour handicap :")
    print(test_handicap['mse'].mean())
       
    # Comparaison avec chiffre sur activite des handicapés
    
    population_handicapee = population_handicap[(population_handicap['handicap'] == True) & (population_handicap['age'] > 14) & (population_handicap['age'] < 65)]
    proportion_handicap_emploi = (len(population_handicapee[population_handicapee['emploi'] == True])/ len(population_handicapee)) * 100
    proportion_handicap_activite = (len(population_handicapee[population_handicapee['activite'] == True])/ len(population_handicapee)) * 100
    
    print( " Pourcentage d'handicapés en emploi", proportion_handicap_emploi) 
    print( " Pourcentage d'handicapés en activite", proportion_handicap_activite)  
    return population_handicap['handicap']
