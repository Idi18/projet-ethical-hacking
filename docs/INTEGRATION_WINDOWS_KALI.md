

\# Guide d'intégration — Windows, Kali et Debian



\## 1. Objectif



Ce document présente les informations nécessaires pour intégrer

l'agent Windows V4 au serveur Kali du projet Ethical Hacking.



Les échanges sont réalisés dans un laboratoire VMware isolé,

au moyen de sockets TCP et de messages JSON.



L'intégration au serveur principal reste à effectuer.



\## 2. Architecture réseau



| Machine | Adresse IPv4 | Rôle |

|---|---|---|

| Windows 11 hôte | 192.168.109.1 | Agent Windows |

| Kali Linux | 192.168.109.129 | Serveur |

| Debian Linux | 192.168.109.133 | Client Linux de test |



Réseau : VMware VMnet1 (Host-only)

Masque : 255.255.255.0

Port utilisé pendant les tests : 5001



Le port par défaut défini dans shared/protocol.py est 5000.

Il faut donc configurer explicitement le port 5001 pour

reproduire les tests existants.



\## 3. Fichiers concernés



\### Agent Windows



\- agents/windows/main.py

\- agents/windows/commandes\_locales.py

\- agents/windows/registry.py

\- agents/windows/security\_audit.py

\- agents/windows/sam\_audit.py



\### Protocole commun



\- shared/protocol.py



\### Serveur principal prévu



\- serveur/main.py

\- serveur/socket\_server.py

\- serveur/command\_interpreter.py

\- serveur/error\_handler.py

\- serveur/clients\_manager.py



Au moment de la vérification, ces cinq fichiers du serveur

principal étaient vides dans origin/main.



Le serveur test\_serveur\_kali.py a été utilisé séparément

pour les validations réseau. Il ne remplace pas encore

le serveur principal.



\## 4. Structure des messages JSON



Format général :



{

&#x20;   "type": "nom\_du\_message",

&#x20;   "id": "identifiant\_unique",

&#x20;   "data": {}

}



Chaque message est encodé en UTF-8 et terminé par un

caractère de nouvelle ligne.



Les fonctions de création, encodage et décodage sont

définies dans shared/protocol.py.



Le serveur doit respecter les identifiants de messages

pour associer chaque réponse à sa demande.



\## 5. Identification de l'agent



\### Étape 1 : HELLO



Lorsqu'il se connecte, Windows envoie un message HELLO

contenant notamment :



\- Le nom de l'agent.

\- Le système d'exploitation.

\- Les adresses IPv4 détectées.

\- La version du protocole annoncée.



\### Étape 2 : HELLO\_ACK



Le serveur répond avec un message HELLO\_ACK.



Son champ data contient notamment :



{

&#x20;   "agent\_id": "identifiant-attribue",

&#x20;   "server": "nom-du-serveur"

}



L'agent Windows attend cette confirmation avant de

traiter les autres demandes.



\## 6. Messages pris en charge par Windows V4



| Demande | Réponse |

|---|---|

| ping | pong |

| sysinfo | result |

| cmd autorisée | result |

| cmd interdite | error |

| registry | result informatif |

| screenshot | result informatif |

| Type inconnu | error |



Les réponses conservent l'identifiant de la demande.



\### Diagnostics CMD autorisés



La commande cmd accepte uniquement :



\- date

\- ordinateur

\- windows



Le champ args doit être une liste vide.



Exemple de demande :



{

&#x20;   "type": "cmd",

&#x20;   "id": "test-date-001",

&#x20;   "data": {

&#x20;       "command": "date",

&#x20;       "args": \[]

&#x20;   }

}



Exemple de résultat :



{

&#x20;   "type": "result",

&#x20;   "id": "test-date-001",

&#x20;   "data": {

&#x20;       "ok": true,

&#x20;       "payload": {

&#x20;           "commande": "date",

&#x20;           "diagnostic": {

&#x20;               "ok": true,

&#x20;               "sortie": "2026-11-22 19:50:12",

&#x20;               "erreur": "",

&#x20;               "code\_retour": 0

&#x20;           }

&#x20;       }

&#x20;   }

}



La date ci-dessus est un exemple issu du format de sortie,

et non une valeur attendue pour les prochains tests.



Toute commande non autorisée doit produire une réponse

de type error avec le code COMMAND\_NOT\_ALLOWED.



Le serveur ne doit pas considérer les commandes arbitraires

comme prises en charge par cet agent.



\## 7. Fonctions limitées aux tests locaux



\### Registre Windows



Le fichier registry.py a été testé localement avec :



HKEY\_CURRENT\_USER\\Software\\MonProjetTP



Valeur :

Status = Actif



Une demande distante registry renvoie uniquement

un état informatif.



\### Capture d'écran



Le module security\_audit.py a été testé localement.



Une demande distante screenshot renvoie uniquement

un état informatif ; aucune image n'est transmise

par le programme principal.



\### SAM



Le module sam\_audit.py est expérimental.



La récupération effective des ruches protégées SAM

et SYSTEM n'a pas été démontrée.



Aucune récupération distante de ces données n'est

intégrée au programme principal.



\## 8. Gestion des erreurs réseau



Windows V4 utilise les paramètres suivants :



MAX\_TENTATIVES = 3

DELAI\_RECONNEXION = 3



En cas de refus de connexion, l'agent tente une

nouvelle connexion dans la limite définie.



Après trois échecs, il s'arrête.



Une déconnexion normale du serveur met fin à la session.



Le démarrage reste manuel.



\## 9. Lancement des tests



\### Sur Kali Linux



Dans le terminal Kali :



python3 \~/projet-ethical-hacking/test\_serveur\_kali.py



Cette commande suppose que le fichier de test est

présent dans le dossier indiqué.



Le serveur de test doit afficher :



\[KALI] Serveur en attente sur 192.168.109.129:5001



\### Sur Windows



Dans CMD Windows, depuis la racine du projet :



.\\dist\\agent-windows-v4.exe --ip 192.168.109.129 --port 5001



L'agent se connecte au serveur et traite les

demandes prévues par le programme de test.



\## 10. Tests déjà réalisés



Les validations suivantes ont été observées :



\- Connexion TCP Windows-Kali.

\- HELLO et HELLO\_ACK.

\- PING et PONG.

\- SYSINFO et RESULT.

\- Diagnostic CMD date autorisé.

\- Rejet d'une commande CMD non autorisée.

\- Trois tentatives lors d'une connexion refusée.

\- Compilation de l'exécutable Windows V4.

\- Communication de l'exécutable V4 avec Kali.



Ces résultats concernent le serveur de test,

pas encore le serveur principal du groupe.



\## 11. Intégration au serveur principal



Pour intégrer les composants, il faudra :



1\. Utiliser une version commune de shared/protocol.py.

2\. Définir le même port TCP pour le serveur et les agents.

3\. Vérifier le traitement de HELLO et HELLO\_ACK.

4\. Implémenter la réception des messages délimités

&#x20;  par un retour à la ligne.

5\. Associer les réponses aux identifiants des demandes.

6\. Vérifier les messages pris en charge par chaque agent.

7\. Gérer les connexions et les déconnexions.

8\. Tester Windows et Debian avec le serveur principal.

9\. Vérifier les exigences officielles et documenter

&#x20;  les fonctionnalités non réalisées.



Le serveur devra traiter uniquement les demandes

explicitement prises en charge par chaque client.



\## 12. Coordination GitHub



Dépôt :

https://github.com/Idi18/projet-ethical-hacking



Branche Windows :

windows-integration



Dernier commit Windows vérifié avant ce document :

63a4c78



Le protocole commun est actuellement développé

sur la branche windows-integration.



Avant toute fusion, il faut comparer les changements

du coéquipier afin d'éviter d'écraser son travail.



\## 13. Limites de sécurité



Le laboratoire utilise un réseau VMware isolé.



Les communications TCP/JSON ne disposent pas encore

d'une authentification applicative et d'un chiffrement

démontrés.



Les tests doivent rester limités aux machines autorisées

du laboratoire.



Les fonctions sensibles ne doivent pas être présentées

comme fonctionnelles à distance lorsqu'elles ne le sont pas.



\## 14. Conclusion



L'agent Windows V4 est fonctionnel dans les scénarios

de test TCP réalisés avec Kali.



Les prochaines étapes concernent la mise en commun

du protocole, le développement du serveur principal,

l'intégration de l'agent Linux et les essais finaux.



Ce document sert de référence d'intégration pour

éviter les incompatibilités entre les composants.



