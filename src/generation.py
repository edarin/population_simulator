# -*- coding: utf-8 -*-
"""

S'occupe de générer une population à partir d'inputs
de description de la population

- L'input (marges dans les programmes) est une 
Series de la librairie pandas. 

Son index reprend les colonnes qui seront imputées

"""
from numpy.testing import assert_almost_equal
from pandas import Series, DataFrame


def complete_input(incomplete_marges):
    # est-ce utile ? 
    complete_marges = incomplete_marges
    return complete_marges
    

def check_input_format(marges):
    ''' réalise des tests sur le format utilisé pour la
        génération de la table
    '''
    assert isinstance(marges, Series)
    assert all(0 <= marges)
    assert all(marges <= 1)
    assert_almost_equal(marges.sum(), 1)
    return True



def generate_population(marges, size):
    ''' 
        retourne une population ayant les caractèristiques
        marquées dans l'objet marges.
        - marges
        - size est la taille en nombre de ligne de la 
            population génrée.
        Note importante : 
            La taille obtenue n'est pas exactement size.
            On part du principe que la taille est là pour 
            controler à peu près le temps de calcul mais 
            la taille exacte n'est pas très importante
    '''
    check_input_format(marges)
    size_group = marges*size
    size_group = size_group.round().astype(int)
    def _check_size(vecteur, taille):
        # TODO: should be an option
        return abs(vecteur.sum()/taille - 1) < 0.05
    
    def resize(marges, size):
        # TODO: faire un appel recursif ?
        # TODO: ça doit se trouver sur internet
        pass
    

    if not _check_size(size_group, size):
        resize(marges, size)
    
    nb_to_generate = size_group[size_group > 0]
#    population_values = nb_to_generate.values.repeat(nb_to_generate).index
    population = nb_to_generate.repeat(nb_to_generate)
    population = population.reset_index().iloc[:,:-1]
    return population


if __name__ == '__main__':
    import pandas as pd
    reference = pd.read_csv("data/demographie/pop_age_sexe_2016.csv")
    del reference['total']
    marges = reference.set_index('age_revolu').unstack()
    marges.index.names = ['sexe', 'age']
    marges /= marges.sum()
    generate_population(marges, 1000)