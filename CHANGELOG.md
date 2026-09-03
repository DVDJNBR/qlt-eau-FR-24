# CHANGELOG


## v1.2.1 (2026-09-03)


## v1.2.0 (2026-09-03)

### Bug Fixes

- **dark-mode**: Carte 100% sans mapbox + popup dropdown + mois pleine hauteur
  ([`8aaf410`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/8aaf410ca8836a19628157d7ed0be021e0bea4d4))

- Migration Choroplethmapbox -> Choropleth (go.Choropleth, layout geo au lieu de mapbox). Elimine
  definitivement la dependance a un fournisseur de tuiles (Carto, puis white-bg de secours) : plus
  de fond blanc en dark mode, plus jamais de risque qu'un tiers exige une cle API un jour.
  fitbounds="locations" remplace le calcul manuel de centroide/zoom (get_dept_commune_geo simplifiee
  en consequence). Perte du pitch 3D sur la carte nationale (les traces geo sont plates, pas de
  mapbox-gl) : compromis assume pour un fond de carte fiable. - Popup des selectbox
  (departement/commune) : rendu dans un portail attache a <body>
  (data-testid="stSelectboxVirtualDropdown"), hors de portee du CSS scope a .stApp -> restait blanc
  en dark mode malgre le fix precedent sur le select ferme. Cible directe du portail. - Pills des
  mois : espacement egal (justify-content: space-between) sur toute la hauteur de la carte au lieu
  d'un gap fixe qui laissait un grand vide sous les 12 boutons.

Non testable en local : les inserts DOM-TOM (le jeu de donnees local n'a aucune ligne pour
  971/972/973/974/976) - a verifier une fois deploye.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM

### Features

- **ui**: Page a onglets - A propos / Circulation de la donnee / Architecture
  ([`1472ab7`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/1472ab7b574282109f1bd7e350b6f1605b3e696e))

Trois onglets sous les graphiques, contenu repris du README (stack, pipeline Bronze-Silver-Gold,
  star schema Gold) : - A propos : pitch du projet + badges tech (Azure, Databricks, Terraform,
  Delta Lake, Python, FastAPI, Streamlit, Hub'Eau API) + lien GitHub. - Circulation de la donnee :
  flow Hub'Eau -> Bronze -> Silver -> Gold -> Quality Checks -> API REST, couleurs alignees sur les
  diagrammes mermaid du README. - Architecture cloud & BDD : cartes services Azure + detail du star
  schema Gold (dimensions/faits/agregats).

Ajout d'un helper _md_html() : le HTML multi-niveaux interpole (ex. boucle generant des <div>
  imbriques) peut deborder de l'indentation du template englobant et se faire interpreter comme un
  bloc de code Markdown au lieu de HTML brut. Le helper retire l'indentation de chaque ligne avant
  st.markdown(..., unsafe_allow_html=True).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.1.0 (2026-09-03)

### Features

- **ui**: Manometre de conformite (theme tuyauterie)
  ([`6c31cba`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/6c31cbacd34c13b84a97b96476955c2838d93b22))

Remplace le chiffre brut "Conformite" par un vrai manometre (jauge a aiguille, bandes
  rouge/orange/vert 70-80/80-95/95-100), inspire des refs manometres/tuyauterie fournies. Place dans
  la ligne des KPI (colonne ~250px) plutot qu'a cote des pills mois (colonne trop etroite pour
  qu'une gauge angulaire Plotly se dessine sans se faire rogner).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.0.0 (2026-09-03)

### Bug Fixes

- Adjust streamlit pills CSS to support recent DOM changes
  ([`434751b`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/434751b7136e2fd27e47ca9fddd1f32c3b71d1c7))

Streamlit changed the DOM structure for `st.pills`. This commit updates the injected CSS selectors
  from `button[role="radio"]` to `button[data-testid^="stBaseButton-pills"]`. It also properly
  configures flex layout for the new `stButtonGroup` container to restore the full-width centered
  layout of the month pills, and fixes the dark mode color inheritance for the p tags within the
  pills.

Co-authored-by: DVDJNBR <235466974+DVDJNBR@users.noreply.github.com>

- Center month pills in Streamlit app\n\nUpdates the custom CSS rules for `stButtonGroup` to ensure
  the month selection pills are correctly centered on the page instead of left-aligned.
  ([`7f9a63d`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/7f9a63d471e16ad6909d0b021d47577a5e4a76d6))

Co-authored-by: DVDJNBR <235466974+DVDJNBR@users.noreply.github.com>

- Dark mode pills/bouton retour + pills pleine largeur
  ([`567d127`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/567d1272d8f1a5fe7c8e293dcec83063b43a27e5))

- Cibler button[role="radio"] (attribut réel des pills Streamlit) pour fond sombre + texte clair en
  dark mode - Cibler .stButton > button pour le bouton retour en dark mode - .stButton >
  button:disabled : fond très sombre, texte grisé - Pills : flex: 1 1 auto sur button[role="radio"]
  pour étalement complet

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Dark mode — pills mois, selectbox et header blanc
  ([`f9d1f97`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/f9d1f972e5144055118f0f668960b1196aeb39a0))

- config.toml : thème sombre par défaut (primaryColor/bg/text sombres) → les widgets natifs (pills,
  selectbox) héritent du thème correct → supprime le bandeau blanc en haut causé par
  backgroundColor="#ffffff" - CSS mode sombre simplifié (config.toml gère déjà les widgets natifs) -
  CSS mode clair revu pour surcharger agressivement le thème sombre : fond, header, pills,
  selectbox, dropdown, labels

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Déployer via un compte dédié (deploy) sans TOTP au lieu de ubuntu
  ([`90ff111`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/90ff111796155549dba4c4649bdc81723f87ca0f))

Le client SSH utilisé par appleboy/ssh-action ne sait pas répondre au second facteur
  (keyboard-interactive/TOTP) exigé pour le compte ubuntu, ce qui bloquait systématiquement le
  déploiement après le fix de port. Le compte "deploy" est restreint côté serveur (Match User + clé
  forcée à une seule commande), donc pas besoin de TOTP pour lui.

- Explicit light mode CSS to handle theme toggle correctly
  ([`0bb28c4`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/0bb28c4a705e9ae5ef084d105e908081ac319fe4))

- Force-recreate container on deploy to avoid name conflict
  ([`c2ac332`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/c2ac332948fe9186c31fecb4e76d95e4c87b7ee7))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Indentationerror and duplicate function definition in st_main.py
  ([`ddd1834`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/ddd1834712cc3ea8a24c45cc5a03f37a8461c46f))

- Mode sombre, centrage mois, max-width
  ([`17c3657`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/17c365796564c1c4d9c2d8c25dfd0054feb3a8dc))

- Injecter le CSS light (fond blanc) quand dark_mode=False pour éviter que le fond noir persiste au
  passage en mode clair - Cibler .stApp et ses enfants avec !important pour forcer le thème -
  Centrer les pills mois via flexbox (justify-content: center) - Limiter la largeur du conteneur à
  1200px par défaut

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- More aggressive CSS for background toggle and add base theme config
  ([`346820e`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/346820e9f9d088cb766b2d3a5a6ad1df9d102af4))

- Pills pleine largeur, retour toujours visible, thème clair robuste
  ([`01a6347`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/01a6347bbe5afcc59906f0c6ba96e0cf32f5f7ca))

- Supprimer default= sur st.pills (évite le warning session state) - Bouton retour toujours affiché,
  disabled+grisé sur vue France - Pills étalées sur toute la largeur (flex: 1 1 auto /
  space-between) - config.toml base=light : Streamlit génère du CSS clair nativement, le dark mode
  est entièrement géré par CSS injecté (BaseUI, header, pills) - CSS dark renforcé pour couvrir
  selectbox, menu, pills, header

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Préciser le port SSH (5790) du VPS dans le workflow de déploiement
  ([`9f8eb14`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/9f8eb1404ccf030f6c112548509446fe45b83fa7))

Le SSH du VPS n'écoute pas sur le port 22 par défaut, ce qui faisait timeout l'étape de déploiement
  (appleboy/ssh-action).

- Remplacer carto-darkmatter/positron par white-bg (Carto exige une clé API)
  ([`3528ceb`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/3528cebea379171551189820b2f4bc5cc808a605))

Carto a rendu obligatoire une clé API pour ses tuiles de fond de carte, cassant la carte choroplèthe
  déployée ("API KEY REQUIRED" en watermark). white-bg n'a besoin d'aucune tuile ni clé.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM

- Resolve st.pills warning and force dark mode by default
  ([`fc3bf60`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/fc3bf60ee5b2799e3971b3bc9c42957005ce07b2))

- Restaure st_main original + thème sombre natif via config.toml
  ([`05aac10`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/05aac102d72c32ad6fae8d47a9f022d867aae0e2))

- Restaure st_main.py depuis bd1efc3 (dernière version fonctionnelle) avant les tentatives CSS de
  Gemini qui cassaient pills/selectbox - dark_mode = True par défaut - config.toml : base="dark" +
  couleurs sombres → Streamlit applique le thème sombre nativement aux widgets (pills mois,
  selectbox dept/commune, header) sans besoin de CSS overrides fragiles

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Thème clair robuste, mois centrés, titres Plotly lisibles
  ([`4151f80`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/4151f8073031a986c85f07ceb875e2913dedbe10))

- CSS clair : cibler les composants BaseUI (select, input, menu, pills) pour forcer couleurs de
  fond/texte blancs en mode light - Centrage pills : flex+wrap+justify-center sur plusieurs
  sélecteurs pour couvrir toutes les versions de Streamlit - PLOTLY_FONT_COLOR : couleur de police
  explicite transmise à tous les update_layout (title, axes, légendes) pour éviter les titres trop
  clairs - config.toml : thème de base dark avec variables Streamlit pour aligner les widgets sur le
  thème par défaut

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **api**: Pass app object directly to uvicorn instead of module string
  ([`6e40c32`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/6e40c3287bb361279870eeee4da67480ac57f65a))

Running as `python scripts/api_qualite_eau.py` fails with ModuleNotFoundError because scripts/ is
  not a Python package. Passing the app object directly avoids the module resolution entirely.
  reload=False since hot reload requires the string form.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **dark-mode**: Fond de carte noir + pills et champs de recherche corriges
  ([`2f0ee10`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/2f0ee107f04cbedb86c201b9025341d4a7b19bdd))

- Mapbox custom (calque background sans source, donc sans cle API) pour un fond de carte sombre en
  mode nuit, au lieu du white-bg toujours clair. - Selecteurs CSS pills mis a jour : Streamlit 1.56+
  n expose plus les data-testid stBaseButton-pills(Active), on cible data-variant="pills" et
  aria-checked. - Icones de dropdown (departement/commune) et popovers BaseWeb visibles en dark mode
  (fill svg + fond menu).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM

- **deps**: Replace deltalake with deltalake[pyarrow] for read support
  ([`db5a130`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/db5a130164649b7c0fd751f314319721d6759bac))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **readme**: Replace \n with <br/> in Mermaid node labels
  ([`ac21d86`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/ac21d866deb6b29c4cc0a16d223f09f3c83ebbb0))

GitHub's Mermaid renderer displays \n literally — <br/> is required for line breaks in node labels.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### Build System

- Add Docker configuration for deployment
  ([`63be6ad`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/63be6ad4277f55e5d9446e54d5cc5fc3a05436d6))

* Add `Dockerfile` to containerize the Streamlit application using Python 3.13-slim and `uv` package
  manager for fast dependency installation. * Add `docker-compose.yml` defining the `streamlit-app`
  service, mapping port 8501. * Add `.dockerignore` to exclude unnecessary files like `.venv`,
  `.git`, and `app/data` (which contains large parquet and geojson files not needed in the image
  since they might be downloaded or mounted, or it might be better to keep the image slim if data is
  volatile, actually the data files probably are needed if they are shipped, but `.dockerignore`
  will reduce context size and we can adjust if needed). * Wait, looking at `st_main.py`, it
  downloads data if missing. * This resolves the `docker compose build` failure in the `test-build`
  CI job caused by missing configuration files.

Co-authored-by: DVDJNBR <235466974+DVDJNBR@users.noreply.github.com>

### Chores

- Clean up repo and rewrite README
  ([`5f4ea01`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/5f4ea013a2fcf74ba4e79689c626ef5e2ae31c4b))

- Remove tasks.py tracking was kept (useful for infra reproducibility) - Update .gitignore: add
  _bmad/, .claude/, .gemini/, logs/, node_modules/, NOTES_PERSO.md, PROJECT_STATUS.md, test
  notebooks, and fix formatting bug - Rewrite README with full architecture, table inventory, and
  usage guide

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Remove semantic release workflow (unused)
  ([`e5d7e83`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/e5d7e83eeedbcaad396ccda3d1024e4029047813))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Touch app to trigger deploy
  ([`b6cfb7d`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/b6cfb7dd05815276a9e4030f2352cc0ed030a11a))

- **gitignore**: Remove .cloud/ from tracking (local infra only)
  ([`b69a3dc`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/b69a3dc9a95b7fc3d95074c39b1b90b7e0d7fb6e))

Terraform config contains subscription-specific values and is managed locally. Deploy with `invoke
  azure-deploy` as documented in README.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **main**: Add missing notebooks and remove unused CHANGELOG
  ([`6ca15a4`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/6ca15a425f6a6a5211a91144f6eea7cbb5fc131d))

- Add notebooks 02_Silver, 03_Gold, 04_Quality_Checks (were only on feature branches) - Remove
  CHANGELOG.md (semantic release not used in this project)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **tasks**: Remove emojis from tasks.py
  ([`575ba87`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/575ba870a6b943933d8861bac80d0f1819a10f36))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **tasks**: Remove unused imports, duplicate logger config, bare excepts
  ([`292b3bd`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/292b3bdf1eb5c64df841b19aa25fefbecbf73228))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### Code Style

- Comprehensive dark mode CSS for widgets and metrics
  ([`fbbf44d`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/fbbf44d30a328c5122a990e8f9474fae2b3c9277))

- Limit app max-width for better readability
  ([`c536cb6`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/c536cb6d68ffa2f83a7218a155f5e23778560b18))

- Ultra-aggressive CSS selectors for dark mode widgets
  ([`c1b079c`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/c1b079cfdcb88069f7f26f260ae01af18ddba232))

- Unified KPI cards and extreme CSS for dark mode widgets
  ([`27d0e0e`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/27d0e0eb22ec3bf9dc716aef178661b4e5a9ac3d))

### Continuous Integration

- Ajout workflow GitHub Actions deploy vers VPS
  ([`abee90c`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/abee90cd3f0f9d9e59355c8c14bc8bb8a608468b))

Déploiement automatique sur push main (app/**) : - rsync app/ → VPS (hors data/ et __pycache__) -
  docker compose build --no-cache + up -d

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Ajout workflow_dispatch + trigger deploy
  ([`87f0c13`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/87f0c13bbfab4bd48bc09783d53aa0bd74270ab3))

- Ip VPS en secret (VPS_IP) au lieu d'être hardcodée
  ([`f9890f3`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/f9890f37e0e5dddfe37b055704e29725cb08dad1))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Trigger deploy après ajout workflow
  ([`791fb60`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/791fb607d055d85f48569584a1086d2d5c7a1bd8))

### Documentation

- Fix layoutDirection LR pour les ER diagrams (guillemets JSON)
  ([`0e9f024`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/0e9f024f94cf61e60f0ed5ec30b8ab8bfa57a4c6))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Galerie screenshots dans le README
  ([`ef26405`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/ef264052e3f5d204559379e502806a4ce1053165))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Galeries screenshots contextuelles (app / databricks / api)
  ([`0f7aa32`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/0f7aa328fe3cb14508bdd0b0ec6f7395810c2495))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Schémas erDiagram → classDiagram direction LR (layout horizontal)
  ([`64375d3`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/64375d3f05e1fa1de5b8fd1fce7e42e5e3875452))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Section Dashboard d'analyse avec lien et galerie app
  ([`21c1180`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/21c118033add1f390341e1da8c3e199980addac7))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Sommaire cliquable + assets screenshots nommés
  ([`b55dfaa`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/b55dfaa2556a9ac810b1f3a6dc049f6a5ddb052a))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **readme**: Learning context, tech badges, split architecture diagrams
  ([`3a06a77`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/3a06a77d38c0158508149c3f9e101029500b882e))

- Add shields.io badges (Azure, Databricks, Terraform, Delta Lake, Python) - Clarify project is a
  data engineering learning project - Split architecture into 2 diagrams: notebook pipeline (LR) +
  data layers (TD) - Bronze/Silver/Gold color coding, no emojis in diagrams - Subgraph styling for
  data layers diagram

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **readme**: Restructure with context, task-based setup, and erDiagram schemas
  ([`ab7698d`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/ab7698d21dcfbe7f67adb7f54d0ef9dc020926fd))

- Open with project purpose before architecture diagram - Reorder sections: context → reproduce
  (tasks) → data schemas - Replace tables list with 3 erDiagram (Bronze / Silver / Gold) showing
  actual columns and relationships per layer

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### Features

- **ci**: Reinstaller python-semantic-release
  ([`ac91696`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/ac916962ce5d30bd814fe4837e6f45df52d797f7))

Deja configure une fois (commit 452a342, release v0.1.0 en 2025-10-29), puis retire (e5d7e83,
  "unused") lors d une reecriture du pyproject.toml qui a fait disparaitre la section
  [tool.semantic_release]. Remis en place a l identique : meme parser (allowed_tags
  feat/fix/docs/style/ refactor/perf/test/build/ci/chore, minor=feat, patch=fix/perf), meme workflow
  GitHub Actions sur push main.

Le pyproject.toml affichait deja version = "1.0.0" (bump manuel, desynchronise du tag v0.1.0) : un
  tag v1.0.0 est cree sur ce commit pour servir de nouvelle base, plutot que de laisser
  semantic-release repartir de v0.1.0 et recalculer une version inferieure a partir de tous les
  commits feat/fix/perf accumules depuis octobre.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM

- **env**: Add .env.example and auto-preserve DATABRICKS_TOKEN in env-save
  ([`e73f9ce`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/e73f9ceceb6f872b01c937e16d406d6b8e38d4d3))

- Add .env.example documenting all required variables with setup instructions - env-save now
  preserves existing DATABRICKS_TOKEN and DATABRICKS_NOTEBOOKS_PATH (these can't be fetched from
  Terraform; token must be created manually) - env-save warns when DATABRICKS_TOKEN is still empty
  after save

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **scripts**: Add orchestration workflow creator and REST API
  ([`646f509`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/646f50990d3fe66cab75bd3a2c19879426999314))

- scripts/create_workflow.py: creates Databricks job Pipeline_Qualite_Eau_Complet via REST API (4
  tasks in sequence, daily schedule at 02:00 Paris, paused by default) - scripts/api_qualite_eau.py:
  FastAPI exposing Gold tables from ADLS via deltalake (no Databricks compute required), endpoints
  for conformite/communes/parametres/stats - README: rewrite with Mermaid architecture diagrams and
  full usage guide - pyproject.toml: add fastapi, uvicorn, deltalake, databricks-sdk deps, remove
  semantic_release config (unused)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **ui**: Add styled custom HTML/CSS header with droplet SVG icon
  ([`59f6fe4`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/59f6fe45a891dfd7c407d0171e3737a523dd4814))

Co-authored-by: DVDJNBR <235466974+DVDJNBR@users.noreply.github.com>

- **ui**: Mois empiles verticalement a gauche de la carte + perf caching
  ([`a9b1ee9`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/a9b1ee93d8d3698f9f3d4d9d52b463d3b8e2b713))

- Colonnes [1.4, 8.6] : pills des mois a gauche, carte a droite (plus de scroll pour changer de
  mois), max-width bloc porte a 1400px. - load_data() passe en cache_resource (cache_data
  copie/re-serialise a chaque acces, prohibitif avec un GeoJSON communes de ~45 Mo). - Pre-calcul
  commune_name_to_code / sorted_communes / dept_options dans load_data() au lieu de retrier ~35 000
  noms a chaque rerun. - get_dept_commune_geo() et build_conformity_trend/build_commune_trend mis en
  cache (cache_resource / cache_data) au lieu de recalculer le centroide et les tendances a chaque
  interaction. - Suppression de df_raw (charge mais jamais utilise). - Carte encadree (fond sombre,
  coins arrondis) : white-bg reste blanc (seul style mapbox sans cle), habille en carte plutot que
  bord-a-bord.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM

- **ui**: Redesign header - logo badge + lockup nom/scope
  ([`a3be564`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/a3be564c42c21d01d40ec489ba73460adae69414))

- Icone remplacee par un badge carre a coins arrondis (degrade bleu + ombre portee), goutte blanche
  avec reflet en trait fin, plus proche d un logo d app que d une icone flottante. - Titre
  restructure en lockup a la watt-watcher : eyebrow uppercase "SUIVI QUALITE DE L'EAU POTABLE" + nom
  de la portee courante (France ou departement selectionne) suivi de "2024" en degrade bleu, au lieu
  d une seule longue phrase.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM

### Performance Improvements

- Éviter le re-parsing JSON du geojson départements à chaque rerun
  ([`3617f8a`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/3617f8a0caf10e3d030ad324d1514396de01a3c5))

La vérification de validité de departements.geojson tournait au niveau module, donc à chaque rerun
  Streamlit (clic utilisateur), pas juste au premier chargement. Mise en cache via
  @st.cache_resource pour n'exécuter le check/téléchargement qu'une seule fois par cycle de vie du
  conteneur.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### Refactoring

- Migrate deploy to git pull pattern (like tictactoe/portfolio)
  ([`59e4adb`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/59e4adb5f0d098d6fbf80f32adfac961e700e8ab))

- Remove rsync step, VPS now clones/pulls from GitHub directly - Auto-init: clones repo on first
  run, preserving existing data/ - Trigger on all pushes to main (not just app/**)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>


## v0.1.0 (2025-10-29)

### Features

- Add Hub'eau API ingestion and Semantic Release configuration
  ([`452a342`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/452a34264100bb9417b4f043ad5af21c0f5c61fa))

- Add Bronze layer ingestion notebook with Hub'eau API integration - Add test notebook for
  Databricks and Azure Data Lake connection - Configure Semantic Release with Python Semantic
  Release - Add GitHub Actions workflow for automated versioning - Update notebooks with incremental
  ingestion logic (day-by-day)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
