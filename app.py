import os
import csv
import base64
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Strategic Market Research | IVIG Market",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed", # Disables native sidebar
)

# ----------------------------
# THEME COLORS & LOGO LOGIC
# ----------------------------
NAVY = "#0F172A"
TEAL = "#0F766E"
SLATE = "#64748B"

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

# ----------------------------
# CSS HIDING & MAIN UI POLISH
# ----------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif !important;
    }}

    /* --- PERMANENT UI ERADICATION --- */
    /* Hide all Streamlit navigation, footers, and native sidebars to prevent lockouts */
    [data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    footer {{ display: none !important; }}
    .viewerBadge_container, #viewerBadge_container {{ display: none !important; }}
    
    /* Adjust main container to fill screen */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
    }}

    /* --- LOGIN FORM STYLING --- */
    .stTextInput input {{
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        padding: 12px 14px !important;
        background: #ffffff !important;
        color: {NAVY} !important;
    }}
    .stTextInput input:focus {{
        border-color: {TEAL} !important;
        box-shadow: 0 0 0 2px rgba(15, 118, 110, 0.2) !important;
    }}

    /* Secure Login Button */
    .stButton > button {{
        background: linear-gradient(135deg, {TEAL} 0%, {NAVY} 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(15, 118, 110, 0.45) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# LOGGING (WHO ACCESSED)
# ----------------------------
def log_access(name, email):
    log_file = "smr_ivig_access_log.csv"
    record = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "viewer_name": name.strip(),
        "viewer_email": email.strip()
    }
    try:
        write_header = not os.path.exists(log_file)
        with open(log_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp_utc", "viewer_name", "viewer_email"])
            if write_header:
                writer.writeheader()
            writer.writerow(record)
    except Exception:
        pass

# ----------------------------
# ACCESS CONTROL (CENTERED DASHBOARD GATEWAY)
# ----------------------------
def check_access():
    expected_password = str(st.secrets.get("ACCESS_CODE", "SMR2026")).strip()

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # CENTERED LOGIN SCREEN
    st.markdown("<div style='margin-top: 10vh;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        if LOGO_B64:
            st.markdown(f'<div style="text-align:center;"><img src="data:image/svg+xml;base64,{LOGO_B64}" style="height:55px; margin-bottom:20px;" /></div>', unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='text-align:center; color:{NAVY}; font-weight:800; font-size:2.2rem; margin-bottom:0;'>Strategic Market Research</h1>", unsafe_allow_html=True)
            
        st.markdown(f"<p style='text-align:center; color:{TEAL}; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:30px;'>Emergent BioSolutions Advisory</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown(f"<h3 style='color:{NAVY}; font-weight:700; margin-bottom:16px; text-align:center;'>🔐 Secure Login</h3>", unsafe_allow_html=True)
            name = st.text_input("Name*")
            email = st.text_input("Email*")
            password = st.text_input("Access Code*", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            enter = st.form_submit_button("Enter Dashboard", use_container_width=True)

    if enter:
        clean_name = name.strip()
        clean_email = email.strip()
        clean_pass = password.strip()
        
        if not clean_name or not clean_email or not clean_pass:
            with col2: st.warning("⚠️ Please fill in all fields.")
        elif clean_pass != expected_password:
            with col2: st.error("❌ Invalid Access Code.")
        else:
            st.session_state.authenticated = True
            st.session_state.viewer_name = clean_name
            log_access(clean_name, clean_email)
            st.rerun()

    st.stop()

# ----------------------------
# MAIN APP EXECUTION
# ----------------------------
check_access()

# --- TOP BAR FOR LOGOUT ---
col1, col2 = st.columns([5, 1])
with col2:
    st.markdown(f"<div style='text-align:right; font-size:0.8rem; font-weight:600; color:{SLATE}; margin-bottom:8px;'>Verified: <span style='color:{TEAL}'>{st.session_state.viewer_name}</span></div>", unsafe_allow_html=True)
    if st.button("🔒 End Secure Session", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ----------------------------
# HTML DASHBOARD CONTENT
# ----------------------------
html_logo = f'<img src="data:image/svg+xml;base64,{LOGO_B64}" style="height:48px; width:auto; margin-left:auto; margin-right:auto; margin-bottom:1.5rem;" />' if LOGO_B64 else ""

RAW_HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global IVIG Market (2025–2035) & Strategic Positioning</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #0f172a; margin: 0; padding: 0; }
        
        .chart-container { 
            position: relative; 
            width: 100%; 
            max-width: 900px; 
            margin-left: auto; 
            margin-right: auto; 
            height: 350px; 
            max-height: 400px; 
        }
        @media (min-width: 768px) { 
            .chart-container { height: 400px; } 
        }

        .stat-card {
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        .strategy-row {
            transition: background-color 0.2s ease;
        }
        .strategy-row:hover {
            background-color: #f1f5f9;
        }
        
        /* Sidebar styling */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
</head>
<body class="antialiased selection:bg-teal-200 selection:text-teal-900">

    <nav class="sticky top-0 bg-white/95 backdrop-blur-md border-b border-slate-200 z-50 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16 items-center">
                <div class="flex-shrink-0 flex items-center gap-2">
                    <div class="w-6 h-6 bg-slate-900 rounded-sm text-white flex items-center justify-center font-bold text-xs">IVIG</div>
                    <span class="font-bold text-slate-800 tracking-tight">Market Intelligence Overview</span>
                </div>
                <div class="hidden md:flex space-x-8">
                    <a href="#snapshot" class="text-sm font-medium text-slate-600 hover:text-teal-600 transition-colors">Executive Snapshot</a>
                    <a href="#dynamics" class="text-sm font-medium text-slate-600 hover:text-teal-600 transition-colors">Market Dynamics</a>
                    <a href="#indications" class="text-sm font-medium text-slate-600 hover:text-teal-600 transition-colors">Indication & Disruption</a>
                    <a href="#competition" class="text-sm font-medium text-slate-600 hover:text-teal-600 transition-colors">Competitive Landscape</a>
                    <a href="#emergent-strategy" class="text-sm font-medium text-teal-700 bg-teal-50 px-3 py-1 rounded-full hover:bg-teal-100 transition-colors">Emergent Strategy</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-20">

        <header class="text-center max-w-4xl mx-auto pt-8">
            LOGO_PLACEHOLDER
            <div class="inline-block px-4 py-1.5 rounded-full bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-600 uppercase tracking-wider mb-4">
                Boardroom Briefing Document
            </div>
            <h1 class="text-4xl md:text-5xl font-extrabold text-slate-900 leading-tight tracking-tight mb-6">
                Global IVIG Market (2025–2035)
            </h1>
            <p class="text-xl text-slate-600 font-light mb-4">
                Supply-Constrained Growth, Therapy Substitution & Strategic Positioning
            </p>
            <p class="text-sm text-teal-800 font-bold bg-teal-50 border border-teal-200 shadow-sm inline-block px-5 py-2 rounded-lg">
                Client Perspective: Emergent BioSolutions
            </p>
        </header>

        <section id="snapshot" class="scroll-mt-24">
            <div class="mb-8">
                <h2 class="text-2xl font-bold text-slate-900 border-b-2 border-teal-500 inline-block pb-1">1. Executive Overview & Strategic Snapshot</h2>
                <p class="mt-4 text-slate-600 leading-relaxed max-w-5xl">
                    The following dashboard synthesizes the fundamental economics of the Global Intravenous Immunoglobulin (IVIG) market. This section presents top-line metrics to establish the scale of the opportunity. Analysis indicates a robust but structurally bottlenecked market, moving from $13.1 Billion in 2025 to $22.0 Billion by 2035. Growth is dictated not simply by patient demand, but by the physical limits of global plasma collection.
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="stat-card bg-white rounded-xl p-6 border border-slate-200 shadow-sm border-l-4 border-l-slate-800">
                    <p class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Market Size (2025)</p>
                    <div class="text-3xl font-extrabold text-slate-900">$13.1<span class="text-lg text-slate-500 font-medium"> Bn</span></div>
                    <p class="text-xs text-slate-500 mt-2">Baseline revenue actuals</p>
                </div>
                <div class="stat-card bg-white rounded-xl p-6 border border-slate-200 shadow-sm border-l-4 border-l-teal-500">
                    <p class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Forecast Size (2035)</p>
                    <div class="text-3xl font-extrabold text-slate-900">$22.0<span class="text-lg text-slate-500 font-medium"> Bn</span></div>
                    <p class="text-xs text-slate-500 mt-2">Base case modeled projection</p>
                </div>
                <div class="stat-card bg-white rounded-xl p-6 border border-slate-200 shadow-sm border-l-4 border-l-indigo-500">
                    <p class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">10-Year CAGR</p>
                    <div class="text-3xl font-extrabold text-slate-900">5.3<span class="text-lg text-slate-500 font-medium"> %</span></div>
                    <p class="text-xs text-slate-500 mt-2">Driven by volume and price mix</p>
                </div>
                <div class="stat-card bg-white rounded-xl p-6 border border-slate-200 shadow-sm border-l-4 border-l-rose-500">
                    <p class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Market Concentration</p>
                    <div class="text-3xl font-extrabold text-slate-900">80.0<span class="text-lg text-slate-500 font-medium"> %</span></div>
                    <p class="text-xs text-slate-500 mt-2">Share controlled by Top 4 players</p>
                </div>
            </div>
        </section>

        <section id="dynamics" class="scroll-mt-24">
            <div class="mb-8">
                <h2 class="text-2xl font-bold text-slate-900 border-b-2 border-teal-500 inline-block pb-1">2. Structural Market Dynamics: The Plasma Ceiling</h2>
                <p class="mt-4 text-slate-600 leading-relaxed max-w-5xl">
                    Unlike traditional pharmaceutical markets, IVIG operates as a supply-constrained biologics market. The fundamental truth of this sector is that market growth is strictly tethered to the availability of human source plasma. The chart and data below visualize the divergence between total addressable patient demand and actual available supply constraints over the forecast period.
                </p>
            </div>

            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 lg:p-8 flex flex-col lg:flex-row gap-8 items-center">
                <div class="w-full lg:w-2/3">
                    <div class="chart-container">
                        <canvas id="marketDynamicsChart"></canvas>
                    </div>
                </div>
                <div class="w-full lg:w-1/3 space-y-6">
                    <h3 class="text-lg font-bold text-slate-900">Regional Imbalances & Yield Constraints</h3>
                    <p class="text-sm text-slate-600">
                        Analysis indicates that while aggregate global plasma supply technically covers global demand, severe regional imbalances dictate market access. The US acts as the global collection hub, maintaining a surplus, whereas regions like Europe face structural deficits (~34M gram gap by 2035).
                    </p>
                    <div class="bg-slate-50 rounded p-4 border border-slate-100">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-xs font-semibold text-slate-500 uppercase">Average Realized ASP (2025)</span>
                            <span class="text-sm font-bold text-slate-900">$43.8 / gram</span>
                        </div>
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-xs font-semibold text-slate-500 uppercase">Average Realized ASP (2035)</span>
                            <span class="text-sm font-bold text-slate-900">$52.4 / gram</span>
                        </div>
                        <p class="text-xs text-slate-500 mt-3 italic border-t border-slate-200 pt-2">
                            Data suggests price yields are highly sensitive to supply caps. Pricing acts as the primary clearing mechanism for unmet regional demand.
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <section id="indications" class="scroll-mt-24">
            <div class="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div class="max-w-4xl">
                    <h2 class="text-2xl font-bold text-slate-900 border-b-2 border-teal-500 inline-block pb-1">3. Indication-Level Concentration & Disruption Risk</h2>
                    <p class="mt-4 text-slate-600 leading-relaxed">
                        The IVIG market is highly concentrated across a few major indications in Immunology and Neurology. However, the market is facing unprecedented therapy substitution risk. Emerging targeted therapies, specifically FcRn inhibitors (e.g., efgartigimod), are actively displacing chronic IVIG maintenance use in select autoimmune disorders like MG and CIDP.
                    </p>
                </div>
                <div class="flex gap-2 shrink-0">
                    <button onclick="updateIndicationChart('2025')" id="btn-2025" class="px-4 py-2 text-sm font-medium rounded bg-teal-600 text-white shadow-sm transition-colors">2025 Data</button>
                    <button onclick="updateIndicationChart('2035')" id="btn-2035" class="px-4 py-2 text-sm font-medium rounded bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 transition-colors">2035 Data</button>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col justify-center">
                    <div class="chart-container flex items-center justify-center">
                        <canvas id="indicationDonutChart"></canvas>
                    </div>
                </div>
                <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 overflow-x-auto">
                    <table class="w-full text-left text-sm whitespace-nowrap">
                        <thead>
                            <tr class="border-b border-slate-200 text-slate-500">
                                <th class="pb-3 font-semibold">Indication</th>
                                <th class="pb-3 font-semibold text-right">2025 Rev ($Mn)</th>
                                <th class="pb-3 font-semibold text-right">2035 Rev ($Mn)</th>
                                <th class="pb-3 font-semibold text-right">CAGR (%)</th>
                                <th class="pb-3 font-semibold text-center">Disruption Risk</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 text-slate-700" id="indicationTableBody">
                        </tbody>
                    </table>
                    <p class="text-xs text-slate-500 mt-4 italic border-t border-slate-100 pt-3">
                        Interpretation: Primary Immunodeficiency (PI) represents the durable bedrock of IVIG demand. Conversely, Neurology (CIDP, MG) presents higher substitution risk due to FcRn inhibitor penetration, limiting the ceiling for autoimmune-driven IVIG expansion over the next decade.
                    </p>
                </div>
            </div>
        </section>

        <section id="competition" class="scroll-mt-24">
            <div class="mb-8">
                <h2 class="text-2xl font-bold text-slate-900 border-b-2 border-teal-500 inline-block pb-1">4. Competitive Landscape & Market Control</h2>
                <p class="mt-4 text-slate-600 leading-relaxed max-w-5xl">
                    Market share in the IVIG ecosystem is fundamentally an expression of plasma collection infrastructure. The data demonstrates profound concentration. Entering the core IVIG market directly requires staggering capital expenditure for center networks and fractionation capacity, creating a nearly impenetrable moat for non-integrated players.
                </p>
            </div>

            <div class="bg-slate-900 rounded-xl shadow-lg p-6 lg:p-8 text-white">
                <div class="flex flex-col lg:flex-row gap-8">
                    <div class="w-full lg:w-1/2">
                        <h3 class="text-lg font-semibold mb-4 text-slate-200">Global Revenue Share (2025)</h3>
                        <div class="chart-container" style="height: 280px;">
                            <canvas id="competitorChart"></canvas>
                        </div>
                    </div>
                    <div class="w-full lg:w-1/2 flex flex-col justify-center space-y-6">
                        <div class="border-l-4 border-teal-400 pl-4">
                            <h4 class="font-bold text-lg">CSL Behring & Grifols Dominance</h4>
                            <p class="text-slate-300 text-sm mt-1">Together holding ~47% of the global market. These entities operate massive proprietary collection networks (e.g., Grifols operates 400+ centers globally), controlling the upstream value chain.</p>
                        </div>
                        <div class="border-l-4 border-indigo-400 pl-4">
                            <h4 class="font-bold text-lg">High Capital Intensity</h4>
                            <p class="text-slate-300 text-sm mt-1">Directly building a competing pooled-IVIG franchise involves billions in CAPEX and years of regulatory lag for fractionation approvals. Analysis indicates this is an unfavorable entry path for outsiders.</p>
                        </div>
                        <div class="border-l-4 border-rose-400 pl-4">
                            <h4 class="font-bold text-lg">The Niche Challenger Reality</h4>
                            <p class="text-slate-300 text-sm mt-1">Players like ADMA Biologics maintain profitable but capped shares (~5.5% by 2035) by relying partially on third-party plasma and focusing heavily on specialized or targeted applications rather than sheer volume scale.</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section id="emergent-strategy" class="scroll-mt-24 pb-12">
            <div class="mb-8">
                <h2 class="text-2xl font-bold text-slate-900 border-b-2 border-teal-500 inline-block pb-1">5. Strategic Positioning for Emergent BioSolutions</h2>
                <p class="mt-4 text-slate-600 leading-relaxed max-w-5xl">
                    Emergent BioSolutions is <strong>not</strong> a core IVIG leader and lacks the integrated plasma collection network required for direct broad-scale competition. However, Emergent holds distinct capabilities in targeted hyperimmune products, biodefense/government stockpiles, and CDMO/manufacturing. The following matrix evaluates potential strategic pathways, answering the critical question: <em>Where should Emergent play?</em>
                </p>
            </div>

            <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mb-6">
                <div class="grid grid-cols-1 md:grid-cols-12 bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-500 uppercase tracking-wider">
                    <div class="p-4 md:col-span-3">Strategic Pathway</div>
                    <div class="p-4 md:col-span-2 text-center">2030 TAM ($Bn)</div>
                    <div class="p-4 md:col-span-2 text-center">Emergent Fit</div>
                    <div class="p-4 md:col-span-2 text-center">Execution Risk</div>
                    <div class="p-4 md:col-span-3">Strategic Verdict</div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-12 border-b border-slate-100 strategy-row items-center cursor-pointer" onclick="highlightStrategy('adj')">
                    <div class="p-4 md:col-span-3 font-semibold text-slate-900 flex items-center gap-2">
                        <span id="indicator-adj" class="text-teal-600 font-bold hidden">&#8594;</span>
                        Adjacency Focus (Hyperimmune + MCM)
                    </div>
                    <div class="p-4 md:col-span-2 text-center font-medium text-slate-700">$3.3</div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-2 py-1 rounded text-xs font-bold bg-teal-100 text-teal-800">High</span></div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-2 py-1 rounded text-xs font-bold bg-yellow-100 text-yellow-800">Moderate</span></div>
                    <div class="p-4 md:col-span-3 text-sm text-slate-600">Leverages existing capabilities (ANTHRASIL, VIGIV). Highest ROI pathway.</div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-12 border-b border-slate-100 strategy-row items-center cursor-pointer" onclick="highlightStrategy('cdmo')">
                    <div class="p-4 md:col-span-3 font-semibold text-slate-900 flex items-center gap-2">
                        <span id="indicator-cdmo" class="text-teal-600 font-bold hidden">&#8594;</span>
                        CDMO / Specialty Fill-Finish
                    </div>
                    <div class="p-4 md:col-span-2 text-center font-medium text-slate-700">$2.0</div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-2 py-1 rounded text-xs font-bold bg-yellow-100 text-yellow-800">Moderate</span></div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-2 py-1 rounded text-xs font-bold bg-yellow-100 text-yellow-800">Moderate</span></div>
                    <div class="p-4 md:col-span-3 text-sm text-slate-600">Monetizes existing manufacturing footprint without downstream plasma risk.</div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-12 strategy-row items-center cursor-pointer" onclick="highlightStrategy('direct')">
                    <div class="p-4 md:col-span-3 font-semibold text-slate-900 flex items-center gap-2">
                        <span id="indicator-direct" class="text-teal-600 font-bold hidden">&#8594;</span>
                        Direct Pooled-IVIG Buildout
                    </div>
                    <div class="p-4 md:col-span-2 text-center font-medium text-slate-700">$16.9</div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-2 py-1 rounded text-xs font-bold bg-rose-100 text-rose-800">Low</span></div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-2 py-1 rounded text-xs font-bold bg-rose-100 text-rose-800">Very High</span></div>
                    <div class="p-4 md:col-span-3 text-sm text-slate-600">Prohibitive CAPEX ($1B+) required to build competitive plasma network.</div>
                </div>
            </div>

            <div id="strategy-deep-dive" class="bg-teal-50 border border-teal-200 rounded-xl p-6 transition-all duration-300">
                <h3 class="text-xl font-bold text-teal-900 mb-2">Recommendation: Double-Down on Adjacencies</h3>
                <p class="text-teal-800 leading-relaxed mb-4">
                    Data suggests Emergent should fiercely avoid direct, head-to-head competition with CSL and Grifols in the broad IVIG space. The required upstream plasma economics are insurmountable in the near term. Instead, Emergent is uniquely positioned to dominate the <strong>$3.3Bn to $5.0Bn Serviceable Available Market</strong> spanning hyperimmune products and government medical countermeasure (MCM) procurement.
                </p>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div class="bg-white rounded p-4 border border-teal-100 text-center shadow-sm">
                        <div class="text-2xl font-bold text-teal-700 mb-1">0.52</div>
                        <div class="text-xs text-slate-500 uppercase font-semibold">Serviceable Base (%)</div>
                    </div>
                    <div class="bg-white rounded p-4 border border-teal-100 text-center shadow-sm">
                        <div class="text-2xl font-bold text-teal-700 mb-1">$232.8 Mn</div>
                        <div class="text-xs text-slate-500 uppercase font-semibold">Est. 2035 Rev Potential</div>
                    </div>
                    <div class="bg-white rounded p-4 border border-teal-100 text-center shadow-sm">
                        <div class="text-2xl font-bold text-teal-700 mb-1">28%</div>
                        <div class="text-xs text-slate-500 uppercase font-semibold">EBITDA Margin Target</div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer class="bg-slate-900 py-10 border-t border-slate-800 mt-10">
        <div class="max-w-7xl mx-auto px-4 text-center text-slate-400 text-sm">
            &copy; 2026 Strategy Consulting Deliverable. Prepared for Emergent BioSolutions Internal Review. <br> All values in USD Millions. Forecast period 2025–2035.
        </div>
    </footer>

    <script>
        // --- Data Storage ---
        const indicationData = {
            '2025': [
                { name: 'PI & Serious Infection', rev: 2163.9, cagr: '4.5%', risk: 'Low' },
                { name: 'CIDP', rev: 2590.2, cagr: '3.6%', risk: 'High' },
                { name: 'GBS', rev: 353.2, cagr: '3.4%', risk: 'Low' },
                { name: 'Myasthenia Gravis (MG)', rev: 1146.4, cagr: '2.4%', risk: 'High' },
                { name: 'ITP', rev: 494.4, cagr: '3.1%', risk: 'Moderate' },
                { name: 'Kawasaki Disease', rev: 150.5, cagr: '2.5%', risk: 'Low' },
                { name: 'Other / Under-captured', rev: 6191.7, cagr: '6.4%', risk: 'Low' }
            ],
            '2035': [
                { name: 'PI & Serious Infection', rev: 3995.8, cagr: '4.5%', risk: 'Low' },
                { name: 'CIDP', rev: 3885.5, cagr: '3.6%', risk: 'High' },
                { name: 'GBS', rev: 555.2, cagr: '3.4%', risk: 'Low' },
                { name: 'Myasthenia Gravis (MG)', rev: 1475.2, cagr: '2.4%', risk: 'High' },
                { name: 'ITP', rev: 712.5, cagr: '3.1%', risk: 'Moderate' },
                { name: 'Kawasaki Disease', rev: 201.2, cagr: '2.5%', risk: 'Low' },
                { name: 'Other / Under-captured', rev: 11136.6, cagr: '6.4%', risk: 'Low' }
            ]
        };

        const topPlayers = ['CSL Behring', 'Grifols', 'Takeda', 'Octapharma', 'ADMA', 'Mid-tier/Other'];
        const share2025 = [25.0, 22.0, 19.0, 14.0, 2.0, 18.0];

        const chartColors = ['#0f172a', '#334155', '#475569', '#0d9488', '#0f766e', '#115e59', '#cbd5e1'];

        let indicationChartInstance = null;

        // --- Core Interaction Handling & UI Updates ---
        document.addEventListener('DOMContentLoaded', () => {
            initMarketDynamicsChart();
            initCompetitorChart();
            updateIndicationChart('2025');
            highlightStrategy('adj'); // Default strategy highlight
        });

        // 1. Line/Bar Combo Chart (Market Dynamics)
        function initMarketDynamicsChart() {
            const ctx = document.getElementById('marketDynamicsChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['2025', '2027', '2029', '2031', '2033', '2035'],
                    datasets: [
                        {
                            type: 'line',
                            label: 'Global Market Revenue ($Mn)',
                            data: [13090.5, 14545.9, 16104.7, 17937.1, 19830.4, 21962.2],
                            borderColor: '#0d9488',
                            backgroundColor: '#0d9488',
                            borderWidth: 3,
                            tension: 0.3,
                            yAxisID: 'y'
                        },
                        {
                            type: 'bar',
                            label: 'Actual Volume Sold (Mn grams)',
                            data: [298.8, 335.5, 375.4, 401.7, 411.0, 418.9],
                            backgroundColor: '#cbd5e1',
                            borderRadius: 4,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: { position: 'top', labels: { usePointStyle: true, boxWidth: 8 } },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) { label += ': '; }
                                    if (context.parsed.y !== null) {
                                        label += context.dataset.type === 'line' ? '$' + context.parsed.y.toFixed(1) : context.parsed.y.toFixed(1);
                                    }
                                    return label;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            type: 'linear', display: true, position: 'left',
                            title: { display: true, text: 'Revenue ($Mn)' },
                            grid: { color: '#f1f5f9' }
                        },
                        y1: {
                            type: 'linear', display: true, position: 'right',
                            title: { display: true, text: 'Volume (Mn grams)' },
                            grid: { drawOnChartArea: false }
                        }
                    }
                }
            });
        }

        // 2. Indication Donut Chart & Table update
        function updateIndicationChart(year) {
            document.getElementById('btn-2025').className = year === '2025' ? 'px-4 py-2 text-sm font-medium rounded bg-teal-600 text-white shadow-sm transition-colors' : 'px-4 py-2 text-sm font-medium rounded bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 transition-colors';
            document.getElementById('btn-2035').className = year === '2035' ? 'px-4 py-2 text-sm font-medium rounded bg-teal-600 text-white shadow-sm transition-colors' : 'px-4 py-2 text-sm font-medium rounded bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 transition-colors';

            const data = indicationData[year];
            const labels = data.map(d => d.name);
            const revenues = data.map(d => d.rev);

            const tbody = document.getElementById('indicationTableBody');
            tbody.innerHTML = '';
            data.forEach((row, index) => {
                const tr = document.createElement('tr');
                const riskColor = row.risk === 'High' ? 'text-rose-600 bg-rose-50' : (row.risk === 'Moderate' ? 'text-yellow-700 bg-yellow-50' : 'text-teal-700 bg-teal-50');
                tr.innerHTML = `
                    <td class="py-3 font-medium flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full inline-block" style="background-color: ${chartColors[index % chartColors.length]}"></span>
                        ${row.name}
                    </td>
                    <td class="py-3 text-right">$${indicationData['2025'][index].rev.toFixed(1)}</td>
                    <td class="py-3 text-right font-semibold">$${indicationData['2035'][index].rev.toFixed(1)}</td>
                    <td class="py-3 text-right">${row.cagr}</td>
                    <td class="py-3 text-center"><span class="px-2 py-1 rounded text-xs font-bold ${riskColor}">${row.risk}</span></td>
                `;
                tbody.appendChild(tr);
            });

            if (indicationChartInstance) {
                indicationChartInstance.data.labels = labels;
                indicationChartInstance.data.datasets[0].data = revenues;
                indicationChartInstance.update();
            } else {
                const ctx = document.getElementById('indicationDonutChart').getContext('2d');
                indicationChartInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: revenues,
                            backgroundColor: chartColors,
                            borderWidth: 1,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '65%',
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: function(context) { return ' $' + context.parsed.toFixed(1) + ' Mn'; }
                                }
                            }
                        }
                    }
                });
            }
        }

        // 3. Competitor Bar Chart
        function initCompetitorChart() {
            const ctx = document.getElementById('competitorChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: topPlayers,
                    datasets: [{
                        label: '2025 Market Share (%)',
                        data: share2025,
                        backgroundColor: ['#0d9488', '#0f766e', '#115e59', '#134e4a', '#64748b', '#94a3b8'],
                        borderRadius: 4
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) { return context.parsed.x + '% Share'; }
                            }
                        }
                    },
                    scales: {
                        x: { 
                            grid: { color: '#334155' },
                            ticks: { color: '#cbd5e1' },
                            title: { display: true, text: '% Market Share', color: '#cbd5e1' }
                        },
                        y: { 
                            grid: { display: false },
                            ticks: { color: '#f8fafc', font: { weight: 'bold' } }
                        }
                    }
                }
            });
        }

        // 4. Strategic Options Interaction
        function highlightStrategy(id) {
            document.querySelectorAll('[id^="indicator-"]').forEach(el => el.classList.add('hidden'));
            document.getElementById(`indicator-${id}`).classList.remove('hidden');

            const contentDiv = document.getElementById('strategy-deep-dive');
            
            if(id === 'adj') {
                contentDiv.className = 'bg-teal-50 border border-teal-200 rounded-xl p-6 transition-all duration-300';
                contentDiv.innerHTML = `
                    <h3 class="text-xl font-bold text-teal-900 mb-2">Recommendation: Double-Down on Adjacencies</h3>
                    <p class="text-teal-800 leading-relaxed mb-4">
                        Data suggests Emergent should fiercely avoid direct, head-to-head competition with CSL and Grifols in the broad IVIG space. The required upstream plasma economics are insurmountable in the near term. Instead, Emergent is uniquely positioned to dominate the <strong>$3.3Bn to $5.0Bn Serviceable Available Market</strong> spanning hyperimmune products and government medical countermeasure (MCM) procurement.
                    </p>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div class="bg-white rounded p-4 border border-teal-100 text-center shadow-sm">
                            <div class="text-2xl font-bold text-teal-700 mb-1">0.52</div>
                            <div class="text-xs text-slate-500 uppercase font-semibold">Serviceable Base (%)</div>
                        </div>
                        <div class="bg-white rounded p-4 border border-teal-100 text-center shadow-sm">
                            <div class="text-2xl font-bold text-teal-700 mb-1">$232.8 Mn</div>
                            <div class="text-xs text-slate-500 uppercase font-semibold">Est. 2035 Rev Potential</div>
                        </div>
                        <div class="bg-white rounded p-4 border border-teal-100 text-center shadow-sm">
                            <div class="text-2xl font-bold text-teal-700 mb-1">28%</div>
                            <div class="text-xs text-slate-500 uppercase font-semibold">EBITDA Margin Target</div>
                        </div>
                    </div>
                `;
            } else if (id === 'cdmo') {
                contentDiv.className = 'bg-slate-100 border border-slate-300 rounded-xl p-6 transition-all duration-300';
                contentDiv.innerHTML = `
                    <h3 class="text-xl font-bold text-slate-900 mb-2">Secondary Option: Leverage CDMO Capabilities</h3>
                    <p class="text-slate-700 leading-relaxed mb-4">
                        As a secondary pathway, Emergent can utilize its existing manufacturing and fill-finish capabilities to act as a CDMO for mid-tier challengers. This avoids the upfront plasma collection CAPEX while capturing margin downstream.
                    </p>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div class="bg-white rounded p-4 border border-slate-200 text-center shadow-sm">
                            <div class="text-2xl font-bold text-slate-800 mb-1">0.45</div>
                            <div class="text-xs text-slate-500 uppercase font-semibold">Serviceable Base (%)</div>
                        </div>
                        <div class="bg-white rounded p-4 border border-slate-200 text-center shadow-sm">
                            <div class="text-2xl font-bold text-slate-800 mb-1">$99.1 Mn</div>
                            <div class="text-xs text-slate-500 uppercase font-semibold">Est. 2035 Rev Potential</div>
                        </div>
                        <div class="bg-white rounded p-4 border border-slate-200 text-center shadow-sm">
                            <div class="text-2xl font-bold text-slate-800 mb-1">22%</div>
                            <div class="text-xs text-slate-500 uppercase font-semibold">EBITDA Margin Target</div>
                        </div>
                    </div>
                `;
            } else if (id === 'direct') {
                contentDiv.className = 'bg-rose-50 border border-rose-200 rounded-xl p-6 transition-all duration-300';
                contentDiv.innerHTML = `
                    <h3 class="text-xl font-bold text-rose-900 mb-2">Strategic Warning: Avoid Direct Core Entry</h3>
                    <p class="text-rose-800 leading-relaxed mb-4">
                        Entering the core pooled-IVIG space directly is ill-advised. It requires scaling plasma collection centers against entrenched leaders with 400+ centers. The capability gap is too wide, and the payback period too long for a viable ROI without a massive transformative acquisition.
                    </p>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div class="bg-white rounded p-4 border border-rose-200 text-center shadow-sm opacity-70">
                            <div class="text-2xl font-bold text-rose-700 mb-1">$1.1 Bn+</div>
                            <div class="text-xs text-slate-500 uppercase font-semibold">Est. Base CAPEX</div>
                        </div>
                        <div class="bg-white rounded p-4 border border-rose-200 text-center shadow-sm opacity-70">
                            <div class="text-2xl font-bold text-rose-700 mb-1">Low</div>
                            <div class="text-xs text-slate-500 uppercase font-semibold">Strategic Fit</div>
                        </div>
                        <div class="bg-white rounded p-4 border border-rose-200 text-center shadow-sm opacity-70">
                            <div class="text-2xl font-bold text-rose-700 mb-1">Very High</div>
                            <div class="text-xs text-slate-500 uppercase font-semibold">Execution Risk</div>
                        </div>
                    </div>
                `;
            }
        }
    </script>
</body>
</html>
"""

# Insert logo safely if exists
final_html = RAW_HTML_CONTENT.replace("LOGO_PLACEHOLDER", html_logo)

# Render HTML inside Streamlit container
components.html(final_html, height=1200, scrolling=True)