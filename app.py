import os
import csv
import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Strategic Market Research | IVIG & Emergent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# THEME COLORS & LOGO LOGIC
# =========================
BURGUNDY = "#5B0F2E"
BURGUNDY_DARK = "#431022"
BURGUNDY_MID = "#7A1C41"
BURGUNDY_SOFT = "#A45A7B"
GOLD = "#C9A227"
CARD = "rgba(255, 255, 255, 0.85)"
INK = "#1A1014"
MUTED = "#6B5B63"
BORDER = "rgba(255, 255, 255, 0.9)"

PREVIEW_NOTE = (
    "This dashboard is for preview purposes only. Competitor identities and specific "
    "market share revenues have been intentionally masked and abstracted into Tiers."
)

def load_logo_base64() -> str | None:
    candidates = [
        Path("smrlogonew.svg"), 
        Path(__file__).with_name("smrlogonew.svg"), 
        Path.cwd() / "smrlogonew.svg", 
        Path("logo.svg"), 
        Path(__file__).with_name("logo.svg")
    ]
    for path in candidates:
        if path.exists():
            try: return base64.b64encode(path.read_bytes()).decode("utf-8")
            except Exception: pass
    return None

LOGO_B64 = load_logo_base64()

# =========================
# CSS HIDING & UI POLISH
# =========================
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: {INK} !important;
    }}

    /* UI HIDING FOR WHITE-LABELING */
    [data-testid="stToolbar"] {{ display: none !important; }}
    .viewerBadge_container, #viewerBadge_container {{ display: none !important; }}
    footer {{ display: none !important; }}
    header[data-testid="stHeader"] {{ background: transparent !important; box-shadow: none !important; }}

    /* CUSTOM ELEGANT SCROLLBAR */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(91,15,46,0.15); border-radius: 10px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(91,15,46,0.3); }}

    /* LIVING GRADIENT BACKGROUND */
    .stApp {{
      background: radial-gradient(circle at 15% 0%, rgba(201,162,39,0.04) 0%, transparent 40%),
                  radial-gradient(circle at 85% 100%, rgba(91,15,46,0.03) 0%, transparent 40%),
                  linear-gradient(180deg, #FCFAFB 0%, #F4ECEF 100%);
      background-attachment: fixed;
    }}

    /* SIDEBAR REFINEMENT */
    [data-testid="stSidebar"] {{
        background: rgba(255,255,255,0.6) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(91,15,46,0.08) !important;
    }}

    /* SLEEK BUTTON STYLING */
    .stButton > button {{
        background: linear-gradient(135deg, {BURGUNDY} 0%, {BURGUNDY_MID} 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.02em;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 4px 14px rgba(91,15,46,0.2) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(91,15,46,0.3) !important;
    }}

    /* INPUT FIELDS */
    .stTextInput input {{
        border-radius: 8px !important;
        border: 1px solid rgba(91,15,46,0.15) !important;
        padding: 12px 14px !important;
        background: rgba(255,255,255,0.8) !important;
        transition: all 0.2s ease !important;
    }}
    .stTextInput input:focus {{
        border-color: {GOLD} !important;
        background: #fff !important;
        box-shadow: 0 0 0 3px rgba(201,162,39,0.15) !important;
    }}

    /* APP-LIKE NAVIGATION */
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] {{
        padding: 10px 14px !important;
        margin-bottom: 6px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover {{
        background: rgba(91,15,46,0.04) !important;
        transform: translateX(3px) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input[checked]) {{
         background: #ffffff !important;
         border-left: 4px solid {BURGUNDY} !important;
         box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] p {{
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        color: {INK} !important;
    }}

    /* FROSTED BRANDING HEADER */
    .smr-brand {{
      background: rgba(255,255,255,0.7);
      border: 1px solid {BORDER};
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.03);
      margin-bottom: 24px;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
    }}
    
    .hero {{
      background: linear-gradient(135deg, {BURGUNDY} 0%, {BURGUNDY_MID} 60%, {BURGUNDY_SOFT} 100%);
      color: white;
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 20px;
      padding: 34px 40px;
      box-shadow: 0 20px 40px rgba(61,16,33,0.15), inset 0 1px 0 rgba(255,255,255,0.2);
      margin-bottom: 24px;
      animation: floatIn 0.6s cubic-bezier(0.25, 0.8, 0.25, 1);
      position: relative;
      overflow: hidden;
    }}
    .hero::before {{
      content: ''; position: absolute; top: -50%; right: -10%; width: 60%; height: 200%;
      background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
      transform: rotate(-45deg);
    }}
    .hero h2 {{ margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em; text-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
    
    /* GLASSMORPHISM DATA CARDS */
    .metric-card {{
      background: {CARD};
      backdrop-filter: blur(20px);
      border: 1px solid {BORDER};
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 12px 36px rgba(91,15,46,0.03), 0 2px 8px rgba(0,0,0,0.02);
      min-height: 135px;
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }}
    .metric-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 16px 40px rgba(91,15,46,0.08);
      border-color: rgba(201,162,39,0.3);
    }}
    .metric-label {{
      color: {MUTED}; font-size: 0.82rem; margin-bottom: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
    }}
    .metric-value {{
      color: {BURGUNDY}; font-size: 2.6rem; font-weight: 800; line-height: 1; letter-spacing: -0.02em; margin-bottom: 12px;
    }}
    .metric-foot {{ color: {MUTED}; font-size: 0.85rem; line-height: 1.4; }}

    .section-card {{
      background: {CARD};
      backdrop-filter: blur(20px);
      border: 1px solid {BORDER};
      border-radius: 20px;
      padding: 24px;
      box-shadow: 0 12px 36px rgba(91,15,46,0.03);
      margin-bottom: 24px;
    }}
    .section-title {{ font-size: 1.2rem; font-weight: 800; color: {BURGUNDY}; margin-bottom: 6px; letter-spacing: -0.01em; }}
    .section-sub {{ color: {MUTED}; font-size: 0.9rem; margin-bottom: 20px; line-height: 1.5; }}
    
    .insight-box {{
      background: #ffffff;
      border: 1px solid rgba(201,162,39,0.2);
      border-left: 6px solid {GOLD};
      border-radius: 12px;
      padding: 20px 24px;
      color: {INK};
      font-size: 0.95rem;
      line-height: 1.6;
      margin-bottom: 24px;
      box-shadow: 0 8px 24px rgba(201,162,39,0.05);
    }}
    
    .viewer-chip {{
      display:inline-block; padding:6px 12px; border-radius:999px; font-size:0.75rem; font-weight:700;
      background: rgba(91,15,46,0.06); border: 1px solid rgba(91,15,46,0.1); color: {BURGUNDY};
      margin-top:10px; margin-bottom: 10px;
    }}

    @keyframes floatIn {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: translateY(0px); }} }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# UI Component Helpers
# =========================
def fmt_mn(value: float, mult: float = 1.0) -> str:
    if pd.isna(value): return "—"
    adj_val = value * mult
    if abs(adj_val) >= 1000: return f"≈${adj_val/1000:.1f}B"
    return f"≈${adj_val:,.0f}M"

def card_metric(label: str, value: str, foot: str):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>', unsafe_allow_html=True)

def section_open(title: str, subtitle: str = ""):
    st.markdown(f'<div class="section-card"><div class="section-title">{title}</div><div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)

def section_close():
    st.markdown("</div>", unsafe_allow_html=True)

def chart_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, family="'Plus Jakarta Sans', sans-serif"),
        margin=dict(l=10, r=10, t=40, b=10), legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, x=0),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="'Plus Jakarta Sans', sans-serif", bordercolor=BORDER),
    )
    fig.update_xaxes(showgrid=False, linecolor="rgba(0,0,0,0.05)", tickfont=dict(size=11, color=MUTED))
    fig.update_yaxes(gridcolor="rgba(91,15,46,0.04)", zeroline=False, tickfont=dict(size=11, color=MUTED))
    return fig

def brand_sidebar():
    logo_html = f'<img src="data:image/svg+xml;base64,{LOGO_B64}" style="height:48px; width:auto; margin-bottom:12px;" />' if LOGO_B64 else ""
    st.sidebar.markdown(f'<div class="smr-brand">{logo_html}<h1 style="color:{BURGUNDY}; margin:0; font-size:1.1rem; font-weight:800; letter-spacing:-0.02em; line-height:1.2;">Strategic Market Research</h1><p style="color:{MUTED}; margin:4px 0 0 0; font-size:0.82rem; font-weight:500;">Emergent BioSolutions<br>Advisory Board</p></div>', unsafe_allow_html=True)

def page_header(title: str, subtitle: str):
    logo_html = f'<img src="data:image/svg+xml;base64,{LOGO_B64}" style="height:42px; width:auto; filter: brightness(0) invert(1);" />' if LOGO_B64 else ""
    st.markdown(f'<div class="hero"><div class="kicker" style="color:var(--gold); font-size:0.75rem; font-weight:800; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:8px; display:inline-block;">Strategic Market Research</div><div class="hero-head">{logo_html}<h2>{title}</h2></div><p style="font-size: 1rem; color: rgba(255,255,255,0.9); margin:0; max-width:900px; line-height:1.5;">{subtitle}</p></div>', unsafe_allow_html=True)

def page_footer():
    st.markdown(f'<div style="margin-top:30px; text-align:center; padding: 24px; color:{MUTED}; font-size:0.8rem; border-top: 1px solid rgba(0,0,0,0.06);"><strong>Strategic Market Research</strong> &copy; {datetime.now().year} — {PREVIEW_NOTE}</div>', unsafe_allow_html=True)

def log_access(name: str, email: str):
    log_path = Path("smr_ivig_access_log.csv")
    record = {"timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), "viewer_name": name.strip(), "viewer_email": email.strip()}
    try:
        write_header = not log_path.exists()
        with log_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp_utc", "viewer_name", "viewer_email"])
            if write_header: writer.writeheader()
            writer.writerow(record)
    except Exception: pass

# =========================
# DATA ENGINE (Built-in, No Excel Required)
# =========================
@st.cache_data(show_spinner=False)
def load_data():
    data = {}
    # 1. Market Dynamics
    data["market"] = pd.DataFrame({
        "Year": ["2025", "2027", "2029", "2031", "2033", "2035"],
        "Revenue ($Mn)": [13090.5, 14545.9, 16104.7, 17937.1, 19830.4, 21962.2],
        "Volume (Mn g)": [298.8, 335.5, 375.4, 401.7, 411.0, 418.9]
    })
    
    # 2. Indications
    data["indications"] = pd.DataFrame({
        "Indication": ["Immunology (PI)", "Neurology (CIDP)", "Neurology (MG)", "Hematology (ITP)", "Others / Uncaptured"],
        "2025 Rev ($Mn)": [2164.0, 2590.3, 358.5, 128.0, 6614.6],
        "2035 Rev ($Mn)": [3821.2, 3535.1, 412.8, 153.1, 12171.2],
        "CAGR": ["5.8%", "3.2%", "1.4%", "1.8%", "6.3%"],
        "Disruption Risk": ["Low", "High (FcRn)", "Critical", "Moderate", "Low"]
    })
    
    # 3. Value Chain Margin
    data["value_chain"] = pd.DataFrame({
        "Value Chain Layer": ["Plasma Collection", "Fractionation", "Fill-Finish (CDMO)", "Brand & Distribution"],
        "EBITDA Margin": [16.0, 28.0, 20.0, 18.0],
        "Capital Risk": ["Very High", "Extreme ($400M+)", "Moderate", "Low"]
    })

    # 4. Regional
    data["regions"] = pd.DataFrame({
        "Region": ["United States", "Asia Pacific", "Europe", "Latin America", "Middle East & Africa"],
        "2025 Rev ($Mn)": [4387.7, 4218.6, 2816.5, 860.5, 807.2],
        "2035 Rev ($Mn)": [7527.3, 7010.2, 4488.7, 1505.6, 1430.5],
        "Map Proxy": ["USA", "CHN", "DEU", "BRA", "ZAF"]
    })

    # 5. Competitors (MASKED)
    data["competitors"] = pd.DataFrame({
        "Market Tier": ["Tier 1 Leaders (Top 2)", "Tier 2 Majors (Next 2)", "Mid-Tier Challengers"],
        "Market Share (%)": [47.0, 33.0, 20.0],
        "Strategic Moat": ["Extreme (400+ Centers)", "High (Integrated)", "Low (3rd Party Plasma)"]
    })

    # 6. Emergent Strategy
    data["emergent"] = pd.DataFrame({
        "Strategic Pathway": ["Adjacency (Hyper/MCM)", "CDMO / Fill-Finish", "Direct Pooled-IVIG"],
        "2030 TAM ($Mn)": [3308.0, 1963.6, 20244.6],
        "2035 Rev Potential ($Mn)": [232.8, 99.1, 34.4],
        "EBITDA Target": ["28.0%", "22.0%", "14.0%"],
        "Execution Risk": ["Moderate", "Moderate", "Very High"]
    })

    return data

# =========================
# RENDER VIEWS
# =========================
def render_overview(data, mult_factor):
    page_header("Executive Overview", "A curated view of IVIG market size, growth direction, and structural dynamics.")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: card_metric("2025 Market Revenue", fmt_mn(13090.5), "Baseline revenue actuals.")
    with c2: card_metric("2035 Market Revenue", fmt_mn(21962.2, mult_factor), "Directional ceiling under assumptions.")
    with c3: card_metric("10-Year CAGR", "5.3%", "Driven by volume and price mix.")
    with c4: card_metric("Market Concentration", "80.0%", "Share held by Top 4 Entities.")

    insight_text = "<strong>Strategic View:</strong> The market remains structurally bottlenecked. Growth is dictated not simply by patient demand, but by the physical limits of global plasma collection and extreme CAPEX requirements."
    st.markdown(f'<div class="insight-box">{insight_text}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.6, 1])
    with col1:
        section_open("Global Market Trajectory", "Divergence between Revenue and physical Volume.")
        df_m = data["market"].copy()
        df_m["Revenue ($Mn)"] = df_m["Revenue ($Mn)"] * mult_factor
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_m["Year"], y=df_m["Revenue ($Mn)"], mode="lines+markers", name="Market revenue ($Mn)", line=dict(color=BURGUNDY, width=3), marker=dict(size=8, color=BURGUNDY)))
        fig.add_trace(go.Bar(x=df_m["Year"], y=df_m["Volume (Mn g)"], name="Actual Volume (Mn g)", marker_color=GOLD, opacity=0.6, yaxis="y2"))
        fig.update_layout(yaxis=dict(title="$Mn"), yaxis2=dict(title="Volume (g)", overlaying="y", side="right", showgrid=False), bargap=0.55)
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()

    with col2:
        section_open("Value Chain Margin Capture", "EBITDA profile across the ecosystem.")
        df_v = data["value_chain"]
        fig = px.bar(df_v, x="EBITDA Margin", y="Value Chain Layer", orientation="h", color="EBITDA Margin", color_continuous_scale=[[0, GOLD], [1, BURGUNDY]])
        fig.update_layout(coloraxis_showscale=False, xaxis_title="EBITDA Margin (%)", yaxis_title="")
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
    page_footer()

def render_dynamics(data, mult_factor):
    page_header("Market Dynamics & Supply", "The fundamental reality of plasma economics and price realization.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        section_open("Average Realized ASP Scaling", "Price per Gram scaling acts as the clearing mechanism.")
        df_p = pd.DataFrame({"Year": ["2025", "2030", "2035"], "ASP ($/g)": [43.8, 48.6, 52.4 * mult_factor]})
        fig = px.line(df_p, x="Year", y="ASP ($/g)", markers=True, color_discrete_sequence=[BURGUNDY])
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    with col2:
        section_open("Value Chain Economics", "Capital risk vs Margin reward.")
        st.dataframe(data["value_chain"], use_container_width=True, hide_index=True)
        section_close()

    st.markdown('<div class="insight-box"><strong>The Plasma Ceiling:</strong> Realized pricing continues to aggressively climb because upstream plasma availability cannot meet raw epidemiological demand. Price acts as a restrictor.</div>', unsafe_allow_html=True)
    page_footer()

def render_indications(data, mult_factor):
    page_header("Indication & Disruption Risk", "How targeted biologics (FcRn inhibitors) threaten established neurology pools.")
    
    df_ind = data["indications"].copy()
    df_ind["2035 Rev ($Mn)"] = df_ind["2035 Rev ($Mn)"] * mult_factor
    
    col1, col2 = st.columns([1, 1.3])
    with col1:
        section_open("2035 Revenue Composition", "Modeled distribution post-disruption.")
        fig = px.pie(df_ind, values="2035 Rev ($Mn)", names="Indication", hole=0.6, color_discrete_sequence=[BURGUNDY, BURGUNDY_MID, GOLD, BURGUNDY_SOFT, "#E1D2DA"])
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    with col2:
        section_open("Substitution Risk Matrix", "Vulnerability assessment by indication.")
        st.dataframe(df_ind, use_container_width=True, hide_index=True)
        section_close()
        
    st.markdown('<div class="insight-box"><strong>The Disruption Threat:</strong> A single CIDP patient consumes ~1,000 grams of IVIG annually. High adoption of FcRn blockers in CIDP and MG represents a massive volumetric threat to standard IVIG growth ceilings.</div>', unsafe_allow_html=True)
    page_footer()

def render_regions(data, mult_factor):
    page_header("Regional Analysis", "Geographic opportunity, import dependency, and pricing power.")

    df_reg = data["regions"].copy()
    df_reg["2035 Rev ($Mn)"] = df_reg["2035 Rev ($Mn)"] * mult_factor

    section_open("Global Opportunity Heatmap (2035)", "Intensity of 2035 IVIG market opportunity.")
    fig = px.choropleth(
        df_reg, locations="Map Proxy", color="2035 Rev ($Mn)", 
        color_continuous_scale=[[0, "#FAF5F7"], [0.5, GOLD], [1, BURGUNDY]],
        hover_name="Region", projection="natural earth"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), geo=dict(showframe=False, showcoastlines=True, coastlinecolor="rgba(0,0,0,0.08)", projection_scale=1.1, bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    section_close()

    col1, col2 = st.columns([1.4, 1])
    with col1:
        section_open("Regional Demand Overview", "Summary table.")
        st.dataframe(df_reg.drop(columns=["Map Proxy"]), use_container_width=True, hide_index=True)
        section_close()
    with col2:
        section_open("Top Regional Markets (2035)", "US completely dominates due to pricing & supply.")
        fig = px.bar(df_reg.sort_values("2035 Rev ($Mn)"), x="2035 Rev ($Mn)", y="Region", orientation="h", color="2035 Rev ($Mn)", color_continuous_scale=[[0, GOLD], [1, BURGUNDY]])
        fig.update_layout(coloraxis_showscale=False, xaxis_title="$Mn", yaxis_title="")
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
    page_footer()

def render_competition(data):
    page_header("Competitive Landscape", "Preview of market control. Player identities and exact revenues have been securely masked.")

    df_comp = data["competitors"].copy()

    col1, col2 = st.columns([1, 1.2])
    with col1:
        section_open("Market Concentration", "Aggregated Share by Tier.")
        fig = px.pie(df_comp, values="Share (%)", names="Market Tier", hole=0.6, color_discrete_sequence=[BURGUNDY, BURGUNDY_MID, GOLD])
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()

    with col2:
        section_open("Structural Moats by Tier", "Why direct entry is restricted.")
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
        section_close()

    st.markdown('<div class="insight-box"><strong>Strategic Lockout:</strong> The Top 4 entities effectively barricade the core pooled-IVIG space against non-integrated entrants due to upstream plasma collection ownership.</div>', unsafe_allow_html=True)
    page_footer()

def render_emergent(data, mult_factor):
    page_header("Emergent BioSolutions Strategy", "Analyzing optimal entry vectors, bypassing direct IVIG competition.")
    
    df_em = data["emergent"].copy()
    df_em["2035 Rev Potential ($Mn)"] = df_em["2035 Rev Potential ($Mn)"] * mult_factor

    c1, c2, c3 = st.columns(3)
    with c1: card_metric("Best Margin Profile", "Hyperimmunes", "28% EBITDA Target.")
    with c2: card_metric("Secondary Pathway", "CDMO Fill-Finish", "Monetizes footprint without plasma risk.")
    with c3: card_metric("Path to Avoid", "Direct IVIG", "Requires $1B+ in CAPEX.")

    col1, col2 = st.columns([1.5, 1])
    with col1:
        section_open("Strategic Pathway Economics", "Evaluating 2035 Revenue Potential vs Risk.")
        fig = px.bar(df_em, x="Strategic Pathway", y="2035 Rev Potential ($Mn)", color="Execution Risk", color_discrete_map={"Moderate": GOLD, "Very High": BURGUNDY_DARK})
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    with col2:
        section_open("Strategy Assessment Matrix", "Financials & viability.")
        st.dataframe(df_em.drop(columns=["2030 TAM ($Mn)"]), use_container_width=True, hide_index=True)
        section_close()

    st.markdown('<div class="insight-box"><strong>Recommendation: Double-Down on Adjacencies.</strong> Emergent must fiercely avoid direct competition with integrated plasma leaders. Instead, dominate the high-margin Serviceable Available Market spanning hyperimmune products and CDMO processing.</div>', unsafe_allow_html=True)
    page_footer()

def render_methodology(data):
    page_header("Methodology & Coverage", "A concise explanation of how the dashboard analytics are built.")
    col1, col2 = st.columns(2)
    with col1:
        section_open("Modeling Approach", "How the market view is constructed.")
        st.markdown("**Epidemiological Demand Cascade:** Relevant Population × Incidence Rate × Diagnosed % × Treated % × IVIG Penetration %.")
        section_close()
    with col2:
        section_open("Data Restrictions", "Anonymization rules.")
        st.markdown("This dashboard represents a **curated preview layer**. Specific competitive identities and internal revenues are abstracted to protect proprietary intelligence.")
        section_close()
    page_footer()

# =========================
# ACCESS GATEWAY
# =========================
def check_access():
    expected_password = str(st.secrets.get("ACCESS_CODE", "SMR2026")).strip()
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True

    brand_sidebar()
    with st.sidebar:
        st.markdown("<h3 style='color:var(--ink); font-weight:700; margin-bottom:12px;'>🔐 Access Login</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            name = st.text_input("Name*")
            email = st.text_input("Email*")
            company = st.text_input("Company / Organization")
            password = st.text_input("Access Code*", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            enter = st.form_submit_button("Secure Login", use_container_width=True)

    if enter:
        clean_name, clean_email, clean_pass = name.strip(), email.strip(), password.strip()
        if not clean_name or not clean_email or not clean_pass:
            st.sidebar.warning("⚠️ Please fill in your Name, Email, and Access Code.")
        elif clean_pass != expected_password:
            st.sidebar.error("❌ Invalid Access Code. Please try again.")
        else:
            st.session_state.authenticated = True
            st.session_state.viewer_name = clean_name
            st.session_state.viewer_company = company.strip()
            log_access(clean_name, clean_email)
            st.rerun()

    if not st.session_state.authenticated:
        st.markdown("""<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:60vh;"><h2 style='color:var(--burgundy); font-weight:800; font-size:2.4rem;'>Dashboard Secured</h2><p style='color:var(--muted); font-size:1.1rem;'>Please use the sidebar to authenticate and load the market view.</p></div>""", unsafe_allow_html=True)
        st.stop()
    return True

check_access()

# =========================
# AUTHENTICATED SHELL
# =========================
data = load_data()
brand_sidebar()

viewer_name = st.session_state.get("viewer_name", "Guest")
viewer_company = st.session_state.get("viewer_company", "")
viewer_chip = viewer_name + (f" | {viewer_company}" if viewer_company else "")
st.sidebar.markdown(f'<div class="viewer-chip">Verified: {viewer_chip}</div>', unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-weight:700; color:var(--burgundy); margin-bottom:4px;'>⚙️ Scenario Engine</p>", unsafe_allow_html=True)
slider_val = st.sidebar.slider("FcRn Substitution Impact", min_value=-15, max_value=25, value=0, step=5, format="%d%%")
# Invert logic: If substitution goes UP, overall IVIG revenue multiplier goes DOWN.
engine_multiplier = 1.0 - (slider_val / 200.0) 

page = st.sidebar.radio(
    "",
    [
        "Executive Overview",
        "Market Dynamics & Supply",
        "Indication & Disruption Risk",
        "Regional Analysis",
        "Competitive Landscape",
        "Emergent Strategy",
        "Methodology & Coverage"
    ],
)

st.sidebar.markdown("---")
if st.sidebar.button("End Session", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

# Router
if page == "Executive Overview": render_overview(data, engine_multiplier)
elif page == "Market Dynamics & Supply": render_dynamics(data, engine_multiplier)
elif page == "Indication & Disruption Risk": render_indications(data, engine_multiplier)
elif page == "Regional Analysis": render_regions(data, engine_multiplier)
elif page == "Competitive Landscape": render_competition(data)
elif page == "Emergent Strategy": render_emergent(data, engine_multiplier)
elif page == "Methodology & Coverage": render_methodology(data)
