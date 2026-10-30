# Mettre Harvest en ligne (gratuit, avec Vercel)

Structure :
- `public/` : le site (index.html, styles.css, app.js) — inchangé
- `api/prices.py` : remplace server.py, tourne sur Vercel (la clé API reste côté serveur)
- `vercel.json`

## Étapes
1. Créez un dépôt GitHub et envoyez-y tout ce dossier (le `.env` n'est PAS envoyé).
2. Sur https://vercel.com : « Add New → Project » → importez le dépôt → Deploy.
3. Dans le projet : Settings → Environment Variables → ajoutez
   `DATA_GOV_IN_API_KEY` = votre clé data.gov.in (Production + Preview), puis Redeploy.
4. Votre site est en ligne sur `https://votre-projet.vercel.app`.

Sans GitHub : installez Node, puis `npx vercel` dans ce dossier, et `npx vercel env add DATA_GOV_IN_API_KEY`.

## Ajouter des données / du code
- Nouvelle culture : ajoutez-la dans `dataset` (public/app.js) et dans `ALIASES` (api/prices.py).
- Nouvelle source de données : créez un fichier `api/xxx.py` (même modèle que prices.py) → disponible sur `/api/xxx`.
- Chaque `git push` redéploie automatiquement le site.
