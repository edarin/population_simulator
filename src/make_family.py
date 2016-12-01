# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 15:04:32 2016

@author: edarin
"""

import pandas as pd

reference_famille = pd.read_csv("data/menages/enfants/type_famille.csv", index_col='type_famille')
reference_famille['effectif'] *= 1000
reference_famille.loc['Couples', 'effectif'] *=2

reference_famille['proba'] = reference_famille['effectif']/reference_famille['effectif_ref']

reference_famille = reference_famille.drop(['Total'])

population_menage[population_menage['statut_marital'] == 1].loc[::2]