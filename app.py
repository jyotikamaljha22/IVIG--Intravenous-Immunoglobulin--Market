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
import streamlit.components.v1 as components

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
BURGUNDY = "#4A0C25" # Deepened for a more premium look
BURGUNDY_DARK = "#2D0716"
BURGUNDY_MID = "#7A143D"
BURGUNDY_SOFT = "#A83F68"
GOLD = "#C49A23"
CARD = "#FFFFFF"
INK = "#1A1A1A"
MUTED = "#6B7280"
BORDER = "#E5E7EB"

PREVIEW_NOTE = (
    "This deliverable is for strategic review. Competitor identities and specific "
    "market share revenues have been intentionally abstracted into Tiers."
)

@st.cache_data
def load_logo_base64() -> str | None:
    candidates = [
        Path("smrlogonew.svg"), 
        Path(__file__).with_name("smrlogonew.svg"), 
        Path.cwd() / "smrlogonew.svg"
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

    /* PERMANENT SIDEBAR LOCK & JAILBREAK UI */
    [data-testid="stSidebarCollapseButton"] {{ display: none !important; width: 0 !important; }}
    
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] {{
        display: flex !important; visibility: visible !important; position: fixed !important;
        top: 15px !important; left: 15px !important; z-index: 999999 !important;
        background: {BURGUNDY} !important; border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important; box-shadow: 0 4px 14px rgba(74,12,37,0.3) !important;
        align-items: center !important; justify-content: center !important;
        padding: 0.4rem !important; cursor: pointer !important; transition: all 0.2s ease !important;
    }}
    [data-testid="collapsedControl"] svg, [data-testid="stSidebarCollapsedControl"] svg {{
        fill: white !important; color: white !important; width: 1.5rem !important; height: 1.5rem !important;
    }}

    /* CUSTOM ELEGANT SCROLLBAR */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(74,12,37,0.15); border-radius: 10px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(74,12,37,0.3); }}

    /* LIVING GRADIENT BACKGROUND */
    .stApp {{
      background: radial-gradient(circle at 15% 0%, rgba(196,154,35,0.03) 0%, transparent 40%),
                  radial-gradient(circle at 85% 100%, rgba(74,12,37,0.03) 0%, transparent 40%),
                  #FAFAFA;
      background-attachment: fixed;
    }}

    /* SIDEBAR REFINEMENT */
    [data-testid="stSidebar"] {{
        background: {BURGUNDY_DARK} !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div, [data-testid="stSidebar"] label {{
        color: rgba(255,255,255,0.85) !important;
    }}

    /* SLEEK BUTTON STYLING */
    .stButton > button {{
        background: linear-gradient(135deg, {GOLD} 0%, #A37F1C 100%) !important;
        color: {BURGUNDY_DARK} !important;
        border: none !important; border-radius: 8px !important;
        padding: 10px 24px !important; font-weight: 800 !important; font-size: 0.9rem !important;
        letter-spacing: 0.02em; transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(196,154,35,0.3) !important;
    }}
    .stButton > button:hover {{ transform: translateY(-2px) !important; box-shadow: 0 6px 16px rgba(196,154,35,0.45) !important; }}

    /* INPUT FIELDS */
    .stTextInput input {{
        border-radius: 8px !important; border: 1px solid rgba(255,255,255,0.2) !important;
        padding: 12px 14px !important; background: rgba(255,255,255,0.05) !important; color: white !important;
    }}
    .stTextInput input:focus {{ border-color: {GOLD} !important; box-shadow: 0 0 0 2px rgba(196,154,35,0.3) !important; }}

    /* APP-LIKE NAVIGATION */
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] {{
        padding: 10px 14px !important; margin-bottom: 4px !important; border-radius: 8px !important;
        transition: all 0.2s ease !important; cursor: pointer !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover {{ background: rgba(255,255,255,0.05) !important; transform: translateX(3px) !important; }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input[checked]) {{
         background: rgba(255,255,255,0.1) !important; border-left: 4px solid {GOLD} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] p {{ font-weight: 600 !important; font-size: 0.92rem !important; color: white !important; }}

    /* BRANDING HEADERS */
    .smr-brand {{
      background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.02) 100%);
      border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; padding: 20px;
      margin-bottom: 24px; backdrop-filter: blur(16px);
    }}
    .hero {{
      background: linear-gradient(135deg, {BURGUNDY} 0%, {BURGUNDY_MID} 100%);
      color: white; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;
      padding: 34px 40px; box-shadow: 0 20px 40px rgba(74,12,37,0.15); margin-bottom: 32px;
      position: relative; overflow: hidden;
    }}
    .hero::before {{
      content: ''; position: absolute; top: -50%; right: -10%; width: 60%; height: 200%;
      background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 60%); transform: rotate(-45deg);
    }}
    .hero h2 {{ margin: 0; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.02em; position: relative; z-index: 2; line-height: 1.2; }}
    .hero p {{ position: relative; z-index: 2; margin-top: 12px; font-size: 1.05rem; opacity: 0.9; }}
    
    /* GLASSMORPHISM DATA CARDS */
    .metric-card {{
      background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: 24px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.02); min-height: 135px; transition: all 0.3s ease;
    }}
    .metric-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 24px rgba(74,12,37,0.06); border-color: {GOLD}; }}
    .metric-label {{ color: {MUTED}; font-size: 0.82rem; margin-bottom: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }}
    .metric-value {{ color: {BURGUNDY}; font-size: 2.4rem; font-weight: 800; line-height: 1; letter-spacing: -0.02em; margin-bottom: 8px; }}
    .metric-foot {{ color: {MUTED}; font-size: 0.85rem; line-height: 1.4; }}

    .section-card {{
      background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; padding: 28px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.02); margin-bottom: 24px;
    }}
    .section-title {{ font-size: 1.25rem; font-weight: 800; color: {BURGUNDY}; margin-bottom: 6px; letter-spacing: -0.01em; }}
    .section-sub {{ color: {MUTED}; font-size: 0.95rem; margin-bottom: 24px; line-height: 1.5; }}
    
    .insight-box {{
      background: #ffffff; border: 1px solid rgba(196,154,35,0.2); border-left: 6px solid {GOLD};
      border-radius: 8px; padding: 20px 24px; color: {INK}; font-size: 1rem; line-height: 1.6;
      margin-bottom: 24px; box-shadow: 0 8px 24px rgba(196,154,35,0.05);
    }}
    
    .viewer-chip {{
      display:inline-block; padding:6px 14px; border-radius:999px; font-size:0.75rem; font-weight:700;
      background: rgba(255,255,255,0.1); color: {GOLD}; margin-top:10px; margin-bottom: 20px;
      border: 1px solid rgba(255,255,255,0.15);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- JAILBREAK SCRIPT ---
components.html(
    """<script>setTimeout(function() {var e = window.parent.document.querySelector('[data-testid="collapsedControl"]'); if(e) e.click();}, 100);</script>""",
    height=0, width=0
)

# =========================
# UI Component Helpers
# =========================
def fmt_mn(value: float) -> str:
    if pd.isna(value): return "—"
    if abs(value) >= 1000: return f"≈${value/1000:.1f}B"
    return f"≈${value:,.0f}M"

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
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", zeroline=False, tickfont=dict(size=11, color=MUTED))
    return fig

def brand_sidebar():
    if LOGO_B64:
        st.sidebar.markdown(f'<img src="data:image/svg+xml;base64,{LOGO_B64}" style="height:42px; width:auto; margin-bottom:12px; filter: brightness(0) invert(1);" />', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div class="smr-brand"><h1 style="color:white; margin:0; font-size:1.15rem; font-weight:800; line-height:1.2;">Strategic Market Research</h1><p style="color:rgba(255,255,255,0.7); margin:4px 0 0 0; font-size:0.85rem; font-weight:500;">Emergent BioSolutions<br>Advisory Board</p></div>', unsafe_allow_html=True)

def page_header(title: str, subtitle: str):
    if LOGO_B64:
        logo_html = f'<img src="data:image/svg+xml;base64,{LOGO_B64}" style="height:42px; width:auto; filter: brightness(0) invert(1); z-index:2; position:relative;" />'
    else:
        logo_html = ""
        
    st.markdown(f'<div class="hero"><div style="color:{GOLD}; font-size:0.75rem; font-weight:800; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:8px; z-index:2; position:relative;">Confidential Strategic Advisory</div><div class="hero-head">{logo_html}<h2>{title}</h2></div><p>{subtitle}</p></div>', unsafe_allow_html=True)

def page_footer():
    st.markdown(f'<div style="margin-top:40px; text-align:center; padding: 24px; color:{MUTED}; font-size:0.85rem; border-top: 1px solid {BORDER};"><strong>Strategic Market Research</strong> &copy; {datetime.now().year} — {PREVIEW_NOTE}</div>', unsafe_allow_html=True)

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
# DATA ENGINE (Definitive Base Case)
# =========================
@st.cache_data(show_spinner=False)
def load_data():
    data = {}
    
    # 1. Market Dynamics
    data["market"] = pd.DataFrame({
        "Year": ["2025", "2027", "2029", "2031", "2033", "2035"],
        "Revenue ($Mn)": [13090.5, 14545.9, 16104.7, 17937.1, 19830.4, 21962.2],
        "Volume (Mn g)": [298.8, 335.5, 375.4, 401.7, 411.0, 418.9],
        "Pre-Erosion Demand (Mn g)": [298.8, 335.5, 381.0, 420.0, 450.0, 486.4],
        "Available Supply (Mn g)": [317.1, 350.0, 390.0, 425.2, 480.0, 570.9]
    })
    
    # 2. Indications
    data["indications"] = pd.DataFrame({
        "Indication": ["Immunology (PI)", "Neurology (CIDP)", "Neurology (MG)", "Hematology (ITP)", "Others / Off-Label"],
        "2025 Rev ($Mn)": [2164.0, 2590.3, 358.5, 128.0, 6614.6],
        "2035 Rev ($Mn)": [3821.2, 3535.1, 412.8, 153.1, 12171.2],
        "CAGR (25-35)": ["5.8%", "3.2%", "1.4%", "1.8%", "6.3%"],
        "Disruption Risk": ["Low", "High", "Critical", "Moderate", "Low"]
    })
    
    # 3. Patient Funnel (Epidemiology)
    data["funnel"] = pd.DataFrame({
        "Stage": ["Total Diagnosed", "Medically Treated", "IVIG Eligible", "Actual IVIG Penetration"],
        "Patients": [54560, 46921, 43167, 28058] # Example cascade for PI
    })
    
    # 4. Standard of Care Cost
    data["soc"] = pd.DataFrame({
        "Modality": ["Oral AD / Augmentation", "Psychotherapy", "TMS / ECT", "Spravato / Ketamine", "High-Dose IVIG (CIDP)"],
        "Annual Cost per Patient ($)": [2000, 3500, 8500, 23000, 50000]
    })
    
    # 5. Value Chain & Profit Pools
    data["value_chain"] = pd.DataFrame({
        "Value Chain Layer": ["Plasma Collection", "Fractionation", "Fill-Finish (CDMO)", "Brand & Distribution"],
        "Revenue Split (%)": [24.0, 34.0, 12.0, 30.0],
        "EBITDA Margin (%)": [16.0, 28.0, 20.0, 18.0]
    })

    # 6. Delivery Economics (Waterfall)
    data["waterfall"] = pd.DataFrame({
        "Measure": ["absolute", "relative", "relative", "relative", "total"],
        "Label": ["All-Day Clinic", "Half-Day Savings", "Short Clinic Savings", "Take-Home Savings", "Take-Home Model"],
        "Value": [1635, -780, -435, -115, 305]
    })
    
    # 7. Clinical Pipeline
    data["pipeline"] = pd.DataFrame({
        "Asset / Molecule": ["Efgartigimod (Vyvgart)", "Rozanolixizumab", "Nipocalimab", "Batoclimab", "Pozelimab"],
        "Mechanism": ["FcRn Inhibitor", "FcRn Inhibitor", "FcRn Inhibitor", "FcRn Inhibitor", "Complement C5"],
        "Key Indications": ["MG, CIDP, ITP", "MG", "MG, SLE", "MG (China)", "MG"],
        "Status": ["Approved (Expanding)", "Approved", "Phase 3 / Appr", "Phase 3", "2026 Submission"]
    })

    # 8. Regional
    data["regions"] = pd.DataFrame({
        "Region": ["United States", "Asia Pacific", "Europe", "Latin America", "Middle East & Africa"],
        "2035 Rev ($Mn)": [7527.3, 7010.2, 4488.7, 1505.6, 1430.5],
        "Map Proxy": ["USA", "CHN", "DEU", "BRA", "ZAF"]
    })

    # 9. Competitors
    data["competitors"] = pd.DataFrame({
        "Market Tier": ["Tier 1 Leaders (Top 2)", "Tier 2 Majors (Next 2)", "Mid-Tier Challengers"],
        "Market Share (%)": [47.0, 33.0, 20.0]
    })

    # 10. Emergent Strategy Matrix (Bubble Data)
    data["emergent"] = pd.DataFrame({
        "Strategic Pathway": ["Adjacency (Hyper/MCM)", "CDMO / Fill-Finish", "Partnered Specialty Ig", "Direct Pooled-IVIG"],
        "Execution Risk Score": [2, 2, 3, 4], # 1=Low, 4=Very High
        "Execution Risk": ["Moderate", "Moderate", "High", "Very High"],
        "2030 TAM ($Mn)": [3308.0, 1963.6, 4282.3, 20244.6],
        "2035 Rev Potential ($Mn)": [232.8, 99.1, 41.3, 34.4],
    })

    return data

# =========================
# RENDER VIEWS
# =========================
def render_overview(data):
    page_header("Executive Overview", "A definitive view of global IVIG market size, growth direction, and structural dynamics.")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: card_metric("2025 Market Revenue", fmt_mn(13090.5), "Baseline revenue actuals.")
    with c2: card_metric("2035 Market Revenue", fmt_mn(21962.2), "Directional ceiling under base case.")
    with c3: card_metric("10-Year CAGR", "5.3%", "Driven aggressively by price mix.")
    with c4: card_metric("Market Concentration", "80.0%", "Share securely held by Top 4 Entities.")

    insight_text = "<strong>Strategic View:</strong> The market remains structurally bottlenecked. Growth is dictated not simply by patient demand, but by the physical limits of global plasma collection and extreme CAPEX requirements."
    st.markdown(f'<div class="insight-box">{insight_text}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.6, 1])
    with col1:
        section_open("Global Market Trajectory", "Divergence between Revenue and physical Volume.")
        df_m = data["market"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_m["Year"], y=df_m["Revenue ($Mn)"], mode="lines+markers", name="Market revenue ($Mn)", line=dict(color=BURGUNDY, width=3), marker=dict(size=8)))
        fig.add_trace(go.Bar(x=df_m["Year"], y=df_m["Volume (Mn g)"], name="Actual Volume (Mn g)", marker_color=GOLD, opacity=0.7, yaxis="y2"))
        fig.update_layout(yaxis=dict(title="$Mn"), yaxis2=dict(title="Volume (g)", overlaying="y", side="right", showgrid=False), bargap=0.55)
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()

    with col2:
        section_open("Value Chain Margin Capture", "EBITDA profile across the ecosystem.")
        df_v = data["value_chain"]
        fig = px.bar(df_v, x="EBITDA Margin (%)", y="Value Chain Layer", orientation="h", color="EBITDA Margin (%)", color_continuous_scale=[[0, GOLD], [1, BURGUNDY]])
        fig.update_layout(coloraxis_showscale=False, xaxis_title="EBITDA Margin (%)", yaxis_title="")
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
    page_footer()

def render_epidemiology(data):
    page_header("Epidemiology & Patient Funnel", "Addressable boundaries defined by treatment failure, willingness to adopt, and medical eligibility.")
    
    df_funnel = data["funnel"]
    
    col1, col2 = st.columns([1, 1])
    with col1:
        section_open("Patient Funnel Attrition (Primary Immunodeficiency Model)", "Severe drop-off to actual IVIG-penetrated base.")
        # CONSULTING UPGRADE: Funnel Chart
        fig = go.Figure(go.Funnel(
            y=df_funnel["Stage"],
            x=df_funnel["Patients"],
            textinfo="value+percent initial",
            marker=dict(color=[BURGUNDY, BURGUNDY_MID, BURGUNDY_SOFT, GOLD])
        ))
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    with col2:
        section_open("Volumetric Consumption Index", "The 'Volume Sink' reality by indication.")
        df_dose = pd.DataFrame({"Indication": ["PI", "CIDP", "MG", "Kawasaki"], "Annual Dose (g)": [450, 1000, 180, 36]})
        fig = px.bar(df_dose.sort_values("Annual Dose (g)"), x="Annual Dose (g)", y="Indication", orientation="h", color="Annual Dose (g)", color_continuous_scale=[[0, GOLD], [1, BURGUNDY]])
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Grams / Patient / Year", yaxis_title="")
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    st.markdown('<div class="insight-box"><strong>The Volume Sink Reality:</strong> CIDP is the ultimate volume sink of the industry. A single adult CIDP patient consumes the volumetric equivalent of nearly 28 pediatric Kawasaki patients, magnifying the impact of any market disruption.</div>', unsafe_allow_html=True)
    page_footer()

def render_soc(data):
    page_header("Current SOC & Pricing Landscape", "Baseline economics establishing the pricing umbrella for targeted therapeutics.")
    
    df_soc = data["soc"]
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        section_open("Annual Cost Burden per Patient ($)", "Comparing standard interventions vs IVIG.")
        fig = px.bar(df_soc.sort_values("Annual Cost per Patient ($)"), x="Annual Cost per Patient ($)", y="Modality", orientation="h", color="Annual Cost per Patient ($)", color_continuous_scale=[[0, GOLD], [1, BURGUNDY]])
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Cost ($)", yaxis_title="")
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    with col2:
        section_open("Treatment Modality Economics", "Cost segmentation matrix.")
        st.dataframe(df_soc, use_container_width=True, hide_index=True)
        section_close()
        
    st.markdown('<div class="insight-box"><strong>Economic Baseline:</strong> High-dose IVIG for conditions like CIDP establishes an extreme cost baseline ($50,000+ purely in drug costs). Payers are actively incentivizing step-throughs to targeted biologics to cap their volumetric financial exposure.</div>', unsafe_allow_html=True)
    page_footer()

def render_dynamics(data):
    page_header("Market Dynamics & Supply Limits", "The fundamental reality of plasma economics and price realization.")
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        section_open("Supply vs Demand Gap", "Pre-erosion demand heavily outstrips available supply.")
        df_m = data["market"]
        fig = go.Figure()
        # Fill between demand and supply to show the gap visually
        fig.add_trace(go.Scatter(x=df_m["Year"], y=df_m["Available Supply (Mn g)"], mode="lines", name="Available Supply", line=dict(color=GOLD, width=2)))
        fig.add_trace(go.Scatter(x=df_m["Year"], y=df_m["Pre-Erosion Demand (Mn g)"], mode="lines", name="Unconstrained Demand", fill='tonexty', fillcolor='rgba(91,15,46,0.1)', line=dict(color=BURGUNDY, width=3, dash='dash')))
        fig.update_layout(yaxis=dict(title="Volume (Mn g)"), hovermode="x unified")
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    with col2:
        section_open("Average Realized ASP Scaling", "Price per Gram scaling acts as the clearing mechanism.")
        df_p = pd.DataFrame({"Year": ["2025", "2030", "2035"], "ASP ($/g)": [43.8, 48.6, 52.4]})
        fig = px.line(df_p, x="Year", y="ASP ($/g)", markers=True, color_discrete_sequence=[BURGUNDY])
        fig.update_traces(line=dict(width=4), marker=dict(size=10))
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()

    st.markdown('<div class="insight-box"><strong>The Plasma Ceiling:</strong> Realized pricing continues to aggressively climb because upstream plasma availability cannot meet raw epidemiological demand. If emerging therapies fail to displace IVIG in neurology, the supply chain will plunge back into catastrophic global shortages.</div>', unsafe_allow_html=True)
    page_footer()

def render_indications(data):
    page_header("Indication & Disruption Risk", "How targeted biologics (FcRn inhibitors) threaten established neurology pools.")
    
    df_ind = data["indications"]
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        section_open("Indication Risk Matrix (2035)", "Sizing the market by disruption vulnerability.")
        # CONSULTING UPGRADE: Treemap
        fig = px.treemap(df_ind, path=['Disruption Risk', 'Indication'], values='2035 Rev ($Mn)', color='Disruption Risk',
                         color_discrete_map={"Critical": BURGUNDY_DARK, "High": BURGUNDY, "Moderate": BURGUNDY_SOFT, "Low": GOLD})
        fig.update_layout(margin=dict(t=20, l=10, r=10, b=10))
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    with col2:
        section_open("Substitution Risk Database", "Granular assessment by indication.")
        st.dataframe(df_ind[["Indication", "2035 Rev ($Mn)", "CAGR (25-35)", "Disruption Risk"]], use_container_width=True, hide_index=True)
        section_close()
        
    st.markdown('<div class="insight-box"><strong>Strategic Divergence:</strong> Primary Immunodeficiency (PI) remains the ultimate defensive moat (Low Risk). Neurological applications are lucrative but highly vulnerable to FcRn displacement (High/Critical Risk).</div>', unsafe_allow_html=True)
    page_footer()

def render_delivery_econ(data):
    page_header("Delivery Innovation & Economics", "Care-model cost and capacity fundamentally divide scalable vs non-scalable modalities.")
    
    df_waterfall = data["waterfall"]
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        section_open("Care Model Cost Compression", "Step-down economic impact of delivery innovation.")
        # CONSULTING UPGRADE: Waterfall Chart
        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=df_waterfall["Measure"],
            x=df_waterfall["Label"],
            y=df_waterfall["Value"],
            connector={"line": {"color": "rgba(0,0,0,0.1)", "width": 1}},
            decreasing={"marker": {"color": GOLD}},
            increasing={"marker": {"color": BURGUNDY}},
            totals={"marker": {"color": BURGUNDY_DARK}}
        ))
        fig.update_layout(yaxis_title="Base Visit Cost ($)", showlegend=False)
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    with col2:
        section_open("Throughput Expansion Multiplier", "Theoretical patient volume scalability.")
        df_econ = data["economics"]
        fig = px.line(df_econ, x="Care Model Paradigm", y="Throughput Expansion", markers=True, color_discrete_sequence=[BURGUNDY])
        fig.update_traces(line=dict(width=4), marker=dict(size=10))
        fig.update_layout(xaxis_title="", yaxis_title="Throughput Multiplier (x)")
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()

    st.markdown('<div class="insight-box"><strong>Delivery as a Moat:</strong> Transitioning from an all-day clinic model to a take-home model strips operating costs while expanding systemic capacity exponentially, entirely bypassing the physical real estate bottleneck.</div>', unsafe_allow_html=True)
    page_footer()

def render_pipeline(data):
    page_header("Clinical Pipeline & FcRn Risk", "The rapid advancement of targeted therapies aggressively eroding IVIG reliance.")
    
    df_pipe = data["pipeline"]
    
    section_open("Late-Stage Targeted Therapeutics Threat", "Monoclonal antibodies and Complement inhibitors targeting the Autoimmune pool.")
    # Styled dataframe for premium look
    st.dataframe(df_pipe, use_container_width=True, hide_index=True)
    section_close()
    
    st.markdown('<div class="insight-box"><strong>Pipeline Threat:</strong> The proliferation of FcRn inhibitors (Vyvgart, Nipocalimab) guarantees that IVIG will lose its monopoly in high-volume autoimmune neurology. Treatment-naïve patients are increasingly being routed directly to novel biologics, starving IVIG of new patient starts.</div>', unsafe_allow_html=True)
    page_footer()

def render_value_chain(data):
    page_header("Value Chain & Profit Pools", "Where revenue is captured and margin is maximized across the ecosystem.")
    
    df_vc = data["value_chain"]
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        section_open("Gross Revenue Split", "Top-line distribution.")
        fig = px.pie(df_vc, values="Revenue Split (%)", names="Value Chain Layer", hole=0.6, color_discrete_sequence=[BURGUNDY, GOLD, BURGUNDY_MID, BURGUNDY_SOFT])
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    with col2:
        section_open("EBITDA Profiling", "Margin comparison across the ecosystem.")
        fig = px.bar(df_vc.sort_values("EBITDA Margin (%)"), x="EBITDA Margin (%)", y="Value Chain Layer", orientation="h", color="EBITDA Margin (%)", color_continuous_scale=[[0, GOLD], [1, BURGUNDY]])
        fig.update_layout(coloraxis_showscale=False, xaxis_title="EBITDA Margin (%)", yaxis_title="")
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    st.markdown('<div class="insight-box"><strong>Value Migration:</strong> Fractionation commands the highest EBITDA margin (28%) due to virtually insurmountable barriers to entry. However, Formulation/Fill-Finish offers highly attractive margins (20%) with substantially lower raw capital risk, representing an optimal strategic insertion point.</div>', unsafe_allow_html=True)
    page_footer()

def render_regions(data):
    page_header("Regional Analysis", "Geographic opportunity, import dependency, and pricing power.")

    df_reg = data["regions"]

    section_open("Global Opportunity Heatmap (2035)", "Intensity of 2035 IVIG market opportunity.")
    fig = px.choropleth(
        df_reg, locations="Map Proxy", color="2035 Rev ($Mn)", 
        color_continuous_scale=[[0, "#FAFAFA"], [0.5, GOLD], [1, BURGUNDY]],
        hover_name="Region", projection="natural earth"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), geo=dict(showframe=False, showcoastlines=True, coastlinecolor="rgba(0,0,0,0.1)", projection_scale=1.1, bgcolor='rgba(0,0,0,0)'))
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

    df_comp = data["competitors"]

    col1, col2 = st.columns([1, 1.2])
    with col1:
        section_open("Market Concentration", "Aggregated Share by Tier.")
        fig = px.pie(df_comp, values="Market Share (%)", names="Market Tier", hole=0.6, color_discrete_sequence=[BURGUNDY_DARK, BURGUNDY_MID, GOLD])
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()

    with col2:
        section_open("Structural Moats by Tier", "Why direct entry is restricted.")
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
        section_close()

    st.markdown('<div class="insight-box"><strong>Strategic Lockout:</strong> The Top 4 entities effectively barricade the core pooled-IVIG space against non-integrated entrants due to upstream plasma collection ownership.</div>', unsafe_allow_html=True)
    page_footer()

def render_emergent(data):
    page_header("Emergent Strategy Matrix", "Analyzing optimal entry vectors, bypassing direct IVIG competition.")
    
    df_em = data["emergent"]

    c1, c2, c3 = st.columns(3)
    with c1: card_metric("Best Margin Profile", "Hyperimmunes", "28% EBITDA Target.")
    with c2: card_metric("Secondary Pathway", "CDMO Fill-Finish", "Monetizes footprint without plasma risk.")
    with c3: card_metric("Path to Avoid", "Direct IVIG", "Requires $1B+ in CAPEX.")

    col1, col2 = st.columns([1.5, 1])
    with col1:
        section_open("Strategic Pathway Matrix", "Plotting Execution Risk vs Revenue Potential.")
        # CONSULTING UPGRADE: Bubble Chart
        fig = px.scatter(df_em, x="Execution Risk Score", y="2035 Rev Potential ($Mn)", size="2030 TAM ($Mn)", color="Strategic Pathway", 
                         color_discrete_sequence=[BURGUNDY, GOLD, BURGUNDY_MID, BURGUNDY_DARK], hover_name="Strategic Pathway", size_max=50)
        fig.update_xaxes(tickvals=[1, 2, 3, 4], ticktext=["Low", "Moderate", "High", "Very High"], title="Execution Risk")
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
        
    with col2:
        section_open("Strategy Assessment", "Financials & viability.")
        st.dataframe(df_em[["Strategic Pathway", "2035 Rev Potential ($Mn)", "EBITDA Target"]], use_container_width=True, hide_index=True)
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
        st.markdown("<h3 style='color:white; font-weight:800; margin-bottom:12px;'>🔐 Access Login</h3>", unsafe_allow_html=True)
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
            st.sidebar.error("❌ Invalid Access Code.")
        else:
            st.session_state.authenticated = True
            st.session_state.viewer_name = clean_name
            st.session_state.viewer_company = company.strip()
            log_access(clean_name, clean_email)
            st.rerun()

    if not st.session_state.authenticated:
        if LOGO_B64:
            st.markdown(f'<div style="text-align:center; margin-top:15vh;"><img src="data:image/svg+xml;base64,{LOGO_B64}" style="height:65px; margin-bottom:20px;" /></div>', unsafe_allow_html=True)
        st.markdown(f"""<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:30vh;"><h2 style='color:{BURGUNDY}; font-weight:800; font-size:2.6rem; letter-spacing:-0.02em;'>Dashboard Secured</h2><p style='color:{MUTED}; font-size:1.1rem; margin-top:10px;'>Please use the sidebar to authenticate and load the strategic report.</p></div>""", unsafe_allow_html=True)
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

page = st.sidebar.radio(
    "",
    [
        "Executive Overview",
        "Epidemiology & Patient Funnel",
        "Current SOC & Pricing Landscape",
        "Market Dynamics & Supply",
        "Indication & Disruption Risk",
        "Delivery Innovation & Economics",
        "Clinical Pipeline & FcRn Risk",
        "Value Chain & Profit Pools",
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
if page == "Executive Overview": render_overview(data)
elif page == "Epidemiology & Patient Funnel": render_epidemiology(data)
elif page == "Current SOC & Pricing Landscape": render_soc(data)
elif page == "Market Dynamics & Supply": render_dynamics(data)
elif page == "Indication & Disruption Risk": render_indications(data)
elif page == "Delivery Innovation & Economics": render_delivery_econ(data)
elif page == "Clinical Pipeline & FcRn Risk": render_pipeline(data)
elif page == "Value Chain & Profit Pools": render_value_chain(data)
elif page == "Regional Analysis": render_regions(data)
elif page == "Competitive Landscape": render_competition(data)
elif page == "Emergent Strategy": render_emergent(data)
elif page == "Methodology & Coverage": render_methodology(data)
