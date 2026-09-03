"""
Dashboard Streamlit — Qualité de l'eau potable en France (2024)
Carte pleine largeur avec insets DOM-TOM (Option B) + drill-down départements
"""

import streamlit as st
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
st.set_page_config(page_title="Qualité de l'eau en France 2024", layout="wide", page_icon=":material/water_drop:")

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

# Config insets DOM-TOM : (code, nom, lat, lon, zoom, x_domain)
DOM_TOM_CONFIG = [
    ("971", "Guadeloupe",  16.17, -61.57,  7.5, [0.00, 0.185]),
    ("972", "Martinique",  14.67, -61.00,  8.5, [0.20, 0.385]),
    ("973", "Guyane",       4.00, -53.00,  4.5, [0.40, 0.585]),
    ("974", "La Réunion", -21.10,  55.50,  7.0, [0.60, 0.785]),
    ("976", "Mayotte",    -12.80,  45.15,  9.5, [0.80, 0.985]),
]
DOMTOM_CODES = {c[0] for c in DOM_TOM_CONFIG}

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

def make_gauge_fig(value):
    """Manomètre de conformité (esthétique tuyauterie/pression)."""
    needle_color = "#e2e8f0" if _dark else "#1a202c"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix="%", font=dict(size=22, color=PLOTLY_FONT_COLOR)),
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
        height=110, margin=dict(l=15, r=15, t=5, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PLOTLY_FONT_COLOR),
    )
    return fig

# Injection CSS adaptative
# NB : depuis Streamlit ~1.56 les boutons pills n'ont plus de data-testid
# "stBaseButton-pills(Active)" — on cible button[data-variant="pills"] et
# l'état sélectionné via aria-checked.
_CSS_COMMON = """
    /* Largeur max */
    .block-container { max-width: 1400px !important; padding-left: 2rem !important; padding-right: 2rem !important; }
    /* Sélecteur de mois : pills empilés verticalement, étirés sur toute la
       hauteur de la carte à droite (espacement égal plutôt qu'un petit gap fixe). */
    .st-key-selected_month_label, .st-key-selected_month_label > div {
        height: 100% !important;
    }
    .st-key-selected_month_label div[data-testid="stButtonGroup"] {
        display: flex !important; flex-direction: column !important;
        align-items: stretch !important; justify-content: space-between !important;
        height: 100% !important; width: 100% !important;
    }
    .st-key-selected_month_label div[data-testid="stButtonGroup"] > div {
        display: flex !important; flex-direction: column !important;
        justify-content: space-between !important; height: 100% !important; width: 100% !important;
    }
    .st-key-selected_month_label button[data-variant="pills"] {
        width: 100% !important; justify-content: center !important;
    }
    /* Toggle thème : éviter le retour à la ligne du label */
    .st-key-dark_mode label p { white-space: nowrap !important; }
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
        /* BaseUI widgets (selectbox, input) */
        [data-baseweb="select"] > div, [data-baseweb="input"] > div,
        [data-baseweb="base-input"], [data-baseweb="textarea"] {{
            background-color: #151921 !important; color: #e2e8f0 !important; border-color: #232a35 !important;
        }}
        [data-baseweb="select"] svg {{ fill: #e2e8f0 !important; }}
        [data-baseweb="menu"], [data-baseweb="popover"] > div {{
            background-color: #151921 !important; color: #e2e8f0 !important;
        }}
        [data-baseweb="menu"] li:hover {{ background-color: #232a35 !important; }}
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
           graphique Plotly plutôt qu'un rendu bord-à-bord. */
        [data-testid="stPlotlyChart"] {{
            background: #151921; border: 1px solid #232a35; border-radius: 12px;
            padding: 10px; overflow: hidden;
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
col_title, col_theme = st.columns([9, 1])
with col_title:
    scope_text = "France" if st.session_state.view_level == "National" else dept_names.get(st.session_state.selected_dept_code, "Département")
    kicker_color = "#5b6472" if _dark else "#94a3b8"

    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
            <div style="flex-shrink: 0; width: 52px; height: 52px; border-radius: 14px;
                        background: linear-gradient(135deg, #60A5FA 0%, #2563EB 100%);
                        display: flex; align-items: center; justify-content: center;
                        box-shadow: 0 4px 14px rgba(37,99,235,0.35);">
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3.5" y="18" width="17" height="3.2" rx="1.6" fill="#ffffff" opacity="0.85"/>
                    <rect x="10.5" y="14" width="3" height="4.5" rx="1" fill="#ffffff"/>
                    <circle cx="12" cy="9" r="5" stroke="#ffffff" stroke-width="2"/>
                    <line x1="12" y1="4" x2="12" y2="14" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
                    <line x1="7" y1="9" x2="17" y2="9" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
                    <circle cx="12" cy="9" r="1.6" fill="#ffffff"/>
                </svg>
            </div>
            <div style="display: flex; flex-direction: column; gap: 2px; line-height: 1;">
                <span style="font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em; color: {kicker_color}; text-transform: uppercase;">Suivi qualité de l'eau potable</span>
                <h1 style="margin: 0; padding: 0; font-size: 2.15rem; font-weight: 800; line-height: 1.25; letter-spacing: -0.02em; background: linear-gradient(90deg, #60A5FA 0%, #3B82F6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{scope_text} <span style="opacity: 0.55;">· 2024</span></h1>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_theme:
    st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
    st.toggle("Mode sombre", key="dark_mode")

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

# --- KPIs : 2 métriques + 3 blocs colorés ---
nb_zones    = len(df_m)
mean_rate   = df_m["compliance_rate"].mean() if not df_m.empty else 0
nb_conforme  = len(df_m[df_m["compliance_rate"] >= 95])
nb_vigilance = len(df_m[(df_m["compliance_rate"] >= 80) & (df_m["compliance_rate"] < 95)])
nb_alerte    = len(df_m[df_m["compliance_rate"] < 80])

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Zones", f"{nb_zones}")
with c2:
    st.caption("Conformité")
    st.plotly_chart(
        make_gauge_fig(mean_rate),
        use_container_width=True, config={"displayModeBar": False}, key="gauge_conformite",
    )

if _dark:
    KPI_CARDS = [
        (c3, "Conforme ≥95%",    nb_conforme,  "#0a1f14", "#1e4030", "#32ff7e", "#a0aec0"),
        (c4, "Vigilance 80–95%", nb_vigilance, "#1a1500", "#3a3000", "#ffaf40", "#a0aec0"),
        (c5, "Alerte &lt;80%",   nb_alerte,    "#1a0808", "#3a1515", "#ff4d4d", "#a0aec0"),
    ]
else:
    KPI_CARDS = [
        (c3, "Conforme ≥95%",    nb_conforme,  "#f0fff4", "#9ae6b4", "#276749", "#4a5568"),
        (c4, "Vigilance 80–95%", nb_vigilance, "#fffaf0", "#fbd38d", "#c05621", "#4a5568"),
        (c5, "Alerte &lt;80%",   nb_alerte,    "#fff5f5", "#fed7d7", "#c53030", "#4a5568"),
    ]
for col, label, count, bg, border, color, label_color in KPI_CARDS:
    with col:
        st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};padding:15px;border-radius:12px">
                <div style="font-size:0.8rem;color:{label_color};margin-bottom:6px">{label}</div>
                <div style="font-size:2rem;font-weight:700;color:{color};line-height:1">{count}</div>
            </div>
        """, unsafe_allow_html=True)

# --- Recherche (sous les KPIs) ---
st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
st.caption("Rechercher par")
sr_dept, sr_commune, sr_reset = st.columns([6, 6, 2])

with sr_dept:
    search_dept  = st.selectbox(
        "Département",
        options=list(dept_options.keys()),
        format_func=lambda c: dept_options[c],
        index=0,
        placeholder="Rechercher un département…",
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
        placeholder="Rechercher une commune…",
        key="commune_search",
    )

with sr_reset:
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
    st.button(
        "← Retour",
        on_click=reset_view,
        disabled=st.session_state.view_level != "Department",
        use_container_width=True,
    )

st.divider()

# ============================================================
# MOIS (empilés verticalement) + CARTE
# ============================================================

def coloraxis_config():
    return dict(
        colorscale=COLOR_SCALE, cmin=70, cmax=100,
        colorbar=dict(
            title=dict(text="%", font=dict(size=11)),
            thickness=12, len=0.35, x=0.005, y=0.65, yanchor="middle",
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

col_months, col_map = st.columns([1.4, 8.6], gap="medium")

with col_months:
    st.pills(
        "Mois", options=list(MOIS_LABELS.values()),
        key="selected_month_label",
        label_visibility="collapsed",
    )

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

        for i, (code, name, lat, lon, zoom, x_dom) in enumerate(DOM_TOM_CONFIG):
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
                domain={"x": x_dom, "y": [0.01, 0.22]},
            )})

        # Étiquettes des insets
        label_x = [0.093, 0.293, 0.493, 0.693, 0.893]
        for (code, name, *_), x_c in zip(DOM_TOM_CONFIG, label_x):
            fig.add_annotation(
                text=name, x=x_c, y=0.235,
                xref="paper", yref="paper",
                showarrow=False, font=dict(size=9, color="#718096"),
                xanchor="center",
            )

        fig.update_layout(
            **common_map_layout(),
            geo=geo_config(domain={"x": [0, 1], "y": [0.25, 1.0]}),
            coloraxis=coloraxis_config(),
            height=680,
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
            height=580,
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
            height=580,
        )
        st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="dept_map")

st.divider()

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

def make_conformity_fig(df_td, title, zone_label="Zone", df_commune_td=None, commune_label=None):
    vals = df_td["Conformité"].dropna()
    ymin = max(0, vals.min() - 5) if not vals.empty else 0
    ymax = min(100, vals.max() + 2) if not vals.empty else 100

    if df_commune_td is not None:
        c_vals = df_commune_td["Conformité"].dropna()
        if not c_vals.empty:
            ymin = min(ymin, max(0, c_vals.min() - 5))
            ymax = max(ymax, min(100, c_vals.max() + 2))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_td["mois"], y=df_td["Conformité"],
        name=zone_label,
        mode="lines+markers",
        line=dict(color="#60a5fa", width=2.5),
        marker=dict(size=6, color="#60a5fa"),
        fill="tozeroy", fillcolor="rgba(96,165,250,0.08)",
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
        template=PLOTLY_TEMPLATE, height=220,
        title=dict(text=title, font=dict(size=13, color=PLOTLY_FONT_COLOR), x=0, pad=dict(l=0)),
        yaxis=dict(range=[ymin, ymax], title="%", ticksuffix="%", tickfont=dict(color=PLOTLY_FONT_COLOR)),
        xaxis=dict(tickfont=dict(size=10, color=PLOTLY_FONT_COLOR)),
        showlegend=df_commune_td is not None,
        legend=dict(orientation="h", y=-0.25, x=0, font=dict(size=10, color=PLOTLY_FONT_COLOR)),
        margin=dict(l=10, r=10, t=35, b=40 if df_commune_td is not None else 10),
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
    ),
    use_container_width=True, config={"displayModeBar": False},
)

st.caption("Source : Hub'Eau API (2024). Cliquez sur un département pour zoomer.")

st.divider()

# ============================================================
# PANNEAU PARAMÈTRES : niveaux réels de prélèvement
# ============================================================

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
        template=PLOTLY_TEMPLATE, height=260,
        title=dict(
            text=f"Niveaux physico-chimiques — {scope_label} (% de la limite légale)",
            font=dict(size=13, color=PLOTLY_FONT_COLOR), x=0,
        ),
        yaxis=dict(title="% limite", ticksuffix="%", rangemode="tozero", tickfont=dict(color=PLOTLY_FONT_COLOR)),
        xaxis=dict(tickfont=dict(size=10, color=PLOTLY_FONT_COLOR)),
        legend=dict(orientation="h", y=-0.25, x=0, font=dict(size=10, color=PLOTLY_FONT_COLOR)),
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PLOTLY_FONT_COLOR),
    )
    return fig


# Scope label
if search_commune:
    params_label = search_commune
elif st.session_state.view_level == "Department" and dept_code:
    params_label = dept_names.get(dept_code, dept_code)
else:
    params_label = "France"

df_pct, df_bact = get_params_scope(df_params_dept, df_params_commune)

if df_pct.empty and df_bact.empty:
    st.info("Aucune donnée de paramètres disponible pour cette sélection.")
else:
    col_pct, col_bact = st.columns([3, 2])
    with col_pct:
        if not df_pct.empty:
            st.plotly_chart(
                make_params_fig(df_pct, params_label),
                use_container_width=True, config={"displayModeBar": False},
            )
    with col_bact:
        _has_detections = bool(not df_bact.empty and df_bact["valeur_mediane"].sum() > 0)
        if _has_detections:
            _bg, _border, _accent = ("#1a0808", "#3a1515", "#ff4d4d") if _dark else ("#fff5f5", "#fed7d7", "#c53030")
            _total = int(df_bact["valeur_mediane"].sum())
            _breakdown = " · ".join(
                f"{nom} : {int(df_bact[df_bact['nom_parametre'] == nom]['valeur_mediane'].sum())}"
                for nom in BACT_COLORS
                if not df_bact[df_bact["nom_parametre"] == nom].empty
            )
        else:
            _bg, _border, _accent = ("#0a1f14", "#1e4030", "#32ff7e") if _dark else ("#f0fff4", "#9ae6b4", "#276749")
            _total, _breakdown = 0, "E. coli · Entérocoques — RAS"

        st.markdown(_md_html(f"""
            <div style="background:{_bg}; border:2px solid {_accent}; border-radius:12px; padding:20px;
                        height:220px; display:flex; flex-direction:column; justify-content:center;
                        align-items:center; text-align:center;">
                <div style="font-size:0.85rem; color:{_muted}; margin-bottom:6px;">Détections bactériologiques — {params_label}</div>
                <div style="font-size:2.6rem; font-weight:800; color:{_accent}; line-height:1;">{_total}</div>
                <div style="font-size:0.8rem; color:{_accent}; margin-top:8px;">{_breakdown}</div>
            </div>
        """), unsafe_allow_html=True)

st.divider()

# ============================================================
# PANNEAU INFOS : À propos / Circulation de la donnée / Architecture
# ============================================================

TECH_BADGES = [
    ("Azure",      "#0078D4"),
    ("Databricks", "#FF3621"),
    ("Terraform",  "#7B42BC"),
    ("Delta Lake", "#00A1F1"),
    ("Python 3.13", "#3776AB"),
    ("FastAPI",    "#009688"),
    ("Streamlit",  "#FF4B4B"),
    ("Hub'Eau API", "#3B82F6"),
]

tab_about, tab_flow, tab_infra = st.tabs(["À propos", "Circulation de la donnée", "Architecture cloud & BDD"])

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
        <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:12px;">
            {"".join(f'<span style="background:{color}22; color:{color}; border:1px solid {color}55; padding:5px 12px; border-radius:999px; font-size:0.8rem; font-weight:600;">{name}</span>' for name, color in TECH_BADGES)}
        </div>
        <p style="margin-top:16px;">
            <a href="https://github.com/DVDJNBR/qlt-eau-FR-24" target="_blank" style="color:#60A5FA; font-size:0.9rem;">→ Code source sur GitHub</a>
        </p>
    """), unsafe_allow_html=True)

with tab_flow:
    PIPELINE_STEPS = [
        ("Hub'Eau API", "Source", "#3B82F6"),
        ("01 · Ingestion", "Bronze", "#cd7f32"),
        ("02 · Transformation", "Silver", "#c0c0c0"),
        ("03 · Agrégations", "Gold", "#ffd700"),
        ("04 · Quality Checks", "Contrôles", "#4caf50"),
        ("API REST", "Exposition", "#3B82F6"),
    ]
    _steps_html = ""
    for i, (title, subtitle, color) in enumerate(PIPELINE_STEPS):
        _steps_html += f"""
            <div style="display:flex; flex-direction:column; align-items:center; gap:4px; min-width:110px;">
                <div style="width:100%; padding:14px 10px; border-radius:12px; background:{color}22; border:2px solid {color}; text-align:center;">
                    <div style="font-weight:700; font-size:0.85rem; color:{PLOTLY_FONT_COLOR};">{title}</div>
                    <div style="font-size:0.72rem; color:{_muted}; margin-top:2px;">{subtitle}</div>
                </div>
            </div>
        """
        if i < len(PIPELINE_STEPS) - 1:
            _steps_html += f'<div style="font-size:1.4rem; color:{_muted}; padding:0 4px;">→</div>'

    st.markdown(_md_html(f"""
        <div style="display:flex; align-items:center; overflow-x:auto; padding:16px 4px; gap:2px;">
            {_steps_html}
        </div>
        <p style="color:{_muted}; font-size:0.85rem; margin-top:8px;">
            Ingestion incrémentale depuis Hub'Eau → nettoyage/standardisation Silver →
            star schema + KPIs Gold → contrôles qualité Spark natif → exposition REST
            directe depuis ADLS (sans compute Databricks au moment de la lecture).
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
