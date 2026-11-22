\# Documentation technique — Agent Windows



\## 1. Présentation



L'agent Windows est une composante du projet universitaire Ethical Hacking, développé en Python dans un environnement de laboratoire VMware.



Il communique avec un serveur TCP situé sur une machine virtuelle Kali Linux. Les messages échangés utilisent le format JSON, avec un protocole commun défini dans `shared/protocol.py`.



\## 2. Architecture du laboratoire



| Machine | Adresse IP | Fonction |

|---|---|---|

| Windows 11 (ordinateur hôte) | 192.168.109.1 | Agent Windows |

| Kali Linux (VMware) | 192.168.109.129 | Serveur de test TCP |

| Debian Linux (VMware) | 192.168.109.133 | Client Linux de test |



Le réseau VMware VMnet1 (Host-only) permet aux machines de communiquer localement, sans nécessiter d'accès Internet.



\## 3. Fichiers de la partie Windows



\- `agents/windows/main.py` : programme principal, connexion TCP et traitement des messages JSON.

\- `agents/windows/registry.py` : modification locale d'une valeur de registre Windows.

\- `agents/windows/security\_audit.py` : fonction locale de capture d'écran encodée en Base64.

\- `agents/windows/sam\_audit.py` : module expérimental lié aux ruches SAM et SYSTEM, non intégré à l'agent principal.

\- `shared/protocol.py` : structure commune des messages JSON.



\## 4. Fonctionnalités validées



\### Communication TCP/JSON



L'agent peut se connecter à un serveur TCP, transmettre son identification et répondre à certains messages.



Les échanges suivants ont été testés avec succès :



\- `HELLO` : identification de l'agent, de son système d'exploitation et de ses adresses IP.

\- `HELLO\_ACK` : confirmation d'identification envoyée par le serveur.

\- `PING` / `PONG` : contrôle de communication.

\- `SYSINFO` / `RESULT` : transmission des informations générales sur le système Windows.



Les messages sont délimités par des retours à la ligne pour permettre leur lecture sur une connexion TCP.



\### Registre Windows



La fonction locale `add\_registry\_key()` a été testée avec succès.



Valeur vérifiée :



`HKEY\_CURRENT\_USER\\Software\\MonProjetTP`



`Status = Actif`



Dans la version actuelle de `main.py`, le message `REGISTRY` renvoie uniquement un statut de disponibilité et ne déclenche pas de modification à distance.



\### Capture d'écran locale



Le module `security\_audit.py` contient une fonction capable de réaliser une capture locale et de l'encoder en Base64.



Cette fonction a été testée localement. Le message `SCREENSHOT` reçu par l'agent principal renvoie uniquement un statut et ne déclenche pas de capture à distance.



\## 5. Exécution de l'agent



Depuis le dossier principal du projet, avec l'environnement Python configuré :



```cmd

.\\venv\\Scripts\\python.exe agents\\windows\\main.py --ip 192.168.109.129 --port 5001

```



Une version exécutable a également été générée avec PyInstaller :



`dist\\agent-windows-v2.exe`



Commande de lancement :



```cmd

dist\\agent-windows-v2.exe --ip 192.168.109.129 --port 5001

```



Ces exemples nécessitent qu'un serveur compatible soit déjà démarré sur Kali.



\## 6. Résultats des tests



Les tests suivants ont été réalisés :



| Test | Résultat |

|---|---|

| Connectivité réseau Windows–Kali | Réussi |

| Connexion TCP locale Windows | Réussi |

| Échange HELLO / HELLO\_ACK | Réussi |

| Échange PING / PONG | Réussi |

| Échange SYSINFO / RESULT | Réussi |

| Exécution du programme compilé | Réussi |

| Communication de l'exécutable avec Kali | Réussi |

| Modification et lecture locales du registre | Réussi |

| Vérification des protections Microsoft Defender | Trois protections déclarées actives |

| Consultation des permissions du fichier SAM | Accès refusé depuis le terminal utilisé |



\## 7. Limites et travaux restants



\- Le serveur Kali utilisé pour les tests est un programme de démonstration, distinct du serveur principal du projet.

\- Les traitements `REGISTRY` et `SCREENSHOT` du programme principal ne réalisent aucune action distante.

\- Les messages `CMD` et `SAM\_AUDIT` ne sont pas pris en charge dans la version actuelle de `main.py`.

\- L'intégration avec le serveur Kali définitif reste à réaliser.

\- Un ancien processus `agent-windows.exe` fonctionne dans Windows et son origine doit encore être identifiée.

\- Les fonctionnalités finales devront être comparées aux consignes officielles avant la remise.



\## 8. Preuves et captures



Les captures d'écran sont conservées séparément pour documenter les différentes étapes.



Parmi les preuves réalisées :



\- `21\_test\_tcp\_executable\_v2\_serveur.png`

\- `22\_test\_tcp\_executable\_v2\_agent.png`

\- `23\_test\_tcp\_windows\_kali\_serveur.png`

\- `24\_test\_tcp\_windows\_kali\_agent.png`

\- `27\_audit\_permissions\_sam\_windows.png`

\- `28\_verification\_registre\_windows.png`

\- `29\_verification\_defender\_windows.png`



Les captures constituent des preuves des tests effectués, et non une validation automatique de toutes les exigences du projet.



\## 9. Conclusion



La partie Windows dispose d'un agent Python capable de communiquer avec un serveur TCP/JSON. Sa version exécutable a été compilée et testée avec succès, notamment lors d'une communication avec Kali Linux dans le laboratoire VMware.



Les fonctions locales du registre, de capture d'écran et plusieurs contrôles de sécurité ont également été examinés. La prochaine étape consiste à vérifier la conformité aux exigences finales et à intégrer l'agent au serveur principal du groupe.

