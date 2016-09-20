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
test_pop = distance_to_reference(population, effectifs_age_sexe, sample_size, ['age','sexe'])
print(test_pop['ratio'].describe())

######### Activité

### reference_activite: lecture de la table de référence
reference_activite = pd.read_csv("data/demographie/activite.csv")
reference_activite = pd.melt(reference_activite, id_vars=['classe_age'],
                             value_vars=['femme', 'homme'], var_name = 'sexe',
                             value_name='effectif')

reference_activite['effectif'] *= 1000


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
ratio = distance_to_reference(population[population['activite'] == 1], reference_activite, sample_size, ['sexe', 'classe_age', 'activite'])
ratio = distance_to_reference(population, reference_activite, sample_size,
                     ['sexe', 'classe_age', 'activite'],
                     nb_modalite=2)

print(ratio['ratio'].describe())

### Salaire

#revenus = [21820704, 503723963299] # (nbr de déclarant en case 1aj, montant total de cette case) -> 2014
#revenus_moy = revenus[1] / float(revenus[0])
#pourcent= REVENUS[0] / float(nbr_foyer)
#
#
## In[ ]:
#
#def generate_random_cerfa():
#    cerfa = {}
#
#    if random.random() < PERCENT_REVENUS_NOT_0 * 1.3:
#        cerfa['1AJ'] = max(random.gauss(14000, 23500), 0)
#    else:
#        cerfa['1AJ'] = 0
#    return cerfa
#
#def gradiant(a, b):
#    if a > b:
#        return min((a / b - 1) * random.random(), 0.5)
#    else:
#        return min((b / a - 1) * random.random(), 0.5)
#
#
#def find_gaussian_parameters(number_not_0, total_value, distribution_percentage_null=5):
#    def simulate_population(th, mu, sigma, percentage_repr):
#        total_result = 0
#        number_not_null = 0
#        for i in range(0, int(TOTAL_DECLARATIONS * percentage_repr)):
#            result = simulate_one_gaussian(th, mu, sigma)
#            total_result += result
#            if result > 0:
#                number_not_null += 1
#        return number_not_null / percentage_repr, total_result / percentage_repr
#
#    def simulate_one_gaussian(th, mu, sigma):
#        if random.random() < th:
#            return max(random.gauss(mu, sigma), 0)
#        return 0
#
#    # Between 0 and 1
#    number_not_0 = float(number_not_0)
#    total_value = float(total_value)
#
#    percentage_repr = 0.001
#    mu = total_value / number_not_0
#    sigma = mu / 2
#    mu_step = mu / 2
#    sigma_step = sigma / 2
#    th = (1 + distribution_percentage_null / 100.0) * number_not_0 / TOTAL_DECLARATIONS
#    print(repr(th))
#    max_number_of_simulations = 100
#    for i in range(0, max_number_of_simulations):
#        sim_not_0, sim_tot_value = simulate_population(th, mu, sigma, percentage_repr)
#        if sim_not_0 > number_not_0:
#            mu -= mu_step * gradiant(number_not_0, sim_not_0)
#            # sigma -= sigma_step * gradiant(number_not_0, sim_not_0)
#        else:
#            mu += mu_step * gradiant(sim_not_0, number_not_0)
#            # sigma += sigma_step * gradiant(sim_not_0, number_not_0)
#
#        if sim_tot_value > total_value:
#            # mu -= mu_step * gradiant(total_value, sim_tot_value)
#            sigma -= sigma_step * gradiant(total_value, sim_tot_value)
#        else:
#            # mu += mu_step * gradiant(sim_tot_value, total_value )
#            sigma += sigma_step * gradiant(sim_tot_value, total_value)
#        print('Total target ' + str(sim_tot_value/total_value) + ' not 0 target: ' + str(sim_not_0/number_not_0) + ' mu=' +  repr(mu) + ' sigma=' + repr(sigma) + ' th=' + str(th))
#        mu_step = mu_step * 0.995
#        sigma_step = sigma_step * 0.995
#        percentage_repr = percentage_repr * 1.01
#
#
#find_gaussian_parameters(21820704, 503723963299, distribution_percentage_null=5)
#
#
## ### Gestion des situations familiales
## Idée : obtenir le nombre moyen d'enfant = 1.7
#
## In[ ]:
#
## Statistiques by familly, approximated to match the declaration d'impots
## Voir la distribution réelle mais bloquer par nbenf > 4 répartition en 3 plus calage car moyenne au-dessus de la réalité
#CHILDREN_PER_FAMILY = [(1, 46), (2, 38.5), (3, 12.5), (4, 2), (5, 1)]
#TOTAL_CHILDREN = float(sum(w*c for c, w in CHILDREN_PER_FAMILY))
#print('TOTAL_CHILDREN = ', float(sum(w*c for c, w in CHILDREN_PER_FAMILY)))
## Familles avec enfants a charge de moins de 18 ans
#FAMILLES = 9321480
#
#
## In[ ]:
#
#def weighted_choice(choices):
#   total = sum(w for c, w in choices)
#   r = random.uniform(0, total)
#   upto = 0
#   for c, w in choices:
#      if upto + w >= r:
#         return c
#      upto += w
#   assert False, "Shouldn't get here"
#
#
#    # Age is random between 18 and 88
#   cerfa['0DA'] = int(random.random() * 70 + 18)
#
#    # Drawing the situation
#    # situation = weighted_choice(POSSIBLE_SITUATIONS)
#    # cerfa[situation] = 1
#
#    ## We only give children to married or pacces. This is an approximation
#    # enfants = 0
#    # if situation == 'M' or situation == 'O':
#    #     if random.random() < (FAMILLES / float(POSSIBLE_SITUATIONS[0][1] + POSSIBLE_SITUATIONS[2][1])):
#    #         enfants = weighted_choice(CHILDREN_PER_FAMILY)
#    #
#    # if enfants > 0:
#    #     cerfa['F'] = enfants
#
#    # Distribution that has a cool shape and required properties 5500, 26500
#
#
## In[ ]:
#
#situations = [['M', 12002841], ['D', 5510809], ['O', 983754], ['C', 14934477], ['V', 3997578]]
#nbr_foyer = int(sum(w for c, w in situations))
#print("Nombre de déclarations :",nbr_foyer)
#
##to do : pour l'instant références implémentées en dur
#
#pourcent_situations = situations # connaitre la proportion pour distribuer
#for x in pourcent_situations :
#    x[1] = float(x[1])/nbr_foyer
#pourcent_situations
#
#openfisca_entry_variables = ['1AJ', '1AS', '1AP', '1AO'] # à compléter au fur et à mesure
#index = np.arange(nbr_foyer/1000)
#population = pd.DataFrame(columns=openfisca_entry_variables, index = index)
#len(population)
#population.head()

