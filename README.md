# Projet Ethical Hacking — Architecture client/serveur Python

## 1. Présentation

Ce projet universitaire consiste à développer et tester une architecture client/serveur Python dans un laboratoire VMware autorisé.

L'architecture comprend trois composants :

- **Kali Linux V5** : serveur TCP central, gestion des connexions, diagnostics et réponses des agents.
- **Windows 11 V4** : agent Windows exécutant des diagnostics prédéfinis.
- **Debian Linux** : agent Linux compatible avec le protocole JSON du serveur.

Les échanges utilisent des sockets TCP et des messages JSON encodés en UTF-8.

## 2. Architecture réseau

| Machine | Adresse IP | Rôle |
|---|---|---|
| Kali Linux | 192.168.109.129 | Serveur TCP |
| Windows 11 virtuel | 192.168.109.134 | Agent Windows |
| Debian Linux | 192.168.109.133 | Agent Linux |
| Windows principal | 192.168.109.1 | Développement et Git |

Le réseau principal utilisé pour les tests est **VMware VMnet1 (Host-only)**.

Le serveur écoute sur le **port TCP 5001**.

Ces adresses correspondent au laboratoire et peuvent changer selon la configuration réseau VMware.

## 3. Protocole de communication

Les messages sont transmis en JSON, encodés en UTF-8 et séparés par un retour à la ligne.

Exemple de message :

```json
{
  "type": "ping",
  "id": "test-001",
  "data": {}
}
```

Les principaux échanges sont :

- `hello` / `hello_ack` : identification et acceptation du client.
- `ping` / `pong` : vérification de la connexion.
- `sysinfo` / `result` : récupération des informations système.
- `cmd` / `result` : exécution des diagnostics Windows autorisés.
- `interfaces` / `result` : récupération des interfaces réseau Linux.
- `error` : signalement des erreurs.

Les identifiants des messages permettent d'associer les demandes aux réponses correspondantes.

## 4. Serveur Kali Linux V5

Le serveur est organisé autour des fichiers suivants :

- `serveur/main.py` : gestion des sessions et enchaînement des diagnostics.
- `serveur/socket_server.py` : réception des connexions TCP.
- `serveur/clients_manager.py` : suivi des clients connectés.
- `serveur/command_interpreter.py` : préparation des commandes autorisées.
- `serveur/error_handler.py` : traitement et journalisation des erreurs.

Le serveur utilise `ThreadPoolExecutor` et un mécanisme de verrouillage pour protéger les données partagées.

La limite configurée est de **quatre sessions simultanées**.

Deux sessions TCP parallèles ont été testées avec succès. Un test complémentaire avec quatre clients simulés s'est terminé avec le résultat `4/4 clients terminés` et `TEST MULTI-CLIENTS REUSSI` (preuve n°63 et script `test_4_clients.py`). Ce test valide ce scénario de charge, sans constituer un test de performance approfondi.

Le serveur est capable de reconnaître les agents Windows et Linux et d'adapter les diagnostics en fonction du système.

## 5. Agent Windows V4

L'agent Windows est développé en Python et a également été compilé sous forme d'exécutable.

Fichier testé dans la VM : `agent-windows-v4.exe`.

Fonctionnalités validées :

- Connexion TCP au serveur Kali V5.
- Identification par `HELLO / HELLO_ACK`.
- Détection de l'adresse IPv4 de la VM hors boucle locale.
- Réponse `PING / PONG`.
- Transmission des informations système Windows.
- Exécution de la commande prédéfinie `date`.
- Réception et validation des résultats par Kali.
- Refus des commandes non autorisées.
- Fermeture correcte de la session.

Le 25 novembre 2026, une nouvelle communication complète a été réalisée entre Windows 11 et Kali V5.

Le serveur a reçu le résultat de la commande `date` avec un code de retour égal à zéro.

### Registre Windows

Le module `agents/windows/registry.py` utilise la bibliothèque Python `winreg`.

Une création de clé a été testée localement sur le Windows principal.

Une vérification manuelle a également été réalisée dans la VM Windows 11 :

- Clé : `HKEY_CURRENT_USER\Software\MonProjetTP`
- Valeur : `Status`
- Type : `REG_SZ`
- Donnée : `Actif`

L'écriture manuelle et la présence de cette valeur dans le registre de la VM ont été confirmées.

Le 26 novembre 2026, le diagnostic REGISTRY a ete valide entre le serveur Kali V5 et la machine virtuelle Windows 11. Le serveur a demande la lecture de la cle HKEY_CURRENT_USER\Software\MonProjetTP et a recu la valeur Status = Actif avec le statut success. La lecture distante est donc validee. En revanche, l ecriture du registre declenchee depuis Kali reste non validee.

### Capture d'écran Windows

Le module `agents/windows/security_audit.py` a été testé localement sur le Windows principal avec succès.

L'exécution de cette fonction depuis l'agent Windows dans la VM et sa réception par le serveur Kali n'ont pas été démontrées.

### Audit SAM

Le fichier `agents/windows/sam_audit.py` contient une fonction expérimentale d'audit.

La récupération effective de la base SAM n'a pas été validée. Les restrictions d'accès et les droits administrateur constituent des limites importantes.

### Démarrage de l'agent Windows

Le lancement manuel fonctionne avec le fichier `lancer-agent.bat`.

Les vérifications réalisées dans la VM montrent :

- Aucune tâche planifiée portant le nom de l'agent n'a été trouvée.
- Le dossier Startup de l'utilisateur est vide.
- La clé `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` ne contient pas l'agent.

Le démarrage automatique au lancement de Windows n'est donc pas validé.

## 6. Agent Debian Linux

L'agent Debian a été intégré au protocole JSON commun utilisé par Kali V5.

Fonctionnalités validées :

- Connexion TCP Debian → Kali.
- Identification `HELLO / HELLO_ACK`.
- Réponse `PING / PONG`.
- Transmission des informations système.
- Réception de la demande `interfaces`.
- Envoi des interfaces et adresses IP à Kali.
- Fermeture normale de la session.

### Diagnostic des interfaces réseau

Le test du 25 novembre 2026 a confirmé que Kali reçoit correctement les adresses réseau de Debian :

| Interface | Adresse IP |
|---|---|
| `lo` | 127.0.0.1 |
| `ens33` | 192.168.109.133 |
| `ens37` | 192.168.104.135 |

Les interfaces `ens33` et `ens37` permettent de récupérer des adresses différentes de localhost.

Le serveur Kali affiche une réponse de type `result`, puis confirme la réussite de la session.

**Preuve : capture n°58 — Diagnostic des interfaces Debian reçu par Kali V5.**

### Autres fonctionnalités Linux

Le fichier principal de l'agent Linux contient des traitements concernant :

- `/etc/passwd`.
- Les permissions de `/etc/shadow`.
- Le parcours récursif des dossiers `/root` et `/home`.
- La capture d'écran.

Les lectures et parcours correspondants ont été observés localement sur Debian (preuves n°60, 61, 62 et 64). Leur exécution complète à travers le protocole agent–serveur n'est pas démontrée. La capture d'écran Debian a échoué en raison de l'accès à l'affichage graphique (preuve n°65).

Le démarrage automatique de l'agent Debian doit également être confirmé par un test après redémarrage de la VM.

## 7. Exécution dans le laboratoire

### Démarrer le serveur Kali

Depuis le dossier racine du projet :

```bash
python3 -m serveur.main
```

Le serveur utilise le port `5001`. La version intégrée du fichier `serveur/main.py` est configurée pour écouter sur `0.0.0.0` (toutes les interfaces) ; dans le laboratoire, les agents se connectent à l'adresse Kali `192.168.109.129`. Cette configuration doit rester limitée au réseau VMware autorisé.

### Démarrer l'agent Windows

Dans la VM Windows 11 :

```cmd
"%USERPROFILE%\Desktop\lancer-agent.bat"
```

Ce fichier lance l'exécutable Windows V4 avec l'adresse et le port du serveur Kali.

### Démarrer l'agent Debian

Depuis le dossier racine du projet contenant le fichier intégré :

```bash
python3 agents/linux/main.py --ip 192.168.109.129 --port 5001
```

Le test final des interfaces a été réalisé sur Debian avec une copie actualisée du fichier principal, nommée `main_nouveau.py`.

## 8. Résultats des tests

| Test | Résultat |
|---|---|
| Connexion Windows → Kali | Réussi |
| Connexion Debian → Kali | Réussi |
| HELLO / HELLO_ACK | Réussi |
| PING / PONG | Réussi |
| SYSINFO / RESULT | Réussi |
| Diagnostic Windows `date` | Réussi |
| Réception des interfaces Debian | Réussi |
| Gestion des erreurs du serveur | Testée |
| Enregistrement et déconnexion des clients | Réussi |
| Dix clients simulés dans le gestionnaire | Testé |
| Deux connexions TCP parallèles | Réussi |
| Quatre clients simulés en parallèle | Réussi (4/4 ; capture n°63) |
| Lecture REGISTRY Windows VMware depuis Kali V5 | Réussi : Status = Actif, statut success (nouvelle capture 62) |
| Déconnexion inattendue et reconnexion Windows–Kali | Réussi (nouvelle capture 63) |
| Écriture manuelle dans le registre Windows 11 | Réussi |
| Écriture du registre depuis l'agent réseau | Non validée |
| Capture d'écran Windows locale | Réussi |
| Capture d'écran distante Windows | Non validée |
| Récupération SAM | Non validée |
| Lecture locale de `/etc/passwd` et permissions de `/etc/shadow` | Vérifiées localement (captures n°60 et 61) |
| Parcours local de `/root` et `/home` | Testé localement (captures n°62 et 64) |
| Capture d'écran Debian | Échec d'accès à l'affichage graphique (capture n°65) |
| Fonctions Linux supplémentaires depuis le serveur Kali | Non validées de bout en bout |
| Démarrage automatique Windows | Non validé |
| Démarrage automatique Debian | À confirmer |

Le ZIP de remise contient 39 captures de preuve (numérotées de manière non continue, jusqu'a la capture 69) et le script `test_4_clients.py`. Certaines captures démontrent des tests locaux, et non des opérations à distance.

## 9. Limites et sécurité

Le projet a été développé et testé dans un environnement VMware autorisé.

Les limites identifiées sont :

- Absence d'authentification applicative démontrée.
- Absence de chiffrement TLS démontré.
- Certaines fonctions Windows ne sont validées qu'en exécution locale.
- Plusieurs fonctionnalités Linux nécessitent des tests complémentaires.
- Démarrage automatique des agents non entièrement validé.
- Restrictions d'accès aux fichiers protégés du système.
- Test de quatre clients simulés réussi, sans campagne de performance ni montée en charge étendue.

Les opérations touchant aux données sensibles des systèmes doivent être limitées au périmètre autorisé du laboratoire.

## 10. Organisation GitHub et livraison

Dépôt GitHub :

https://github.com/Idi18/projet-ethical-hacking

Branche principale : `main`.

Le développement a été réalisé sur les branches `windows-agent`, `windows-integration`, `debian-agent` puis `integration-finale`. La branche `integration-finale` a été fusionnée dans `main` le 27 novembre 2026 via la Pull Request #1 (commit de fusion `4c4a087`), sans conflit. Cette fusion inclut les dernières corrections de l'agent Debian et l'ajout de la fonction fork dans le serveur.

Le projet contient les répertoires suivants :

- `agents/windows/`
- `agents/linux/`
- `serveur/`
- `shared/`
- `docs/`

Il contient également `README.md`, `DEMONSTRATION.md` et `requirements.txt`.

L'archive de remise finale est générée à partir de la branche `main`. Les captures de preuve et le script de test bonus `test_4_clients.py` y sont ajoutés.


## 11. Conclusion

Le projet démontre le fonctionnement d'une architecture client/serveur Python utilisant des sockets TCP et un protocole commun JSON.

Les communications entre le serveur Kali V5 et les agents Windows et Debian ont été validées.

Les diagnostics `PING`, `SYSINFO`, la commande Windows `date`, la lecture REGISTRY (Status = Actif) et la récupération des interfaces réseau Debian ont fonctionné pendant les tests d’intégration. La gestion des déconnexions inattendues et la reconnexion ont également été validées sur VMware.

Le projet comprend également des mécanismes de gestion des clients, de traitement des erreurs et de connexions parallèles.

Le test bonus de quatre clients simulés a réussi (4/4). Les fonctionnalités restant à vérifier sont distinguées des résultats réellement obtenus afin de présenter un bilan fidèle de l'état du projet.

Test du Planificateur Windows : lancement automatique du Bloc-notes apres ouverture de session reussi (preuve 69). Ce test ne valide pas le demarrage automatique de l agent Windows.
