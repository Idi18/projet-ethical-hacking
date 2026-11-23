\# Projet Ethical Hacking — Architecture client/serveur Python



\## 1. Présentation



Ce projet universitaire consiste à développer une architecture client/serveur en Python, dans un environnement de laboratoire VMware.



L'architecture comprend trois composants :



\- \*\*Kali Linux :\*\* serveur principal assurant les communications TCP, la gestion des clients et les diagnostics.

\- \*\*Windows 11 :\*\* agent client permettant l'identification du système et l'exécution de diagnostics prédéfinis.

\- \*\*Debian Linux :\*\* agent client Linux destiné à être intégré au serveur commun.



Les machines communiquent à l'aide de sockets TCP et de messages JSON.



Les tests sont effectués uniquement dans un environnement VMware autorisé.



\## 2. Architecture réseau



| Machine | Adresse IP | Fonction |

|---|---|---|

| Kali Linux | 192.168.109.129 | Serveur principal |

| Windows 11 virtuel | 192.168.109.134 | Agent Windows |

| Debian Linux | 192.168.109.133 | Agent Linux à intégrer |

| Windows principal | 192.168.109.1 | Développement et gestion GitHub |



\*\*Réseau :\*\* VMware VMnet1 (Host-only)



\*\*Port TCP utilisé :\*\* 5001



Les adresses IP correspondent à la configuration du laboratoire et peuvent nécessiter une adaptation sur d'autres machines.



\## 3. Structure du projet



```text

projet-ethical-hacking/

│

├── agents/

│   ├── windows/

│   │   ├── main.py

│   │   ├── commandes\_locales.py

│   │   ├── registry.py

│   │   ├── security\_audit.py

│   │   └── sam\_audit.py

│   │

│   └── linux/

│       ├── main.py

│       ├── filesystem.py

│       └── security\_audit.py

│

├── serveur/

│   ├── main.py

│   ├── socket\_server.py

│   ├── command\_interpreter.py

│   ├── clients\_manager.py

│   └── error\_handler.py

│

├── shared/

│   └── protocol.py

│

├── docs/

│   ├── WINDOWS\_AGENT.md

│   ├── INTEGRATION\_WINDOWS\_KALI.md

│   └── screenshots/

│

└── README.md

```



Les fichiers de l'agent Debian existent dans l'arborescence, mais leur implémentation et leur intégration restent à confirmer.



\## 4. Protocole de communication



Le projet utilise des messages JSON encodés en UTF-8, terminés par un retour à la ligne.



Exemple :



```json

{

&#x20; "type": "ping",

&#x20; "id": "test-001",

&#x20; "data": {}

}

```



Les principaux échanges comprennent :



| Message | Fonction |

|---|---|

| `hello` | Identification du client |

| `hello\_ack` | Confirmation du serveur |

| `ping` / `pong` | Vérification de la communication |

| `sysinfo` | Demande d'informations système |

| `cmd` | Diagnostic prédéfini |

| `result` | Transmission du résultat |

| `error` | Signalement d'une erreur |



Le serveur vérifie les identifiants des réponses afin de les associer aux demandes envoyées.



\## 5. Serveur Kali V5



Le serveur Kali V5 comprend cinq modules :



\- `main.py` : démarrage du serveur et gestion des sessions.

\- `socket\_server.py` : ouverture du socket TCP et acceptation des connexions.

\- `clients\_manager.py` : suivi des clients et de leurs déconnexions.

\- `command\_interpreter.py` : préparation et vérification des diagnostics autorisés.

\- `error\_handler.py` : classification et journalisation des erreurs.



\### Gestion parallèle



Le serveur V5 utilise `ThreadPoolExecutor` pour traiter plusieurs connexions.



Le nombre maximal de sessions simultanées est actuellement fixé à quatre.



Le dictionnaire partagé du gestionnaire de clients est protégé par un verrou `threading.Lock`.



Deux sessions TCP simultanées ont été testées avec succès le 23 novembre 2026.



\## 6. Agent Windows V4



L'agent Windows V4 prend en charge :



\- L'identification auprès du serveur.

\- La transmission des informations système.

\- Les échanges PING/PONG.

\- Les diagnostics autorisés `date`, `ordinateur` et `windows`.

\- Le refus des commandes non autorisées.

\- Les tentatives limitées de reconnexion.



Les modules de registre et de capture d'écran ont également fait l'objet de tests locaux.



Les demandes distantes `registry` et `screenshot` renvoient actuellement un statut informatif, sans déclencher ces opérations.



Le module d'audit SAM demeure expérimental ; aucune récupération effective de données protégées n'a été démontrée.



\## 7. Installation et lancement



\### Prérequis



\- Python 3 installé sur Kali Linux.

\- Un environnement VMware configuré avec un réseau Host-only.

\- L'agent Windows V4 ou son exécutable préparé sur Windows 11.

\- Les fichiers du projet disponibles sur les machines concernées.



\### Démarrer le serveur Kali



Dans le terminal Kali, depuis le répertoire du projet :



```bash

python3 -m serveur.main

```



Le serveur affiche notamment :



```text

\[SERVEUR] Demarrage Kali V5

\[SERVEUR] Maximum clients simultanes : 4

\[SERVEUR] En attente sur 192.168.109.129:5001

```



\### Démarrer l'agent Windows



Dans le CMD de la machine virtuelle Windows 11, depuis le dossier contenant l'exécutable :



```cmd

agent-windows-v4.exe --ip 192.168.109.129 --port 5001

```



L'agent établit une connexion TCP avec Kali et traite les demandes prévues par le serveur.



\### Agent Debian



Les instructions définitives seront ajoutées après réception et validation du code de l'agent Debian.



\## 8. Tests réalisés



Les validations suivantes ont été effectuées :



| Test | Résultat |

|---|---|

| Connexion Windows–Kali | Réussi |

| Identification HELLO / HELLO\_ACK | Réussi |

| Échange PING / PONG | Réussi |

| SYSINFO / RESULT | Réussi |

| Diagnostic Windows `date` | Réussi |

| Refus d'une commande non autorisée | Réussi lors des tests Windows précédents |

| Gestion des erreurs de connexion | Réussi |

| Journalisation des erreurs Kali | Réussi |

| Enregistrement et déconnexion des clients | Réussi |

| Gestion concurrente de dix clients simulés dans le gestionnaire | Réussi |

| Deux sessions TCP parallèles sur Kali V5 | Réussi |

| Intégration complète Debian | À vérifier |



Les captures et les journaux associés aux tests doivent être conservés avec les preuves du rapport.



\## 9. Limites actuelles



Les limites identifiées sont :



\- L'intégration complète de l'agent Debian reste à réaliser.

\- Le démarrage automatique de l'agent Windows n'a pas été validé.

\- Certaines fonctionnalités Windows sont disponibles uniquement lors de tests locaux.

\- L'audit SAM n'a pas permis de démontrer une récupération effective de données protégées.

\- Les communications TCP/JSON ne disposent pas d'une authentification applicative ou d'un chiffrement démontrés.

\- Le comportement du serveur avec quatre clients simultanés n'a pas encore été testé ; le test réseau a porté sur deux sessions.



Les fonctionnalités non vérifiées ne sont pas considérées comme validées.



\## 10. Organisation GitHub



\*\*Dépôt :\*\* https://github.com/Idi18/projet-ethical-hacking



\*\*Branche d'intégration Windows–Kali :\*\* `windows-integration`



\*\*Dernier commit vérifié :\*\* `dbfca02`



Cette branche contient l'agent Windows V4, le serveur Kali V5 et leur documentation.



L'intégration de Debian devra être effectuée après comparaison des branches et vérification du protocole commun.



Une fusion vers `main` ne sera réalisée qu'après les tests d'intégration.



\## 11. Documentation



Pour davantage d'informations :



\- `docs/WINDOWS\_AGENT.md` : conception et tests de l'agent Windows.

\- `docs/INTEGRATION\_WINDOWS\_KALI.md` : protocole commun et résultats d'intégration.

\- `docs/screenshots/` : emplacement prévu pour les preuves visuelles.



\## 12. Conclusion



Le projet dispose d'une communication opérationnelle entre un agent Windows V4 et un serveur Kali V5.



Le serveur prend en charge les diagnostics autorisés, la gestion des clients, les erreurs et les connexions TCP parallèles grâce aux threads.



Les résultats obtenus constituent une base fonctionnelle pour l'intégration du client Debian et les essais finaux.



La conformité complète aux exigences du projet devra être vérifiée avant la remise.

