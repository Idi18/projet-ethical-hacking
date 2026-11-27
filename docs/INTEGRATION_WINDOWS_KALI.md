\# Guide d'intégration — Windows, Kali et Debian



\*\*Projet :\*\* Ethical Hacking — Client/serveur Python  

\*\*Mise à jour :\*\* 23 novembre 2026  

\*\*Branche GitHub :\*\* `windows-integration`  

\*\*Dernier commit vérifié :\*\* `3e3c708`



\## 1. Objectif



Ce document présente l'architecture, les échanges réseau, les tests effectués et les étapes restantes pour intégrer les trois composants du projet :



\- L'agent Windows V4.

\- Le serveur Kali V4.

\- L'agent Debian développé par l'autre membre du groupe.



Les communications reposent sur des sockets TCP et des messages JSON dans un laboratoire VMware.



\*\*État actuel :\*\* l'intégration Windows–Kali V4 a été réalisée et testée avec succès le 23 novembre 2026. L'intégration de Debian reste à valider.



\## 2. Architecture réseau



| Machine | Adresse IPv4 | Rôle |

|---|---|---|

| Windows principal | 192.168.109.1 | Développement, GitHub et transfert des fichiers |

| Windows 11 virtuel | 192.168.109.134 | Agent Windows testé |

| Kali Linux | 192.168.109.129 | Serveur principal |

| Debian Linux | 192.168.109.133 | Client Linux à intégrer |



\*\*Réseau de laboratoire :\*\* VMware VMnet1 (Host-only)  

\*\*Masque :\*\* 255.255.255.0  

\*\*Port utilisé :\*\* 5001



Le protocole commun définit initialement le port 5000, mais les tests d'intégration ont été réalisés sur le port 5001.



\## 3. Fichiers du projet



\### Agent Windows



\- `agents/windows/main.py`

\- `agents/windows/commandes\_locales.py`

\- `agents/windows/registry.py`

\- `agents/windows/security\_audit.py`

\- `agents/windows/sam\_audit.py`



\### Serveur Kali V4



\- `serveur/main.py`

\- `serveur/socket\_server.py`

\- `serveur/command\_interpreter.py`

\- `serveur/error\_handler.py`

\- `serveur/clients\_manager.py`



Ces cinq modules sont désormais développés et intégrés dans le serveur V4.



\### Protocole commun



\- `shared/protocol.py`



Ce fichier définit les types de messages et les fonctions utilisées pour construire et encoder les messages JSON.



\### Agent Debian



Les fichiers définitifs et leur compatibilité avec le protocole commun restent à vérifier lors de l'intégration du travail du second membre.



\## 4. Structure des messages JSON



Les messages suivent généralement cette structure :



```json

{

&#x20; "type": "nom\_du\_message",

&#x20; "id": "identifiant\_unique",

&#x20; "data": {}

}

```



Chaque message est encodé en UTF-8 et se termine par un retour à la ligne.



Le serveur V4 lit les messages, contrôle leur format général et associe les réponses aux demandes grâce à leur identifiant.



Une limite de taille est également appliquée lors de la réception des messages par le serveur V4.



\## 5. Identification des agents



\### HELLO



L'agent Windows se connecte au serveur et transmet un message `hello` contenant notamment :



\- Le nom de l'agent.

\- Son système d'exploitation.

\- Les adresses IPv4 détectées.

\- La version déclarée du protocole.



\### HELLO\_ACK



Le serveur répond par `hello\_ack` et attribue un identifiant au client.



Exemple du format des données :



```json

{

&#x20; "agent\_id": "identifiant-attribue",

&#x20; "server": "Serveur Kali"

}

```



Le module `clients\_manager.py` enregistre les clients et suit leurs déconnexions.



\*\*Résultat du 23 novembre 2026 :\*\* identification et attribution d'identifiant réussies avec l'agent Windows V4.



\## 6. Messages pris en charge par Windows V4



| Demande | Réponse |

|---|---|

| `ping` | `pong` |

| `sysinfo` | `result` |

| `cmd` autorisée | `result` |

| `cmd` interdite | `error` |

| `registry` | `result` informatif |

| `screenshot` | `result` informatif |

| Type inconnu | `error` |



\### Diagnostics CMD autorisés



L'agent Windows V4 accepte les diagnostics suivants :



\- `date`

\- `ordinateur`

\- `windows`



Exemple :



```json

{

&#x20; "type": "cmd",

&#x20; "id": "test-date-001",

&#x20; "data": {

&#x20;   "command": "date",

&#x20;   "args": \[]

&#x20; }

}

```



L'agent Windows limite les diagnostics aux commandes explicitement autorisées.



Le refus d'une commande non autorisée a été testé lors des précédents essais. Le test final du serveur Kali V4 du 23 novembre a principalement validé la commande `date`.



\## 7. Fonctionnalités Windows encore limitées



\### Registre Windows



Le module `registry.py` a été testé localement avec la clé :



`HKEY\_CURRENT\_USER\\Software\\MonProjetTP`



Valeur : `Status = Actif`.



Une demande distante `registry` retourne actuellement des informations d'état ; l'exécution distante de modifications du registre n'a pas été démontrée.



\### Capture d'écran



Le module `security\_audit.py` a été testé localement.



Le programme principal ne transmet pas d'image lors d'une demande distante `screenshot` : il retourne uniquement une réponse informative.



\### Audit SAM



Le module `sam\_audit.py` est expérimental.



La récupération effective des ruches protégées SAM et SYSTEM n'a pas été démontrée. Aucune extraction distante de ces informations n'est intégrée au fonctionnement validé.



Ces limites doivent être indiquées dans le rapport final.



\## 8. Gestion des erreurs et des connexions



\### Agent Windows V4



Paramètres utilisés :



\- `MAX\_TENTATIVES = 3`

\- `DELAI\_RECONNEXION = 3`



En cas de refus de connexion, l'agent effectue au maximum trois tentatives.



Une déconnexion normale termine la session.



\### Serveur Kali V4



Le serveur dispose de :



\- `socket\_server.py` : écoute et acceptation des connexions TCP.

\- `error\_handler.py` : classification et journalisation des erreurs.

\- `clients\_manager.py` : enregistrement et déconnexion des clients.

\- `command\_interpreter.py` : préparation des diagnostics et validation des réponses.

\- `main.py` : orchestration des sessions.



Les connexions successives sont prises en charge. Le traitement simultané de plusieurs clients n'a pas été démontré.



\### Démarrage automatique Windows



Le lancement de l'agent reste manuel dans les tests validés.



La consultation de la clé de démarrage utilisateur n'a révélé que OneDrive. La recherche d'une tâche planifiée correspondant à l'agent n'a pas encore établi l'existence d'un démarrage automatique.



Cette exigence reste à vérifier.



\## 9. Lancement du serveur et de l'agent



\### Sur Kali Linux



Depuis le répertoire du projet :



```bash

cd \~/projet-ethical-hacking-github

python3 -m serveur.main

```



Le serveur doit notamment afficher :



```text

\[SERVEUR] Demarrage du serveur Kali V4

\[SERVEUR] En attente sur 192.168.109.129:5001

```



\### Sur la machine virtuelle Windows 11



Depuis le dossier contenant l'exécutable :



```cmd

agent-windows-v4.exe --ip 192.168.109.129 --port 5001

```



L'agent contacte alors le serveur et traite les demandes de diagnostic prévues.



\## 10. Tests réalisés



\### Tests antérieurs



\- Communication TCP Windows–Kali.

\- Échanges HELLO / HELLO\_ACK.

\- Échanges PING / PONG.

\- SYSINFO / RESULT.

\- Diagnostic CMD `date`.

\- Refus d'une commande CMD non autorisée.

\- Gestion des tentatives de connexion.

\- Compilation et exécution de l'agent Windows V4.

\- Tests locaux du registre et de la capture d'écran.

\- Vérification de la journalisation d'erreurs du serveur.



\### Tests du 23 novembre 2026



\*\*Gestion des clients\*\*



\- Enregistrement d'un client Windows simulé.

\- Attribution d'un identifiant unique.

\- Déconnexion.

\- Vérification du nombre de clients actifs.



\*\*Interpréteur de commandes\*\*



\- Préparation du message `cmd` pour `date`.

\- Vérification du format du message.

\- Test local réussi.



\*\*Intégration Windows–Kali V4\*\*



Le serveur principal a réussi :



1\. La réception de la connexion Windows.

2\. Le traitement du message `hello`.

3\. L'envoi du message `hello\_ack`.

4\. L'échange `ping` / `pong`.

5\. La demande `sysinfo`.

6\. Le diagnostic `date`.

7\. L'enregistrement de la déconnexion.

8\. Le retour à l'attente d'une nouvelle connexion.



Le journal du serveur affiche notamment :



```text

\[SUCCES] Session de diagnostic terminee

\[CLIENT] Deconnexion : windows-agent

\[SERVEUR] Clients connectes : 0

\[SERVEUR] Pret pour une nouvelle connexion

```



\*\*Conclusion des essais :\*\* l'intégration Windows–Kali V4 fonctionne pour les scénarios de diagnostic testés.



\## 11. État de l'intégration



| Élément | État |

|---|---|

| Protocole JSON commun | Validé avec Windows |

| Port TCP commun | Validé sur 5001 |

| HELLO / HELLO\_ACK | Validé |

| PING / PONG | Validé |

| SYSINFO / RESULT | Validé |

| Diagnostic CMD `date` | Validé |

| Gestion des clients | Validée pour les sessions testées |

| Gestion des erreurs | Testée |

| Connexions successives | Testées |

| Plusieurs clients simultanés | Non démontré |

| Agent Debian | À intégrer et tester |

| Démarrage automatique Windows | Non confirmé |

| Vérification complète des exigences | À effectuer |



Les prochaines priorités sont l'intégration Debian et la comparaison des fonctionnalités réalisées avec les consignes officielles.



\## 12. Coordination GitHub



\*\*Dépôt :\*\*  

https://github.com/Idi18/projet-ethical-hacking



\*\*Branche de développement :\*\*  

`windows-integration`



\*\*Dernier commit vérifié :\*\*  

`3e3c708`



\*\*Message du commit :\*\*  

`Integration du serveur Kali V4 et gestion des clients`



Ce commit inclut les cinq modules du serveur Kali V4.



Le 23 novembre 2026, le `git push` a réussi et la branche locale était synchronisée avec `origin/windows-integration`.



Le code Windows et les modules du serveur sont ainsi sauvegardés dans cette branche.



Avant toute fusion avec le travail Debian, les modifications du coéquipier doivent être comparées et les éventuels conflits doivent être résolus dans une branche d'intégration.



La branche `main` ne doit pas être considérée comme mise à jour tant que cette fusion n'a pas été effectuée.



\## 13. Limites de sécurité



Les tests ont été effectués dans un laboratoire VMware sur un réseau Host-only.



Les communications TCP/JSON ne disposent pas d'une authentification applicative et d'un chiffrement démontrés.



Le serveur doit rester limité au réseau autorisé du laboratoire.



Les diagnostics du programme principal sont limités à un ensemble prédéfini de commandes.



Les fonctionnalités sensibles ou non validées à distance doivent être présentées comme expérimentales ou incomplètes dans le rapport.



\## 14. Conclusion



Le 23 novembre 2026, l'agent Windows V4 et le serveur Kali V4 ont réussi leur test d'intégration.



Les cinq modules du serveur principal ont été développés et publiés sur GitHub dans le commit `3e3c708`.



Les fonctionnalités validées comprennent l'identification des clients, les échanges TCP/JSON, les diagnostics système autorisés, la gestion des déconnexions et la journalisation des erreurs.



Le projet n'est toutefois pas encore entièrement finalisé.



Les prochaines étapes concernent :



1\. L'intégration de l'agent Debian.

2\. Les tests du projet commun.

3\. La vérification des exigences officielles encore ouvertes.

4\. La mise à jour des preuves et du rapport.

5\. La fusion contrôlée des branches.

6\. La préparation de l'archive finale.



Ce document constitue la référence technique de l'intégration Windows–Kali V4 et de la préparation de l'intégration Debian.

