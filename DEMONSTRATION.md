\# Guide de démonstration — Projet Ethical Hacking



\## 1. Présentation



Ce projet universitaire a été réalisé dans un laboratoire VMware autorisé. Il présente une architecture client/serveur Python utilisant des sockets TCP et des messages JSON.



\*\*Machines utilisées :\*\*

\- Kali Linux : serveur central.

\- Windows 11 : agent Windows.

\- Debian Linux : agent Linux.



\## 2. Démarrage du serveur Kali



Dans le terminal Kali, depuis le dossier principal du projet :



```bash

python3 -m serveur.main

```



Le serveur écoute sur le port TCP 5001 et accepte jusqu'à quatre connexions simultanées selon sa configuration.



\## 3. Démonstration de l'agent Windows



Dans la VM Windows 11, lancer manuellement le fichier :



`lancer-agent.bat`



Les tests validés comprennent la connexion TCP, l'identification du client, PING/PONG, les informations système, la commande autorisée `date` et la gestion des erreurs.



\## 4. Démonstration de l'agent Debian



Dans la VM Debian, depuis le dossier du projet :



```bash

python3 agents/linux/main.py --ip 192.168.109.129 --port 5001

```



Les tests validés comprennent la connexion TCP, PING/PONG, les informations système et la récupération des interfaces réseau.



Les lectures de `/etc/passwd`, les permissions de `/etc/shadow` et les parcours de `/root` et `/home` ont également été testés localement.



\## 5. Bonus — Quatre clients simultanés



Le script `test\_4\_clients.py` a permis de simuler quatre clients TCP.



Résultat obtenu :



```text

RESULTAT : 4/4 clients termines

TEST MULTI-CLIENTS REUSSI

```



Preuve : capture n°63.



\## 6. Fonctionnalités et limites



\*\*Fonctionnalités validées :\*\*

\- Communication client/serveur TCP.

\- Identification et diagnostics des agents.

\- Gestion des connexions et des erreurs.

\- Capture d'écran locale sur Windows.

\- Vérification locale de la clé de registre Windows.

\- Test de quatre clients simultanés.



\*\*Fonctionnalités non entièrement validées :\*\*

\- Démarrage automatique de l'agent Windows.

\- Déclenchement d'une capture d'écran Windows depuis Kali.

\- Récupération effective de la base SAM.

\- Capture d'écran Debian, ayant rencontré une erreur liée à l'environnement graphique.

\- Démarrage automatique Debian après redémarrage, à confirmer.

\- Exécution distante de certaines fonctions Linux supplémentaires.



Ces limites sont indiquées afin de distinguer les fonctionnalités développées des tests réellement réussis.



\## 7. Fichiers de livraison



L'archive `projet-ethical-hacking-code-final.zip` contient le code source, le README, les captures de preuve, le script bonus et l'exécutable Windows V4.



La branche GitHub utilisée est `integration-finale`.



\## 8. Conclusion



Les essais réalisés démontrent le fonctionnement des communications entre Kali, Windows et Debian, ainsi que les mécanismes de diagnostic et de gestion des connexions. Les fonctionnalités restantes sont identifiées dans la documentation du projet.

