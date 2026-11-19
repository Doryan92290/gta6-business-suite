# Studio de montage vertical — MVP

Ce module génère un **brouillon**, jamais une publication automatique.

## Premier essai (depuis un iPhone)
1. GitHub : **Actions** → **Studio vertical GTA VI (brouillons)** → **Run workflow**.
2. Laisser **demo = true** puis lancer. Cette vidéo est créée de zéro (aucun clip Twitch ni contenu Rockstar).
3. Ouvrir l'exécution terminée, descendre aux **Artifacts**, télécharger **clip-vertical-brouillon**.
4. Le ZIP contient : **clip_vertical.mp4** (format 720×1280), **subtitles.srt**, **thumbnail.jpg**, **caption.txt**, **manifest.json**.

## Avec une vraie vidéo autorisée
1. Obtenir une autorisation de montage et de diffusion sur chaque plateforme, pour l'image ET le son.
2. Mettre la source MP4 sur une adresse **HTTPS publique directe**. Ne jamais utiliser une URL privée ou signée : les paramètres des runs sur ce dépôt public peuvent être visibles.
3. Sélectionner **demo=false**, cocher **rights_confirmed**, remplir le lien MP4, le titre, le créateur, le mode blur/crop et la durée de 1 à 90 s.
4. Le script extrait un segment, convertit en 9:16, transcrit les paroles localement via le modèle CPU **faster-whisper tiny**, incruste les sous-titres, ajoute le crédit, fabrique une miniature et une légende.
5. Relire les sous-titres et **regarder entièrement la vidéo** avant toute publication. Vérifier les autorisations, les règles des plateformes, et les conditions des campagnes rémunérées.

**Limites :** vidéos sources jusqu'à 250 Mo et 90 s de résultat. Le modèle de transcription peut se tromper. Les sources Twitch détectées par le bot sont seulement des candidats ; elles ne sont pas téléchargées automatiquement. Aucun compte TikTok, YouTube ou Instagram n'est encore connecté ; aucun post n'est envoyé. Le dépôt et les artifacts étant publics, n'y envoyer aucune vidéo confidentielle ni lien d'accès secret.

## Technique
Python 3.12, FFmpeg, faster-whisper (en dehors de la démo). Pas de paiement ni d'API IA payante requise pour le rendu. L'exécution GitHub reste soumise aux limites Actions du compte.