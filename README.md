# population_simulator

Nous voulons construire une base de données représentative de la
population française en utilisant des variables globales sur elle mais
sans utiliser d'échantillon d'enquête ou autre.

Cette démarche permettra à chacun d'utiliser la base et de l'enrichir sans
pour autant avoir accès à des données personnelles ou couvertes par un
secret légal.

Nous fairons le plus possible en sorte que le code soit réutilisable
pour simuler des populations d'autres pays ou d'autres types (entreprises,
clients, etc.) mais dans le premier temps du développement, nous travaillerons
 en visant à reproduire la population française.


# Contenu du package

## Calage

Usuellement, on cherche à produire des statistiques à partir d'un
échantillon représentatif de la population. Pour que l'échantillon corresponde
au mieux à la population, on recale les pondérations.

Une première idée est de simuler assez grossièrement un éventail de situation
et par simple jeu de calage arriver assez proche de la population

## Génération

On peut aussi tester une approche très différente. Comme l'on a dès le
début toutes les informations nécessaires et que nous n'en avons pas d'autres
contenues dans un échantillon, on peut essayer de générer tout de suite
des individus ayant des caractéristiques tirées dans des distributions
statistiques cohérentes.

## Distance aux caractéristiques connues

Quelle que soit la méthode retenue, nous avons besoin de savoir si l'échantillon
réel ou généré est compatible avec les distributions que nous connaissons.


# Vision

Si l'on considère que la population ne respecte pas telle ou telle
caractéristique, il faut normalement simplement ajouter cette caractéristique
dans la liste des choses à respecter lors de la génération.
Grâce à ce procédé itératif, nous aurons normalement une base de plus en plus
proche de la base réelle.

# Installation

    git clone https://github.com/edarin/population_simulator.git
puis
    pip install --editable .
