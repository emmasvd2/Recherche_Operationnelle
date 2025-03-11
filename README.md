# Projet de Coloration de Graphes

## Description du Projet
Ce projet a pour but d'implémenter des algorithmes de **coloration de graphes**, en utilisant des approches heuristiques et exactes. L'objectif est de minimiser le nombre de couleurs utilisées pour colorer un graphe donné, tout en respectant les contraintes de non-adjacence.

## Objectifs
- **Comprendre et implémenter** les concepts de la coloration de graphes.
- **Développer et comparer** plusieurs algorithmes de coloration.
- **Tester et analyser** la performance des algorithmes sur divers graphes.
- **Visualiser les graphes colorés** grâce à Graphviz.

## Structure du Projet
**Fichiers de graphes utilisés**
- `anna.col`
- `myciel3.col` 
- `myciel5.col`
- `myciel7.col` 
- `queen9_9.col`
- `color.unknown` 
- `graphe6.py` : Implémentation des algorithmes 
- `README.md` : Documentation principale 


## Algorithmes Implémentés
 1️. **Welsh-Powell**
- Trie les sommets par degré décroissant.
- Affecte une couleur valide au sommet non coloré ayant le degré maximal.
- Répète jusqu'à ce que tous les sommets soient colorés.

**Avantages** : rapide, simple à implémenter.  
**Inconvénients** : Ne trouve pas toujours une solution optimale.

2️. **Hill-Climbing Amélioré**
- Initialise une coloration aléatoire.
- Modifie itérativement les couleurs pour réduire les conflits.
- Utilise un critère d'arrêt basé sur le nombre d'itérations et le temps.

**Avantages** : peut trouver des solutions optimisées.  
**Inconvénients** : peut rester bloqué dans un optimum local.

## Instructions d'Installation
1. **Cloner le projet**  
   ```bash
   git clone https://github.com/emmasvd2/Recherche_Operationnelle.git
   cd Recherche_Operationnelle
   ```
2. **Lancer le projet**
3. ```bash
   python graphe6.py
   ```
   
**Résultats Expérimentaux**
| Graphe       | Welsh-Powell (couleurs) | Hill-Climbing (couleurs) | Temps WP (s) | Temps HC (s) |
|-------------|-----------------------|----------------------|------------|------------|
| myciel3.col  | 6                     | 5                    | 0.0        | 0.001      |
| myciel5.col  | 6                     | 19                   | 0.01       | 0.06       |
| anna.col     | 11                    | 60                   | 0.043      | 1.38       |
| queen9_9.col | 15                    | 33                   | 0.092      | 1.22       |


- Welsh-Powell est plus rapide mais utilise parfois plus de couleurs.
- Hill-Climbing peut réduire le nombre de couleurs, mais est plus lent.

**Fonctionnalités**
- Charger un graphe depuis un fichier DIMACS.
- Créer un graphe interactivement.
- Sauvegarder une coloration dans un fichier.
- Visualiser un graphe coloré en PNG.
- Comparer les performances des algorithmes.


**Auteurs**
- Emma Stievenard
- Chahinez Mezouar
