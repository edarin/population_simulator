# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 15:25:48 2016

Création de la table des couples

@author: edarin
"""
from get_couple import pick_age

pop_homme = population[(population['statut_marital'] == 1) & (population['sexe'] == 'homme')]
pop_femme = population[(population['statut_marital'] == 1) & (population['sexe'] == 'femme')]


def find_femme(age):
    femme = pop_femme[pop_femme['age'] == pick_age(age)]
    if femme.empty == True:
        return find_femme(age)
    return femme
    
    
index= np.arange(len(population[population['statut_marital'] == 1]))

population_menage = pd.DataFrame(index=index, columns = population.columns)
population_menage['ident_men']=''

    
y=0
for x in np.arange(len(pop_homme)):
        
    homme = pop_homme.iloc[x]
    femme = find_femme(homme['age']).iloc[0]
    
    
    population_menage.iloc[y]=femme
    population_menage.iloc[y]['ident_men'] = x
    population_menage.iloc[y+1]=homme
    population_menage.iloc[y+1]['ident_men'] = x
    y +=2

population_autre_couple = population[population['statut_marital'] != 1]

population_autre_couple['ident_men'] = np.arange(len(pop_femme), 
                                        len(pop_femme) + len(population_autre_couple))

population_menage = pd.concat([population_menage,population_autre_couple])                                        