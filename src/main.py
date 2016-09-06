# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 19:39:23 2016

@author: aeidelman

Premier exemple de génération de population,
il sert plus de plan pour la suite qu'autre chose

"""

import numpy as np
from pandas import DataFrame

class Generator(object):
    
    def __init__(self, size):
        assert isinstance(size, int)
        self.size = size
        self.population = DataFrame(index=range(size))

       
    def generate_independant_labelled_columns(self,
                                              modalites,
                                              proba):
        ''' genere une variable 
            - modalité: liste des modalités
            - probabilité: liste des proba associés
        '''
        assert isinstance(modalites, list)
        assert isinstance(proba,  list)
        assert sum(proba) == 1
        return np.random.choice(modalites,
                                self.size,
                                p=proba)
                                
if __name__ == '__main__':
    size_test = 1000
    test = Generator(size_test)
    genre = test.generate_independant_labelled_columns(['homme', 'femme'],
                                                       [0.48,0.52])