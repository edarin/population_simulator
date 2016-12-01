# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 15:25:48 2016

Création de la table des couples

@author: edarin
"""
import pandas as pd
import numpy as np

from get_couple import pick_age

def get_statut_marital(table, col, population_marital):
    table[col] = population_marital.apply(lambda row: np.random.choice(4, 1, p=[row['celib'], row['marrie'], row['veuf'], row['divorce']]), axis=1)
    # Gérer le nbr de femmes mariées vs le nbr d'hommes mariés    
    table_mariage = table[table[col] == 1]    
    if len(table_mariage[table_mariage.sexe == 'homme']) != len(table_mariage[table_mariage.sexe == 'femme']):
        return get_statut_marital(table, col, population_marital)
    return table[col]
    

def generate_Couple(reference_marital, population):
    """
    Génère le statut marital pour chaque individu de la table population
    
    Variable catégorielle :
    # Célibataire = '0'', 
    # Marié.e = '1',
    # Veuf.ve = '2'
    # Divorcé.e = '3'
    
    # Champ : France inclus Mayotte
    # Source : Insee, estimations de population, 2015
    
    """
    for sexe in ['homme', 'femme']:
        reference_marital[sexe][['celib', 'marrie', 'veuf', 'divorce']] = reference_marital[sexe][['celib', 'marrie', 'veuf', 'divorce']].div(reference_marital[sexe]['total'], axis=0)
        del reference_marital[sexe]['total']
        
    reference_marital = pd.concat([pd.DataFrame(reference_marital['femme']), 
                                                pd.DataFrame(reference_marital['homme'])], 
                                                             keys=['femme', 'homme'])
    
    # Associer à la table population -> transformation en DataFrame
    reference_marital.index.names = ['sexe', 'index']
    reference_marital = reference_marital.reset_index(level=['sexe'])
        
    population_marital = population.copy()
    population_marital = population_marital.merge(reference_marital, on= ['sexe', 'age'] )
    
    # Attribution du statut -> colonne "Statut_marital" de la table "Population"
    population['statut_marital'] = ''
    population['statut_marital'] = get_statut_marital(population, 'statut_marital', population_marital)
    
    print("Proportion générée des statuts maritaux :")
    print(population[population['age'] >=15].statut_marital.value_counts(normalize=True, sort=False))
    
    return population['statut_marital']

def find_femme(table,age):
    '''
    Trouver l'individu femme en couple correspondant
    '''
    femme = table[table['age'] == pick_age(age)]
    if femme.empty == True:
        return find_femme(table, age)
    return femme

def generate_pop_men(population):    
    # Associer les femmes et les hommes
    
    pop_homme = population[(population['statut_marital'] == 1) & (population['sexe'] == 'homme')]
    pop_homme = pop_homme.reset_index(drop=True)    
    pop_femme = population[(population['statut_marital'] == 1) & (population['sexe'] == 'femme')]
    pop_femme = pop_femme.reset_index(drop=True)    
    # Construire la table ménage
    index= np.arange(len(pop_femme))
    
    population_menage = pd.DataFrame(index=index, columns = population.columns)
    
    
    for x in np.arange(len(pop_homme)):
    
        homme = pop_homme.iloc[x]
        femme = find_femme(pop_femme, homme['age']).iloc[0]
        pop_femme.iloc[x]=femme
 
    pop_homme.columns = [x+'_conj' for x in pop_homme.columns] 
    population_menage = pd.concat([pop_femme, pop_homme], axis=1)      
        
    # Préparer la colonne ident_men pour les autres types de ménages
    population_autre_couple = population[population['statut_marital'] != 1]
  
    population_menage = pd.concat([population_menage,population_autre_couple])
    
    return population_menage
#Verification ?

