
# coding: utf-8



import random
import numpy as np
import pandas as pd

from numpy.testing import assert_almost_equal
# ### Génération Table Population
from generation import generate_population



sample_size = 10000

# ### Sexe et Age
#
# Issu de données INSEE 2016

# À noter : âge = 100 correspond à 100 et plus
effectifs_age_sexe = pd.read_csv("data/demographie/pop_age_sexe_2016.csv")
del effectifs_age_sexe['total']

effectif = effectifs_age_sexe.set_index('age_revolu').unstack()
effectif.index.names = ['sexe', 'age']
marges = effectif/effectif.sum()

population = generate_population(marges, sample_size)


#### test de la probabilité

## génère un dataframe avec les marges de la population générées
effectifs_generes = pd.DataFrame(population.groupby(['sexe', 'age']).size()).reset_index()
effectifs_generes.rename(columns={0: 'valeur'}, inplace=True)
effectifs_generes['marges_generees'] = effectifs_generes['valeur']/effectifs_generes['valeur'].sum()

ratio_des_marges = effectifs_generes.merge(pd.DataFrame(marges).reset_index())
ratio_des_marges.rename(columns={0: 'marges_ref'}, inplace=True)

xx

ratio = ratio_des_marges['marges_generees']/ratio_des_marges['marges_ref']
ratio.describe()


######### Activité

### reference_activite: lecture de la table de référence
reference_activite = pd.read_csv("data/demographie/activite.csv")
reference_activite = pd.melt(reference_activite, id_vars=['pop_active'],
                             value_vars=['femme', 'homme'], var_name = 'sexe',
                             value_name='activite')

reference_activite['activite'] *= 1000
effectif_population_active = sum(reference_activite['activite'])
print("Effectif de la population active", effectif_population_active)


##### reference_activite : création colonne age_inf et age_sup
classe_ages = reference_activite['pop_active'].str.replace(' ans', '')
max_age = reference_sexe.age.max()
classe_ages = classe_ages.str.replace(' ou plus', '-' + str(max_age))
reference_activite['age_inf'] = classe_ages.str.split('-').str[0].astype(int)
reference_activite['age_sup'] = classe_ages.str.split('-').str[1].astype(int)




##### reference_activite : création de la colonne proba_activite

reference_activite['proba_activite'] = ''

def proba(tab_output, tab_ref, column_output, column_input, sexe, age_inf, age_sup):
    '''
    Crée la probabilité d'un évènement (ex: être actif)
    Entrée : nombre d'occurences de cet événèment par catégorie ('tab_output')
    Opération : soustraire cette somme par le total de la population correspondante
    -> avoir une table de référence ('tab_ref')

    Définition des catégories : cond_ref et cond_output
    '''
    cond_ref = (tab_ref['age'] >= age_inf) & (tab_ref['age'] <= age_sup)
    cond_output = (tab_output.age_inf == age_inf) & (tab_output.sexe == sexe)
    tab_output[column_output][cond_output] = tab_output[column_input]/ int(sum(tab_ref[sexe][cond_ref]))
    return tab_output


def de_effectif_a_ratio(tab1, tab2):


    return output

effectif_classe_age
de_effectif_a_ratio(effectif_classe_age, reference_activite[['pop_active','classe_age','sexe']])


for idx, row in reference_activite.iterrows():
    proba(reference_activite, effectifs_age_sexe, 'proba_activite', 'activite', 'femme', int(row['age_inf']), int(row['age_sup']) )
    proba(reference_activite, reference_sexe, 'proba_activite', 'activite', 'homme', int(row['age_inf']), int(row['age_sup']) )

reference_activite['proba_activite'] = pd.to_numeric(reference_activite['proba_activite'])


# TODO: faire des asserts

population_activite = population.copy()


population_activite['pop_active'] =''
def get_classe_age(tab, colname, name, age_inf, age_sup):
    cond = (tab['age'] >= age_inf) & (tab['age'] <= age_sup)
    tab[colname][cond] = name


for idx, row in reference_activite.iterrows():
    get_classe_age(population_activite, 'pop_active', row['pop_active'], int(row['age_inf']), int(row['age_sup']))


population_activite = population_activite.merge(reference_activite, how='left')

population['activite'] = ''
population['activite'] = np.random.binomial(1, population_activite['proba_activite'])

xx


#reference_activite['variable'] = reference_activite[['pop_active', 'sexe']].apply(lambda x: ''.join(x), axis=1)
#est-ce nécssaire de joindre les deux colonnes ? -> je pense pas

assert (sum(reference_activite.activite[:8])) == effectif_population_active, "Vérifier que la somme est bien égale à l'effectif de la population active"
reference_activite


##pour les femmes, force brute
#reference_activite.loc[0, 'proportion_echantillon'] = len(population[(population['age'] >= 15) & (population['age'] < 24) & (population['sexe'] ==0)])
#reference_activite.loc[1, 'proportion_echantillon'] = len(population[(population['age'] >= 24) & (population['age'] < 49) & (population['sexe'] ==0)])
#reference_activite.loc[2, 'proportion_echantillon'] = len(population[(population['age'] >= 50) & (population['age'] < 64) & (population['sexe'] ==0)])
#reference_activite.loc[3, 'proportion_echantillon'] = len(population[population['age'] >= 65 & (population['sexe'] ==0)])
##pour les hommes, force brute
#reference_activite.loc[4, 'proportion_echantillon'] = len(population[(population['age'] >= 15) & (population['age'] < 24) & (population['sexe'] ==1)])
#reference_activite.loc[5, 'proportion_echantillon'] = len(population[(population['age'] >= 24) & (population['age'] < 49) & (population['sexe'] ==1)])
#reference_activite.loc[6, 'proportion_echantillon'] = len(population[(population['age'] >= 50) & (population['age'] < 64) & (population['sexe'] ==1)])
#reference_activite.loc[7, 'proportion_echantillon'] = len(population[population['age'] >= 65 & (population['sexe'] ==1)])


reference_activite['proportion_echantillon'] = reference_activite['proportion_echantillon'].astype(int)
reference_activite


# In[57]:

#pour les femmes, force brute
reference_activite.loc[0, 'pop_totale'] = sum(reference_sexe[(reference_sexe['age'] >= 15) & (reference_sexe['age'] < 24)].femme)
reference_activite.loc[1, 'pop_totale'] = sum(reference_sexe[(reference_sexe['age'] >= 24) & (reference_sexe['age'] < 49)].femme)
reference_activite.loc[2, 'pop_totale'] = sum(reference_sexe[(reference_sexe['age'] >= 50) & (reference_sexe['age'] < 64)].femme)
reference_activite.loc[3, 'pop_totale'] = sum(reference_sexe[reference_sexe['age'] >= 65].femme)
#pour les hommes, force brute
reference_activite.loc[4, 'pop_totale'] = sum(reference_sexe[(reference_sexe['age'] >= 15) & (reference_sexe['age'] < 24)].homme)
reference_activite.loc[5, 'pop_totale'] = sum(reference_sexe[(reference_sexe['age'] >= 24) & (reference_sexe['age'] < 49)].homme)
reference_activite.loc[6, 'pop_totale'] = sum(reference_sexe[(reference_sexe['age'] >= 50) & (reference_sexe['age'] < 64)].homme)
reference_activite.loc[7, 'pop_totale'] = sum(reference_sexe[reference_sexe['age'] >= 65].homme)

reference_activite["proba_activite"] = reference_activite["activite"] / reference_activite["pop_totale"]
reference_activite["proba_inactivite"] = 1 - reference_activite["proba_activite"]


reference_activite


# In[18]:

#Génération population inactive jeune
population.loc[population['age'] < 15, "activite"] = 0
population.head(n=10)

list(population.groupby(['sexe','age']))


# In[63]:

#génération femme 15-24
indic_activite = np.arange(2)
population.loc[(population['sexe']==0) & (population['age'] >= 15) & (population['age'] < 24), 'activite'] = np.random.choice(indic_activite, reference_activite.loc[0, 'proportion_echantillon'], list(reference_activite[['proba_activite','proba_inactivite']].loc[0]))
population.loc[(population['sexe']==0) & (population['age'] >= 25) & (population['age'] < 49), 'activite'] = np.random.choice(indic_activite, reference_activite.loc[1, 'proportion_echantillon'], list(reference_activite[['proba_activite','proba_inactivite']].loc[1]))
population.loc[(population['sexe']==0) & (population['age'] >= 50) & (population['age'] < 64), 'activite'] = np.random.choice(indic_activite, reference_activite.loc[2, 'proportion_echantillon'], list(reference_activite[['proba_activite','proba_inactivite']].loc[2]))
population.loc[(population['sexe']==0) & (population['age'] >= 65), 'activite'] = np.random.choice(indic_activite, reference_activite.loc[3, 'proportion_echantillon'], list(reference_activite[['proba_activite','proba_inactivite']].loc[3]))


# In[ ]:

activite_somme = {name: sum(reference_activite[name]) for name in reference_activite.columns}
activite_somme


# In[ ]:

liste_variable = ["femme", "homme"]
for variable in liste_variable:
    reference_activite["proba_{0}".format(variable)] = reference_activite[variable]/reference_activite['total']

assert sum(reference_activite.proba_femme+reference_activite.proba_homme) == 4, "Ce sont des probabilités"
# à préciser car forme proba pas explicite
reference_activite


# In[ ]:

#Génération population inactive jeune
population.loc[population['age'] < 15, "activite"] = 0
population[population.age < 15].activite
#Population inactive > 65
population.loc[(population['age']>15) & (population['age'] < 24) & (population['sexe'] == 0), 'activite'] = 1


# In[ ]:




# In[68]:

nbr_population_active = int(sum(reference_activite["total"]/effectif_population)*sample_size)
nbr_population_active


# In[ ]:

nbr_population_active = int(sum(reference_activite["total"]/effectif_population)*sample_size)
print("Effectif populaction active dans notre échantillon ", nbr_population_active)
nbr_population_inactive = sample_size - nbr_population_active
print("Effectif populaction inactive dans notre échantillon ", nbr_population_inactive)

#Calcul de la proportion de femmes et d'hommes actifs par âge
liste_variable = ["femme", "homme"]
for variable in liste_variable:
    reference_activite["proba_{0}".format(variable)] = reference_activite[variable]/sum(reference_activite[variable])

assert sum(reference_activite.proba_femme) == 1, "Nous voulons une probabilité"
assert sum(reference_activite.proba_homme) == 1, "Nous voulons une probabilité"

reference_activite.head()


# In[ ]:

reference_activite.T.head()


# In[ ]:




# In[ ]:

population.loc[(population['sexe'] == 0) & (population['age'] > 65), 'activite']


# In[ ]:

population.loc[population['sexe'] == 0 , name] = np.random.choice(ages, nbr_femme, p=table_de_reference.proba_femme)
population.loc[population['sexe'] == 1, name] = np.random.choice(ages, nbr_homme, p=table_de_reference.proba_homme)


# In[ ]:

population.loc[(population['sexe'] == 0) & (population['age'] > 15), 'activite'] = np.random.choice(nb.arange(2), nbr_femme, p=table_de_reference.proba_femme)


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:

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

