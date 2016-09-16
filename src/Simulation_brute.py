# coding: utf-8
import random
import numpy as np
import pandas as pd

from numpy.testing import assert_almost_equal
# ### Génération Table Population
from generation import generate_population

sample_size = 10000

##### Sexe et Age
#
# Issu de données INSEE 2016

# À noter : âge = 100 correspond à 100 et plus
effectifs_age_sexe = pd.read_csv("data/demographie/pop_age_sexe_2016.csv")
del effectifs_age_sexe['total']

effectifs_age_sexe = pd.melt(effectifs_age_sexe, id_vars=['age'],
                             value_vars=['femme', 'homme'], var_name ='sexe',
                             value_name='valeur')   
nbr_population_totale = effectifs_age_sexe['valeur'].sum()
                             
def get_proba(tab, col):
    div = tab[col]/tab[col].sum()
    return div

marges = get_proba(effectifs_age_sexe.set_index(['sexe', 'age']), 'valeur')                                                       
marges = effectifs_age_sexe.set_index(['sexe', 'age'])['valeur'] / effectifs_age_sexe.set_index(['age', 'sexe'])['valeur'].sum()

population = generate_population(marges, sample_size)

#### test de la probabilité

## génère un dataframe avec les marges de la population générées
effectifs_generes = pd.DataFrame(population.groupby(['sexe', 'age']).size()).reset_index()
effectifs_generes.rename(columns={0: 'valeur'}, inplace=True)
effectifs_generes['marges_generees'] = effectifs_generes['valeur']/effectifs_generes['valeur'].sum()

marges_ref = pd.DataFrame(marges).reset_index() #transforme en df pour le merge
marges_ref.rename(columns={'valeur': 'marges_ref'}, inplace=True)

ratio_des_marges = effectifs_generes.merge(marges_ref)
ratio = ratio_des_marges['marges_generees']/ratio_des_marges['marges_ref']
print(ratio.describe())

######### Activité

### reference_activite: lecture de la table de référence
reference_activite = pd.read_csv("data/demographie/activite.csv")
reference_activite = pd.melt(reference_activite, id_vars=['classe_age'],
                             value_vars=['femme', 'homme'], var_name = 'sexe',
                             value_name='effectif')

reference_activite['effectif'] *= 1000
nbr_population_active = sum(reference_activite['effectif'])
##### reference_activite : création colonne age_inf et age_sup
classe_ages = reference_activite['classe_age'].str.replace(' ans', '')
max_age = effectifs_age_sexe['age'].max()
classe_ages = classe_ages.str.replace(' ou plus', '-' + str(max_age))

def get_classes_age(tab, age_col, classes):
    ''' ajoute une colonne à tab contenant la classe d'age
        faisant référence aux catégories de la serie classes
    '''
    assert isinstance(classe_ages, pd.Series) 
    assert classes.name not in tab.columns
    age = tab[age_col]
    
    tab[classes.name] = ''
    for classe in classes.unique():
        age_inf = int(classe.split('-')[0])
        age_sup = int(classe.split('-')[1])
        cond_classe = (age >= age_inf) & (age <= age_sup)
        tab.loc[cond_classe, classes.name] = classe
    return tab

effectifs_age_sexe = get_classes_age(effectifs_age_sexe,
                                     'age',
                                     classe_ages)

##### reference_activite : création de la colonne proba_activite
reference_activite['effectif_reference'] = ''


def ajout_effectif_reference(tab_output, tab_ref, column_output, sexe, age_inf, age_sup):
    '''
    Ajoute à la table d'intérêt l'effectif de référence 
    '''
    cond_output = (tab_output.age_inf == age_inf) & (tab_output.sexe == sexe)
    tab_output[column_output][cond_output] = int(sum(tab_ref['valeur'][cond_ref]))


def effectif_to_ratio(tab_output, column_output, column_subject, column_ref):
    '''
    Crée la probabilité en divisant l'effectif de la variable d'intérêt par l'effectif total
    '''
    tab_output[column_output] = tab_output[column_subject] / tab_output[column_ref]

xxx
for idx, row in reference_activite.iterrows():
    ajout_effectif_reference(reference_activite, effectifs_age_sexe, 'effectif_reference', 'femme', int(row['age_inf']), int(row['age_sup']))
    ajout_effectif_reference(reference_activite, effectifs_age_sexe, 'effectif_reference', 'homme', int(row['age_inf']), int(row['age_sup']))


reference_activite['proba_activite'] = ''
effectif_to_ratio(reference_activite, 'proba_activite', 'effectif', 'effectif_reference')

# def proba(tab_output, tab_ref, column_output, column_input, sexe, age_inf, age_sup):
#    '''
#    Crée la probabilité d'un évènement (ex: être actif)
#    Entrée : nombre d'occurences de cet événèment par catégorie ('tab_output')
#    Opération : soustraire cette somme par le total de la population correspondante
#    -> avoir une table de référence ('tab_ref')
#
#    Définition des catégories : cond_ref et cond_output
#    '''
#    cond_ref = (tab_ref['age'] >= age_inf) & (tab_ref['age'] <= age_sup) & (tab_ref.sexe == sexe)
#    cond_output = (tab_output.age_inf == age_inf) & (tab_output.sexe == sexe)
#    tab_output[column_output][cond_output] = tab_output[column_input]/ int(sum(tab_ref['valeur'][cond_ref]))
reference_activite['proba_activite'] = pd.to_numeric(reference_activite['proba_activite'])


# TODO: faire des asserts

population['classe_age'] = ''

def get_classe_age(tab, colname, name, age_inf, age_sup):
    '''
    Adjoint une colonne our indiquer la classe d'àge (string)'
    '''
    cond = (tab['age'] >= age_inf) & (tab['age'] <= age_sup)
    tab[colname][cond] = name


for idx, row in reference_activite.iterrows():
    get_classe_age(population, 'classe_age', row['classe_age'], int(row['age_inf']), int(row['age_sup']))

population_activite = population.copy()


population_activite = population_activite.merge(reference_activite, how='left')

population['activite'] = ''
population['activite'] = np.random.binomial(1, population_activite['proba_activite'])

##

ratio_des_effectifs = pd.DataFrame(population[population['activite'] == 1].groupby(['sexe', 'classe_age', 'activite']).size()).reset_index()
ratio_des_effectifs.rename(columns={0: 'effectif_genere'}, inplace=True)

ratio_des_effectifs['effectif_reference'] = round((reference_activite[reference_activite['age_inf'] != 0]['effectif'] * sample_size) / nbr_population_totale).astype(int).reset_index(drop=True)

ratio = ratio_des_effectifs['effectif_genere']/ratio_des_effectifs['effectif_reference']
print(ratio.describe())
xx

## Vérifier que le tirage se rapproche de la réalité




revenus = [21820704, 503723963299] # (nbr de déclarant en case 1aj, montant total de cette case) -> 2014
revenus_moy = revenus[1] / float(revenus[0])
pourcent= REVENUS[0] / float(nbr_foyer)


# In[ ]:

def generate_random_cerfa():
    cerfa = {}

    if random.random() < PERCENT_REVENUS_NOT_0 * 1.3:
        cerfa['1AJ'] = max(random.gauss(14000, 23500), 0)
    else:
        cerfa['1AJ'] = 0
    return cerfa

def gradiant(a, b):
    if a > b:
        return min((a / b - 1) * random.random(), 0.5)
    else:
        return min((b / a - 1) * random.random(), 0.5)


def find_gaussian_parameters(number_not_0, total_value, distribution_percentage_null=5):
    def simulate_population(th, mu, sigma, percentage_repr):
        total_result = 0
        number_not_null = 0
        for i in range(0, int(TOTAL_DECLARATIONS * percentage_repr)):
            result = simulate_one_gaussian(th, mu, sigma)
            total_result += result
            if result > 0:
                number_not_null += 1
        return number_not_null / percentage_repr, total_result / percentage_repr

    def simulate_one_gaussian(th, mu, sigma):
        if random.random() < th:
            return max(random.gauss(mu, sigma), 0)
        return 0

    # Between 0 and 1
    number_not_0 = float(number_not_0)
    total_value = float(total_value)

    percentage_repr = 0.001
    mu = total_value / number_not_0
    sigma = mu / 2
    mu_step = mu / 2
    sigma_step = sigma / 2
    th = (1 + distribution_percentage_null / 100.0) * number_not_0 / TOTAL_DECLARATIONS
    print(repr(th))
    max_number_of_simulations = 100
    for i in range(0, max_number_of_simulations):
        sim_not_0, sim_tot_value = simulate_population(th, mu, sigma, percentage_repr)
        if sim_not_0 > number_not_0:
            mu -= mu_step * gradiant(number_not_0, sim_not_0)
            # sigma -= sigma_step * gradiant(number_not_0, sim_not_0)
        else:
            mu += mu_step * gradiant(sim_not_0, number_not_0)
            # sigma += sigma_step * gradiant(sim_not_0, number_not_0)

        if sim_tot_value > total_value:
            # mu -= mu_step * gradiant(total_value, sim_tot_value)
            sigma -= sigma_step * gradiant(total_value, sim_tot_value)
        else:
            # mu += mu_step * gradiant(sim_tot_value, total_value )
            sigma += sigma_step * gradiant(sim_tot_value, total_value)
        print('Total target ' + str(sim_tot_value/total_value) + ' not 0 target: ' + str(sim_not_0/number_not_0) + ' mu=' +  repr(mu) + ' sigma=' + repr(sigma) + ' th=' + str(th))
        mu_step = mu_step * 0.995
        sigma_step = sigma_step * 0.995
        percentage_repr = percentage_repr * 1.01


find_gaussian_parameters(21820704, 503723963299, distribution_percentage_null=5)


# ### Gestion des situations familiales
# Idée : obtenir le nombre moyen d'enfant = 1.7

# In[ ]:

# Statistiques by familly, approximated to match the declaration d'impots
# Voir la distribution réelle mais bloquer par nbenf > 4 répartition en 3 plus calage car moyenne au-dessus de la réalité
CHILDREN_PER_FAMILY = [(1, 46), (2, 38.5), (3, 12.5), (4, 2), (5, 1)]
TOTAL_CHILDREN = float(sum(w*c for c, w in CHILDREN_PER_FAMILY))
print('TOTAL_CHILDREN = ', float(sum(w*c for c, w in CHILDREN_PER_FAMILY)))
# Familles avec enfants a charge de moins de 18 ans
FAMILLES = 9321480


# In[ ]:

def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w >= r:
         return c
      upto += w
   assert False, "Shouldn't get here"


    # Age is random between 18 and 88
   cerfa['0DA'] = int(random.random() * 70 + 18)

    # Drawing the situation
    # situation = weighted_choice(POSSIBLE_SITUATIONS)
    # cerfa[situation] = 1

    ## We only give children to married or pacces. This is an approximation
    # enfants = 0
    # if situation == 'M' or situation == 'O':
    #     if random.random() < (FAMILLES / float(POSSIBLE_SITUATIONS[0][1] + POSSIBLE_SITUATIONS[2][1])):
    #         enfants = weighted_choice(CHILDREN_PER_FAMILY)
    #
    # if enfants > 0:
    #     cerfa['F'] = enfants

    # Distribution that has a cool shape and required properties 5500, 26500


# In[ ]:

situations = [['M', 12002841], ['D', 5510809], ['O', 983754], ['C', 14934477], ['V', 3997578]]
nbr_foyer = int(sum(w for c, w in situations))
print("Nombre de déclarations :",nbr_foyer)

#to do : pour l'instant références implémentées en dur

pourcent_situations = situations # connaitre la proportion pour distribuer
for x in pourcent_situations :
    x[1] = float(x[1])/nbr_foyer
pourcent_situations

openfisca_entry_variables = ['1AJ', '1AS', '1AP', '1AO'] # à compléter au fur et à mesure
index = np.arange(nbr_foyer/1000)
population = pd.DataFrame(columns=openfisca_entry_variables, index = index)
len(population)
population.head()

