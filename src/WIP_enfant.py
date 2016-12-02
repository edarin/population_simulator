# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 10:28:55 2016

@author: edarin
"""

def generate_Enfants(reference_typefam, population_menage):
    
    reference_typefam['effectif'] *= 1000
    reference_typefam.loc[reference_typefam['type_fam'] == 'Couples', 'effectif'] *= 2
    reference_typefam['proba'] = reference_typefam.effectif / reference_typefam.effectif_ref
    
    # -> penser à générer l'effectif de réfeérence depuis le script et non à la mano
    
    population_enfant = population_menage[population_menage['age'] >= 15]
    population_enfant['type_fam'] = ''
    
    population_enfant.loc[population_enfant['statut_marital'] == 1, 'type_fam'] = 'Couples'
    
    for sexe in ['femme', 'homme']:
        population_enfant.loc[(population_enfant['statut_marital'] != 1) & (population_enfant['sexe'] == sexe), 'type_fam'] = '{0} solo'.format(sexe)
    
    population_enfant = population_enfant.merge(reference_typefam, how='outer', on='type_fam')
    
    
    population_enfant['enfant'] = np.random.binomial(1, population_enfant['proba'])
    
    test_enfant = distance_to_reference(population_enfant, reference_enfant, sample_size,
                         ['type_fam'],
                         nb_modalite=2)
    print ("Test effectifs simulés pour activité :")
    print(test_activite['ratio'].describe())
    
    return population_enfant
    