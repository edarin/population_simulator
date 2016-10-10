# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 18:48:43 2016

@author: edarin
"""


import numpy as np
import json

type_couple = json.load(open ("/home/edarin/Dev/population_simulator/src/data/menages/ecart_couple_homme.json", 'r'))


def normalize(elements):
    sum = 0
    output = []
    for element in elements:
        sum += element
    for element in elements:
        output.append(element / sum)
    return output

type_couple_proba = {}
for element in type_couple:
   type_couple_proba[element['age']] = normalize([element['Femme plus jeune'],
                                                 element["Conjoints du meme age"],
                                                 element["Femme plus agee"]])

ecart_age = json.load(open ("/home/edarin/Dev/population_simulator/src/data/menages/ecart_age.json", 'r'))

# L'homme est plus jeune que sa conjointe
ecart_age_negatif = [x['ecart_age'] for x in ecart_age[:14]]
proba_negatif = normalize([x['pourcent'] for x in ecart_age[:14]])

# L'homme a le même âge que sa conjointe (-1,0,1)
ecart_age_egal = [x['ecart_age'] for x in ecart_age[14:17]]
proba_egal = normalize([x['pourcent'] for x in ecart_age[14:17]])

# L'homme est plus vieux que sa conjointe
ecart_age_positif = [x['ecart_age'] for x in ecart_age[17:]]
proba_positif = normalize([x['pourcent'] for x in ecart_age[17:]])

def pick_age(age_homme):
    type = np.random.choice(["Femme plus jeune",
                             "Conjoints du meme age",
                             "Femme plus agee"],
                            p=type_couple_proba[age_homme])
    if type == "Femme plus jeune":
        quelle_femme = age_homme - np.random.choice(ecart_age_positif, p=proba_positif)
    elif type == "Conjoints du meme age":
        quelle_femme = age_homme + np.random.choice(ecart_age_egal, p=proba_egal)
    elif type == "Femme plus agee":
        quelle_femme = age_homme - np.random.choice(ecart_age_negatif, p=proba_negatif)

    # We can't have below 18 and above 100
    if quelle_femme < 18:
        return pick_age(age_homme)
    if quelle_femme > 100:
        return pick_age(age_homme)
    return quelle_femme















