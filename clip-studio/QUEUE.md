# GTA VI Clip Queue — mode sécurisé

À chaque exécution de `clipping_discovery.yml`, le bot Twitch :
1. Cherche les clips récents via l'API Twitch (identifiants stockés dans GitHub Secrets).
2. Produit `candidates.json` en artifact temporaire.
3. Filtre certaines expressions potentiellement sensibles et conserve seulement des métadonnées et des liens Twitch publics.
4. Actualise `web/clips.json`, déclenchant le déploiement GitHub Pages pour `web/clips.html`.

**Ce mécanisme ne télécharge aucune vidéo Twitch**, ne vérifie pas les droits, et ne permet aucune réutilisation par défaut. Le titre seul ne suffit pas à garantir un contenu approprié. L'humain doit regarder chaque extrait avant de l'utiliser.

Pour un vrai montage, récupérer un fichier vidéo qui vous est explicitement concédé (créateur, campagne ou votre propre gameplay) et utiliser manuellement le workflow `Studio vertical GTA VI (brouillons)` en confirmant les droits.

Ne jamais saisir de source vidéo privée ou une URL avec jeton dans les inputs publics de GitHub Actions.
