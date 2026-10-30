"""
Dashboard Streamlit — Qualité de l'eau potable en France (2024)
Carte pleine largeur avec insets DOM-TOM (Option B) + drill-down départements
"""

import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import json
import re
from pathlib import Path

def _md_html(s: str) -> str:
    """Retire l'indentation de chaque ligne avant st.markdown : du HTML multi-niveaux
    interpolé (ex. boucle générant des <div> imbriqués) peut se retrouver indenté de
    4+ espaces, ce que Markdown interprète comme un bloc de code au lieu de HTML brut."""
    return re.sub(r"^[ \t]+", "", s, flags=re.MULTILINE)

# --- Configuration ---
ASSETS_DIR = Path(__file__).parent.parent / "assets"
APP_ASSETS_DIR = Path(__file__).parent / "assets"
st.set_page_config(page_title="Qualité de l'eau en France 2024", layout="wide", page_icon=str(APP_ASSETS_DIR / "logo-icon.svg"))

# Logo dans la barre d'en-tête native de Streamlit (au niveau du menu ⋮).
# st.logo() n'accepte qu'une image statique, pas de HTML dynamique : le titre
# qui change selon le département sélectionné reste dans le corps de page.
st.logo(str(APP_ASSETS_DIR / "logo-icon.svg"), size="large")

# Après un déploiement, les fichiers JS chunkés (Selectbox, ButtonGroup, ...) servis par
# l'onglet déjà ouvert n'existent plus sur le serveur (nouveaux hash) : le prochain clic
# sur un widget lève "Failed to fetch dynamically imported module". Un rechargement complet
# de la page recharge l'index à jour et résout l'erreur ; on ne le fait qu'une fois par
# chargement pour éviter une boucle si l'erreur est en fait persistante.
components.html(
    """
    <script>
    (function() {
        var top = window.top;
        if (top.__qltEauChunkReloadArmed) return;
        top.__qltEauChunkReloadArmed = true;
        function isChunkError(msg) {
            return typeof msg === "string" && msg.indexOf("Failed to fetch dynamically imported module") !== -1;
        }
        function handle(msg) {
            if (isChunkError(msg) && !top.__qltEauChunkReloading) {
                top.__qltEauChunkReloading = true;
                top.location.reload();
            }
        }
        top.addEventListener("error", function(e) { handle(e.message); });
        top.addEventListener("unhandledrejection", function(e) {
            handle(e.reason && e.reason.message);
        });
    })();
    </script>
    """,
    height=0,
)

# Le CSS dark/light est injecté plus bas après initialisation du session state

DATA_DIR = Path(__file__).parent / "data"

# Téléchargement automatique des GeoJSON si absents ou au mauvais format
import urllib.request

_GEOJSON_BASE = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master"

@st.cache_resource
def _ensure_geojson_files():
    """Télécharge les GeoJSON si absents/invalides. Exécuté une seule fois (cache_resource) au lieu de à chaque rerun."""
    dept_path = DATA_DIR / "departements.geojson"
    dept_ok = False
    if dept_path.exists():
        sample = json.loads(dept_path.read_text(encoding="utf-8"))
        dept_ok = isinstance(sample, dict) and "features" in sample
    if not dept_ok:
        with urllib.request.urlopen(f"{_GEOJSON_BASE}/departements.geojson", timeout=30) as r:
            data = json.load(r)
        with open(dept_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    domtom_path = DATA_DIR / "departements_domtom.geojson"
    if not domtom_path.exists():
        with urllib.request.urlopen(f"{_GEOJSON_BASE}/departements-avec-outre-mer.geojson", timeout=30) as r:
            data = json.load(r)
        data["features"] = [f for f in data["features"] if f["properties"]["code"] in {"971","972","973","974","976"}]
        with open(domtom_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

_ensure_geojson_files()

MOIS_LABELS = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre",
}

# Colorscale partagée (format go.Figure)
COLOR_SCALE = [[0.0, "#ff4d4d"], [0.8, "#ffaf40"], [0.95, "#32ff7e"], [1.0, "#18dcff"]]

# Config insets DOM-TOM : (code, nom, lat, lon, zoom, y_domain)
# Empilés verticalement dans une colonne à gauche de la carte métropole
# (plutôt qu'une rangée sous la carte) : y_domain va du haut vers le bas.
DOM_TOM_CONFIG = [
    ("971", "Guadeloupe",  16.17, -61.57,  7.5, [0.815, 1.000]),
    ("972", "Martinique",  14.67, -61.00,  8.5, [0.610, 0.795]),
    ("973", "Guyane",       4.00, -53.00,  4.5, [0.405, 0.590]),
    ("974", "La Réunion", -21.10,  55.50,  7.0, [0.200, 0.385]),
    ("976", "Mayotte",    -12.80,  45.15,  9.5, [0.000, 0.180]),
]
DOMTOM_CODES = {c[0] for c in DOM_TOM_CONFIG}

# --- Simplification des contours ---
# departements.geojson pèse 3,4 Mo : tracé à l'échelle de la France, ses
# points distants de quelques mètres sont invisibles, mais Plotly les
# sérialise et Streamlit les renvoie au navigateur à chaque rerun (chaque
# clic). Douglas-Peucker, une fois au chargement : 3,4 Mo -> 0,4 Mo.
def _rdp(pts, tol):
    keep = np.zeros(len(pts), dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        seg = pts[b] - pts[a]
        rel = pts[a + 1:b] - pts[a]
        norm = np.hypot(*seg)
        d = (np.abs(seg[0] * rel[:, 1] - seg[1] * rel[:, 0]) / norm if norm
             else np.hypot(rel[:, 0], rel[:, 1]))
        i = int(np.argmax(d))
        if d[i] > tol:
            m = a + 1 + i
            keep[m] = True
            stack += [(a, m), (m, b)]
    return pts[keep]


def _simplify_geojson(gj, tol):
    """Simplifie les contours en place (tolérance en degrés)."""
    def ring(r):
        if len(r) < 8:
            return r
        out = _rdp(np.asarray(r, dtype=float), tol)
        return np.round(out, 4).tolist() if len(out) >= 4 else r
    for f in gj["features"]:
        g = f.get("geometry")
        if not g:
            continue
        if g["type"] == "Polygon":
            g["coordinates"] = [ring(r) for r in g["coordinates"]]
        elif g["type"] == "MultiPolygon":
            g["coordinates"] = [[ring(r) for r in poly] for poly in g["coordinates"]]
    return gj


# --- Chargement des données ---
# cache_resource (et non cache_data) : cache_data re-sérialise/copie la valeur à
# chaque accès — prohibitif avec un GeoJSON communes de ~45 Mo. Les objets
# retournés sont partagés et ne doivent jamais être mutés après chargement.
@st.cache_resource
def load_data():
    df_agg_commune = pd.read_parquet(DATA_DIR / "agg_commune_mois.parquet")
    df_agg_dept    = pd.read_parquet(DATA_DIR / "agg_dept_mois.parquet")

    with open(DATA_DIR / "departements.geojson", encoding="utf-8") as f:
        geojson_dept = json.load(f)
    with open(DATA_DIR / "communes_france.geojson", encoding="utf-8") as f:
        geojson_commune_all = json.load(f)
    with open(DATA_DIR / "departements_domtom.geojson", encoding="utf-8") as f:
        geojson_domtom = json.load(f)
    # ~500 m pour la métropole (vue France entière), ~100 m pour les DOM-TOM
    # affichés en médaillons zoomés. Les communes ne sont jamais tracées
    # toutes ensemble : laissées intactes.
    _simplify_geojson(geojson_dept, 0.005)
    _simplify_geojson(geojson_domtom, 0.001)

    dept_names    = {f["properties"]["code"]: f["properties"]["nom"] for f in geojson_dept["features"]}
    domtom_names  = {f["properties"]["code"]: f["properties"]["nom"] for f in geojson_domtom["features"]}
    dept_names.update(domtom_names)
    commune_names = {f["properties"]["code"]: f["properties"]["nom"] for f in geojson_commune_all["features"]}

    df_agg_dept["nom_dept"]       = df_agg_dept["code_departement"].map(dept_names)
    df_agg_commune["nom_commune"] = df_agg_commune["code_commune"].map(commune_names)

    df_params_dept    = pd.read_parquet(DATA_DIR / "parametres_dept_mois.parquet")
    df_params_commune = pd.read_parquet(DATA_DIR / "parametres_commune_mois.parquet")

    # Pré-calculs pour éviter de retrier ~35 000 noms à chaque rerun
    commune_name_to_code = {v: k for k, v in commune_names.items()}
    sorted_communes      = sorted(commune_names.values(), key=lambda x: x.lower())
    dept_options         = {"": ""} | {code: nom for code, nom in sorted(dept_names.items(), key=lambda x: x[1])}

    return (df_agg_commune, df_agg_dept,
            geojson_dept, geojson_commune_all, geojson_domtom,
            dept_names, commune_names, commune_name_to_code,
            sorted_communes, dept_options,
            df_params_dept, df_params_commune)

(df_agg_commune, df_agg_dept,
 geojson_dept, geojson_commune_all, geojson_domtom,
 dept_names, commune_names, commune_name_to_code,
 sorted_communes, dept_options,
 df_params_dept, df_params_commune) = load_data()

# --- Session state ---
if "view_level"           not in st.session_state: st.session_state.view_level           = "National"
if "selected_dept_code"   not in st.session_state: st.session_state.selected_dept_code   = None
if "selected_month_label" not in st.session_state: st.session_state.selected_month_label = "Janvier"
if "commune_search"       not in st.session_state: st.session_state.commune_search       = ""
if "dark_mode"            not in st.session_state: st.session_state.dark_mode            = True

# Thème courant
_dark            = st.session_state.get("dark_mode", False)
PLOTLY_TEMPLATE  = "plotly_dark" if _dark else "plotly"
PLOTLY_FONT_COLOR = "#e2e8f0" if _dark else "#1a202c"
_card_bg     = "#151921" if _dark else "#f8fafc"
_card_border = "#232a35" if _dark else "#e2e8f0"
_muted       = "#94a3b8" if _dark else "#64748b"

# Habillage de la bande d'en-tête native de Streamlit (celle du menu ⋮),
# vide à droite du logo st.logo(). Pas d'API officielle pour y injecter du
# contenu : overlay en position fixe, calé sur la hauteur réelle du header
# (60px) et au-dessus de son z-index (999990). Purement visuel, non cliquable.
# Le kicker est injecté ici (statique), la source/scope juste après le calcul
# de scope_text plus bas (dépend du département sélectionné) — même bande,
# deux injections successives pour éviter tout décalage d'affichage.
st.markdown(f"""
    <div class="header-kicker" style="position:fixed; top:0; left:74px; height:60px; z-index:1000000;
                display:flex; align-items:center; pointer-events:none;">
        <span style="font-size:0.68rem; font-weight:700; letter-spacing:0.12em;
                     color:{_muted}; text-transform:uppercase;">
            Suivi qualité de l'eau potable
        </span>
    </div>
""", unsafe_allow_html=True)

def make_gauge_fig(value):
    """Manomètre de conformité (esthétique tuyauterie/pression)."""
    needle_color = "#e2e8f0" if _dark else "#1a202c"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix="%", font=dict(size=17, color=PLOTLY_FONT_COLOR)),
        gauge=dict(
            axis=dict(range=[70, 100], showticklabels=False, ticks=""),
            bar=dict(color=needle_color, thickness=0.25),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[70, 80], color="#ff4d4d"),
                dict(range=[80, 95], color="#ffaf40"),
                dict(range=[95, 100], color="#32ff7e"),
            ],
        ),
    ))
    fig.update_layout(
        height=100, margin=dict(l=15, r=15, t=5, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PLOTLY_FONT_COLOR),
    )
    return fig

# Injection CSS adaptative
# NB : depuis Streamlit ~1.56 les boutons pills n'ont plus de data-testid
# "stBaseButton-pills(Active)" — on cible button[data-variant="pills"] et
# l'état sélectionné via aria-checked.
_CSS_COMMON = """
    /* Largeur max. padding-top réduit : Streamlit réserve 6rem (96px) par
       défaut pour un gros bloc titre qui n'existe plus dans notre page
       (kicker/scope vivent dans la bannière native) - il ne restait qu'un
       grand vide au-dessus des onglets. 4.5rem (72px) laisse juste la place
       de la bannière native (60px) + une petite marge. */
    .block-container { max-width: 1400px !important; padding-left: 2rem !important; padding-right: 2rem !important; padding-top: 4.5rem !important; }
    /* Sélecteur de mois : grille 4 colonnes x 3 rangées (recherche
       département/commune passée côte à côte au-dessus a fait gagner en
       hauteur - les mois passent à 4 par ligne au lieu de 6 pour rester
       dans la même largeur totale sans redevenir une bande figée). */
    .st-key-selected_month_label div[data-testid="stButtonGroup"] > div {
        display: flex !important; flex-direction: row !important; flex-wrap: wrap !important;
        gap: 6px !important;
    }
    .st-key-selected_month_label button[data-variant="pills"] {
        flex: 0 0 calc(25% - 6px) !important; justify-content: center !important;
    }
    /* Toggle thème : discret (gris, pas de bleu), repositionné dans la
       bannière native (au-dessus du z-index du header 999990). Soleil/lune
       en ::before/::after (data URI) plutôt qu'en éléments markdown à côté
       du widget : un st.container flex autour du toggle cassait le clic
       (le widget restait bloqué sur son état initial, cf. historique). */
    .st-key-dark_mode {
        position: fixed !important; top: 0 !important; right: 160px !important;
        height: 60px !important; display: flex !important; align-items: center !important;
        z-index: 1000001 !important; width: auto !important;
    }
    .st-key-dark_mode label > div:nth-of-type(1) {
        background-color: #c3c9d1 !important;
    }
    .st-key-dark_mode label:has(input:checked) > div:nth-of-type(1) {
        background-color: #6b7280 !important;
    }
    .st-key-dark_mode::before, .st-key-dark_mode::after {
        display: block !important; line-height: 0 !important; align-self: center !important;
    }
    .st-key-dark_mode::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='5' fill='%239aa4b2'/%3E%3Cg stroke='%239aa4b2' stroke-width='2' stroke-linecap='round'%3E%3Cline x1='12' y1='1' x2='12' y2='3'/%3E%3Cline x1='12' y1='21' x2='12' y2='23'/%3E%3Cline x1='4.2' y1='4.2' x2='5.6' y2='5.6'/%3E%3Cline x1='18.4' y1='18.4' x2='19.8' y2='19.8'/%3E%3Cline x1='1' y1='12' x2='3' y2='12'/%3E%3Cline x1='21' y1='12' x2='23' y2='12'/%3E%3Cline x1='4.2' y1='19.8' x2='5.6' y2='18.4'/%3E%3Cline x1='18.4' y1='5.6' x2='19.8' y2='4.2'/%3E%3C/g%3E%3C/svg%3E");
        margin-right: 6px;
    }
    .st-key-dark_mode::after {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24'%3E%3Cpath d='M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z' fill='%239aa4b2'/%3E%3C/svg%3E");
        margin-left: 6px;
    }
    /* Logo plus grand dans la bannière native : size="large" de st.logo()
       plafonne à 32px, la bannière (60px de haut) a de la marge pour plus. */
    [data-testid="stHeaderLogo"] {
        height: 44px !important; width: auto !important;
    }
    /* Mobile (<768px) : le kicker et le texte de scope sont en position fixe
       à des offsets pixel fixes (left:65px / left:300px) calés sur la largeur
       du logo et du kicker en desktop. Sur un écran étroit, le texte de scope
       (longueur variable selon le département) risque de chevaucher le menu
       natif Streamlit (⋮ / Deploy) ou le toggle de thème à droite - ce sont
       de purs éléments décoratifs, on les masque plutôt que de risquer un
       chevauchement avec des éléments cliquables. */
    @media (max-width: 768px) {
        .header-kicker, .header-scope { display: none !important; }
    }
    /* Mobile (<640px, seuil interne de Streamlit pour l'empilement des
       st.columns) : la grille de mois 6x2 devient trop étroite par pill
       (largeur de conteneur / 6) pour rester lisible - on repasse à 3
       colonnes (4 rangées) pour garder des pills assez larges. */
    @media (max-width: 640px) {
        .st-key-selected_month_label button[data-variant="pills"] {
            flex: 0 0 calc(33.333% - 6px) !important;
        }
    }
    /* Petit telephone (<480px) : les 2rem de marge fixe de chaque cote
       (32px x2) pesent proportionnellement plus sur une largeur d'ecran
       reduite - on les reduit pour rendre cette largeur au contenu. */
    @media (max-width: 480px) {
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    }
"""
# Carte KPI "Conformité" (manomètre) : même habillage que les cartes colorées
# (fond/bordure/coins arrondis) pour que les 5 blocs de la ligne KPI soient
# visuellement découpés de façon cohérente, pas seulement 3 sur 5.
_CSS_COMMON += f"""
    .st-key-gauge_card {{
        background: {_card_bg}; border: 1px solid {_card_border};
        border-radius: 12px; padding: 10px 15px 0 15px;
        height: 160px; box-sizing: border-box;
        display: flex; flex-direction: column; justify-content: center;
    }}
    /* Onglets stylés façon badge (inspiré de watt-watcher.dvdjnbr.fr) :
       l'onglet actif a un fond teinté dans la couleur d'accent et un liseré
       du bas en accent - plus qu'un simple soulignement (l'indicateur natif
       react-aria, un simple trait de 2px, est masqué au profit de ce style).
       NB : Streamlit a migré ses tabs de BaseWeb vers react-aria - le
       sélecteur est [data-testid="stTab"], plus [data-baseweb="tab"]. */
    [data-testid="stTab"] {{
        border-radius: 8px 8px 0 0 !important; padding: 8px 16px !important;
        font-weight: 600 !important;
    }}
    [data-testid="stTab"] .react-aria-SelectionIndicator {{ display: none !important; }}
    [data-testid="stTab"]:hover {{ background: {_card_bg} !important; }}
    [data-testid="stTab"][aria-selected="true"] {{
        background: rgba(59, 130, 246, 0.16) !important;
        border-bottom: 2px solid #3b82f6 !important;
    }}
"""

if _dark:
    st.markdown(f"""
        <style>
        {_CSS_COMMON}
        /* Fond global + header */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main,
        header[data-testid="stHeader"], [data-testid="stToolbar"] {{
            background-color: #0b0d11 !important; color: #e2e8f0 !important;
        }}
        .stMetric {{ background-color: #151921; border: 1px solid #232a35; padding: 15px; border-radius: 12px; }}
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ color: #e2e8f0 !important; }}
        /* Widgets selectbox/input : Streamlit a migré de BaseWeb vers
           react-aria (comme les tabs) - [data-baseweb=...] ne matche plus
           rien, la boîte fermée du selectbox restait donc blanche en dark
           mode malgré ces règles (jamais appliquées). stSelectboxVirtualDropdown
           reste valide pour le popup ouvert (portail séparé) - seule la boîte
           fermée avait besoin d'un nouveau sélecteur. */
        .react-aria-ComboBox > div {{
            background-color: #151921 !important; color: #e2e8f0 !important; border-color: #232a35 !important;
        }}
        .react-aria-ComboBox input {{ background-color: transparent !important; color: #e2e8f0 !important; }}
        .react-aria-ComboBox button svg {{ fill: #e2e8f0 !important; }}
        /* Popup des selectbox (département/commune) : rendu dans un portail attaché
           à <body>, hors de portée du CSS scopé à .stApp — cible directe requise. */
        [data-testid="stSelectboxVirtualDropdown"] {{
            background-color: #151921 !important;
        }}
        [data-testid="stSelectboxVirtualDropdown"] [role="option"] {{
            color: #e2e8f0 !important;
        }}
        [data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover {{
            background-color: #232a35 !important;
        }}
        /* Pills dark */
        button[data-variant="pills"] {{
            background-color: #1e2530 !important; color: #e2e8f0 !important; border-color: #232a35 !important;
        }}
        button[data-variant="pills"]:hover {{
            background-color: #232a35 !important;
        }}
        button[data-variant="pills"][aria-checked="true"] {{
            background-color: #3b82f6 !important; color: #ffffff !important; border-color: #3b82f6 !important;
        }}
        button[data-variant="pills"] p {{ color: inherit !important; }}
        /* st.button (retour, etc.) dark */
        .stButton > button {{
            background-color: #1e2530 !important; color: #e2e8f0 !important; border-color: #232a35 !important;
        }}
        .stButton > button:disabled {{
            background-color: #13181f !important; color: #4a5568 !important;
        }}
        hr {{ border-color: #232a35 !important; }}
        label, p, h1, h2, h3, .stMarkdown, .stCaption {{ color: #e2e8f0 !important; }}
        /* Carte encadrée : bordure/coins arrondis sombres autour de chaque
           graphique Plotly plutôt qu'un rendu bord-à-bord. Pas de padding ici :
           Streamlit mesure la largeur de cet élément (bounding box, donc
           padding inclus) pour dimensionner le graphique Plotly - un padding
           CSS ici fait rendre Plotly 2*padding trop large, et l'overflow:hidden
           tronque alors le bord droit (ex. le dernier mois "Déc" coupé). La
           respiration visuelle vient déjà des marges internes de chaque figure
           (margin=dict(l=10, r=10, ...)), pas besoin de padding au conteneur. */
        [data-testid="stPlotlyChart"] {{
            background: #151921; border: 1px solid #232a35; border-radius: 12px;
            overflow: hidden;
        }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <style>
        {_CSS_COMMON}
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main,
        header[data-testid="stHeader"], [data-testid="stToolbar"] {{
            background-color: #f8fafc !important; color: #1a202c !important;
        }}
        </style>
    """, unsafe_allow_html=True)

def reset_view():
    st.session_state.view_level         = "National"
    st.session_state.selected_dept_code = None
    st.session_state["dept_search"]     = ""
    st.session_state["commune_search"]  = ""

# Auto-détection département depuis la commune (avant tout widget)
_stored_commune = st.session_state.get("commune_search", "")
if _stored_commune:
    _c_code = commune_name_to_code.get(_stored_commune)
    if _c_code:
        _dept_rows = df_agg_commune[df_agg_commune["code_commune"] == _c_code]
        if not _dept_rows.empty:
            _auto_dept = str(_dept_rows["code_departement"].iloc[0])
            if st.session_state.get("selected_dept_code") != _auto_dept:
                st.session_state.selected_dept_code = _auto_dept
                st.session_state["dept_search"]     = _auto_dept
                st.session_state.view_level         = "Department"

# Mois courant (session state, mis à jour par les pills après les KPIs)
selected_month_label = st.session_state["selected_month_label"] or "Janvier"
selected_month = next(k for k, v in MOIS_LABELS.items() if v == selected_month_label)

# --- Header ---
# Le logo + le kicker vivent dans la bannière native (overlay plus haut).
# scope_text dépend du département sélectionné (mis à jour juste au-dessus,
# après l'auto-détection depuis une commune) : injecté ici, juste à droite
# du kicker, dans la même bande fixe plutôt que sur une ligne dans le corps
# de page — récupère la place que prenait l'ancien st.caption().
scope_text = "France" if st.session_state.view_level == "National" else dept_names.get(st.session_state.selected_dept_code, "Département")
st.markdown(f"""
    <div class="header-scope" style="position:fixed; top:0; left:300px; height:60px; z-index:1000000;
                display:flex; align-items:center; pointer-events:none;">
        <span style="font-size:0.68rem; color:{_muted}; opacity:0.75;">
            {scope_text} · 2024 · Source : Hub'Eau API
        </span>
    </div>
""", unsafe_allow_html=True)

# Toggle dark mode : widget seul (pas de container/markdown à côté — ça
# cassait le clic, cf. commentaire CSS plus haut). Soleil/lune en CSS
# ::before/::after sur .st-key-dark_mode, purement décoratif.
st.toggle("Mode sombre", key="dark_mode", label_visibility="collapsed")

# ============================================================
# PANNEAU INFOS : À propos / Circulation de la donnée / Architecture
# ============================================================

# Badges shields.io "for-the-badge", même convention que sur le portfolio
# (github.com/ileriayo/markdown-badges) — pas de tag Hub'Eau ici, ce n'est
# pas une techno du stack mais la source de données (déjà nommée dans le texte).
TECH_BADGES = [
    "https://img.shields.io/badge/python-%233670A0.svg?style=for-the-badge&logo=python&logoColor=ffdd54",
    "https://img.shields.io/badge/Databricks-%23FF3621.svg?style=for-the-badge&logo=databricks&logoColor=white",
    "https://img.shields.io/badge/azure-%230078D4.svg?style=for-the-badge&logo=microsoftazure&logoColor=white",
    "https://img.shields.io/badge/Delta%20Lake-00ADD8.svg?style=for-the-badge",
    "https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white",
    "https://img.shields.io/badge/fastapi-%23009688.svg?style=for-the-badge&logo=fastapi&logoColor=white",
    "https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white",
]

tab_about, tab_flow, tab_infra, tab_dashboard = st.tabs(
    [
        ":material/info: À propos",
        ":material/sync_alt: Circulation de la donnée",
        ":material/cloud: Architecture cloud & BDD",
        ":material/dashboard: Dashboard",
    ],
    default=":material/dashboard: Dashboard",
)

with tab_about:
    st.markdown(_md_html(f"""
        <p style="font-size:1.05rem; line-height:1.6; color:{PLOTLY_FONT_COLOR};">
            Projet d'apprentissage data engineering pour se familiariser avec Azure Databricks,
            Delta Lake et l'écosystème Azure (ADLS Gen2, Terraform). Le pipeline ingère les
            données publiques de qualité de l'eau potable en France depuis
            l'<a href="https://hubeau.eaufrance.fr/page/api-qualite-eau-potable" target="_blank" style="color:#60A5FA;">API Hub'Eau</a>,
            les transforme selon une architecture Medallion <b>Bronze → Silver → Gold</b>,
            et les expose via une API REST FastAPI sans compute Databricks.
        </p>
        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:12px;">
            {"".join(f'<img src="{url}" alt="" height="28" style="border-radius:4px;">' for url in TECH_BADGES)}
        </div>
        <p style="margin-top:16px;">
            <a href="https://github.com/DVDJNBR/qlt-eau-FR-24" target="_blank" style="color:#60A5FA; font-size:0.9rem;">→ Code source sur GitHub</a>
        </p>
    """), unsafe_allow_html=True)

with tab_flow:
    # Chemin de la donnée "en live" : icônes + exemple représentatif de ce que
    # contient chaque étage (JSON brut, ligne de table, résultat de contrôle,
    # route API), avec un point lumineux qui parcourt les connecteurs en boucle
    # continue (CSS pur — pas de JS/composant custom). Inspiré de la page
    # Pipeline de watt_watcher (PipelineDiagram + section Architecture cloud).
    FLOW_ICONS = {
        "source":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M7 10l5 5 5-5"/><path d="M5 19h14"/></svg>',
        "bronze":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h16M4 8v10a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V8M4 8l2-4h12l2 4"/></svg>',
        "silver":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h6M4 10h4M4 14h6M4 18h4"/><path d="M13 6h7v12h-7z"/></svg>',
        "gold":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="6" rx="7" ry="2.5"/><path d="M5 6v6c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V6"/><path d="M5 12v6c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-6"/></svg>',
        "checks":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg>',
        "api":       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M8 4 3 12l5 8M16 4l5 8-5 8"/></svg>',
        "dashboard": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="19" x2="5" y2="11"/><line x1="12" y1="19" x2="12" y2="5"/><line x1="19" y1="19" x2="19" y2="14"/></svg>',
    }

    _preview_source = """<div class="flow-path">GET /api/v1/qualite_eau_potable/resultats_dis</div>
<pre class="flow-json">{
  "code_commune": "59350",
  "nom_commune": "Lille",
  "date_prelevement": "2024-06-12",
  "libelle_parametre": "Escherichia coli",
  "resultat_numerique": 0,
  "conclusion_conformite_prelevement": "C"
}</pre>"""

    _preview_bronze = """<div class="flow-path">bronze/water_quality/hubeau &middot; partition&eacute; par ann&eacute;e</div>
<pre class="flow-json">{
  "code_commune": "59350",
  "nom_commune": "Lille",
  ...
}</pre>
<div class="flow-note">&Eacute;crit tel quel, aucune transformation.</div>"""

    _preview_silver = """<div class="flow-path">Table : silver_conformite</div>
<div class="flow-kv"><span>id</span><b>SMP-48213</b></div>
<div class="flow-kv"><span>dept</span><b>59</b></div>
<div class="flow-kv"><span>param</span><b>1301</b></div>
<div class="flow-kv"><span>concl.</span><b>C</b></div>"""

    _preview_gold = """<div class="flow-path">Table : agg_conformite_departement</div>
<div class="flow-kv"><span>dept</span><b>59</b></div>
<div class="flow-kv"><span>tests</span><b>1&nbsp;842</b></div>
<div class="flow-kv"><span>conformes</span><b>1&nbsp;503</b></div>
<div class="flow-kv"><span>taux</span><b>81.6%</b></div>"""

    _preview_checks = """<div class="flow-check">&#10003; dim_communes : commune_code unique (34 968 lignes)</div>
<div class="flow-check">&#10003; factconformite : is_compliant_pc bool&eacute;en</div>"""

    _preview_api = """<div class="flow-route"><span class="flow-method">GET</span> /conformite/departements/{code}</div>"""

    _preview_dashboard = """<div class="flow-here">&#9679; Vous &ecirc;tes ici</div>"""

    FLOW_STAGES = [
        ("source",    "Hub'Eau API",     "Source",            "#3B82F6", _preview_source),
        ("bronze",    "Bronze",          "Ingestion brute",   "#cd7f32", _preview_bronze),
        ("silver",    "Silver",          "Nettoyage",         "#c0c0c0", _preview_silver),
        ("gold",      "Gold",            "Agrégations",  "#ffd700", _preview_gold),
        ("checks",    "Quality Checks",  "Contrôles Spark", "#4caf50", _preview_checks),
        ("api",       "API REST",        "Exposition",        "#3B82F6", _preview_api),
        ("dashboard", "Dashboard",       "Ce que vous voyez",  "#a855f7", _preview_dashboard),
    ]

    _N = len(FLOW_STAGES)
    _T = round((_N - 1) * 1.1, 2)          # durée totale d'un cycle (s)
    _step = _T / (_N - 1)

    _cols_html, _conn_html = [], []
    for i, (kind, title, subtitle, color, preview) in enumerate(FLOW_STAGES):
        _delay = -round(i * _step, 2)
        _cols_html.append(f"""
            <div class="flow-col">
                <div class="flow-node" style="--flow-color:{color}; animation-delay:{_delay}s;">
                    <span class="flow-node-icon">{FLOW_ICONS[kind]}</span>
                    <div class="flow-node-title">{title}</div>
                    <div class="flow-node-sub">{subtitle}</div>
                </div>
                <div class="flow-preview" style="--flow-color:{color};">{preview}</div>
            </div>
        """)
    for i in range(_N - 1):
        _delay = -round(i * _step, 2)
        _conn_html.append(f"""
            <div class="flow-connector">
                <span class="flow-connector-line"></span>
                <span class="flow-connector-spark" style="--flow-color:{FLOW_STAGES[i][3]}; animation-delay:{_delay}s;"></span>
            </div>
        """)

    _flow_row = _cols_html[0] + _conn_html[0] + f"""
        <div class="flow-datalake">
            <span class="flow-datalake-label">Data lake &middot; ADLS Gen2</span>
            <div class="flow-datalake-row">
                {_cols_html[1]}
                {_conn_html[1]}
                {_cols_html[2]}
            </div>
        </div>
    """
    for i in range(3, _N):
        _flow_row += _conn_html[i - 1] + _cols_html[i]

    _flow_css = """
    <style>
        .flow-wrap { overflow-x:auto; padding:8px 4px 16px; }
        .flow-row  { display:flex; align-items:flex-start; gap:0; min-width:max-content; }
        .flow-col  { display:flex; flex-direction:column; align-items:center; gap:8px; width:132px; flex:0 0 auto; }
        .flow-node { width:100%; box-sizing:border-box; padding:12px 8px; border-radius:12px;
                      background:color-mix(in srgb, var(--flow-color) 14%, transparent);
                      border:1.5px solid var(--flow-color); text-align:center;
                      animation: flowPulse __T__s ease-in-out infinite; }
        .flow-node-icon { display:inline-flex; width:20px; height:20px; color:var(--flow-color); }
        .flow-node-title { font-weight:700; font-size:0.8rem; color:FONTCOLOR; margin-top:4px; }
        .flow-node-sub   { font-size:0.68rem; color:MUTEDCOLOR; margin-top:1px; }
        .flow-preview { width:100%; box-sizing:border-box; min-height:96px; padding:8px;
                         border-radius:8px; background:CARDBG; border:1px solid CARDBORDER;
                         font-size:0.62rem; color:MUTEDCOLOR; overflow:hidden; }
        .flow-path  { font-size:0.6rem; color:var(--flow-color); margin-bottom:4px; word-break:break-all; }
        .flow-json  { margin:0; font-size:0.6rem; line-height:1.4; white-space:pre-wrap; word-break:break-word; color:MUTEDCOLOR; }
        .flow-note  { margin-top:4px; font-style:italic; opacity:0.8; }
        .flow-kv { display:flex; justify-content:space-between; gap:6px; padding:1.5px 0; border-bottom:1px solid CARDBORDER; }
        .flow-kv:last-child { border-bottom:none; }
        .flow-kv span { color:MUTEDCOLOR; min-width:0; overflow-wrap:break-word; }
        .flow-kv b { color:FONTCOLOR; font-weight:600; white-space:nowrap; flex:0 0 auto; }
        .flow-check { color:#4caf50; margin-bottom:3px; }
        .flow-route { font-size:0.68rem; }
        .flow-method { background:#3B82F622; color:#3B82F6; border:1px solid #3B82F655; border-radius:5px; padding:1px 5px; font-weight:700; font-size:0.6rem; margin-right:5px; }
        .flow-here  { color:#a855f7; font-weight:700; font-size:0.7rem; }
        .flow-datalake { border:1.5px dashed color-mix(in srgb, MUTEDCOLOR 45%, transparent); border-radius:14px;
                          padding:20px 10px 10px; position:relative; margin:0 2px; }
        .flow-datalake-label { position:absolute; top:-9px; left:12px; background:BODYBG; padding:0 6px;
                                font-size:0.62rem; color:MUTEDCOLOR; font-weight:600; }
        .flow-datalake-row { display:flex; align-items:flex-start; }
        .flow-connector { position:relative; width:34px; height:20px; margin-top:22px; flex:0 0 auto; }
        .flow-connector-line { position:absolute; top:50%; left:0; right:0; height:2px; background:CARDBORDER; transform:translateY(-50%); }
        .flow-connector-spark { position:absolute; top:50%; left:0; width:7px; height:7px; border-radius:50%;
                                 background:var(--flow-color); box-shadow:0 0 8px var(--flow-color);
                                 transform:translate(-50%,-50%); opacity:0;
                                 animation: flowTravel __T__s linear infinite; }

        @keyframes flowPulse {
            0%   { box-shadow:none; }
            2%   { box-shadow:0 0 14px var(--flow-color); }
            SLICEm2 { box-shadow:0 0 14px var(--flow-color); }
            SLICEpct { box-shadow:none; }
            100% { box-shadow:none; }
        }
        @keyframes flowTravel {
            0%      { left:0%; opacity:0; }
            3%      { opacity:1; }
            SLICEm3 { left:100%; opacity:1; }
            SLICEpct, 100% { left:100%; opacity:0; }
        }
        @media (prefers-reduced-motion: reduce) {
            .flow-node, .flow-connector-spark { animation:none !important; }
        }
    </style>
    """
    _slice = 100 / (_N - 1)
    _flow_css = (_flow_css
        .replace("__T__", str(_T))
        .replace("SLICEm2", f"{max(0.1, _slice - 2):.2f}%")
        .replace("SLICEm3", f"{max(0.1, _slice - 3):.2f}%")
        .replace("SLICEpct", f"{_slice:.2f}%")
        .replace("FONTCOLOR", PLOTLY_FONT_COLOR)
        .replace("MUTEDCOLOR", _muted)
        .replace("CARDBG", _card_bg)
        .replace("CARDBORDER", _card_border)
        .replace("BODYBG", "#0e1117" if _dark else "#ffffff")
    )

    st.markdown(_flow_css, unsafe_allow_html=True)
    st.markdown(_md_html(f"""
        <div class="flow-wrap"><div class="flow-row">{_flow_row}</div></div>
        <p style="color:{_muted}; font-size:0.85rem; margin-top:4px;">
            Ingestion incrémentale depuis Hub'Eau → nettoyage/standardisation Silver →
            star schema + KPIs Gold → contrôles qualité Spark natif → exposition REST
            directe depuis ADLS (sans compute Databricks au moment de la lecture).
            Le point lumineux illustre le sens de circulation, en continu — chaque
            vignette montre un exemple réel de ce que contient l'étage correspondant.
        </p>
    """), unsafe_allow_html=True)

with tab_infra:
    AZURE_SERVICES = [
        ("Azure Data Lake Storage Gen2", "Stockage Delta Lake (Bronze/Silver/Gold), partitionné par année/département."),
        ("Azure Databricks", "Notebooks Spark pour l'ingestion, la transformation et les contrôles qualité."),
        ("Terraform", "Infrastructure as Code — provisionnement ADLS Gen2 + workspace Databricks."),
        ("Delta Lake", "Format de table transactionnel (ACID) sous-jacent à toutes les couches."),
    ]
    col_infra = st.columns(2)
    for i, (name, desc) in enumerate(AZURE_SERVICES):
        with col_infra[i % 2]:
            st.markdown(_md_html(f"""
                <div style="background:{_card_bg}; border:1px solid {_card_border}; border-radius:12px; padding:14px; margin-bottom:12px;">
                    <div style="font-weight:700; color:{PLOTLY_FONT_COLOR}; margin-bottom:4px;">{name}</div>
                    <div style="font-size:0.82rem; color:{_muted};">{desc}</div>
                </div>
            """), unsafe_allow_html=True)

    st.markdown(f"<p style='font-weight:700; color:{PLOTLY_FONT_COLOR}; margin-top:8px;'>Schéma Gold (star schema)</p>", unsafe_allow_html=True)
    GOLD_TABLES = [
        ("dim_communes", "Dimension", "commune_code, commune_name, department_code"),
        ("dim_parametres", "Dimension", "parameter_code, parameter_name, unit"),
        ("dim_temps", "Dimension", "date_key, sampling_date, year, month, quarter"),
        ("factmesuresqualite", "Fait", "sampling_id, commune_code FK, parameter_code FK, date_key FK, numeric_result"),
        ("factconformite", "Fait", "sampling_id, parameter_code FK, date_key FK, is_compliant_pc, is_compliant_bact"),
        ("agg_conformite_departement", "Agrégat", "department_code, total_tests, compliant_tests, compliance_rate"),
    ]
    for name, kind, cols in GOLD_TABLES:
        _kind_color = {"Dimension": "#60A5FA", "Fait": "#f97316", "Agrégat": "#32ff7e"}[kind]
        st.markdown(_md_html(f"""
            <div style="display:flex; align-items:baseline; gap:10px; padding:8px 0; border-bottom:1px solid {_card_border};">
                <span style="background:{_kind_color}22; color:{_kind_color}; padding:2px 8px; border-radius:6px; font-size:0.7rem; font-weight:700; white-space:nowrap;">{kind}</span>
                <span style="font-weight:600; color:{PLOTLY_FONT_COLOR}; white-space:nowrap;">{name}</span>
                <span style="font-size:0.78rem; color:{_muted}; font-family:monospace;">{cols}</span>
            </div>
        """), unsafe_allow_html=True)

with tab_dashboard:
    # --- Données du mois courant ---
    dept_code = st.session_state.selected_dept_code
    is_domtom = dept_code in DOMTOM_CODES

    if st.session_state.view_level == "National":
        df_m = df_agg_dept[df_agg_dept["mois"] == selected_month]
    else:
        df_m = df_agg_commune[
            (df_agg_commune["mois"] == selected_month) &
            (df_agg_commune["code_departement"] == dept_code)
        ]

    # --- Recherche (étroite, empilée) + mois (grille 6x2), une seule rangée
    # en haut : la sélection tient dans une bande au lieu d'une ligne
    # recherche pleine largeur + une colonne mois tout en hauteur. ---
    col_search, col_months = st.columns([3, 9], gap="medium")

    with col_search:
        sr_dept, sr_commune = st.columns(2, gap="small")

        with sr_dept:
            search_dept = st.selectbox(
                "Département",
                options=list(dept_options.keys()),
                format_func=lambda c: dept_options[c],
                index=0,
                placeholder="Département…",
                key="dept_search",
            )
            if search_dept and search_dept != st.session_state.get("selected_dept_code"):
                st.session_state.selected_dept_code = search_dept
                st.session_state.view_level = "Department"
                st.rerun()

        with sr_commune:
            search_commune = st.selectbox(
                "Commune",
                options=[""] + sorted_communes,
                index=0,
                placeholder="Commune…",
                key="commune_search",
            )

        st.button(
            "← Retour",
            on_click=reset_view,
            disabled=st.session_state.view_level != "Department",
            use_container_width=True,
        )

    with col_months:
        st.pills(
            "Mois", options=list(MOIS_LABELS.values()),
            key="selected_month_label",
            label_visibility="collapsed",
        )

    # --- KPIs : calculs (rendu plus bas, dans la colonne à droite de la carte) ---
    nb_zones    = len(df_m)
    mean_rate   = df_m["compliance_rate"].mean() if not df_m.empty else 0
    nb_conforme  = len(df_m[df_m["compliance_rate"] >= 95])
    nb_vigilance = len(df_m[(df_m["compliance_rate"] >= 80) & (df_m["compliance_rate"] < 95)])
    nb_alerte    = len(df_m[df_m["compliance_rate"] < 80])

    # --- Paramètres physico-chimiques / bactériologiques : calculs (le statut
    # bactério est rendu dans la colonne KPI, le graphique physico-chimique
    # tout en bas avec les autres graphiques) ---
    PARAM_COLORS = {
        "Nitrates":        "#f97316",
        "Nitrites":        "#ef4444",
        "Trihalométhanes": "#a855f7",
        "Turbidité":       "#06b6d4",
        "Fluorures":       "#84cc16",
    }
    BACT_COLORS = {
        "E. coli":      "#f87171",
        "Entérocoques": "#fb923c",
    }
    MOIS_SHORT = [MOIS_LABELS[m][:3] for m in range(1, 13)]
    STATUS_COLORS = (
        {"Conforme": "#32ff7e", "Vigilance": "#ffaf40", "Alerte": "#ff4d4d"} if _dark
        else {"Conforme": "#276749", "Vigilance": "#c05621", "Alerte": "#c53030"}
    )

    def get_params_scope(df_dept, df_commune):
        """Retourne (df_pct, df_bact) selon la vue courante."""
        if search_commune:
            commune_code = commune_name_to_code.get(search_commune)
            if commune_code:
                src = df_commune[df_commune["code_commune"] == commune_code]
            else:
                src = pd.DataFrame()
        elif st.session_state.view_level == "Department" and dept_code:
            src = df_dept[df_dept["code_departement"] == dept_code]
        else:
            # National : médiane des depts par mois × paramètre
            if df_dept.empty:
                return pd.DataFrame(), pd.DataFrame()
            src = df_dept.groupby(
                ["mois", "code_parametre", "nom_parametre", "type", "limite"]
            ).agg(
                valeur_mediane=("valeur_mediane", "median"),
                pct_limite=("pct_limite", "median"),
            ).reset_index()

        if src.empty:
            return pd.DataFrame(), pd.DataFrame()

        df_pct  = src[src["type"] == "pct"]
        df_bact = src[src["type"] == "count"]
        return df_pct, df_bact

    if search_commune:
        params_label = search_commune
    elif st.session_state.view_level == "Department" and dept_code:
        params_label = dept_names.get(dept_code, dept_code)
    else:
        params_label = "France"

    df_pct, df_bact = get_params_scope(df_params_dept, df_params_commune)

    # ============================================================
    # MOIS (empilés verticalement) + CARTE
    # ============================================================

    def coloraxis_config():
        return dict(
            colorscale=COLOR_SCALE, cmin=70, cmax=100,
            colorbar=dict(
                title=dict(text="%", font=dict(size=11)),
                thickness=12, len=0.35, x=0.175, y=0.85, yanchor="top",
            ),
        )

    def common_map_layout():
        return dict(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor="rgba(0,0,0,0)",
            clickmode="event+select",
            showlegend=False,
        )

    def geo_config(**overrides):
        """Config geo commune : traces Choropleth pures (pas de mapbox/tuiles, donc pas
        de clé API ni de dépendance à un fournisseur tiers). Fond transparent — hérite
        de la couleur de la carte (.stPlotlyChart) posée en CSS, dark ou light."""
        cfg = dict(
            bgcolor="rgba(0,0,0,0)",
            showland=False, showcountries=False, showframe=False,
            showcoastlines=False, showsubunits=False, showocean=False, showlakes=False,
            projection_type="mercator",
            fitbounds="locations",
        )
        cfg.update(overrides)
        return cfg

    @st.cache_resource
    def get_dept_commune_geo(dept: str):
        """Sous-ensemble GeoJSON communes d'un département (35k features filtrées une seule fois)."""
        features = [
            f for f in geojson_commune_all["features"]
            if f["properties"]["code"].startswith(dept)
        ]
        return {"type": "FeatureCollection", "features": features}

    col_map, col_kpi = st.columns([7.5, 2.5], gap="medium")

    with col_kpi:
        # KPI sur 2 rangées de 2 (au lieu d'une colonne empilée tout en
        # hauteur) : rangée 1 = Zones + manomètre Conformité, rangée 2 =
        # statuts Conforme/Vigilance/Alerte (compactés en une carte) + Bactério.
        kpi_r1c1, kpi_r1c2 = st.columns(2, gap="small")
        with kpi_r1c1:
            st.markdown(f"""
                <div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;
                            height:160px;box-sizing:border-box;padding:10px 12px;
                            display:flex;flex-direction:column;justify-content:center;align-items:center;">
                    <span style="font-size:0.75rem;color:{_muted}">Zones</span>
                    <span style="font-size:1.6rem;font-weight:700;color:{PLOTLY_FONT_COLOR}">{nb_zones}</span>
                </div>
            """, unsafe_allow_html=True)
        with kpi_r1c2:
            with st.container(key="gauge_card"):
                st.caption("Conformité")
                st.plotly_chart(
                    make_gauge_fig(mean_rate),
                    use_container_width=True, config={"displayModeBar": False}, key="gauge_conformite",
                )

        kpi_r2c1, kpi_r2c2 = st.columns(2, gap="small")
        with kpi_r2c1:
            if _dark:
                KPI_ROWS = [
                    ("Conforme",  nb_conforme,  "#32ff7e"),
                    ("Vigilance", nb_vigilance, "#ffaf40"),
                    ("Alerte",    nb_alerte,    "#ff4d4d"),
                ]
            else:
                KPI_ROWS = [
                    ("Conforme",  nb_conforme,  "#276749"),
                    ("Vigilance", nb_vigilance, "#c05621"),
                    ("Alerte",    nb_alerte,    "#c53030"),
                ]
            _rows_html = "".join(
                f"""<div style="display:flex;align-items:center;justify-content:space-between;">
                        <span style="font-size:0.72rem;color:{_muted}">{label}</span>
                        <span style="font-size:0.95rem;font-weight:700;color:{color}">{count}</span>
                    </div>"""
                for label, count, color in KPI_ROWS
            )
            st.markdown(_md_html(f"""
                <div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;
                            height:160px;box-sizing:border-box;padding:10px 12px;
                            display:flex;flex-direction:column;justify-content:space-evenly;">
                    {_rows_html}
                </div>
            """), unsafe_allow_html=True)

        with kpi_r2c2:
            # Statut bactériologique
            _has_detections = bool(not df_bact.empty and df_bact["valeur_mediane"].sum() > 0)
            if _has_detections:
                _bact_bg, _bact_border, _bact_accent = ("#1a0808", "#3a1515", "#ff4d4d") if _dark else ("#fff5f5", "#fed7d7", "#c53030")
                _bact_total = int(df_bact["valeur_mediane"].sum())
                _bact_detail = " · ".join(
                    f"{nom} : {int(df_bact[df_bact['nom_parametre'] == nom]['valeur_mediane'].sum())}"
                    for nom in BACT_COLORS
                    if not df_bact[df_bact["nom_parametre"] == nom].empty
                )
            else:
                _bact_bg, _bact_border, _bact_accent = ("#0a1f14", "#1e4030", "#32ff7e") if _dark else ("#f0fff4", "#9ae6b4", "#276749")
                _bact_total, _bact_detail = 0, "E. coli · Entérocoques — RAS"

            st.markdown(_md_html(f"""
                <div style="background:{_bact_bg}; border:1px solid {_bact_border}; border-radius:12px;
                            height:160px; box-sizing:border-box; padding:10px 12px;
                            display:flex; flex-direction:column; justify-content:center;">
                    <div style="display:flex; align-items:center; justify-content:space-between;">
                        <span style="font-size:0.75rem; color:{_muted};">Bactério.</span>
                        <span style="font-size:1.3rem; font-weight:700; color:{_bact_accent};">{_bact_total}</span>
                    </div>
                    <div style="font-size:0.65rem; color:{_bact_accent}; margin-top:4px;">{_bact_detail}</div>
                </div>
            """), unsafe_allow_html=True)

    with col_map:
        if st.session_state.view_level == "National":
            # ── Carte nationale : métropole + 5 insets DOM-TOM ──────────────
            fig = go.Figure()

            df_metro = df_m[~df_m["code_departement"].isin(DOMTOM_CODES)]

            fig.add_trace(go.Choropleth(
                geojson=geojson_dept,
                locations=df_metro["code_departement"],
                z=df_metro["compliance_rate"],
                featureidkey="properties.code",
                coloraxis="coloraxis",
                text=df_metro["nom_dept"],
                hovertemplate="<b>%{text}</b><br>Conformité : %{z:.1f}%<extra></extra>",
                marker_opacity=0.8,
                marker_line_width=0.5,
                marker_line_color="#1e2530",
                geo="geo",
            ))

            for i, (code, name, lat, lon, zoom, y_dom) in enumerate(DOM_TOM_CONFIG):
                feat = [f for f in geojson_domtom["features"] if f["properties"]["code"] == code]
                if not feat:
                    continue
                geo_ft = {"type": "FeatureCollection", "features": feat}
                df_t = df_m[df_m["code_departement"] == code]
                locs  = df_t["code_departement"] if not df_t.empty else pd.Series(dtype=str)
                zvals = df_t["compliance_rate"]   if not df_t.empty else pd.Series(dtype=float)
                texts = [name] * len(df_t)        if not df_t.empty else []

                fig.add_trace(go.Choropleth(
                    geojson=geo_ft, locations=locs, z=zvals,
                    featureidkey="properties.code",
                    coloraxis="coloraxis",
                    text=texts,
                    hovertemplate="<b>%{text}</b><br>Conformité : %{z:.1f}%<extra></extra>",
                    marker_opacity=0.8,
                    marker_line_width=0.5,
                    marker_line_color="#1e2530",
                    geo=f"geo{i+2}",
                ))
                fig.update_layout(**{f"geo{i+2}": geo_config(
                    domain={"x": [0, 0.14], "y": y_dom},
                )})

            # Étiquettes des insets, au-dessus de chaque inset empilé
            for code, name, lat, lon, zoom, y_dom in DOM_TOM_CONFIG:
                fig.add_annotation(
                    text=name, x=0.07, y=y_dom[1] + 0.015,
                    xref="paper", yref="paper",
                    showarrow=False, font=dict(size=9, color="#718096"),
                    xanchor="center", yanchor="bottom",
                )

            fig.update_layout(
                **common_map_layout(),
                geo=geo_config(domain={"x": [0.16, 1.0], "y": [0, 1.0]}),
                coloraxis=coloraxis_config(),
                height=460,
            )

            event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="main_map")

            if event:
                points = event.get("selection", {}).get("points", [])
                if points:
                    clicked = points[0].get("location")
                    if clicked:
                        st.session_state.selected_dept_code = clicked
                        st.session_state.view_level = "Department"
                        st.rerun()

        elif is_domtom:
            # ── Drill-down DOM-TOM : pas de GeoJSON communes → affichage département
            feat = [f for f in geojson_domtom["features"] if f["properties"]["code"] == dept_code]
            geo_ft = {"type": "FeatureCollection", "features": feat}
            df_d = df_agg_dept[(df_agg_dept["mois"] == selected_month) &
                               (df_agg_dept["code_departement"] == dept_code)]

            fig = go.Figure(go.Choropleth(
                geojson=geo_ft,
                locations=df_d["code_departement"] if not df_d.empty else pd.Series(dtype=str),
                z=df_d["compliance_rate"]           if not df_d.empty else pd.Series(dtype=float),
                featureidkey="properties.code",
                coloraxis="coloraxis",
                text=df_d["nom_dept"] if not df_d.empty else [],
                hovertemplate="<b>%{text}</b><br>Conformité : %{z:.1f}%<extra></extra>",
                marker_opacity=0.8,
            ))
            fig.update_layout(
                **common_map_layout(),
                geo=geo_config(),
                coloraxis=coloraxis_config(),
                height=420,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="dept_map")
            st.caption("Données cartographiques communes non disponibles pour ce territoire — affichage au niveau départemental.")

        else:
            # ── Drill-down département (métropole) : niveau commune ──────────
            geo_local = get_dept_commune_geo(dept_code)

            fig = go.Figure(go.Choropleth(
                geojson=geo_local,
                locations=df_m["code_commune"],
                z=df_m["compliance_rate"],
                featureidkey="properties.code",
                coloraxis="coloraxis",
                text=df_m["nom_commune"],
                hovertemplate="<b>%{text}</b><br>Conformité : %{z:.1f}%<extra></extra>",
                marker_opacity=0.8,
                marker_line_width=0.3,
                marker_line_color="#1e2530",
            ))
            fig.update_layout(
                **common_map_layout(),
                geo=geo_config(),
                coloraxis=coloraxis_config(),
                height=420,
            )
            st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="dept_map")

    # ============================================================
    # PANNEAU BAS : Conformité temporelle + zoom commune
    # ============================================================

    @st.cache_data
    def build_conformity_trend(dept_code=None):
        """Conformité mensuelle pondérée depuis df_agg_dept (national ou un département)."""
        df = df_agg_dept[df_agg_dept["code_departement"] == dept_code] if dept_code else df_agg_dept
        g = df.groupby("mois")[["compliant_tests", "total_tests"]].sum().reindex(range(1, 13))
        rate = (g["compliant_tests"] / g["total_tests"] * 100).where(g["total_tests"] > 0)
        return pd.DataFrame({
            "mois": [MOIS_LABELS[m][:3] for m in range(1, 13)],
            "Conformité": rate.to_numpy(),
        })

    @st.cache_data
    def build_commune_trend(commune_code):
        """Conformité mensuelle d'une commune (None si aucune donnée)."""
        df_c = df_agg_commune[df_agg_commune["code_commune"] == commune_code]
        if df_c.empty:
            return None
        rate = df_c.set_index("mois")["compliance_rate"].reindex(range(1, 13))
        return pd.DataFrame({
            "mois": [MOIS_LABELS[m][:3] for m in range(1, 13)],
            "Conformité": rate.to_numpy(),
        })

    def make_conformity_fig(df_td, title, zone_label="Zone", df_commune_td=None, commune_label=None, emphasized=False):
        """emphasized=True (zoom département) : ligne plus épaisse/saturée et courbe
        lissée façon "flux d'eau", plutôt que le trait fin de la vue nationale."""
        vals = df_td["Conformité"].dropna()
        ymin = max(0, vals.min() - 5) if not vals.empty else 0
        ymax = min(100, vals.max() + 2) if not vals.empty else 100

        if df_commune_td is not None:
            c_vals = df_commune_td["Conformité"].dropna()
            if not c_vals.empty:
                ymin = min(ymin, max(0, c_vals.min() - 5))
                ymax = max(ymax, min(100, c_vals.max() + 2))

        line_color = "#3b82f6" if emphasized else "#60a5fa"
        fig = go.Figure()
        # Ligne de base invisible calée sur le bas de l'axe visible : le fill
        # "tonexty" contre cette ligne (plutôt que "tozeroy" jusqu'à 0%) garde
        # le dégradé entièrement dans la zone visible du graphique — avec
        # tozeroy le dégradé s'étirait jusqu'à 0%, bien en dehors du cadrage
        # [ymin, ymax], et rendait un fill quasi invisible.
        fig.add_trace(go.Scatter(
            x=df_td["mois"], y=[ymin] * len(df_td),
            mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=df_td["mois"], y=df_td["Conformité"],
            name=zone_label,
            mode="lines+markers",
            line=dict(color=line_color, width=4 if emphasized else 2.5, shape="spline" if emphasized else "linear"),
            marker=dict(size=7 if emphasized else 6, color=line_color),
            fill="tonexty",
            fillgradient=dict(
                type="vertical",
                colorscale=[
                    [0, "rgba(59,130,246,0.42)" if emphasized else "rgba(96,165,250,0.22)"],
                    [1, "rgba(59,130,246,0.02)" if emphasized else "rgba(96,165,250,0.01)"],
                ],
            ),
            hovertemplate=f"{zone_label} — %{{x}} : %{{y:.1f}}%<extra></extra>",
        ))

        if df_commune_td is not None:
            fig.add_trace(go.Scatter(
                x=df_commune_td["mois"], y=df_commune_td["Conformité"],
                name=commune_label,
                mode="lines+markers",
                line=dict(color="#f97316", width=2, dash="dot"),
                marker=dict(size=6, color="#f97316"),
                hovertemplate=f"{commune_label} — %{{x}} : %{{y:.1f}}%<extra></extra>",
            ))

        fig.update_layout(
            template=PLOTLY_TEMPLATE, height=150,
            title=dict(text=title, font=dict(size=13, color=PLOTLY_FONT_COLOR), x=0, pad=dict(l=0)),
            yaxis=dict(range=[ymin, ymax], title="%", ticksuffix="%", tickfont=dict(color=PLOTLY_FONT_COLOR), automargin=True),
            xaxis=dict(tickfont=dict(size=10, color=PLOTLY_FONT_COLOR), automargin=True),
            showlegend=df_commune_td is not None,
            legend=dict(orientation="h", y=-0.3, x=0, font=dict(size=10, color=PLOTLY_FONT_COLOR)),
            margin=dict(l=10, r=10, t=35, b=45 if df_commune_td is not None else 15),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=PLOTLY_FONT_COLOR),
        )
        return fig

    # Scope de la vue courante
    if st.session_state.view_level == "Department" and dept_code:
        trend_title  = dept_names.get(dept_code, dept_code)
        trend_zone   = trend_title
    else:
        trend_title = "France"
        trend_zone  = "France"

    # Ligne conformité département / France
    dc    = dept_code if st.session_state.view_level == "Department" else None
    df_td = build_conformity_trend(dc)

    # Overlay commune si sélectionnée
    df_commune_td  = None
    commune_label  = None
    if search_commune:
        _c_code = commune_name_to_code.get(search_commune)
        if _c_code:
            df_commune_td = build_commune_trend(_c_code)
            if df_commune_td is not None:
                commune_label = search_commune

    st.plotly_chart(
        make_conformity_fig(
            df_td, f"Conformité 2024 — {trend_title}",
            zone_label=trend_zone,
            df_commune_td=df_commune_td,
            commune_label=commune_label,
            emphasized=(st.session_state.view_level == "Department"),
        ),
        use_container_width=True, config={"displayModeBar": False},
    )

    st.caption("Source : Hub'Eau API (2024). Cliquez sur un département pour zoomer.")

    # ============================================================
    # ÉVOLUTION MENSUELLE DES ZONES PAR STATUT (empilées façon segments
    # de tuyau : coins arrondis + liseré de "raccord" entre chaque
    # segment, dans l'ordre où l'eau traverserait un tuyau conforme)
    # ============================================================

    @st.cache_data
    def build_status_evolution(dept_code=None):
        """Nb de zones Conforme/Vigilance/Alerte par mois (mêmes seuils que les KPI)."""
        df = df_agg_commune[df_agg_commune["code_departement"] == dept_code] if dept_code else df_agg_dept
        rows = []
        for m in range(1, 13):
            dm = df[df["mois"] == m]
            rows.append({
                "mois": MOIS_LABELS[m][:3],
                "Conforme":  int((dm["compliance_rate"] >= 95).sum()),
                "Vigilance": int(((dm["compliance_rate"] >= 80) & (dm["compliance_rate"] < 95)).sum()),
                "Alerte":    int((dm["compliance_rate"] < 80).sum()),
            })
        return pd.DataFrame(rows)

    def make_status_bars_fig(df_evo, title):
        """Barres empilées, coins arrondis + liseré clair entre segments : lecture
        façon coupe de tuyauterie (chaque segment = un raccord empilé sur l'autre)."""
        fig = go.Figure()
        gap_color = "#0e1117" if _dark else "#ffffff"
        for statut in ("Conforme", "Vigilance", "Alerte"):
            fig.add_trace(go.Bar(
                x=df_evo["mois"], y=df_evo[statut],
                name=statut,
                marker=dict(
                    color=STATUS_COLORS[statut],
                    cornerradius=6,
                    line=dict(width=2, color=gap_color),
                ),
                hovertemplate=f"{statut} — %{{x}} : %{{y}} zones<extra></extra>",
            ))
        fig.update_layout(
            template=PLOTLY_TEMPLATE, height=150, barmode="stack", bargap=0.35,
            title=dict(text=title, font=dict(size=13, color=PLOTLY_FONT_COLOR), x=0, pad=dict(l=0)),
            yaxis=dict(title="Zones", tickfont=dict(color=PLOTLY_FONT_COLOR), rangemode="tozero", automargin=True),
            xaxis=dict(tickfont=dict(size=10, color=PLOTLY_FONT_COLOR), automargin=True),
            legend=dict(orientation="h", y=-0.3, x=0, font=dict(size=10, color=PLOTLY_FONT_COLOR)),
            margin=dict(l=10, r=10, t=35, b=45),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=PLOTLY_FONT_COLOR),
        )
        return fig

    df_status_evo = build_status_evolution(dc)
    st.plotly_chart(
        make_status_bars_fig(df_status_evo, f"Zones par statut, mois par mois — {trend_title}"),
        use_container_width=True, config={"displayModeBar": False},
    )

    # ============================================================
    # GRAPHIQUES : niveaux physico-chimiques (PARAM_COLORS, MOIS_SHORT,
    # df_pct et params_label déjà calculés plus haut, avant la carte)
    # ============================================================

    def make_params_fig(df_pct, scope_label):
        """Multi-lignes % de la limite légale pour les paramètres physico-chimiques."""
        fig = go.Figure()

        # Ligne de danger à 100%
        fig.add_shape(
            type="line", x0=-0.5, x1=11.5, y0=100, y1=100,
            line=dict(color="#ff4d4d", width=1.5, dash="dash"),
            xref="x", yref="y",
        )
        fig.add_annotation(
            x=11, y=102, text="Limite légale", font=dict(size=9, color="#ff4d4d"),
            showarrow=False, xref="x", yref="y",
        )

        for nom, color in PARAM_COLORS.items():
            sub = df_pct[df_pct["nom_parametre"] == nom]
            if sub.empty:
                continue
            y_vals = []
            for m in range(1, 13):
                row = sub[sub["mois"] == m]
                y_vals.append(row["pct_limite"].values[0] if not row.empty else None)

            fig.add_trace(go.Scatter(
                x=MOIS_SHORT, y=y_vals,
                name=nom,
                mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(size=5, color=color),
                connectgaps=True,
                hovertemplate=f"<b>{nom}</b><br>%{{x}} : %{{y:.1f}}% limite<extra></extra>",
            ))

        fig.update_layout(
            template=PLOTLY_TEMPLATE, height=170,
            title=dict(
                text=f"Niveaux physico-chimiques — {scope_label}",
                font=dict(size=13, color=PLOTLY_FONT_COLOR), x=0,
            ),
            yaxis=dict(title="% limite", ticksuffix="%", rangemode="tozero", tickfont=dict(color=PLOTLY_FONT_COLOR), automargin=True),
            xaxis=dict(tickfont=dict(size=10, color=PLOTLY_FONT_COLOR), automargin=True),
            legend=dict(orientation="h", y=-0.35, x=0, font=dict(size=10, color=PLOTLY_FONT_COLOR)),
            margin=dict(l=10, r=10, t=40, b=55),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=PLOTLY_FONT_COLOR),
        )
        return fig


    if df_pct.empty:
        st.info("Aucune donnée de paramètres physico-chimiques disponible pour cette sélection.")
    else:
        st.plotly_chart(
            make_params_fig(df_pct, params_label),
            use_container_width=True, config={"displayModeBar": False},
        )

