# coding: utf-8
import numpy as np
import pandas as pd

from make_demo import (generate_SexeAge, generate_Handicap)
from make_travail import (generate_Activite, 
                          generate_Emploi, 
                          add_Salaire,
                          add_Retraite,
                          generate_Etudiants)
from make_couple import (generate_Couple,
                        generate_pop_men)                          

sample_size_target = 1000

''''
TABLE INDIVIDUS
'''

# AgeSexe   
effectifs_age_sexe = pd.read_csv("data/demographie/pop_age_sexe_2016.csv")
generation = generate_SexeAge(effectifs_age_sexe, sample_size_target)
effectifs_age_sexe = generation[1]
population = generation[0]

sample_size = len(population)
max_age = effectifs_age_sexe['age'].max()


### Activité
reference_activite = pd.read_csv("data/demographie/activite_2015.csv")   
population['activite']= generate_Activite(reference_activite, effectifs_age_sexe, population, sample_size)

#Emploi : à partir du taux de chomaĝe
reference_emploi = pd.read_csv("data/travail/chomage.csv")


population['emploi'] = generate_Emploi(reference_emploi, population, max_age)

# Salaire
reference_salaire = pd.read_csv("data/travail/salaire_brut_horaire.csv")
population['salaire'] = add_Salaire(reference_salaire,population, max_age)

# Retraite
reference_retraite = pd.read_csv("data/travail/retraite_2012.csv")
population['retraite'] = add_Retraite(reference_retraite, population, max_age)


#Étudiants
reference_etudes = pd.read_csv("data/demographie/etudes.csv")
population['etudes'] = generate_Etudiants(reference_etudes, population)
# Selon une étude INSEE (2016) -> 23%/
# http://www.insee.fr/fr/themes/document.asp?reg_id=0&ref_id=ip1603#inter6

#### Handicap

reference_handicap = pd.read_csv("data/demographie/handicap_pop.csv")
reference_handicap_jeune = pd.read_csv("data/demographie/handicap_pop_jeune.csv")
population['handicap'] = generate_Handicap(reference_handicap, reference_handicap_jeune, population, effectifs_age_sexe, sample_size)

#### Statut marital
reference_marital = dict()
for sexe in ['homme', 'femme']:
    reference_marital[sexe] = pd.read_csv("data/menages/statut_marital_{0}.csv".format(sexe))
population['statut_marital'] = generate_Couple(reference_marital.copy(), population)


''''
TABLE MÉNAGE
'''''

population_menage = generate_pop_men(population)

##### Le fait d'avoir un.des enfant.s
reference_typefam = pd.read_csv('data/menages/enfants/type_famille.csv')



















