# How it works

## What is the idea ?

We've decided to generate a population in an iterative manner. 
We construct the database by adding each variable separetely based on its joint distribution over prior created variables.

*Example*:
  - First step : generating a population of 1000 `persons`, ie 1000 rows.     
  - Second step: attributing a `sexe` to each person, given the proportion of women and men in the real French population    
  - Third step : put an `age` to each person,  given the joint distribution of age and sexe in France
And so on   

## Implementation

### Which variables ?
We have now generated these variables in our population:
   - `sexe`
   - `age`
   - `marital_situation`
   - `spouse`
   - `pension`
   - `income`
   - `student` (beta)
   - `diasabled` (beta)  
 
And we've also created the possibilty of grouping persons in family, respecting the French family structure.

If you want to add another variable, just fork this repo and find data on its conditionnal distribution in the French population !

### Where do they come from ?

Ther reference databases are of two kinds.

Most of the variables comes from aggregated data from the **French Statistics Institute** website that we desaggregated at indivduals and families level. The main point was then to get the joint distribution and affecting each attributes  while keeping the overall statistically accurate distribution.

Because these data are in open access -and copied in this repo - all code dedicated to these variables can be reproduced.

One variable - the **income** - comes from a database under statistic and tax secrecy : the [ERFS](https://www.insee.fr/en/metadonnees/source/s1069). In order to be as accurate as possible we've decided to ask access to this database and draw the wage distribution from it. Our process : first filtering on relevant variable - for now `sexe` and `age` - and then using a Kernel Density Estimation to reproduce the distrbution. But even if the work on the data base is available in the [`wage_simulation_from_erfs-fpr.ipynb`](wage_simulation_from_erfs-fpr.ipynb) it can't be reused unless one have the access right to the ERFS.

Besides the usual way to add a variable has been also implemented for the income.

To have an overview of the reference databases used, please see the [`https://github.com/edarin/population_simulator/blob/master/src/data/DescriptionTablesReference.ipynb`](data/DescriptionTablesReference.ipynb)

### How to validate the result ?

We've created two metrics to see the discrepancy between the simulated distribution and the real one, to find in the `distance_to_reference` function in the [`tools.py`](tools.py).

One is the **ratio **and its relative mean and standard error between the theoretical distribution and the one we obtained.

The other in the **Mean Squared Prediction Error** (MSE).

### How to launch the script

The only parameter to fix is the population size you target, in the `main.py`.

Launch this script and watch the magic !
