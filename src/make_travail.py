# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 15:54:58 2016

@author: edarin
"""
import pandas as pd
import numpy as np

from tools import (distance_to_reference, get_proba, get_classes_age,
    ajout_effectif_reference,
    from_unique_value_reference_to_standard_reference)
from tools_erfs import open_json
    
def generate_Activite(reference_activite, effectifs_age_sexe, population, sample_size):
    """
     Indicatrice : 1 si actif
     Population active
     Champ : France métropolitaine, population des ménages, actifs de 15 ans ou plus.
     Source : Insee, enquête Emploi.
     2015
    """
    ### reference_activite: lecture de la table de référence
    reference_activite = pd.melt(reference_activite, id_vars=['classe_age'],
                                 value_vars=['femme', 'homme'], var_name = 'sexe',
                                 value_name='effectif')
    
    reference_activite['effectif'] *= 1000
    nbr_population_active = reference_activite['effectif'].sum()
    
    # Note : classe-age est bien les classes d'ages utilisées dans la table activité
    #       -> pas nécessairement universel
    classes_age = reference_activite['classe_age'].str.replace(' ans', '')
    max_age = effectifs_age_sexe['age'].max()
    classes_age = classes_age.str.replace(' ou plus', '-' + str(max_age))
    reference_activite['classe_age'] = classes_age
    
    effectifs_age_sexe = get_classes_age(effectifs_age_sexe,
                                         'age',
                                         classes_age)
    
    
    ##### reference_activite : création de la colonne proba_activite
    reference_activite = ajout_effectif_reference(reference_activite,
                                                  effectifs_age_sexe,
                                                  'effectif_ref',
                                                  ['sexe', 'classe_age'])
    
    reference_activite['proba_activite'] = reference_activite['effectif']/reference_activite['effectif_ref']
    
    population_activite = population.copy()
    population_activite = get_classes_age(population_activite, 'age', classes_age)
    population_activite = population_activite.merge(reference_activite, how='outer')
    
    population_activite['activite'] = np.random.binomial(1, population_activite['proba_activite'])
    
    # Ajout des effectifs des non actifs
    reference_activite = from_unique_value_reference_to_standard_reference(
        reference_activite,
        'activite')
    #### Vérifier que le tirage se rapproche de la réalité
    test_activite = distance_to_reference(population_activite, reference_activite, sample_size,
                         ['sexe', 'classe_age', 'activite'],
                         nb_modalite=2)
    print ("Test effectifs simulés pour activité :")
    print(test_activite['ratio'].describe())
           
    return population_activite['activite'].astype(bool)    

def generate_Emploi(reference_emploi, population, max_age):
    ## Emploi : à partir du taux de chomaĝe
    # Indicatrice : 1 si emploi
    #
    # Taux de chômage trimestriel au sens du BIT en France (hors Mayotte)
    # Données CVS en moyenne trimestrielle, en %
    # Champ : France (hors Mayotte), population des ménages, personnes de 15 ans ou plus
    # Source : Insee, enquête Emploi, 2012(T2)
    
    ###Lecture table
    reference_emploi = pd.melt(reference_emploi, id_vars=['classe_age_chomage'],
                                 value_vars=['femme', 'homme'], var_name = 'sexe',
                                 value_name='taux_chomage')
    reference_emploi['taux_chomage'] /=100
    
    classes_age_chomage = reference_emploi['classe_age_chomage'].str.replace('>49', '50-' + str(max_age))
    reference_emploi['classe_age_chomage'] = classes_age_chomage
    reference_emploi['activite'] = np.bool(True)
    reference_emploi['proba_emploi'] = 1 - reference_emploi['taux_chomage']
    
    ### Récupération du nbr d'actif dans les classes d'âge de l'emploi
    population_emploi = population.copy()
    population_emploi = get_classes_age(population_emploi,
                                         'age',
                                         classes_age_chomage)
    
    ### Création de la variable indicatrice d'être en emploi
    population_emploi = population_emploi.merge(reference_emploi, how='left')
    population_emploi.fillna(0, inplace=True)
    population_emploi['emploi'] = np.random.binomial(1, population_emploi['proba_emploi'])
    population_emploi['emploi'] = population_emploi['emploi'].astype(bool)
    
    assert population_emploi.loc[population_emploi.activite == False, 'emploi'].unique() == False, "Il existe des non-actifs en emploi"
    
    #Vérification
    nbr_population_active_ech = population_emploi.loc[ population['activite'] == True, 'activite'].sum()
    
    test_emploi = pd.DataFrame(population_emploi[population_emploi['activite'] == True].groupby(['classe_age_chomage', 'sexe']).size()).reset_index()
    test_emploi.rename(columns={0: 'effectif_genere'}, inplace=True)
    test_emploi['proba_generee'] = 1 - (test_emploi['effectif_genere'] / nbr_population_active_ech)
    
    test_emploi = test_emploi.merge(reference_emploi, on=['sexe', 'classe_age_chomage'])
    test_emploi['ratio'] = test_emploi['proba_generee'] / test_emploi['proba_emploi']
    
    print ("Test effectifs simulés pour emploi :")
    print(test_emploi['ratio'].describe())
    
    # Taux de chômage population générée
    population_chomage = population_emploi[(population_emploi['activite'] == True) & (population_emploi['emploi'] == False)]
    taux_chomage_genere = len(population_chomage.index) / nbr_population_active_ech
    print ("Taux de chômage généré : ", taux_chomage_genere*100)
       
    return population_emploi['emploi']


def add_Salaire_fromINSEE(reference_salaire, population, max_age):
    """    
    ### Salaire
    # Salaire brut horaire moyen (€)
    # Champ :
    #   - salariés du secteur privé ou d'une entreprise publique, hors agriculture, y compris bénéficiaires de contrats aidés et chefs d'entreprises salariés ;
    #   - sont exclus, les apprentis, les stagiaires, les salariés agricoles et les salariés des particuliers employeurs.
    #   - France entière y compris DOM.
    #Source : Insee, DADS 2012.
    """
    
    reference_salaire = pd.melt(reference_salaire, id_vars=['classe_age_salaire'],
                                 value_vars=['femme', 'homme'], var_name = 'sexe',
                                 value_name='salaire')
    
    classes_age_salaire = reference_salaire['classe_age_salaire'].str.replace('De | ans|', '', case=False)
    classes_age_salaire = classes_age_salaire.str.replace(' à ', '-')
    classes_age_salaire = classes_age_salaire.str.replace('Moins ', '15-')
    classes_age_salaire = classes_age_salaire.str.replace('Plus 65', '65-' + str(max_age))
    reference_salaire['classe_age_salaire'] = classes_age_salaire
    
    duree_travail_legal_an = 1607 # référence légale du nbr d'heures par an pour un tps plein
    duree_travail_legal_mois = int(round(duree_travail_legal_an/12))
    
    reference_salaire['salaire'] *= duree_travail_legal_mois
    reference_salaire['emploi'] = np.bool(True)
    
    population_salaire = population.copy()
    population_salaire = get_classes_age(population_salaire,
                                         'age',
                                         classes_age_salaire)
    
    
    population_salaire = population_salaire.merge(reference_salaire, how='left', on=['sexe', 'classe_age_salaire', 'emploi'])
    population_salaire['salaire'].fillna(0, inplace=True)
    
    return population_salaire['salaire']
    
salaire = open_json('data/travail/salaire_sexe_age.json')

def put_Salaire(population, sexe, condition_age, k, salaire = salaire):
    '''
    Automatisation de l'adjonction du salaire depui
    '''
    condition_sexe = (population.sexe == sexe) 
    condition_emploi = (population.emploi == True)  
    personnes = population[condition_sexe & condition_age & condition_emploi]
    
    salaire_filtered = pd.DataFrame(salaire[k], dtype = np.int64).astype(np.int64)
    
    salaire_filtered.rename(columns={0: 'valeur'}, inplace=True)
    
    salaire_filtered = salaire_filtered[salaire_filtered.valeur >= 0]
    
    population.loc[condition_age & condition_sexe & condition_emploi, 'salaire'] = salaire_filtered[:len(personnes)].values
    population.salaire = pd.to_numeric(population.salaire)    
    return population


def add_SalairefromERFS(population, salaire):
    population['salaire'] = ''
    
    for k in salaire.keys():
        
        age = k.split(', ')[1].strip(')')
        sexe = k.split(', ')[0].strip("('")
        
        if (age != "'>60'") and (age != "'<23'"):
            age = int(age)
            condition_age = (population.age == age)
            population = put_Salaire(population, sexe, condition_age, k)       
            
        if age == "'>60'":
            condition_age = (population.age >= 60)
            population = put_Salaire(population, sexe, condition_age, k)
            
        if age == "'<23'" :
            condition_age = (population.age <= 23)
            population = put_Salaire(population, sexe, condition_age, k)
    population.loc[population.emploi == False, 'salaire'] = 0
    return population['salaire']
    
def add_Retraite(reference_retraite, population, max_age):
    """
    ### Retraite
    
    ## INSEE 2012
    # Montant moyen mensuel de la retraite globale
    # Champ : retraités de droit direct, âgés de 65 ans ou plus,
    #       nés en France ou à l'étranger, résidents en France ou à l'étranger.
    #       Les retraités ne percevant qu'une pension de réversion sont exclus.
    # Source : Drees, échantillon interrégimes de retraités 2012.
    """
    reference_retraite = pd.melt(reference_retraite, id_vars=['classe_age_retraite'],
                                 value_vars=['femme', 'homme'], var_name = 'sexe',
                                 value_name='retraite')
    
    classes_age_retraite = reference_retraite['classe_age_retraite'].str.replace(' ans', '')
    classes_age_retraite = classes_age_retraite.str.replace(' à ', '-')
    classes_age_retraite = classes_age_retraite.str.replace(' et plus', '-' + str(max_age))
    reference_retraite['classe_age_retraite'] = classes_age_retraite
    
    reference_retraite['activite'] = np.bool(False)
    
    population_retraite = population.copy()
    population_retraite = get_classes_age(population_retraite,
                                         'age',
                                         classes_age_retraite)
    
    population_retraite = population_retraite.merge(reference_retraite, how='left', on=['sexe', 'classe_age_retraite', 'activite'])
    population_retraite['retraite'].fillna(0, inplace=True)
    
    assert population_retraite.loc[population_retraite['retraite'] != 0, 'age'].min() == 65, "On ne peut toucher de retraite avant 65 ans"
    
    return population_retraite['retraite']

def generate_Etudiants(reference_etudes, population):
    """
    ### Étudiants
    
    # Entre 15 ans et 25 ans
    # Délibérement pas de distinction de sexe (pas de chiffres précis au niveau de l'âge)
    
    # Note : les millésimes correspondent à la rentrée scolaire.
    # Champ : France (hors Mayotte), enseignement public et privé, y c. scolarisation en apprentissage.
    # Source : Depp. 2013
    """
    
    reference_etudes['age'] = reference_etudes['age'].str.replace(' ans', '')
    reference_etudes['proba_etudes'] /= 100
    reference_etudes['age'] = pd.to_numeric(reference_etudes['age'])
    
    # Comparaison avec le taux genere des non-actifs jeunes
    proba_generee = population[(population['age'] < 26) & (population['age'] > 14)].groupby(['age']).mean()[['activite', 'emploi']]
    proba_generee = proba_generee.reset_index()
    #proba_generee.rename(columns = {'activite':'proba_generee'}, inplace = True)
    proba_generee['activite'] = 1 - proba_generee['activite']
    proba_generee['emploi'] = 1 - proba_generee['emploi']
    reference_etudes = reference_etudes.merge(proba_generee, on = ['age'], how='left')
    
    
    population_etudes = population.copy()
    population_etudes = population_etudes.merge(reference_etudes, on = ['age'], how='left')
    population_etudes.loc[population_etudes['age'] < 15, 'proba_etudes'] = 1
    population_etudes.loc[population_etudes['age'] > 25, 'proba_etudes'] = 0
    population['etudes'] = np.random.binomial(1, population_etudes['proba_etudes'])
    population['etudes'] = population['etudes'].astype(bool)
    
    population_jeune = population[(population['age'] > 17) & (population['age'] < 25)]
    proportion_etude_emploi = (len(population_jeune[(population_jeune['emploi'] == True) & (population_jeune['etudes'] == True)])/ population_jeune['etudes'].sum()) * 100
    print( " Pourcentage d'étudiants en emploi", proportion_etude_emploi)     
    
    return population['etudes']