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
# Champ : France y compris Mayotte.
# Source : Insee, estimations de population (résultats provisoires arrêtés à fin 2015).
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
# Indicatrice : 1 si actif
# Population active
# Champ : France métropolitaine, population des ménages, actifs de 15 ans ou plus.
# Source : Insee, enquête Emploi.
# 2015

### reference_activite: lecture de la table de référence
reference_activite = pd.read_csv("data/demographie/activite_2015.csv")
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

del population['classe_age']

## Emploi : à partir du taux de chomaĝe
# Indicatrice : 1 si emploi
#
# Taux de chômage trimestriel au sens du BIT en France (hors Mayotte)
# Données CVS en moyenne trimestrielle, en %
# Champ : France (hors Mayotte), population des ménages, personnes de 15 ans ou plus
# Source : Insee, enquête Emploi, 2012(T2)

###Lecture table
reference_emploi = pd.read_csv("data/travail/chomage.csv")
reference_emploi = pd.melt(reference_emploi, id_vars=['classe_age_chomage'],
                             value_vars=['femme', 'homme'], var_name = 'sexe',
                             value_name='taux_chomage')
reference_emploi['taux_chomage'] /=100

classes_age_chomage = reference_emploi['classe_age_chomage'].str.replace('>49', '50-' + str(max_age))
reference_emploi['classe_age_chomage'] = classes_age_chomage
reference_emploi['activite'] = np.bool(True)
reference_emploi['proba_emploi'] = 1 - reference_emploi['taux_chomage']

### Récupération du nbr d'actif dans les classes d'âge de l'emploi
population = get_classes_age(population,
                                     'age',
                                     classes_age_chomage)

### Création de la variable indicatrice d'être en emploi
population_emploi = population.copy()
population_emploi = population_emploi.merge(reference_emploi, how='left')
population_emploi.fillna(0, inplace=True)
population['emploi'] = np.random.binomial(1, population_emploi['proba_emploi'])
population['emploi'] = population['emploi'].astype(bool)

assert population.loc[population.activite == False, 'emploi'].unique() == False, "Il existe des non-actifs en emploi"

#Vérification
nbr_population_active_ech = population.loc[ population['activite'] == True, 'activite'].sum()

test_emploi = pd.DataFrame(population[population['activite'] == True].groupby(['classe_age_chomage', 'sexe']).size()).reset_index()
test_emploi.rename(columns={0: 'effectif_genere'}, inplace=True)
test_emploi['proba_generee'] = 1 - (test_emploi['effectif_genere'] / nbr_population_active_ech)

test_emploi = test_emploi.merge(reference_emploi, on=['sexe', 'classe_age_chomage'])
test_emploi['ratio'] = test_emploi['proba_generee'] / test_emploi['proba_emploi']

print ("Test effectifs simulés pour emploi :")
print(test_emploi['ratio'].describe())

# Taux de chômage population générée
population_chomage = population[(population['activite'] == True) & (population['emploi'] == False)]
nbr_population_active_ech = population.loc[ population['activite'] == True, 'activite'].sum()
taux_chomage_genere = len(population_chomage.index) / nbr_population_active_ech
print ("Taux de chômage généré : ", taux_chomage_genere*100)

del population['classe_age_chomage']

### Salaire
# Salaire brut horaire moyen (€)
# Champ :
#   - salariés du secteur privé ou d'une entreprise publique, hors agriculture, y compris bénéficiaires de contrats aidés et chefs d'entreprises salariés ;
#   - sont exclus, les apprentis, les stagiaires, les salariés agricoles et les salariés des particuliers employeurs.
#   - France entière y compris DOM.
#Source : Insee, DADS 2012.


reference_salaire = pd.read_csv("data/travail/salaire_brut_horaire.csv")
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

population = get_classes_age(population,
                                     'age',
                                     classes_age_salaire)


population = population.merge(reference_salaire, how='left', on=['sexe', 'classe_age_salaire', 'emploi'])
population['salaire'].fillna(0, inplace=True)

del population['classe_age_salaire']
### Retraite

## INSEE 2012
# Montant moyen mensuel de la retraite globale
# Champ : retraités de droit direct, âgés de 65 ans ou plus,
#       nés en France ou à l'étranger, résidents en France ou à l'étranger.
#       Les retraités ne percevant qu'une pension de réversion sont exclus.
# Source : Drees, échantillon interrégimes de retraités 2012.

reference_retraite = pd.read_csv("data/travail/retraite_2012.csv")
reference_retraite = pd.melt(reference_retraite, id_vars=['classe_age_retraite'],
                             value_vars=['femme', 'homme'], var_name = 'sexe',
                             value_name='retraite')

classes_age_retraite = reference_retraite['classe_age_retraite'].str.replace(' ans', '')
classes_age_retraite = classes_age_retraite.str.replace(' à ', '-')
classes_age_retraite = classes_age_retraite.str.replace(' et plus', '-' + str(max_age))
reference_retraite['classe_age_retraite'] = classes_age_retraite

reference_retraite['activite'] = np.bool(False)

population = get_classes_age(population,
                                     'age',
                                     classes_age_retraite)

population = population.merge(reference_retraite, how='left', on=['sexe', 'classe_age_retraite', 'activite'])
population['retraite'].fillna(0, inplace=True)

assert population.loc[population['retraite'] != 0, 'age'].min() == 65, "On ne peut toucher de retraite avant 65 ans"

del population['classe_age_retraite']
### Étudiants

# Entre 15 ans et 25 ans
# Délibérement pas de distinction de sexe (pas de chiffres précis au niveau de l'âge)

# Note : les millésimes correspondent à la rentrée scolaire.
# Champ : France (hors Mayotte), enseignement public et privé, y c. scolarisation en apprentissage.
# Source : Depp. 2013

reference_etudes = pd.read_csv("data/demographie/etudes.csv")

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
# Selon une étude INSEE (2016) -> 23%/
# http://www.insee.fr/fr/themes/document.asp?reg_id=0&ref_id=ip1603#inter6

#### Handicap

reference_handicap = pd.read_csv("data/demographie/handicap_pop.csv")

reference_handicap['homme'] *= reference_handicap.iloc[4,1]/100
reference_handicap['femme'] *= reference_handicap.iloc[4,2]/100
reference_handicap['femme']


reference_handicap = reference_handicap.drop(reference_handicap.index[4])
                             

# Ajout jeune handicap
#Table issue du mode de scolarisation -> création artificielle de la catégorie sexe

reference_handicap_jeune = pd.read_csv("data/demographie/handicap_pop_jeune.csv")

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
##

effectifs_age_sexe = get_classes_age(effectifs_age_sexe,
                                     'age',
                                     classes_age_handicap)


##### reference_handicap : création de la colonne proba_handicap
reference_handicap = ajout_effectif_reference(reference_handicap,
                                              effectifs_age_sexe,
                                              'effectif_ref',
                                              ['sexe', 'classe_age_handicap'])
                                       
reference_handicap['proba_handicap'] = reference_handicap['effectif']/reference_handicap['effectif_ref']
reference_handicap['proba_handicap_actif'] = reference_handicap['proba_handicap']* 2/3

population = get_classes_age(population, 'age', classes_age_handicap)


population_handicap = population.copy()
population_handicap = population_handicap.merge(reference_handicap, on=['classe_age_handicap', 'sexe'], how='outer')
population_handicap['proba_handicap'].fillna(0, inplace=True)
population['handicap'] = np.random.binomial(1, population_handicap['proba_handicap'])
population.loc[population['activite']== True]
population['handicap'] = population['handicap'].astype(bool)

# Ajout des effectifs des non actifs
reference_handicap = from_unique_value_reference_to_standard_reference(
    reference_handicap,
    'handicap')
#### Vérifier que le tirage se rapproche de la réalité
test_handicap = distance_to_reference(population, reference_handicap, sample_size,
                     ['sexe', 'classe_age_handicap', 'handicap'],
                     nb_modalite=2)
print ("Test effectifs simulés pour activité :")
print(test_handicap['ratio'].describe())

del population['classe_age_handicap']  

# Comparaison avec chiffre sur activite des handicapés

population_handicapee = population[(population['handicap'] == True) & (population['age'] > 14) & (population['age'] < 65)]
proportion_handicap_emploi = (len(population_handicapee[population_handicapee['emploi'] == True])/ len(population_handicapee)) * 100
proportion_handicap_activite = (len(population_handicapee[population_handicapee['activite'] == True])/ len(population_handicapee)) * 100

print( " Pourcentage d'handicapés en emploi", proportion_handicap_emploi) 
print( " Pourcentage d'handicapés en activite", proportion_handicap_activite) 

#### Statut marital

# Variable catégorielle
# Célibataire = '0'', 
# Marié.e = '1',
# Veuf.ve = '2'
# Divorcé.e = '3'

reference_marital = dict()
for sexe in ['homme', 'femme']:
    reference_marital[sexe] = pd.read_csv("data/menages/statut_marital_{0}.csv".format(sexe))
    reference_marital[sexe][['celib', 'marrie', 'veuf', 'divorce']] = reference_marital[sexe][['celib', 'marrie', 'veuf', 'divorce']].div(reference_marital[sexe]['total'], axis=0)
    del reference_marital[sexe]['total']
    
reference_marital = pd.concat([pd.DataFrame(reference_marital['femme']), pd.DataFrame(reference_marital['homme'])], keys=['femme', 'homme'])

reference_marital.index.names = ['sexe', 'index']
reference_marital = reference_marital.reset_index(level=['sexe'])


population_marital = population.copy()
population_marital = population_marital.merge(reference_marital, on= ['sexe', 'age'] )

population['statut_marital'] = ''
for row in population_marital.index:
    population.loc[row,'statut_marital'] = np.random.choice(4, 1, p=pd.to_numeric(population_marital.loc[row, 'celib':'divorce']))

population['statut_marital'] = population['statut_marital'].astype(int)

population['statut_marital']

print("Proportion générée des statuts maritaux :")
print(population[population['age'] >=15].statut_marital.value_counts(normalize=True, sort=False))



# Beaucoup trop d'handicapés actifs 
  
#### RSA
#reference_rsa = pd.read_csv("data/prestations/rsa_age_2015.csv")
#
#reference_rsa = reference_rsa[reference_rsa['Composante'] == 'Socle seul']
#
#del reference_rsa['Composante']
#
#classes_age_rsa = reference_rsa['classe_age_rsa'].str.replace('De | ans', '', case=False)
#classes_age_rsa = classes_age_rsa.str.replace(' à ', '-')
#classes_age_rsa = classes_age_rsa.str.replace('moins ', '18-')
#classes_age_rsa = classes_age_rsa.str.replace(' ou plus', '-' + str(max_age))
#reference_rsa['classe_age_rsa'] = classes_age_rsa
#
## Affiner avec l'identité sexuelle
## récupérer une proportion grossiere de la répartition des allocataires entre femme et homme
#
#reference_sexe_rsa = pd.read_csv("data/prestations/rsa_sexe_2015.csv")
#reference_sexe_rsa = reference_sexe_rsa[reference_sexe_rsa['Composante'] == 'Socle seul']
#
#nbr_femme_rsa = int(reference_sexe_rsa.loc[reference_sexe_rsa['Type_Famille_RSA'] == 'Femme seule sans enfant', 'effectif'])
#nbr_homme_rsa = int(reference_sexe_rsa.loc[reference_sexe_rsa['Type_Famille_RSA'] == 'Homme seul sans enfant', 'effectif'])
#
#proportion_femme_rsa = nbr_femme_rsa / (nbr_femme_rsa + nbr_homme_rsa)
#
#reference_rsa['femme'] = reference_rsa['effectif']*proportion_femme_rsa
#reference_rsa['homme'] = reference_rsa['effectif']*(1 - proportion_femme_rsa)
#del reference_rsa['effectif']
#
#reference_rsa = pd.melt(reference_rsa, id_vars=['classe_age_rsa'],
#                             value_vars=['femme', 'homme'], var_name = 'sexe',
#                             value_name='effectif')
#reference_rsa['handicap'] = np.bool(False)
#
#population = get_classes_age(population,
#                                     'age',
#                                     classes_age_rsa)
#
#population['pop_active'] = population['activite']
#
#reference_rsa = ajout_effectif_reference(reference_rsa,
#                                         population[population['activite'] ==  False],
#                                         'pop_active',
#                                       ['sexe', 'classe_age_rsa'])
#del population['pop_active']
#
#reference_rsa['proba_rsa'] = reference_rsa['effectif']/reference_rsa['effectif_ref']
#
#tab_ref =  population[population['activite'] ==  False]
#groupby = ['sexe', 'classe_age_rsa']
#col_ref = 'pop_active'
#reference = tab_ref.groupby(groupby)[col_ref].size()
#
#reference = reference.reset_index()
#output = tab_init.merge(reference, on=groupby, how='left')
####Heures travaillées
#reference_heures_travaillees = pd.read_csv("data/travail/nbr_heure_travaillees.csv")
#reference_heures_travaillees = pd.melt(reference_emploi, id_vars=['classe_age_salaire'],
#                             value_vars=['femme', 'homme'], var_name = 'sexe',
#                             value_name='total_heures')
#
#
#
#### Obtention du nbr d'individu en emploi
#duree_travail_legal_an = 1607 # référence légale du nbr d'heures par an pour un tps plein
#reference_heures_travaillees['effectif'] = reference_heures_travaillees['total_heures'] / duree_travail_legal_an
#reference_heures_travaillees['emploi_ech'] = reference_heures_travaillees['effectif'] * (sample_size / nbr_population_totale)
#
#population['pop_active'] = population['activite']
#reference_emploi = ajout_effectif_reference(reference_emploi,
#                                                       population[population['activite'] ==  True],
#                                                       'pop_active',
#                                                       ['sexe', 'classe_age_salaire'])
#del population['pop_active']
#
#### Calcul de la proba conditionnelle d'être en emploi quand en activité (!)
#reference_emploi['proba_emploi_cond_activite'] = reference_emploi['emploi_ech'] / reference_emploi['pop_active']
#reference_emploi['activite'] = np.bool(True)
#
##### Construcion de la table standard
#effectifs_age_sexe = get_classes_age(effectifs_age_sexe,
#                                     'age',
#                                     classes_age_salaire)
#reference_heures_travaillees = ajout_effectif_reference(reference_emploi,
#                                              effectifs_age_sexe,
#                                              'effectif_ref',
#                                              ['sexe', 'classe_age_salaire'])
#reference_heures_travaillees = from_unique_value_reference_to_standard_reference(
#    reference_heures_travaillees,
#    'emploi')
#
#test_heures_travaillees = distance_to_reference(population, reference_heures-travaillees, sample_size,
#                     ['sexe', 'classe_age_salaire', 'emploi'],
#                     nb_modalite=2)
#print ("Test effectifs simulés pour heures :")
#print(test_heures_travaillees['ratio'].describe())























