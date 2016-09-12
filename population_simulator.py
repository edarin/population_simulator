# -*- coding: UTF-8 -*-

"""
    Simulate a population of N inhabitants from the statistics on the tax declaration.

    Statistiques utilisé pour la période 2014
"""

import random


# STATISTICS

# Possible situations:
POSSIBLE_SITUATIONS = [('M', 12002841), ('D', 5510809), ('O', 983754), ('C', 14934477), ('V', 3997578)]

# Statistiques by familly, approximated to match the declaration d'impots
CHILDREN_PER_FAMILY = [(1, 46), (2, 38.5), (3, 12.5), (4, 2), (5, 1)]

# Familles avec enfants a charge de moins de 18 ans
FAMILLES = 9321480

# Declarations:
TOTAL_DECLARATIONS = float(sum(w for c, w in POSSIBLE_SITUATIONS))

REVENUS = [21820704, 503723963299]
REVENUS_AVG = REVENUS[1] / float(REVENUS[0])
PERCENT_REVENUS_NOT_0 = REVENUS[0] / float(TOTAL_DECLARATIONS)

def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w >= r:
         return c
      upto += w
   assert False, "Shouldn't get here"

def generate_random_cerfa():
    cerfa = {}

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
    print repr(th)
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
        print 'Total target ' + str(sim_tot_value/total_value) + ' not 0 target: ' + str(sim_not_0/number_not_0) + ' mu=' +  repr(mu) + ' sigma=' + repr(sigma) + ' th=' + str(th)
        mu_step = mu_step * 0.995
        sigma_step = sigma_step * 0.995
        percentage_repr = percentage_repr * 1.01


find_gaussian_parameters(21820704, 503723963299, distribution_percentage_null=5)
