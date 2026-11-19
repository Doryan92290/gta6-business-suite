# GTA 6 Business Suite — version déployable

Projet expérimental indépendant, non affilié à Rockstar ou Take-Two.

## Modules
- `web/` : site mobile Guide Leonida et checklist navigateur.
- `automation/` : veille des articles officiels Rockstar ; aucune information de jeu n'est générée automatiquement.
- `clipping-bot/` : repérage des clips Twitch (requiert clés Twitch) ; aucun téléchargement, republication ou diffusion de vidéos sans autorisation.
- `ad-studio/` : modèles de briefs et suivi commercial ; aucun démarchage ni promesse de revenus.

## Configuration
1. GitHub > Settings > Pages > Source = GitHub Actions. Le workflow `deploy.yml` publie `web/`.
2. Actions > « Veille GTA VI » > Run workflow pour tester. Les éventuelles annonces à vérifier sont consignées dans un rapport et peuvent créer une issue.
3. Twitch : ajouter des GitHub Actions secrets `TWITCH_CLIENT_ID` et `TWITCH_CLIENT_SECRET` obtenus sur https://dev.twitch.tv/console/apps. Le workflow Twitch ne fonctionne qu'avec ces clés. Aucun secret ne doit être ajouté au code.
4. Les workflows planifiés s'exécutent sur l'infrastructure GitHub dans les limites du forfait et des politiques de GitHub.

La publication de guides, les publicités, les clips et les publications sponsorisées requièrent une vérification humaine des droits, des faits et des conditions du programme.

Version MVP installée par ChatGPT. Le ZIP GTA6 Business Suite précédemment préparé peut contenir des modèles et scripts supplémentaires qui ne sont pas inclus ici.
