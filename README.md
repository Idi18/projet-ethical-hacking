

\# Projet Ethical Hacking — Architecture client/serveur Python



\## 1. Présentation



Ce projet universitaire consiste à développer et tester une architecture client/serveur Python dans un laboratoire VMware autorisé.



L'architecture comprend trois composants :

\- \*\*Kali Linux V5\*\* : serveur TCP central, gestion des connexions et diagnostics.

\- \*\*Windows 11 V4\*\* : agent Windows avec diagnostics prédéfinis.

\- \*\*Debian Linux\*\* : agent Linux compatible avec les diagnostics du serveur Kali V5.



Les machines échangent des messages JSON sur TCP.



\## 2. Architecture réseau



| Machine | Adresse IP | Rôle |

|---|---|---|

| Kali Linux | 192.168.109.129 | Serveur |

| Windows 11 virtuel | 192.168.109.134 | Agent Windows |

| Debian Linux | 192.168.109.133 | Agent Linux |

| Windows principal | 192.168.109.1 | Développement et Git |



Réseau : VMware VMnet1 (Host-only).



Port du serveur : \*\*5001\*\*.



Ces adresses sont propres au laboratoire et peuvent changer selon la configuration VMware.



\## 3. Protocole de communication



Les messages sont encodés en UTF-8, au format JSON, et terminés par un retour à la ligne.



Structure générale :



```json

{

&#x20; "type": "ping",

&#x20; "id": "test-001",

&#x20; "data": {}

}

```



Principaux échanges :

\- `hello` / `hello\_ack` : identification.

\- `ping` / `pong` : vérification de la communication.

\- `sysinfo` / `result` : transmission d'informations système.

\- `cmd` / `result` : diagnostics Windows prédéfinis.

\- `error` : signalement d'erreurs.



Le serveur vérifie la correspondance entre les identifiants des demandes et des réponses.



\## 4. Serveur Kali V5



Le serveur comprend :

\- `serveur/main.py` : gestion des sessions TCP.

\- `serveur/socket\_server.py` : réception des connexions.

\- `serveur/clients\_manager.py` : suivi des clients.

\- `serveur/command\_interpreter.py` : préparation et validation des diagnostics.

\- `serveur/error\_handler.py` : journalisation des erreurs.



Le serveur utilise `ThreadPoolExecutor` et un verrou pour protéger les données partagées.



La limite configurée est de quatre sessions simultanées.



Deux connexions TCP parallèles ont été testées. Le fonctionnement avec quatre connexions simultanées n'a pas été validé.



\## 5. Agent Windows V4



Fonctionnalités testées :

\- Connexion TCP à Kali.

\- Identification du client.

\- Réponses `PING/PONG`.

\- Transmission des informations système.

\- Diagnostic prédéfini `date`.

\- Refus des commandes non autorisées.



Les modules de registre et de capture d'écran ont fait l'objet de tests locaux. Leur exécution distante n'a pas été démontrée.



L'audit SAM demeure expérimental.



\## 6. Agent Debian



L'agent Debian initial a été intégré à la branche commune, puis son fichier principal `agents/linux/main.py` a été adapté au protocole JSON utilisé par Kali V5.



Fonctionnalités testées :

\- Connexion TCP Debian → Kali.

\- Identification `HELLO/HELLO\_ACK`.

\- Réponse `PING/PONG`.

\- Réponse `SYSINFO/RESULT`.

\- Fermeture de session.



Le fichier `agents/linux/diagnostic\_client.py` conserve également un client de diagnostic indépendant.



Les fonctions d'exécution de commandes Bash arbitraires à distance ne sont pas reprises dans la version intégrée.



Les modules `filesystem.py` et `security\_audit.py` ne contiennent pas encore d'implémentation.



Le démarrage automatique par service Linux n'a pas été validé.



\## 7. Exécution dans le laboratoire



\### Serveur Kali



Depuis le répertoire racine du projet :



```bash

python3 -m serveur.main

```



\### Agent Windows



Dans le CMD de la VM Windows 11, depuis le dossier de l'exécutable :



```cmd

agent-windows-v4.exe --ip 192.168.109.129 --port 5001

```



\### Agent Debian



Dans le terminal de la VM Debian, avec la version intégrée du fichier principal :



```bash

python3 \~/main.py --ip 192.168.109.129 --port 5001

```



Le chemin Debian ci-dessus correspond à l'emplacement utilisé pour les tests VMware.



\## 8. Résultats des tests



| Test | Résultat |

|---|---|

| Windows → Kali | Réussi |

| Debian → Kali | Réussi |

| HELLO / HELLO\_ACK | Réussi |

| PING / PONG | Réussi |

| SYSINFO / RESULT | Réussi |

| Diagnostic Windows `date` | Réussi |

| Gestion des erreurs serveur | Testée |

| Enregistrement et déconnexion des clients | Réussi |

| Dix clients simulés dans le gestionnaire | Testé |

| Deux sessions TCP parallèles | Réussi |

| Quatre sessions TCP simultanées | Non validé |

| Fonctions Linux supplémentaires | Non validées |



Les captures de tests ont été présentées durant le développement. Leur présence dans le dossier de remise doit être vérifiée séparément.



\## 9. Limites et sécurité



\- Absence d'authentification applicative démontrée.

\- Absence de chiffrement TCP/TLS démontré.

\- Certaines fonctions Windows ont uniquement été testées localement.

\- Modules Linux supplémentaires non implémentés ou non validés.

\- Démarrage automatique des agents non validé.

\- Tests réalisés uniquement dans un environnement VMware autorisé.



\## 10. Organisation GitHub



Dépôt : https://github.com/Idi18/projet-ethical-hacking



Branche d'intégration : `integration-finale`.



Dernier commit vérifié avant la mise à jour de ce README : `31a718a`.



Cette branche réunit :

\- Le serveur Kali V5.

\- L'agent Windows V4.

\- L'agent Debian adapté aux diagnostics du serveur.

\- Le protocole commun et les modules de test.



La branche `main` n'a pas encore fait l'objet d'une fusion finale dans cette procédure.



\## 11. Conclusion



Les tests confirment une communication fonctionnelle entre le serveur Kali V5 et les agents Windows et Debian pour les diagnostics prévus.



Le projet démontre l'utilisation de sockets TCP, d'un protocole JSON commun, de la gestion des clients et du traitement parallèle de connexions.



Les fonctionnalités non implémentées ou non testées sont clairement distinguées des résultats validés.

