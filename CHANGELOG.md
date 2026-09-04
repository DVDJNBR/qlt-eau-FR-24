# CHANGELOG


## v1.12.4 (2026-09-04)

### Bug Fixes

- **ui**: Boite du selectbox blanche en dark mode (CSS mort, meme cause que les tabs)
  ([`2242355`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/2242355a6589e66db2e8bd7006ae2a8dcbd3e601))

En verifiant s'il restait d'autres selecteurs [data-baseweb=...] morts apres le fix des onglets
  (Streamlit a migre BaseWeb -> react-aria), trouve le meme probleme sur les selectbox
  departement/commune : la boite fermee du champ restait blanche en dark mode, visible et confirme
  au screenshot (les listes deroulantes ouvertes, elles, restaient correctement themees via
  stSelectboxVirtualDropdown, un data-testid toujours valide - seule la boite fermee etait
  affectee).

Remplace [data-baseweb="select/input/base-input/textarea"] par .react-aria-ComboBox (marquage
  actuel) pour la boite, l'input et l'icone. Les regles [data-baseweb="menu"/"popover"] etaient
  redondantes avec stSelectboxVirtualDropdown (deja fonctionnel) - supprimees plutot que reecrites.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.12.3 (2026-09-04)

### Bug Fixes

- **ui**: Onglet actif en vrai badge (le CSS precedent etait mort)
  ([`5420c3d`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/5420c3d27ca81758cf2dea01804b173221193435))

En comparant avec watt-watcher.dvdjnbr.fr (inspiration donnee plus tot dans le projet), l'onglet
  actif ne ressemblait qu'a un simple trait - alors que du CSS "onglet stylise" existait deja.
  Investigation : Streamlit a migre ses tabs de BaseWeb vers react-aria a un moment donne, changeant
  le marquage DOM ([data-baseweb="tab"] -> [role="tab"] / [data-testid="stTab"]). Tout le CSS cible
  sur data-baseweb="tab" etait donc mort silencieusement - ce qui s'affichait etait uniquement le
  style par defaut de Streamlit (texte + soulignement bleu de 2px via un <div
  class="react-aria-SelectionIndicator">), pas notre CSS.

Corrige avec les selecteurs actuels : - [data-testid="stTab"] pour l'onglet, [aria-selected="true"]
  pour l'etat actif. - L'indicateur natif (simple trait) est masque au profit d'un fond teinte bleu
  (rgba(59,130,246,0.16)) + liseré du bas 2px, coins hauts arrondis - un vrai badge plutot qu'un
  trait, dans l'esprit de watt-watcher sans en copier le style exact.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.12.2 (2026-09-04)

### Bug Fixes

- **ui**: Reduit le vide au-dessus des onglets
  ([`1818c85`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/1818c8561d874b8f8fa3c546c6b75b416d685bad))

Streamlit reserve 6rem (96px) de padding-top par defaut sur le block-container, pense pour un gros
  bloc titre. Notre page n'en a plus (kicker/scope vivent dans la banniere native) - il ne restait
  qu'un grand vide entre le haut de la page et les onglets. Reduit a 4.5rem (72px), juste assez pour
  degager la banniere native (60px) plus une petite marge.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.12.1 (2026-09-04)

### Bug Fixes

- **ui**: Premiere passe responsiveness - overlays header + grille de mois
  ([`2fce4d3`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/2fce4d3be11664a4fa90f925362076ae4652bbe3))

- Le kicker ("Suivi qualite de l'eau potable") et le texte de scope/ source ("<departement> - 2024 -
  Source : Hub'Eau API") sont en position fixe a des offsets pixel fixes (left:65px / left:300px)
  calibres pour desktop. Sur un ecran etroit, la longueur variable du texte de scope (selon le
  departement selectionne) risquait de chevaucher le menu natif Streamlit (Deploy / ⋮) ou le toggle
  de theme a droite - purs elements decoratifs, masques via @media (max-width: 768px) plutot que de
  risquer un chevauchement avec des elements cliquables. - Grille de mois (6 colonnes x 2 rangees) :
  en dessous de 640px - seuil interne que Streamlit utilise deja pour empiler ses propres st.columns
  (confirme en inspectant les regles CSS injectees par le framework) - 6 pills par rangee deviennent
  trop etroites pour rester lisibles ; repasse a 3 colonnes (4 rangees) sous ce seuil.

Note methodologique : l'environnement de test navigateur disponible dans cette session a un plancher
  de largeur de fenetre (~1050px, un resize_window vers 390-400px ne redescend pas en dessous) qui
  empeche de verifier visuellement le rendu a une largeur de telephone reelle. Les deux correctifs
  ci-dessus sont bases sur l'inspection du CSS genere par Streamlit (seuil de 640px confirme dans
  son bundle JS) et une lecture du code, pas une capture d'ecran a largeur mobile - a verifier
  manuellement sur un vrai telephone apres deploiement.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM

- **ui**: Reduit le padding lateral sous 480px
  ([`f48ffa3`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/f48ffa30faed2a9a38794d140d1fe546050d4813))

Les 2rem de marge fixe de chaque cote (32px x2) pesent proportionnellement plus sur un tres petit
  ecran (<480px) - reduits a 1rem sous ce seuil pour rendre cette largeur au contenu.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.12.0 (2026-09-04)

### Features

- **ui**: Logo final - tuyau qui tombe du plafond + goutte + coche, favicon aligne
  ([`29837a5`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/29837a56d6622f7967141c0a8a5f9e62858c9822))

- Nouveau logo : tuyau vertical epais qui depasse a peine du haut de l'icone (comme suspendu au
  plafond), rebord discret, se prolongeant en une vraie goutte d'eau (silhouette Material) avec une
  coche epaisse a l'interieur (couleur du degrade de fond, pas une teinte fixe - elle se fond
  litteralement dans le fond via le meme gradient en gradientUnits="userSpaceOnUse"). Nombreuses
  iterations avec l'utilisateur (formes de tuyau, position/taille de goutte et de coche) avant
  validation finale de cette version. - Favicon aligne sur le nouveau logo :
  st.set_page_config(page_icon=...) pointe maintenant vers app/assets/logo-icon.svg au lieu de
  l'icone Material generique ":material/water_drop:". st.image (utilise en interne par page_icon)
  supporte le SVG directement, confirme en local : le lien <link rel="shortcut icon"> genere bien un
  data URI SVG du nouveau logo.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.11.0 (2026-09-03)

### Features

- **ui**: Compaction verticale du dashboard + logo tuyau incliné + fill aqueux
  ([`382b4e9`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/382b4e951ed1addbb3f4f9b7d698d0803b7a7f39))

- En-tête : la source ("France/departement · 2024 · Source : Hub'Eau API") rejoint le kicker dans la
  bande native de Streamlit au lieu d'une ligne dans le corps de page ; le divider juste en dessous
  est retiré. - Recherche département/commune : empilée verticalement dans une colonne étroite (au
  lieu de deux champs pleine largeur côte à côte), laissant toute la largeur restante aux mois. -
  Mois : grille 6 colonnes x 2 rangées (au lieu d'une colonne de pills étirée tout en hauteur à
  gauche de la carte) - la sélection tient dans une seule bande en haut, à côté de la recherche. -
  Carte nationale : les 5 insets DOM-TOM passent d'une rangée sous la carte à une colonne empilée à
  gauche, la carte métropole récupère cette largeur. Hauteurs de carte réduites (680/580 ->
  460/420). - KPI : passent d'une colonne empilée tout en hauteur à une grille 2x2 compacte (Zones +
  manomètre Conformité en haut, statuts Conforme/ Vigilance/Alerte + Bactério en bas). - Graphiques
  du bas : hauteurs réduites (220/240/260 -> 150/150/170), dividers entre panneaux retirés -
  l'ensemble tient dans une fraction de l'espace vertical utilisé avant. - Ligne de conformité : le
  fillgradient ("aqueuse") qui rendait invisible avec fill="tozeroy" (dégradé étiré jusqu'à 0%, bien
  en dehors du cadrage [ymin,ymax]) est remplacé par un fill="tonexty" contre une ligne de base
  invisible calée sur le bas de l'axe visible. Le dégradé reste maintenant entièrement dans la zone
  visible et se voit clairement (bleu soutenu sous la ligne, s'estompant vers le bas). - Logo :
  nouvelle passe, tuyau incliné (simple capsule arrondie pivotée) avec une goutte qui tombe de
  l'extrémité basse, séparée par un espace net - se lit clairement même à la taille d'icône, sans
  ajout de symbole santé/labo (demande explicite : rien de plus).

Note : les inserts DOM-TOM national restent vides à l'affichage - vérifié que agg_dept_mois.parquet
  n'a aucune ligne pour 971/972/973/ 974/976 sur toute l'année. Pré-existant, pas une régression de
  ce changement.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.10.0 (2026-09-03)

### Bug Fixes

- **ui**: Logo - collier de jonction + goutte unique nette
  ([`2f700de`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/2f700de12e7853a510f00ba7d3b3505924de9d4c))

Reference envoyee : segment de tuyau avec collier de jonction (bague + rivet) puis une goutte d'eau
  unique qui tombe avec un espace net sous l'embout. Remplace le filet d'eau/goutte secondaire par
  ce motif plus simple et plus lisible a petite taille.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM

### Features

- **dashboard**: Nouveau graphique zones/statut mensuel façon segments de tuyau
  ([`f7f6553`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/f7f6553dd10e21e4f2f86aede8976b1b839a85a8))

- Nouveau graphique : barres empilées Conforme/Vigilance/Alerte par mois (mêmes seuils que les KPI),
  en bas du panneau graphiques. Coins arrondis + liseré entre segments pour une lecture façon coupe
  de tuyauterie empilée (chaque statut = un raccord posé sur l'autre). Donnée dérivée de
  df_agg_dept/df_agg_commune existants, pas de nouvelle source. - STATUS_COLORS ajouté près de
  PARAM_COLORS/BACT_COLORS (mêmes teintes que les cartes KPI Conforme/Vigilance/Alerte, adaptées
  dark/light).

Tentative de fill en dégradé ("waterflow") sur la ligne de conformité via fillgradient : abandonnée
  après test, le rendu est invisible dans le plotly.js embarqué par Streamlit avec fill="tozeroy" +
  yaxis à plage restreinte (le dégradé s'étire jusqu'à 0%, donc la fenêtre visible ne voit que la
  toute fin, transparente). Fill plein conservé.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.9.1 (2026-09-03)

### Bug Fixes

- **ui**: Logo refait - eau qui coule d'un tuyau ouvert
  ([`af7c8a1`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/af7c8a1377f6164650fae71affc0783438696e36))

Les references envoyees montraient de l'eau coulant d'un tuyau, pas un raccord qui fuit comme je
  l'avais compris. Nouveau dessin : un segment de tuyau horizontal avec une extremite ouverte
  (alesage fonce visible) d'où s'ecoule un filet d'eau se terminant en goutte, plus une petite
  goutte secondaire pour suggerer un flux continu plutot qu'une goutte statique isolee.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.9.0 (2026-09-03)

### Features

- **ui**: Restructuration Dashboard - recherche en haut, KPI empiles a droite de la carte
  ([`6519578`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/651957847012d0bd9aeb39df8102482d736e79f3))

- En-tete simplifie : le gros bloc icone+titre degrade est retire (logo et kicker vivent deja dans
  la banniere native). Remplace par une petite ligne de contexte/source ("France - 2024 - Source :
  Hub'Eau API"), meme esprit que nyc-taxi.dvdjnbr.fr. - Dashboard reorganise : recherche
  departement/commune tout en haut, puis mois (pills) + carte + colonne KPI empilee verticalement a
  droite de la carte (Zones, manometre Conformite, Conforme/Vigilance/ Alerte, et le statut
  bacteriologique desormais integre dans cette meme colonne plutot qu'a cote du graphique
  physico-chimique). Les graphiques (tendance de conformite, niveaux physico-chimiques) restent en
  bas, seuls desormais dans le panneau du bas. -
  get_params_scope()/PARAM_COLORS/BACT_COLORS/MOIS_SHORT deplaces plus haut dans le script (avant la
  carte) puisque le statut bacteriologique en a besoin des la colonne KPI ; plus de calcul duplique.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.8.4 (2026-09-03)

### Bug Fixes

- **ui**: Toggle theme alignement/contraste + icones sur les onglets
  ([`4617100`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/461710055d32e059d632fb2a6b7d6a4553a551c1))

- Toggle dark mode : soleil/switch/lune alignes verticalement (align-self: center sur les
  pseudo-elements), et le switch passe en gris plus fonce quand le mode sombre est active
  (label:has(input: checked)) plutot qu'une seule teinte fixe. - Onglets : icone Material devant
  chaque libelle (info / sync_alt / cloud / dashboard) + habillage pilule sur l'onglet actif et au
  survol, plutot que texte nu + simple soulignement.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.8.3 (2026-09-03)

### Bug Fixes

- **ui**: Logo carre/compact + toggle gris discret avec icones SVG soleil/lune
  ([`0406eb2`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/0406eb2a63b7dcdcd2c428f9cfb14834d0e82704))

- Logo : proportions revues, plus large et beaucoup plus court (rect 6x7 + embout 6x10 au lieu d'une
  longue barre fine) - plus carre, se lit clairement comme un raccord de tuyauterie et non comme une
  forme allongee ambigue. - Toggle dark mode : remplace l'emoji lune par deux icones SVG (soleil a
  gauche, lune a droite) injectees en CSS ::before/::after (data URI), purement decoratives -
  n'interferent jamais avec le clic du widget. Piste de soleil/switch/lune en un seul st.container
  flex abandonnee : ca cassait le clic du widget reel (checked restait bloque sur son etat initial
  malgre des clics visibles). Switch repasse en gris neutre (#8b95a1), plus de bleu.

Verification : le clic ne fonctionnait pas via l'outil d'automatisation (dispatch d'un seul
  evenement "click" via CDP), mais fonctionne normalement pour un vrai clic utilisateur (sequence
  mousedown+mouseup+ click) - confirme en dispatchant cette sequence via JS directement, le theme
  bascule correctement.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.8.2 (2026-09-03)

### Bug Fixes

- **ui**: Tuyau du logo plus epais + toggle dark mode deplace dans la banniere native
  ([`4d76360`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/4d76360ce415f341f0b517d7e24438f54e23f950))

- Logo : corps du tuyau trop fin pour se lire comme un tuyau. Epaissi (hauteur doublee, embout et
  goutte agrandis en consequence). - Toggle dark mode deplace dans la banniere native de Streamlit,
  a cote du kicker deja present : meme technique (overlay CSS position fixed cale sur le z-index
  reel du header), mais cette fois un vrai widget st.toggle() repositionne plutot qu'un texte
  decoratif, donc toujours cliquable. Positionne a right:160px pour ne pas chevaucher les boutons
  natifs Deploy/⋮ (premier essai a right:16px les recouvrait completement). - Le bloc titre du corps
  de page n'a plus besoin de dupliquer le kicker "Suivi qualite de l'eau potable" (deja dans la
  banniere) ni le toggle (deplace lui aussi) : ne reste que l'icone + le titre dynamique (France /
  departement selectionne), qui ne peut pas aller dans st.logo (image statique uniquement).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.8.1 (2026-09-03)

### Bug Fixes

- **ui**: Embout arrondi du logo du meme cote que la goutte
  ([`803f29c`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/803f29c59fdf9d387fa7500a14b74acdbed3a27b))

Le cache arrondi etait a gauche et la goutte/ouverture a droite : deux extremites qui ne se
  correspondent pas donnaient une impression de tuyau casse qui fuit. Redessine avec le tuyau a bord
  plat a gauche (comme s'il continuait dans un mur, pas besoin de cache visible) et l'embout arrondi
  + la goutte ensemble a droite, comme un robinet qui coule depuis son unique sortie.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.8.0 (2026-09-03)

### Features

- **ui**: Texte dans l'espace vide de la bande d'en-tete Streamlit
  ([`55f1e36`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/55f1e36df88d6e3fe689fe045b6c9a6c73f25517))

Le logo st.logo() laissait une grande zone vide a droite, dans la bande d'en-tete native de
  Streamlit (header[data-testid="stHeader"], 60px de haut, z-index 999990). Pas d'API officielle
  pour y injecter du contenu (verifie via recherche + tests) : overlay en position fixe, cale sur la
  hauteur/z-index reels du header, pointer-events:none pour rester strictement non cliquable.
  Affiche "Suivi qualite de l'eau potable" a cote du logo, comble l'espace au lieu de le laisser
  vide.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.7.0 (2026-09-03)

### Features

- **ui**: Logo dans le header natif Streamlit, onglet Dashboard en 4e position, cartes KPI alignees
  ([`4c9f1d5`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/4c9f1d5ade86e4e6f817366d07e521da5525f1aa))

- Logo dans st.logo() : place l'icone dans la barre d'en-tete native de Streamlit (au niveau du menu
  de deploiement), verifie que la fonction existe et son comportement avant d'implementer (st.logo
  n'accepte qu'une image statique, pas de HTML dynamique - le titre qui change selon le departement
  reste donc dans le corps de page). Necessite de copier assets/ dans l'image Docker
  (app/Dockerfile), absent avant. - Logo redessine une 3e fois : le tuyau a extremite fermee +
  goutte au milieu se lisait comme une fuite. Nouvelle version : tuyau fixe a gauche, extremite
  ouverte a droite (alesage visible), goutte qui tombe depuis cette ouverture - lecture "sortie
  d'eau" plutot que "fissure sur un tuyau intact". - Onglets : Dashboard deplace en 4e et derniere
  position, mais reste actif par defaut via le parametre `default=` de st.tabs (verifie present dans
  la version Streamlit installee, 1.63.0). - Toggle dark mode : icone lune repositionnee a gauche du
  switch (flex-direction: row-reverse sur le label du widget). - Cartes KPI : hauteur fixe (150px) +
  centrage vertical sur les 5 blocs (Zones, manometre Conformite, Conforme/Vigilance/Alerte) pour
  qu'ils soient tous alignes au lieu que le manometre depasse des 4 autres.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.6.0 (2026-09-03)

### Features

- **ui**: Onglet Dashboard par defaut + logo tuyau/goutte sans vanne
  ([`36e2486`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/36e2486f1af743d91ce66514eeb24dbbefc6f626))

- Logo : la vanne ne se lisait toujours pas clairement comme un tuyau selon le retour. Remplace par
  un tuyau (corps + brides) surmonte d'une goutte d'eau qui en tombe, sans vanne du tout. - Le
  contenu principal (KPIs, manometre, recherche, carte, tendances, parametres physico-chimiques,
  statut bacteriologique) est deplace dans un 4e onglet "Dashboard", place en premier et donc actif
  par defaut. Les onglets A propos / Circulation de la donnee / Architecture restent cliquables a
  cote.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.5.1 (2026-09-03)

### Bug Fixes

- **ui**: Logo tuyau lisible, toggle dark mode clair, cartes KPI uniformes, onglets sous le titre
  ([`06889dc`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/06889dcf1e22d12bd0947e4a4f361dee64cc468a))

- Logo : le badge affichait une vanne flottante, pas identifiable comme tuyau. Ajout d'un vrai
  segment de tuyau (corps + brides aux deux extremites) avec la vanne montee dessus via une tige,
  pour que la forme se lise immediatement comme "tuyau + vanne". - Toggle dark mode : le label "Mode
  sombre" tronquait en "Mo..." dans une colonne etroite (surtout hors plein ecran). Remplace par une
  icone lune seule (convention universelle, ne tronque jamais) avec un tooltip "Mode sombre" pour
  l'accessibilite. Colonne elargie ([9,1] -> [7,1]) en complement. - Cartes KPI : "Zones" et le
  manometre "Conformite" n'avaient pas le meme habillage (fond/bordure/coins arrondis) que les 3
  cartes colorees (Conforme/Vigilance/Alerte), ce qui les faisait paraitre "fondues" dans la page
  plutot que decoupees comme les autres. Meme traitement visuel applique aux 5 blocs de la ligne
  KPI. - Page a onglets (A propos / Circulation de la donnee / Architecture) deplacee de la fin de
  page jusqu'a directement sous le titre, comme demande.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.5.0 (2026-09-03)

### Features

- **ui**: Ligne de conformite accentuee en zoom departement
  ([`bf31b5e`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/bf31b5e98aea1d59d9ed0e4630110e9e456afa35))

Idee exploratoire : donner un effet "flux d'eau" a la ligne de conformite quand on zoome sur un
  departement plutot que la vue nationale. Version simple et fiable plutot qu'une vraie animation
  SVG (fragile a maintenir avec les classes generees par Plotly) : ligne plus epaisse (4px vs
  2.5px), plus saturee, courbe lissee (shape=spline) et remplissage plus opaque. mode Streamlit non
  verifie visuellement cette fois (outillage navigateur bloque sur plusieurs tabs), mais changement
  mecanique sans nouvelle surface d'API Plotly.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.4.0 (2026-09-03)

### Features

- **ui**: Logo vanne/robinet stylise a la place de la goutte
  ([`944db3b`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/944db3b782cfab3d79016c0aa52545c9b131e5a9))

Icone remplacee dans le badge du header : une roue de vanne (cercle + croix + moyeu) montee sur une
  tige au-dessus d'une conduite, plutot qu'une goutte d'eau generique. Coherent avec le manometre de
  conformite deja en place et avec l'esthetique tuyauterie des refs fournies (roues de vanne rouges,
  manometres a cadran).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


## v1.3.0 (2026-09-03)

### Features

- **ui**: Carte de statut rouge/vert pour les detections bacteriologiques
  ([`64dc250`](https://github.com/DVDJNBR/qlt-eau-FR-24/commit/64dc250f37986b2628eea444ceb98b208d0b314f))

Le graphique en barres etait quasiment toujours vide (E. coli et Enterocoques a 0 la plupart du
  temps), peu lisible. Remplace par une grosse carte de statut : verte "0 - RAS" quand rien a
  signaler, rouge avec le total et le detail par parametre des qu'il y a une detection. Coherent
  avec les cartes KPI (Conforme/Vigilance/Alerte) deja utilisees plus haut dans le tableau de bord.

make_bact_fig() et son graphique en barres/ligne sont supprimes (code mort). Les constantes de theme
  (_card_bg, _card_border, _muted) sont remontees pres du haut du fichier pour etre disponibles
  avant leur premier usage.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_013tnc3w5m39NbSKEovusRGM


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
