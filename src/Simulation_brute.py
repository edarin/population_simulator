# coding: utf-8
import numpy as np
import pandas as pd

from generation import generate_population
from tools import (distance_to_reference, get_proba, get_classes_age,
    ajout_effectif_reference,
    from_unique_value_reference_to_standard_reference)

sample_size_target = 10000


##### Sexe et Age
# Issu de données INSEE 2016
# À noter : âge = 100 correspond à 100 et plus

effectifs_age_sexe = pd.read_csv("data/demographie/pop_age_sexe_2016.csv")
del effectifs_age_sexe['total']

effectifs_age_sexe = pd.melt(effectifs_age_sexe, id_vars=['age'],
                             value_vars=['femme', 'homme'], var_name ='sexe',
                             value_name='effectif_ref')

nbr_population_totale = effectifs_age_sexe['effectif_ref'].sum()
marges = get_proba(effectifs_age_sexe.set_index(['sexe', 'age']), 'effectif_ref')

population = generate_population(marges, sample_size_target)
sample_size = len(population)


#### test de la génération

# just a trick to use distance_to_reference
effectifs_age_sexe['effectif'] = effectifs_age_sexe['effectif_ref']
test_age_sexe = distance_to_reference(population, effectifs_age_sexe, sample_size, ['age','sexe'])
del effectifs_age_sexe['effectif']
print ("Test effectifs simulés pour âge et sexe :")
print(test_age_sexe['ratio'].describe())

######### Activité

### reference_activite: lecture de la table de référence
reference_activite = pd.read_csv("data/demographie/activite.csv")
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

population = get_classes_age(population, 'age', classes_age)
population_activite = population.copy()
population_activite = population_activite.merge(reference_activite, how='outer')

population['activite'] = np.random.binomial(1, population_activite['proba_activite'])
population['activite'] = population['activite'].astype(bool)
# Ajout des effectifs des non actifs
reference_activite = from_unique_value_reference_to_standard_reference(
    reference_activite,
    'activite')
#### Vérifier que le tirage se rapproche de la réalité
test_activite = distance_to_reference(population, reference_activite, sample_size,
                     ['sexe', 'classe_age', 'activite'],
                     nb_modalite=2)
print ("Test effectifs simulés pour activité :")
print(test_activite['ratio'].describe())


## Emploi : hypothèse : tout le monde est à tp plein

###Lecture table
reference_emploi = pd.read_csv("data/travail/nbr_heure_travaillees.csv")
reference_emploi = pd.melt(reference_emploi, id_vars=['classe_age_salaire'],
                             value_vars=['femme', 'homme'], var_name = 'sexe',
                             value_name='total_heures')

classes_age_salaire = reference_emploi['classe_age_salaire'].str.replace('De | ans|', '', case=False)
classes_age_salaire = classes_age_salaire.str.replace(' à ', '-')
classes_age_salaire = classes_age_salaire.str.replace('Moins ', '15-')
classes_age_salaire = classes_age_salaire.str.replace('Plus 65', '65-' + str(max_age))
classes_age_salaire.name = 'classe_age_salaire'
reference_emploi['classe_age_salaire'] = classes_age_salaire

reference_emploi['total_heures'] *= 1000

### Obtention du nbr d'individu en emploi
duree_travail_legal_an = 1607 # référence légale du nbr d'heures par an pour un tps plein
reference_emploi['effectif'] = reference_emploi['total_heures'] / duree_travail_legal_an
reference_emploi['emploi_ech'] = reference_emploi['effectif'] * (sample_size / nbr_population_totale)
nbr_pop_emploi = reference_emploi['effectif'].sum()


### Récupération du nbr d'actif dans les classes d'âge de l'emploi
population = get_classes_age(population,
                                     'age',
                                     classes_age_salaire)


population['pop_active'] = population['activite']
reference_emploi = ajout_effectif_reference(reference_emploi,
                                                       population[population['activite'] ==  True],
                                                       'pop_active',
                                                       ['sexe', 'classe_age_salaire'])
del population['pop_active']

### Calcul de la proba conditionnelle d'être en emploi quand en activité (!)
reference_emploi['proba_emploi_cond_activite'] = reference_emploi['emploi_ech'] / reference_emploi['pop_active']
reference_emploi['activite'] = np.bool(True)

### Création de la variable indicatrice d'être en emploi
population_emploi = population.copy()
population_emploi = population_emploi.merge(reference_emploi, how='left')
population_emploi.fillna(0, inplace=True)
population['emploi'] = np.random.binomial(1, population_emploi['proba_emploi_cond_activite'])
population['emploi'] = population['emploi'].astype(bool)

assert population.loc[population.activite == False, 'emploi'].unique() == False, "Il existe des non-actifs en emploi"

#Vérification

#### Construcion de la table standard
effectifs_age_sexe = get_classes_age(effectifs_age_sexe,
                                     'age',
                                     classes_age_salaire)
reference_emploi = ajout_effectif_reference(reference_emploi,
                                              effectifs_age_sexe,
                                              'effectif_ref',
                                              ['sexe', 'classe_age_salaire'])
reference_emploi = from_unique_value_reference_to_standard_reference(
    reference_emploi,
    'emploi')

test_emploi = distance_to_reference(population, reference_emploi, sample_size,
                     ['sexe', 'classe_age_salaire', 'emploi'],
                     nb_modalite=2)
print ("Test effectifs simulés pour emploi :")
print(test_emploi['ratio'].describe())


### Salaire

reference_salaire = pd.read_csv("data/travail/salaire_brut_horaire.csv")
reference_salaire = pd.melt(reference_salaire, id_vars=['classe_age_salaire'],
                             value_vars=['femme', 'homme'], var_name = 'sexe',
                             value_name='salaire')
reference_salaire['classe_age_salaire'] = classes_age_salaire

duree_travail_legal_mois = int(round(duree_travail_legal_an/12))

reference_salaire['salaire'] *= duree_travail_legal_mois
reference_salaire['emploi'] = np.bool(True)

population = population.merge(reference_salaire, how='left')
population['emploi'].fillna(0, inplace=True)
































