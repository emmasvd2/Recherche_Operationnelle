from graphviz import Graph, Digraph
import random
import copy
import time
from PIL import Image

class GrapheReel:
    def __init__(self, oriente=False):
        self.noeuds = set()
        self.aretes = []
        self.oriente = oriente
        self.coloration_actuelle = None

    def ajouter_noeud(self, identifiant):
        self.noeuds.add(identifiant)

    def ajouter_arete(self, source, destination):
        if source in self.noeuds and destination in self.noeuds:
            self.aretes.append((source, destination))
            if not self.oriente:
                self.aretes.append((destination, source))
            return True
        else:
            print(f"Erreur : les nœuds {source} ou {destination} n'existent pas.")
            return False

    def supprimer_noeud(self, identifiant):
        if identifiant in self.noeuds:
            self.noeuds.remove(identifiant)
            self.aretes = [(s, d) for s, d in self.aretes if s != identifiant and d != identifiant]
            # Mettre à jour la coloration en supprimant le noeud
            if self.coloration_actuelle and identifiant in self.coloration_actuelle:
                del self.coloration_actuelle[identifiant]
            return True
        return False

    def supprimer_arete(self, source, destination):
        if (source, destination) in self.aretes:
            self.aretes.remove((source, destination))
            if not self.oriente and (destination, source) in self.aretes:
                self.aretes.remove((destination, source))
            return True
        return False

    def get_voisins(self, noeud):
        if self.oriente:
            sortants = {dest for src, dest in self.aretes if src == noeud}
            entrants = {src for src, dest in self.aretes if dest == noeud}
            return sortants.union(entrants)
        else:
            return {dest for src, dest in self.aretes if src == noeud}

    def coloration(self):
      """
     Implémentation de l'algorithme de Welsh-Powell pour la coloration de graphe
     Returns:
        tuple: (coloration, stats) avec les statistiques d'exécution
     """
      start_time = time.time()
      iterations = 1  # Welsh-Powell est non itératif
    
     # Liste des couleurs disponibles
      couleurs_base = ["#4287f5", "#42f54b", "#f54242", "#f5f242", "#9942f5", "#f542f2"]
    
      def calcul_conflits(coloration):
        conflits = 0
        for source, dest in self.aretes:
            if coloration.get(source) == coloration.get(dest):
                conflits += 1
        return conflits
    
      # Calcul des degrés pour chaque nœud
      degres = {noeud: len(self.get_voisins(noeud)) for noeud in self.noeuds}
    
     #  Trier les nœuds par degré décroissant
      noeuds_tries = sorted(self.noeuds, key=lambda x: degres[x], reverse=True)
    
     # Initialisation de la coloration
      coloration = {}
      couleur_index = 0
    
     # Calculer les conflits initiaux (tous les nœuds de même couleur)
      coloration_initiale = {noeud: "#FFFFFF" for noeud in self.noeuds}
      conflits_initial = calcul_conflits(coloration_initiale)
    
     # Pour chaque nœud non coloré
      while len(coloration) < len(self.noeuds):
        if couleur_index >= len(couleurs_base):
            nouvelle_couleur = f"#{random.randint(0, 0xFFFFFF):06x}"
            couleurs_base.append(nouvelle_couleur)
        
        couleur_courante = couleurs_base[couleur_index]
        
        for noeud in noeuds_tries:
            if noeud in coloration:
                continue
                
            voisins = self.get_voisins(noeud)
            peut_utiliser_couleur = True
            
            for voisin in voisins:
                if voisin in coloration and coloration[voisin] == couleur_courante:
                    peut_utiliser_couleur = False
                    break
            
            if peut_utiliser_couleur:
                coloration[noeud] = couleur_courante
        
        couleur_index += 1
    
      temps_execution = time.time() - start_time
      conflits_final = calcul_conflits(coloration)
    
      stats = {
        'temps_execution': round(temps_execution, 10),
        'iterations': iterations,
        'conflits_initial': conflits_initial,
        'conflits_final': conflits_final,
        'methode': 'welsh_powell'
        }
    
      self.coloration_actuelle = coloration
      return coloration, stats
    
    def coloration_hill_climbing(self, max_iterations=10000):
     """
     Version améliorée de Hill Climbing pour la coloration de graphe.
     Inclut:
     - Restart aléatoire pour éviter les optimums locaux
     - Sélection intelligente des nœuds à recolorer
     - Adaptation dynamique du nombre de couleurs
     """
     start_time = time.time()

     def calcul_conflits_noeud(noeud, coloration):
        """Calcule le nombre de conflits pour un nœud spécifique"""
        conflits = 0
        voisins = self.get_voisins(noeud)
        for voisin in voisins:
            if coloration[noeud] == coloration[voisin]:
                conflits += 1
        return conflits

     def calcul_conflits_total(coloration):
        """Calcule le nombre total de conflits dans le graphe"""
        return sum(calcul_conflits_noeud(noeud, coloration) for noeud in self.noeuds) // 2

     def get_noeuds_problematiques(coloration):
        """Retourne la liste des nœuds ayant des conflits, triés par nombre de conflits"""
        noeuds_conflits = [(noeud, calcul_conflits_noeud(noeud, coloration)) 
                          for noeud in self.noeuds]
        return [n for n, c in sorted(noeuds_conflits, key=lambda x: x[1], reverse=True) if c > 0]

     # Initialisation avec un nombre minimal de couleurs
     degre_max = max(len(self.get_voisins(noeud)) for noeud in self.noeuds)
     nb_couleurs_initial = degre_max + 1
     couleurs_base = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(nb_couleurs_initial)]
    
     meilleure_coloration = None
     meilleur_score = float('inf')
     nb_restarts = 0
     iterations_sans_amelioration = 0
    
     while nb_restarts < 5 and time.time() - start_time < 60:  # Limite de temps de 60 secondes
        # Initialisation aléatoire
        coloration_actuelle = {noeud: random.choice(couleurs_base) for noeud in self.noeuds}
        conflits_actuels = calcul_conflits_total(coloration_actuelle)
        
        # Phase d'optimisation locale
        iterations_locales = 0
        while iterations_locales < max_iterations and conflits_actuels > 0:
            iterations_locales += 1
            amelioration = False
            
            # Sélection des nœuds problématiques
            noeuds_problematiques = get_noeuds_problematiques(coloration_actuelle)
            if not noeuds_problematiques:
                break
                
            # Tentative d'amélioration pour chaque nœud problématique
            for noeud in noeuds_problematiques:
                meilleure_couleur = None
                meilleur_conflit_local = calcul_conflits_noeud(noeud, coloration_actuelle)
                
                # Test de toutes les couleurs disponibles
                couleur_actuelle = coloration_actuelle[noeud]
                for couleur in couleurs_base:
                    if couleur == couleur_actuelle:
                        continue
                        
                    coloration_actuelle[noeud] = couleur
                    conflits_nouveau = calcul_conflits_noeud(noeud, coloration_actuelle)
                    
                    if conflits_nouveau < meilleur_conflit_local:
                        meilleure_couleur = couleur
                        meilleur_conflit_local = conflits_nouveau
                        amelioration = True
                
                # Application de la meilleure couleur trouvée
                if meilleure_couleur:
                    coloration_actuelle[noeud] = meilleure_couleur
                else:
                    coloration_actuelle[noeud] = couleur_actuelle
            
            # Mise à jour des conflits
            conflits_actuels = calcul_conflits_total(coloration_actuelle)
            
            # Mise à jour de la meilleure solution
            if conflits_actuels < meilleur_score:
                meilleur_score = conflits_actuels
                meilleure_coloration = coloration_actuelle.copy()
                iterations_sans_amelioration = 0
            else:
                iterations_sans_amelioration += 1
            
            # Ajout d'une nouvelle couleur si on est bloqué
            if iterations_sans_amelioration > 1000:
                nouvelle_couleur = f"#{random.randint(0, 0xFFFFFF):06x}"
                couleurs_base.append(nouvelle_couleur)
                iterations_sans_amelioration = 0
        
        nb_restarts += 1

     temps_execution = time.time() - start_time
    
     stats = {
        'temps_execution': round(temps_execution, 10),
        'iterations': iterations_locales,
        'restarts': nb_restarts,
        'conflits_final': meilleur_score,
        'nb_couleurs': len(set(meilleure_coloration.values())) if meilleure_coloration else 0,
        'methode': 'hill_climbing_improved'
     }
    
     if meilleure_coloration and meilleur_score == 0:
        self.coloration_actuelle = meilleure_coloration
        return meilleure_coloration, stats
     else:
        print(f"Échec : Meilleur score atteint = {meilleur_score} conflits")
        return None, stats


    def dessiner(self, fichier_sortie="graphe"):
     """
     Dessine le graphe et sauvegarde en PNG.
     Args:
        fichier_sortie (str): Nom du fichier de sortie (sans extension)
     Returns:
        bool: True si succès, False sinon
     """
     try:
        # Créer le graphe avec le bon moteur
        dot = Digraph() if self.oriente else Graph()
        dot.attr(engine='neato')
        
        # Configuration du rendu
        dot.attr(
            bgcolor='white',  # fond blanc
            size='8,8',      # taille
            dpi='300'        # résolution
        )

        # Style global des nœuds
        dot.attr('node',
            shape='circle',
            style='filled',
            color='black',
            width='0.5',
            height='0.5'
        )

        # Ajouter les nœuds avec leur couleur si disponible
        for noeud in self.noeuds:
            if self.coloration_actuelle and noeud in self.coloration_actuelle:
                dot.node(str(noeud), 
                    fillcolor=self.coloration_actuelle[noeud],
                    style='filled'
                )
            else:
                dot.node(str(noeud), style='filled', fillcolor='white')

        # Ajouter les arêtes une seule fois pour graphe non orienté
        aretes_traitees = set()
        for source, dest in self.aretes:
            if not self.oriente:
                # Pour un graphe non orienté, ne traiter chaque arête qu'une fois
                arete = tuple(sorted([source, dest]))
                if arete not in aretes_traitees:
                    dot.edge(str(source), str(dest))
                    aretes_traitees.add(arete)
            else:
                dot.edge(str(source), str(dest))

        # Sauvegarder avec le format PNG explicitement
        output_path = f"{fichier_sortie}"  # sans extension
        dot.format = 'png'
        dot.render(output_path, view=False, cleanup=True)
        
        print(f"Graphe sauvegardé avec succès dans {output_path}.png")
        return True

     except Exception as e:
        print(f"Erreur lors de la génération du PNG : {str(e)}")
        print("Vérifiez que Graphviz est bien installé sur votre système")
        return False

    def ecrire_coloration(self, coloration, chemin):
        with open(chemin, 'w') as f:
            for noeud, couleur in coloration.items():
                f.write(f"{noeud} {couleur}\n")

    def evaluer_coloration(self, coloration=None):
        """
        Évalue la validité de la coloration et retourne le nombre de couleurs utilisées.
        
        Args:
            coloration (dict, optional): Dictionnaire de la coloration à évaluer.
                                       Si None, utilise la coloration actuelle.
        
        Returns:
            tuple: (est_valide, nombre_couleurs) où:
                  - est_valide (bool): True si la coloration est valide, False sinon
                  - nombre_couleurs (int): Nombre de couleurs différentes utilisées
        """
        if coloration is None:
            coloration = self.coloration_actuelle
        if not coloration:
            return False, 0
            
        # Vérifie si tous les nœuds sont colorés
        if set(coloration.keys()) != self.noeuds:
            return False, 0
        
        # Vérifie la validité de la coloration
        for source, dest in self.aretes:
            if coloration[source] == coloration[dest]:
                return False, len(set(coloration.values()))
        
        # Compte le nombre de couleurs uniques utilisées
        nombre_couleurs = len(set(coloration.values()))
        return True, nombre_couleurs

    @staticmethod
    def lire_fichier(chemin):
      """
      Lit un fichier au format DIMACS et crée un graphe correspondant.
    
      Format DIMACS attendu:
      - Lignes commençant par 'c' : commentaires
      - Ligne commençant par 'p' : p edge NODES EDGES
      - Lignes commençant par 'e' : e SOURCE DEST
    
      Args:
        chemin (str): Chemin vers le fichier DIMACS
        
      Returns:
        GrapheReel: Instance du graphe créé
      """
      graphe = GrapheReel()
      nb_noeuds = 0
      nb_aretes = 0
    
      with open(chemin, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:  # Ignorer les lignes vides
                continue
                
            elements = line.split()
            if not elements:  # Ignorer les lignes sans éléments
                continue
                
            # Traiter selon le premier caractère de la ligne
            if elements[0] == 'c':  # Commentaire
                continue
                
            elif elements[0] == 'p':  # Ligne de problème
                if len(elements) != 4 or elements[1] != 'edge':
                    raise ValueError("Format de ligne 'p' invalide")
                nb_noeuds = int(elements[2])
                nb_aretes = int(elements[3])
                
                # Créer tous les nœuds
                for i in range(1, nb_noeuds + 1):
                    graphe.ajouter_noeud(str(i))
                    
            elif elements[0] == 'e':  # Ligne d'arête
                if len(elements) != 3:
                    raise ValueError(f"Format de ligne 'e' invalide: {line}")
                source = elements[1]
                dest = elements[2]
                graphe.ajouter_arete(source, dest)
                
            else:
                print(f"Attention: ligne ignorée: {line}")
    
      print(f"Graphe lu: {len(graphe.noeuds)} nœuds, {len(graphe.aretes)//2} arêtes")
      if len(graphe.noeuds) != nb_noeuds:
        print(f"Attention: nombre de nœuds différent de celui déclaré ({nb_noeuds})")
      if len(graphe.aretes)//2 != nb_aretes:
        print(f"Attention: nombre d'arêtes différent de celui déclaré ({nb_aretes})")
        
      return graphe

    def ecrire_fichier(self, chemin):
     """
     Écrit le graphe dans un fichier au format DIMACS.
     Format:
     - Commentaire: ligne commençant par 'c'
     - Problème: ligne 'p edge NODES EDGES'
     - Arêtes: lignes 'e SOURCE DEST'
    
     Args:
        chemin (str): Chemin du fichier de sortie
     """
     try:
        with open(chemin, 'w') as f:
            # Écrire l'en-tête et les informations du graphe
            f.write("c Fichier généré automatiquement\n")
            
            # Calculer le nombre d'arêtes (sans duplicats pour graphe non orienté)
            aretes_uniques = set()
            for source, dest in self.aretes:
                if not self.oriente:
                    aretes_uniques.add(tuple(sorted([source, dest])))
                else:
                    aretes_uniques.add((source, dest))
            
            # Écrire la ligne de problème avec le nombre de nœuds et d'arêtes
            f.write(f"p edge {len(self.noeuds)} {len(aretes_uniques)}\n")
            
            # Écrire les arêtes
            aretes_ecrites = set()
            for source, dest in self.aretes:
                if not self.oriente:
                    arete = tuple(sorted([source, dest]))
                    if arete not in aretes_ecrites:
                        f.write(f"e {arete[0]} {arete[1]}\n")
                        aretes_ecrites.add(arete)
                else:
                    f.write(f"e {source} {dest}\n")
                    
        print(f"Graphe sauvegardé dans {chemin} au format DIMACS")
        return True
        
     except Exception as e:
        print(f"Erreur lors de l'écriture du fichier : {str(e)}")
        return False

def creer_graphe_interactif():
    """Fonction pour créer un graphe de manière interactive"""
    print("Création d'un nouveau graphe")
    
    while True:
        reponse = input("Le graphe est-il orienté? (o/n): ").lower()
        if reponse in ['o', 'n']:
            break
        print("Veuillez répondre par 'o' pour oui ou 'n' pour non.")
    
    graphe = GrapheReel(oriente=(reponse == 'o'))
    
    print("\nSaisie des nœuds (appuyez sur Entrée sans rien écrire pour terminer)")
    while True:
        noeud = input("Entrez un nœud (ex: A, B, 1, 2...): ").strip()
        if not noeud:
            break
        graphe.ajouter_noeud(noeud)
        print(f"Nœuds actuels: {sorted(graphe.noeuds)}")
    
    print("\nSaisie des arêtes (appuyez sur Entrée sans rien écrire pour terminer)")
    print("Format: source destination (ex: A B)")
    while True:
        arete = input("Entrez une arête: ").strip()
        if not arete:
            break
        try:
            source, destination = arete.split()
            if graphe.ajouter_arete(source, destination):
                print(f"Arête ajoutée: {source} -> {destination}")
        except ValueError:
            print("Format incorrect. Utilisez: source destination (ex: A B)")
    
    return graphe

def afficher_menu():
    print("\n=== Menu Gestionnaire de Graphes ===")
    print("1.  Créer un nouveau graphe")
    print("2.  Charger un graphe depuis un fichier")
    print("3.  Sauvegarder le graphe")
    print("4.  Ajouter un noeud")
    print("5.  Supprimer un noeud")
    print("6.  Ajouter une arête")
    print("7.  Supprimer une arête")
    print("8.  Afficher le graphe")
    print("9.  Créer une coloration avec l'algorithme Welsh-Powell")
    print("10. Charger une coloration")
    print("11. Sauvegarder la coloration")
    print("12. Évaluer la coloration")
    print("13. Visualiser le graphe (PNG)")
    print("14. Colorer le graphe (Hill-Climbing)")
    print("0.  Quitter")

def main():
    graphe = None
    while True:
        afficher_menu()
        choix = input("\nVotre choix : ")
        
        if choix == "0":
            print("Au revoir!")
            break
            
        elif choix == "1":
            graphe = creer_graphe_interactif()
            if len(graphe.noeuds) > 0:
                print(f"\nGraphe créé avec succès : {len(graphe.noeuds)} nœuds et {len(graphe.aretes)//2 if not graphe.oriente else len(graphe.aretes)} arêtes")
            else:
                print("Aucun nœud n'a été créé.")
            
        elif choix == "2":
            fichier = input("Nom du fichier à charger : ")
            try:
                graphe = GrapheReel.lire_fichier(fichier)
                print(f"Graphe chargé : {len(graphe.noeuds)} noeuds, {len(graphe.aretes)//2 if not graphe.oriente else len(graphe.aretes)} arêtes")
            except Exception as e:
                print(f"Erreur : {str(e)}")
            
        elif choix == "3":
            if graphe:
                fichier = input("Nom du fichier pour la sauvegarde : ")
                graphe.ecrire_fichier(fichier)
                print("Graphe sauvegardé.")
            else:
                print("Aucun graphe n'est chargé.")
            
        elif choix == "4":
            if graphe:
                noeud = input("Identifiant du nouveau noeud : ")
                graphe.ajouter_noeud(noeud)
                print("Noeud ajouté.")
            else:
                print("Aucun graphe n'est chargé.")
            
        elif choix == "5":
            if graphe:
                noeud = input("Identifiant du noeud à supprimer : ")
                if graphe.supprimer_noeud(noeud):
                    print("Noeud supprimé.")
                else:
                    print("Noeud non trouvé.")
            else:
                print("Aucun graphe n'est chargé.")
            
        elif choix == "6":
            if graphe:
                source = input("Noeud source : ")
                dest = input("Noeud destination : ")
                if graphe.ajouter_arete(source, dest):
                    print("Arête ajoutée.")
                else:
                    print("Erreur : vérifiez que les noeuds existent.")
            else:
                print("Aucun graphe n'est chargé.")
            
        elif choix == "7":
            if graphe:
                source = input("Noeud source : ")
                dest = input("Noeud destination : ")
                if graphe.supprimer_arete(source, dest):
                    print("Arête supprimée.")
                else:
                    print("Arête non trouvée.")
            else:
                print("Aucun graphe n'est chargé.")
            
            
        elif choix == "8":
            if graphe:
                print("\nNoeuds :", sorted(list(graphe.noeuds)))
                print("Arêtes :", sorted(list(set(tuple(sorted([s, d])) for s, d in graphe.aretes))))
            else:
                print("Aucun graphe n'est chargé.")
            
        elif choix == "9":
            if graphe:
                coloration = graphe.coloration()
                coloration, stats = graphe.coloration()
                print("\nColoration créée :", coloration)
                print("\nStatistiques:")
                print(f"Temps d'exécution: {stats['temps_execution']} secondes")
                print(f"Nombre d'itérations: {stats['iterations']}")
                print(f"Conflits finaux: {stats['conflits_final']}")
            else:
                print("Aucun graphe n'est chargé.")
            
        elif choix == "10":
            if graphe:
                fichier = input("Nom du fichier de coloration : ")
                try:
                    coloration = graphe.lire_coloration(fichier)
                    print("Coloration chargée :", coloration)
                except Exception as e:
                    print(f"Erreur : {str(e)}")
            else:
                print("Aucun graphe n'est chargé.")
            
        elif choix == "11":
            if graphe and graphe.coloration_actuelle:
                fichier = input("Nom du fichier pour la coloration : ")
                graphe.ecrire_coloration(graphe.coloration_actuelle, fichier)
                print("Coloration sauvegardée.")
            else:
                print("Aucun graphe ou coloration active n'est chargé.")
            
        elif choix == "12":
          if graphe and graphe.coloration_actuelle:
             est_valide, nb_couleurs = graphe.evaluer_coloration()
             if est_valide:
              print(f"La coloration est valide et utilise {nb_couleurs} couleur(s).")
             else:
              print(f"La coloration n'est pas valide. {nb_couleurs} couleur(s) ont été utilisées.")
          else:
             print("Aucun graphe ou coloration active n'est chargé.")
         
        elif choix == "13":
            if graphe:
                fichier = input("Nom du fichier de sortie (sans extension) : ")
                try:
                    graphe.dessiner(fichier)
                    print(f"Graphe sauvegardé dans {fichier}.png")
                except Exception as e:
                    print(f"Erreur lors de la création de l'image : {str(e)}")
            else:
                print("Aucun graphe n'est chargé.")
        
        elif choix == "14":
         if graphe:
          print("\nTentative de coloration du graphe avec Hill-Climbing...")
          coloration, stats = graphe.coloration_hill_climbing(max_iterations=1000)
          if coloration:
            print("\nColoration trouvée :", coloration)
            print("\nStatistiques:")
            print(f"Temps d'exécution: {stats['temps_execution']} secondes")
            print(f"Nombre d'itérations: {stats['iterations']}")
            print(f"Conflits finaux: {stats['conflits_final']}")
          else:
           print("Aucun graphe n'est chargé.")
        
        input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()