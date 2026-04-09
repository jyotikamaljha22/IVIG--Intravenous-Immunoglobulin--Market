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
    page_title="Strategic Market Research | IVIG & Emergent BioSolutions",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed", # Disables native sidebar permanently
)

# ----------------------------
# THEME COLORS & LOGO LOGIC
# ----------------------------
BURGUNDY = "#5B0F2E"
BURGUNDY_DARK = "#431022"
BURGUNDY_MID = "#7A1C41"
BURGUNDY_SOFT = "#A45A7B"
GOLD = "#C9A227"

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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}

    /* --- PERMANENT UI ERADICATION --- */
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
        border: 1px solid rgba(91,15,46,0.2) !important;
        padding: 12px 14px !important;
        background: #ffffff !important;
        color: #23171D !important;
    }}
    .stTextInput input:focus {{
        border-color: {GOLD} !important;
        box-shadow: 0 0 0 2px rgba(201,162,39,0.3) !important;
    }}

    /* Secure Login Button */
    .stButton > button {{
        background: linear-gradient(135deg, {BURGUNDY} 0%, {BURGUNDY_DARK} 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        border: none !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(91,15,46,0.3) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(91,15,46,0.45) !important;
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
            st.markdown(f"<h1 style='text-align:center; color:{BURGUNDY}; font-weight:800; font-size:2.2rem; margin-bottom:0;'>Strategic Market Research</h1>", unsafe_allow_html=True)
            
        st.markdown(f"<p style='text-align:center; color:{GOLD}; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:30px;'>Emergent BioSolutions Advisory</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<h3 style='color:#23171D; font-weight:700; margin-bottom:16px; text-align:center;'>🔐 Secure Login</h3>", unsafe_allow_html=True)
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
    st.markdown(f"<div style='text-align:right; font-size:0.8rem; font-weight:600; color:{BURGUNDY}; margin-bottom:8px;'>Verified: {st.session_state.viewer_name}</div>", unsafe_allow_html=True)
    if st.button("🔒 End Secure Session", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ----------------------------
# HTML DASHBOARD CONTENT (BURGUNDY & GOLD THEME)
# ----------------------------
html_logo = f'<img src="data:image/svg+xml;base64,{LOGO_B64}" style="height:54px; width:auto; margin-bottom:16px;" />' if LOGO_B64 else ""
html_logo_sidebar = f'<img src="data:image/svg+xml;base64,{LOGO_B64}" style="height:38px; width:auto; margin-bottom:12px; filter: brightness(0) invert(1);" />' if LOGO_B64 else ""

HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global IVIG Market (2025–2035) & Strategic Positioning</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        body {{ 
            font-family: 'Plus Jakarta Sans', sans-serif; 
            background-color: #FDFBFC; 
            color: #23171D; 
            margin: 0;
            padding: 0;
        }}
        
        .chart-container {{
            position: relative;
            width: 100%;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
            height: 350px;
            max-height: 400px;
            margin-bottom: 2rem;
            margin-top: 1rem;
            background: #ffffff;
            border-radius: 16px;
            padding: 20px;
            border: 1px solid #E1D2DA;
            box-shadow: 0 10px 30px rgba(91,15,46,0.04);
        }}
        @media (max-width: 768px) {{
            .chart-container {{ height: 250px; max-height: 300px; padding: 10px; }}
        }}
        
        .stat-card {{
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(10px);
        }}
        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 16px 40px rgba(91,15,46,0.08);
            border-color: rgba(201,162,39,0.4);
        }}

        .nav-link {{ transition: all 0.2s ease; font-weight: 500; }}
        .nav-link.active {{ 
            background-color: rgba(255,255,255,0.1); 
            border-left: 4px solid #C9A227; 
            color: #C9A227 !important; 
            font-weight: 700; 
        }}
        
        .data-table {{ width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 0.875rem; text-align: left; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(91,15,46,0.03); border: 1px solid #E1D2DA; }}
        .data-table th {{ background-color: #5B0F2E; color: white; padding: 1rem; font-weight: 700; letter-spacing: 0.02em; }}
        .data-table td {{ padding: 1rem; border-bottom: 1px solid #F0E6EA; color: #4A3F44; }}
        .data-table tr:last-child td {{ border-bottom: none; }}
        .data-table tr:hover td {{ background-color: #FAF5F7; }}
        
        .insight-box {{ 
            border-left: 5px solid #C9A227; 
            background: linear-gradient(135deg, #FFF9EF 0%, #FFFFFF 100%); 
            padding: 1.25rem 1.5rem; 
            margin: 1.5rem 0; 
            border-radius: 12px;
            color: #23171D; 
            font-size: 0.95rem;
            line-height: 1.6;
            box-shadow: 0 8px 24px rgba(201,162,39,0.08);
        }}
        
        .emergent-highlight {{ 
            border-left: 5px solid #5B0F2E; 
            background: linear-gradient(135deg, #FAF5F7 0%, #FFFFFF 100%); 
            padding: 1.25rem 1.5rem; 
            margin: 1.5rem 0; 
            font-weight: 600; 
            color: #5B0F2E; 
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(91,15,46,0.06);
        }}
        
        .strategy-row {{ transition: background-color 0.2s ease; }}
        .strategy-row:hover {{ background-color: #FAF5F7; }}

        h2 {{ color: #5B0F2E; letter-spacing: -0.01em; }}
        h3 {{ color: #431022; }}
        
        /* Inner app layout styling */
        .sidebar {{ height: 100vh; position: sticky; top: 0; background-color: #431022; }}
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(91,15,46,0.2); border-radius: 10px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(91,15,46,0.4); }}
    </style>
</head>
<body class="flex flex-col md:flex-row min-h-screen">

    <div class="md:hidden bg-[#431022] text-white p-4 flex justify-between items-center sticky top-0 z-50 shadow-md">
        <div class="font-bold text-lg text-[#C9A227]">Strategic Market Research</div>
        <button id="mobile-menu-btn" class="text-2xl focus:outline-none">&#9776;</button>
    </div>

    <nav id="sidebar" class="sidebar hidden md:flex flex-col w-full md:w-72 text-slate-300 md:fixed md:h-screen overflow-y-auto z-40 flex-shrink-0 border-r border-black/10 shadow-2xl">
        <div class="p-6 pb-2 border-b border-white/10">
            {html_logo_sidebar}
            <h1 class="text-xl font-bold text-white mb-1 leading-tight">Strategic Market Research</h1>
            <p class="text-xs text-[#C9A227] uppercase tracking-wider font-bold mb-6">Emergent BioSolutions</p>
        </div>
        <div class="px-4 py-6 flex flex-col gap-1 text-sm" id="nav-menu">
            <a href="#snapshot" class="nav-link block px-4 py-2.5 rounded-lg text-white hover:bg-white/10">1. Executive Overview</a>
            <a href="#dynamics" class="nav-link block px-4 py-2.5 rounded-lg text-white hover:bg-white/10">2. Market Dynamics</a>
            <a href="#indications" class="nav-link block px-4 py-2.5 rounded-lg text-white hover:bg-white/10">3. Indication Disruption</a>
            <a href="#value-chain" class="nav-link block px-4 py-2.5 rounded-lg text-white hover:bg-white/10">4. Value Chain & Margin</a>
            <a href="#competition" class="nav-link block px-4 py-2.5 rounded-lg text-white hover:bg-white/10">5. Competitive Control</a>
            <a href="#regional" class="nav-link block px-4 py-2.5 rounded-lg text-white hover:bg-white/10">6. Regional Deep Dive</a>
            <a href="#emergent-strategy" class="nav-link block px-4 py-2.5 rounded-lg text-[#C9A227] font-bold hover:bg-white/10 mt-4 border border-[#C9A227]/30">7. Emergent Strategy</a>
            <a href="#appendix" class="nav-link block px-4 py-2.5 rounded-lg text-white hover:bg-white/10 mt-4">8. Appendix</a>
        </div>
    </nav>

    <main class="flex-1 md:ml-72 p-6 md:p-12 lg:p-16 max-w-6xl">
        
        <header class="mb-16 border-b-2 border-[#E1D2DA] pb-10">
            {html_logo}
            <div class="inline-block bg-[#C9A227] text-white text-xs font-bold uppercase tracking-widest px-3 py-1 rounded-full mb-6 shadow-sm">Confidential Boardroom Briefing</div>
            <h1 class="text-4xl md:text-5xl font-extrabold text-[#5B0F2E] tracking-tight leading-tight mb-6">Global IVIG Market (2025–2035)</h1>
            <h2 class="text-2xl text-[#7A1C41] font-medium leading-relaxed">Supply-Constrained Growth, Therapy Substitution & Strategic Positioning for Emergent BioSolutions</h2>
        </header>

        <section id="snapshot" class="mb-24 scroll-mt-20">
            <div class="mb-8">
                <h2 class="text-3xl font-bold mb-6 border-b-2 border-[#C9A227] pb-2 inline-block">1. Executive Overview & Strategic Snapshot</h2>
                <p class="mt-4 text-[#4A3F44] leading-relaxed text-lg">
                    The following dashboard synthesizes the fundamental economics of the Global Intravenous Immunoglobulin (IVIG) market. Analysis indicates a robust but structurally bottlenecked market, moving from $13.1 Billion in 2025 to $22.0 Billion by 2035. Growth is dictated not simply by patient demand, but by the physical limits of global plasma collection.
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="stat-card rounded-xl p-6 border border-[#E1D2DA] border-l-4 border-l-[#431022]">
                    <p class="text-xs font-bold text-[#A45A7B] uppercase tracking-wider mb-1">Market Size (2025)</p>
                    <div class="text-3xl font-extrabold text-[#5B0F2E]">$13.1<span class="text-lg text-[#7A1C41] font-medium"> Bn</span></div>
                    <p class="text-xs text-[#4A3F44] mt-2">Baseline revenue actuals</p>
                </div>
                <div class="stat-card rounded-xl p-6 border border-[#E1D2DA] border-l-4 border-l-[#C9A227]">
                    <p class="text-xs font-bold text-[#A45A7B] uppercase tracking-wider mb-1">Forecast Size (2035)</p>
                    <div class="text-3xl font-extrabold text-[#5B0F2E]">$22.0<span class="text-lg text-[#7A1C41] font-medium"> Bn</span></div>
                    <p class="text-xs text-[#4A3F44] mt-2">Base case modeled projection</p>
                </div>
                <div class="stat-card rounded-xl p-6 border border-[#E1D2DA] border-l-4 border-l-[#7A1C41]">
                    <p class="text-xs font-bold text-[#A45A7B] uppercase tracking-wider mb-1">10-Year CAGR</p>
                    <div class="text-3xl font-extrabold text-[#5B0F2E]">5.3<span class="text-lg text-[#7A1C41] font-medium"> %</span></div>
                    <p class="text-xs text-[#4A3F44] mt-2">Driven by volume and price mix</p>
                </div>
                <div class="stat-card rounded-xl p-6 border border-[#E1D2DA] border-l-4 border-l-[#9F1D35]">
                    <p class="text-xs font-bold text-[#A45A7B] uppercase tracking-wider mb-1">Market Concentration</p>
                    <div class="text-3xl font-extrabold text-[#5B0F2E]">80.0<span class="text-lg text-[#7A1C41] font-medium"> %</span></div>
                    <p class="text-xs text-[#4A3F44] mt-2">Share controlled by Top 4 players</p>
                </div>
            </div>

            <div class="insight-box">
                <strong>Strategic Imperative:</strong> The IVIG sector is an entrenched oligopoly. For an entity like Emergent BioSolutions, directly entering the core pooled-IVIG space is mathematically unfavorable due to the multi-billion dollar capital expenditure required to establish plasma collection networks. Value must be captured in high-margin adjacencies.
            </div>
        </section>

        <section id="dynamics" class="mb-24 scroll-mt-20">
            <div class="mb-8">
                <h2 class="text-3xl font-bold mb-6 border-b-2 border-[#C9A227] pb-2 inline-block">2. Structural Market Dynamics: The Plasma Ceiling</h2>
                <p class="mt-4 text-[#4A3F44] leading-relaxed text-lg">
                    Unlike traditional pharmaceutical markets, IVIG operates as a supply-constrained biologics market. The fundamental truth of this sector is that market growth is strictly tethered to the availability of human source plasma (growing to ~156 Mn Liters by 2035).
                </p>
            </div>

            <div class="bg-white rounded-xl border border-[#E1D2DA] shadow-sm p-6 lg:p-8 flex flex-col lg:flex-row gap-8 items-center">
                <div class="w-full lg:w-2/3">
                    <h3 class="text-lg font-bold text-[#5B0F2E] mb-2 text-center">Global Market Trajectory: Revenue vs Volume</h3>
                    <div class="chart-container">
                        <canvas id="marketDynamicsChart"></canvas>
                    </div>
                </div>
                <div class="w-full lg:w-1/3 space-y-6">
                    <h3 class="text-lg font-bold text-[#5B0F2E]">Divergence & Yield Constraints</h3>
                    <p class="text-sm text-[#4A3F44]">
                        Analysis indicates a structural divergence: revenue grows at 5.3% while volume grows at only 3.4%. This gap highlights the extreme pricing leverage plasma integrators command in a supply-constrained environment.
                    </p>
                    <div class="bg-[#FAF5F7] rounded-lg p-4 border border-[#E1D2DA]">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-xs font-bold text-[#A45A7B] uppercase">Realized ASP (2025)</span>
                            <span class="text-sm font-bold text-[#5B0F2E]">$43.8 / gram</span>
                        </div>
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-xs font-bold text-[#A45A7B] uppercase">Realized ASP (2035)</span>
                            <span class="text-sm font-bold text-[#5B0F2E]">$52.4 / gram</span>
                        </div>
                        <p class="text-xs text-[#7A1C41] mt-3 italic border-t border-[#E1D2DA] pt-2">
                            Pricing acts as the primary clearing mechanism for unmet regional demand, heavily insulating incumbent gross margins.
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <section id="indications" class="mb-24 scroll-mt-20">
            <div class="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div class="max-w-4xl">
                    <h2 class="text-3xl font-bold mb-6 border-b-2 border-[#C9A227] pb-2 inline-block">3. Indication-Level Disruption Risk</h2>
                    <p class="mt-4 text-[#4A3F44] leading-relaxed text-lg">
                        The IVIG market faces unprecedented therapy substitution risk. Emerging targeted therapies, specifically <strong>FcRn inhibitors</strong> (e.g., efgartigimod, nipocalimab) and complement inhibitors, are actively displacing chronic IVIG maintenance use in autoimmune neurology.
                    </p>
                </div>
                <div class="flex gap-2 shrink-0 pb-2">
                    <button onclick="updateIndicationChart('2025')" id="btn-2025" class="px-4 py-2 text-sm font-bold rounded bg-[#5B0F2E] text-white shadow-sm transition-colors">2025 Data</button>
                    <button onclick="updateIndicationChart('2035')" id="btn-2035" class="px-4 py-2 text-sm font-bold rounded bg-white text-[#5B0F2E] border border-[#E1D2DA] hover:bg-[#FAF5F7] transition-colors">2035 Data</button>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div class="bg-white rounded-xl border border-[#E1D2DA] shadow-sm p-6 flex flex-col justify-center">
                    <h3 class="text-lg font-bold text-[#5B0F2E] mb-2 text-center">Revenue Composition</h3>
                    <div class="chart-container flex items-center justify-center">
                        <canvas id="indicationDonutChart"></canvas>
                    </div>
                </div>
                <div class="bg-white rounded-xl border border-[#E1D2DA] shadow-sm p-6 overflow-x-auto">
                    <table class="w-full text-left text-sm whitespace-nowrap">
                        <thead>
                            <tr class="border-b-2 border-[#E1D2DA] text-[#A45A7B]">
                                <th class="pb-3 font-bold uppercase tracking-wider">Indication</th>
                                <th class="pb-3 font-bold uppercase tracking-wider text-right">2025 Rev ($Mn)</th>
                                <th class="pb-3 font-bold uppercase tracking-wider text-right">2035 Rev ($Mn)</th>
                                <th class="pb-3 font-bold uppercase tracking-wider text-right">CAGR</th>
                                <th class="pb-3 font-bold uppercase tracking-wider text-center">Disruption Risk</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-[#F0E6EA] text-[#4A3F44]" id="indicationTableBody">
                        </tbody>
                    </table>
                    <p class="text-sm text-[#7A1C41] mt-6 italic border-l-4 border-[#C9A227] pl-4 bg-[#FFF9EF] py-2">
                        <strong>The Volume Sink Reality:</strong> A single CIDP patient consumes ~1,000 grams of IVIG annually (vs 36g for Kawasaki). Modeling indicates a catastrophic 30% to 35% volumetric displacement in CIDP and MG due to FcRn blockers by 2035.
                    </p>
                </div>
            </div>
        </section>

        <section id="value-chain" class="mb-24 scroll-mt-20">
            <h2 class="text-3xl font-bold mb-6 border-b-2 border-[#C9A227] pb-2 inline-block">4. Value Chain & Profit Pool Analysis</h2>
            <p class="text-[#4A3F44] leading-relaxed mb-6 text-lg">Understanding where margin is captured across the ecosystem dictates viable entry points for non-integrated players.</p>

            <table class="data-table">
                <thead><tr><th>Value Chain Layer</th><th>Revenue Contribution (%)</th><th>Est. EBITDA Margin (%)</th><th>Capital Intensity & Risk</th></tr></thead>
                <tbody>
                    <tr><td class="font-medium text-[#5B0F2E]">Plasma Collection</td><td>24.0%</td><td>16.0%</td><td>Very High (Donor network scale)</td></tr>
                    <tr class="bg-[#FAF5F7]"><td class="font-bold text-[#5B0F2E]">Fractionation & Purification</td><td class="font-bold">34.0%</td><td class="font-bold text-[#C9A227]">28.0%</td><td>Extreme ($400M+ Capex, 5-7yr lag)</td></tr>
                    <tr><td class="font-medium text-[#5B0F2E]">Formulation / Fill-Finish</td><td>12.0%</td><td class="font-bold text-[#C9A227]">20.0%</td><td>Moderate (Highly viable CDMO entry)</td></tr>
                    <tr><td class="font-medium text-[#5B0F2E]">Brand & Distribution</td><td>30.0%</td><td>18.0%</td><td>Low to Moderate</td></tr>
                </tbody>
            </table>

            <div class="emergent-highlight">
                <strong>Strategic Fit:</strong> Emergent is structurally engineered to capture the highly attractive 20-22% EBITDA margins in Fill-Finish (CDMO) and niche Commercial Brand layers without having to finance or risk the staggering capital required for the upstream 28% Fractionation layer.
            </div>
        </section>

        <section id="competition" class="mb-24 scroll-mt-20">
            <div class="mb-8">
                <h2 class="text-3xl font-bold mb-6 border-b-2 border-[#C9A227] pb-2 inline-block">5. Competitive Landscape & Market Control</h2>
                <p class="mt-4 text-[#4A3F44] leading-relaxed max-w-5xl text-lg">
                    Market share in the IVIG ecosystem is fundamentally an expression of plasma collection infrastructure. The data demonstrates profound concentration. Entering the core IVIG market directly requires scaling against entrenched leaders with 400+ centers, creating a nearly impenetrable moat.
                </p>
                <p class="text-xs font-bold uppercase text-[#A45A7B] mt-2 tracking-wider">Note: Competitor names have been anonymized for this preview.</p>
            </div>

            <div class="bg-white border border-[#E1D2DA] rounded-xl shadow-md p-6 lg:p-8">
                <div class="flex flex-col lg:flex-row gap-8">
                    <div class="w-full lg:w-1/2">
                        <h3 class="text-lg font-bold text-[#5B0F2E] mb-4 text-center">Global Revenue Share (2025)</h3>
                        <div class="chart-container" style="height: 280px;">
                            <canvas id="competitorChart"></canvas>
                        </div>
                    </div>
                    <div class="w-full lg:w-1/2 flex flex-col justify-center space-y-6">
                        <div class="border-l-4 border-[#5B0F2E] pl-4 bg-[#FAF5F7] p-3 rounded-r">
                            <h4 class="font-bold text-lg text-[#431022]">Company 1 & 2 Dominance</h4>
                            <p class="text-[#4A3F44] text-sm mt-1">Together holding ~47% of the global market. These entities operate massive proprietary collection networks globally, exclusively controlling the upstream value chain and suppressing mid-tier margins.</p>
                        </div>
                        <div class="border-l-4 border-[#C9A227] pl-4 bg-[#FFF9EF] p-3 rounded-r">
                            <h4 class="font-bold text-lg text-[#431022]">High Capital Intensity Barrier</h4>
                            <p class="text-[#4A3F44] text-sm mt-1">Directly building a competing pooled-IVIG franchise involves over $1B+ in CAPEX and years of regulatory lag for fractionation approvals. Analysis indicates this is an unfavorable entry path for outsiders.</p>
                        </div>
                        <div class="border-l-4 border-[#A45A7B] pl-4 bg-[#FAF5F7] p-3 rounded-r">
                            <h4 class="font-bold text-lg text-[#431022]">The Niche Challenger Reality</h4>
                            <p class="text-[#4A3F44] text-sm mt-1">Players like Company 5 maintain profitable but capped shares (~5.5% by 2035) by relying partially on third-party plasma and focusing heavily on specialized or targeted applications rather than sheer volume scale.</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section id="regional" class="mb-24 scroll-mt-20">
            <h2 class="text-3xl font-bold mb-6 border-b-2 border-[#C9A227] pb-2 inline-block">6. Regional Opportunity & Access Dynamics</h2>
            <p class="text-[#4A3F44] leading-relaxed mb-8 text-lg">Growth is globally synchronized, but base absolute value resides heavily in the US and APAC. The US represents the highest price pool, while APAC represents the largest demand volume frontier.</p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-white p-6 rounded-xl border border-[#E1D2DA] shadow-sm hover:shadow-md transition">
                    <h4 class="font-bold text-[#5B0F2E] mb-2 text-xl">United States (33.5% Share)</h4>
                    <p class="text-sm text-[#4A3F44] mb-3">The ultimate benchmark market. Features unparalleled pricing ($57.4/g by 2035) and specific home IVIG/SCIG benefits (CMS Q2052). Operates as the global collection hub.</p>
                    <div class="text-xs font-bold text-[#A45A7B] uppercase">Priority: 1 (Pricing)</div>
                </div>
                <div class="bg-white p-6 rounded-xl border border-[#E1D2DA] shadow-sm hover:shadow-md transition">
                    <h4 class="font-bold text-[#5B0F2E] mb-2 text-xl">Europe (21.5% Share)</h4>
                    <p class="text-sm text-[#4A3F44] mb-3">Heavy public tender environments. Regulations suppress domestic compensated plasma collection, creating a severe ~5 million liter deficit, reliant on US imports.</p>
                    <div class="text-xs font-bold text-[#A45A7B] uppercase">Priority: 3 (Tender Managed)</div>
                </div>
                <div class="bg-white p-6 rounded-xl border border-[#E1D2DA] shadow-sm hover:shadow-md transition">
                    <h4 class="font-bold text-[#5B0F2E] mb-2 text-xl">Asia Pacific (32.2% Share)</h4>
                    <p class="text-sm text-[#4A3F44] mb-3">The growth engine. Markets like China are pushing for self-sufficiency, while India sees rising incidence. Commands solid pricing but stringent regulatory hurdles.</p>
                    <div class="text-xs font-bold text-[#A45A7B] uppercase">Priority: 2 (Volume Frontier)</div>
                </div>
            </div>
        </section>

        <section id="emergent-strategy" class="mb-24 scroll-mt-20 pb-12">
            <div class="mb-8">
                <h2 class="text-3xl font-bold mb-6 border-b-2 border-[#C9A227] pb-2 inline-block text-[#5B0F2E]">7. Strategic Positioning for Emergent BioSolutions</h2>
                <p class="mt-4 text-[#4A3F44] leading-relaxed max-w-5xl text-lg">
                    Emergent BioSolutions is <strong>not</strong> a core IVIG leader and lacks the integrated plasma network required for direct competition. However, Emergent holds distinct capabilities in targeted hyperimmune products (ANTHRASIL, VIGIV), biodefense/government stockpiles, and CDMO manufacturing. The following matrix answers the critical question: <em>Where should Emergent play?</em>
                </p>
            </div>

            <div class="bg-white rounded-xl border border-[#E1D2DA] shadow-md overflow-hidden mb-8">
                <div class="grid grid-cols-1 md:grid-cols-12 bg-[#5B0F2E] text-xs font-bold text-white uppercase tracking-wider">
                    <div class="p-4 md:col-span-3">Strategic Pathway</div>
                    <div class="p-4 md:col-span-2 text-center">2030 TAM ($Bn)</div>
                    <div class="p-4 md:col-span-2 text-center">Emergent Fit</div>
                    <div class="p-4 md:col-span-2 text-center">Execution Risk</div>
                    <div class="p-4 md:col-span-3">Strategic Verdict</div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-12 border-b border-[#E1D2DA] strategy-row items-center cursor-pointer bg-[#FAF5F7]" onclick="highlightStrategy('adj')">
                    <div class="p-4 md:col-span-3 font-bold text-[#431022] flex items-center gap-2">
                        <span id="indicator-adj" class="text-[#C9A227] text-lg font-bold">&#8594;</span>
                        Adjacency Focus (Hyperimmune + MCM)
                    </div>
                    <div class="p-4 md:col-span-2 text-center font-bold text-[#5B0F2E] text-lg">$3.3</div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-3 py-1 rounded text-xs font-bold bg-[#C9A227] text-white">High</span></div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-3 py-1 rounded text-xs font-bold bg-[#E1D2DA] text-[#431022]">Moderate</span></div>
                    <div class="p-4 md:col-span-3 text-sm text-[#4A3F44] font-medium">Leverages existing capabilities. 100% insulated from FcRn disruption. Highest ROI.</div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-12 border-b border-[#E1D2DA] strategy-row items-center cursor-pointer" onclick="highlightStrategy('cdmo')">
                    <div class="p-4 md:col-span-3 font-bold text-[#431022] flex items-center gap-2">
                        <span id="indicator-cdmo" class="text-[#C9A227] text-lg font-bold hidden">&#8594;</span>
                        CDMO / Specialty Fill-Finish
                    </div>
                    <div class="p-4 md:col-span-2 text-center font-bold text-[#5B0F2E] text-lg">$2.0</div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-3 py-1 rounded text-xs font-bold bg-[#E1D2DA] text-[#431022]">Moderate</span></div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-3 py-1 rounded text-xs font-bold bg-[#E1D2DA] text-[#431022]">Moderate</span></div>
                    <div class="p-4 md:col-span-3 text-sm text-[#4A3F44] font-medium">Monetizes existing footprint (20% margins) without downstream plasma risk.</div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-12 strategy-row items-center cursor-pointer" onclick="highlightStrategy('direct')">
                    <div class="p-4 md:col-span-3 font-bold text-[#431022] flex items-center gap-2">
                        <span id="indicator-direct" class="text-[#C9A227] text-lg font-bold hidden">&#8594;</span>
                        Direct Pooled-IVIG Buildout
                    </div>
                    <div class="p-4 md:col-span-2 text-center font-bold text-[#5B0F2E] text-lg">$16.9</div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-3 py-1 rounded text-xs font-bold bg-[#9F1D35] text-white">Low</span></div>
                    <div class="p-4 md:col-span-2 text-center"><span class="px-3 py-1 rounded text-xs font-bold bg-[#9F1D35] text-white">Very High</span></div>
                    <div class="p-4 md:col-span-3 text-sm text-[#4A3F44] font-medium">Prohibitive CAPEX ($1B+) required to build competing plasma network.</div>
                </div>
            </div>

            <div id="strategy-deep-dive" class="bg-[#FFF9EF] border border-[#C9A227]/50 rounded-xl p-8 shadow-sm transition-all duration-300">
                <h3 class="text-2xl font-bold text-[#5B0F2E] mb-3">Recommendation: Double-Down on Adjacencies</h3>
                <p class="text-[#4A3F44] leading-relaxed mb-6 text-lg">
                    Data suggests Emergent should fiercely avoid direct, head-to-head competition in the broad IVIG space. The required upstream plasma economics are insurmountable in the near term. Instead, Emergent is uniquely positioned to dominate the <strong>$3.3Bn to $5.0Bn Serviceable Available Market</strong> spanning hyperimmune products and government medical countermeasure (MCM) procurement.
                </p>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <div class="bg-white rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm">
                        <div class="text-3xl font-extrabold text-[#C9A227] mb-2">0.52</div>
                        <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">Serviceable Base (%)</div>
                    </div>
                    <div class="bg-white rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm">
                        <div class="text-3xl font-extrabold text-[#C9A227] mb-2">$232.8 Mn</div>
                        <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">Est. 2035 Rev Potential</div>
                    </div>
                    <div class="bg-white rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm">
                        <div class="text-3xl font-extrabold text-[#C9A227] mb-2">28%</div>
                        <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">EBITDA Margin Target</div>
                    </div>
                </div>
            </div>
        </section>
        
        <section id="appendix" class="mb-24 scroll-mt-20">
            <h2 class="text-3xl font-bold mb-6 border-b-2 border-[#C9A227] pb-2 inline-block">8. Appendix & Methodology</h2>
            <div class="bg-[#431022] text-white p-8 rounded-xl shadow-inner">
                <p class="leading-relaxed mb-4 text-sm opacity-90">
                    <strong>Methodology Note:</strong> Analysis built on synthesized epidemiology, standard-of-care baseline modeling, and explicit infrastructure cost profiling. Market modeling utilizes an aggressive substitution curve for FcRn inhibitors in Neurology.<br><br>
                    <strong>Abbreviations:</strong> TRD (Treatment-Resistant Depression), GAD (Generalized Anxiety Disorder), PTSD (Post-Traumatic Stress Disorder), CIDP (Chronic Inflammatory Demyelinating Polyneuropathy), PI (Primary Immunodeficiency), MG (Myasthenia Gravis).<br><br>
                    <strong>Data Sources:</strong> Calibrated to 2025 observable anchors. Market Research Bureau (MRB) Plasma insights, Corporate Fillings (CSL, Grifols, ADMA, Argenx).
                </p>
            </div>
        </section>

    </main>

    <footer class="bg-[#431022] py-12 border-t border-black/20 mt-10">
        <div class="max-w-7xl mx-auto px-4 text-center text-white/60 text-sm">
            <div class="mb-4 flex justify-center opacity-50">{html_logo}</div>
            <p class="font-bold tracking-widest uppercase mb-2 text-[#C9A227]">Strategic Market Research</p>
            &copy; 2026 Strategy Consulting Deliverable. Prepared for Emergent BioSolutions Internal Review. <br> All values in USD Millions. Forecast period 2025–2035.
        </div>
    </footer>

    <script>
        // --- Data Storage ---
        const indicationData = {{
            '2025': [
                {{ name: 'PI & Serious Infection', rev: 2163.9, cagr: '5.8%', risk: 'Low' }},
                {{ name: 'CIDP', rev: 2590.3, cagr: '3.2%', risk: 'High' }},
                {{ name: 'Myasthenia Gravis (MG)', rev: 358.5, cagr: '1.4%', risk: 'Critical' }},
                {{ name: 'ITP', rev: 128.0, cagr: '1.8%', risk: 'Moderate' }},
                {{ name: 'Other / Uncaptured', rev: 6614.6, cagr: '6.3%', risk: 'Low' }}
            ],
            '2035': [
                {{ name: 'PI & Serious Infection', rev: 3821.2, cagr: '5.8%', risk: 'Low' }},
                {{ name: 'CIDP', rev: 3535.1, cagr: '3.2%', risk: 'High' }},
                {{ name: 'Myasthenia Gravis (MG)', rev: 412.8, cagr: '1.4%', risk: 'Critical' }},
                {{ name: 'ITP', rev: 153.1, cagr: '1.8%', risk: 'Moderate' }},
                {{ name: 'Other / Uncaptured', rev: 12171.2, cagr: '6.3%', risk: 'Low' }}
            ]
        }};

        const topPlayers = ['Company 1', 'Company 2', 'Company 3', 'Company 4', 'Company 5', 'Mid-tier/Other'];
        const share2025 = [25.0, 22.0, 19.0, 14.0, 7.0, 13.0];

        const colorBurgundy = '{BURGUNDY}';
        const colorDark = '{BURGUNDY_DARK}';
        const colorMid = '{BURGUNDY_MID}';
        const colorSoft = '{BURGUNDY_SOFT}';
        const colorGold = '{GOLD}';
        const colorMuted = '#E1D2DA';

        const chartColors = [colorBurgundy, colorMid, colorGold, colorSoft, '#431022', colorMuted];

        let indicationChartInstance = null;

        // --- Core Interaction Handling & UI Updates ---
        document.addEventListener('DOMContentLoaded', () => {{
            initMarketDynamicsChart();
            initCompetitorChart();
            updateIndicationChart('2025');
            
            // Scroll Spy
            const sections = document.querySelectorAll('section');
            const navLinks = document.querySelectorAll('.nav-link');
            const mobileMenuBtn = document.getElementById('mobile-menu-btn');
            const sidebar = document.getElementById('sidebar');

            mobileMenuBtn.addEventListener('click', () => {{
                sidebar.classList.toggle('hidden');
                sidebar.classList.toggle('absolute');
                sidebar.classList.toggle('z-50');
            }});

            window.addEventListener('scroll', () => {{
                let current = '';
                sections.forEach(section => {{
                    const sectionTop = section.offsetTop;
                    if (scrollY >= (sectionTop - 150)) {{
                        current = section.getAttribute('id');
                    }}
                }});

                navLinks.forEach(link => {{
                    // Skip the active styling for emergent strategy to keep its special styling
                    if(!link.getAttribute('href').includes('emergent-strategy')) {{
                        link.classList.remove('active');
                        if (link.getAttribute('href').includes(current)) {{
                            link.classList.add('active');
                        }}
                    }}
                }});
            }});
        }});

        // 1. Line/Bar Combo Chart (Market Dynamics)
        function initMarketDynamicsChart() {{
            const ctx = document.getElementById('marketDynamicsChart').getContext('2d');
            Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
            Chart.defaults.color = '#4A3F44'; 
            
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['2025', '2027', '2029', '2031', '2033', '2035'],
                    datasets: [
                        {{
                            type: 'line',
                            label: 'Global Market Revenue ($Mn)',
                            data: [13090.5, 14545.9, 16104.7, 17937.1, 19830.4, 21962.2],
                            borderColor: colorGold,
                            backgroundColor: colorGold,
                            borderWidth: 3,
                            tension: 0.3,
                            yAxisID: 'y'
                        }},
                        {{
                            type: 'bar',
                            label: 'Actual Volume Sold (Mn grams)',
                            data: [298.8, 335.5, 375.4, 401.7, 411.0, 418.9],
                            backgroundColor: colorMid,
                            borderRadius: 4,
                            yAxisID: 'y1'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    plugins: {{
                        legend: {{ position: 'top', labels: {{ usePointStyle: true, boxWidth: 8 }} }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    let label = context.dataset.label || '';
                                    if (label) {{ label += ': '; }}
                                    if (context.parsed.y !== null) {{
                                        label += context.dataset.type === 'line' ? '$' + context.parsed.y.toFixed(1) : context.parsed.y.toFixed(1);
                                    }}
                                    return label;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            type: 'linear', display: true, position: 'left',
                            title: {{ display: true, text: 'Revenue ($Mn)' }},
                            grid: {{ color: '#F0E6EA' }}
                        }},
                        y1: {{
                            type: 'linear', display: true, position: 'right',
                            title: {{ display: true, text: 'Volume (Mn grams)' }},
                            grid: {{ drawOnChartArea: false }}
                        }},
                        x: {{ grid: {{ display: false }} }}
                    }}
                }}
            }});
        }}

        // 2. Indication Donut Chart & Table update
        function updateIndicationChart(year) {{
            document.getElementById('btn-2025').className = year === '2025' ? 'px-4 py-2 text-sm font-bold rounded bg-[#5B0F2E] text-white shadow-sm transition-colors' : 'px-4 py-2 text-sm font-bold rounded bg-white text-[#5B0F2E] border border-[#E1D2DA] hover:bg-[#FAF5F7] transition-colors';
            document.getElementById('btn-2035').className = year === '2035' ? 'px-4 py-2 text-sm font-bold rounded bg-[#5B0F2E] text-white shadow-sm transition-colors' : 'px-4 py-2 text-sm font-bold rounded bg-white text-[#5B0F2E] border border-[#E1D2DA] hover:bg-[#FAF5F7] transition-colors';

            const data = indicationData[year];
            const labels = data.map(d => d.name);
            const revenues = data.map(d => d.rev);

            const tbody = document.getElementById('indicationTableBody');
            tbody.innerHTML = '';
            data.forEach((row, index) => {{
                const tr = document.createElement('tr');
                const riskColor = row.risk === 'Critical' ? 'text-white bg-[#9F1D35]' : (row.risk === 'High' ? 'text-[#5B0F2E] bg-[#E1D2DA]' : (row.risk === 'Moderate' ? 'text-[#431022] bg-[#C9A227]/40' : 'text-[#431022] bg-slate-100'));
                tr.innerHTML = `
                    <td class="py-4 font-bold flex items-center gap-3">
                        <span class="w-3 h-3 rounded-full inline-block shadow-sm" style="background-color: ${{chartColors[index % chartColors.length]}}"></span>
                        ${{row.name}}
                    </td>
                    <td class="py-4 text-right font-medium">$${{indicationData['2025'][index].rev.toFixed(1)}}</td>
                    <td class="py-4 text-right font-bold text-[#5B0F2E]">$${{indicationData['2035'][index].rev.toFixed(1)}}</td>
                    <td class="py-4 text-right font-bold text-[#C9A227]">${{row.cagr}}</td>
                    <td class="py-4 text-center"><span class="px-3 py-1 rounded-md text-xs font-bold ${{riskColor}}">${{row.risk}}</span></td>
                `;
                tbody.appendChild(tr);
            }});

            if (indicationChartInstance) {{
                indicationChartInstance.data.labels = labels;
                indicationChartInstance.data.datasets[0].data = revenues;
                indicationChartInstance.update();
            }} else {{
                const ctx = document.getElementById('indicationDonutChart').getContext('2d');
                indicationChartInstance = new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: labels,
                        datasets: [{{
                            data: revenues,
                            backgroundColor: chartColors,
                            borderWidth: 0,
                            hoverOffset: 4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '70%',
                        plugins: {{
                            legend: {{ display: false }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{ return ' $' + context.parsed.toFixed(1) + ' Mn'; }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}
        }}

        // 3. Competitor Bar Chart
        function initCompetitorChart() {{
            const ctx = document.getElementById('competitorChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: topPlayers,
                    datasets: [{{
                        label: '2025 Market Share (%)',
                        data: share2025,
                        backgroundColor: [colorBurgundy, colorMid, colorGold, colorSoft, '#431022', colorMuted],
                        borderRadius: 4
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{ return context.parsed.x + '% Share'; }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{ 
                            grid: {{ color: '#F0E6EA' }},
                            title: {{ display: true, text: '% Market Share' }}
                        }},
                        y: {{ 
                            grid: {{ display: false }},
                            ticks: {{ font: {{ weight: 'bold' }} }}
                        }}
                    }}
                }}
            }});
        }}

        // 4. Strategic Options Interaction
        function highlightStrategy(id) {{
            document.querySelectorAll('[id^="indicator-"]').forEach(el => el.classList.add('hidden'));
            document.getElementById(`indicator-${{id}}`).classList.remove('hidden');

            // Reset row backgrounds
            document.querySelectorAll('.strategy-row').forEach(el => el.classList.remove('bg-[#FAF5F7]'));
            document.getElementById(`indicator-${{id}}`).parentElement.parentElement.classList.add('bg-[#FAF5F7]');

            const contentDiv = document.getElementById('strategy-deep-dive');
            
            if(id === 'adj') {{
                contentDiv.className = 'bg-[#FFF9EF] border border-[#C9A227]/50 rounded-xl p-8 shadow-sm transition-all duration-300';
                contentDiv.innerHTML = `
                    <h3 class="text-2xl font-bold text-[#5B0F2E] mb-3">Recommendation: Double-Down on Adjacencies</h3>
                    <p class="text-[#4A3F44] leading-relaxed mb-6 text-lg">
                        Data suggests Emergent should fiercely avoid direct, head-to-head competition in the broad IVIG space. The required upstream plasma economics are insurmountable in the near term. Instead, Emergent is uniquely positioned to dominate the <strong>$3.3Bn to $5.0Bn Serviceable Available Market</strong> spanning hyperimmune products and government medical countermeasure (MCM) procurement.
                    </p>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                        <div class="bg-white rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm">
                            <div class="text-3xl font-extrabold text-[#C9A227] mb-2">0.52</div>
                            <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">Serviceable Base (%)</div>
                        </div>
                        <div class="bg-white rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm">
                            <div class="text-3xl font-extrabold text-[#C9A227] mb-2">$232.8 Mn</div>
                            <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">Est. 2035 Rev Potential</div>
                        </div>
                        <div class="bg-white rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm">
                            <div class="text-3xl font-extrabold text-[#C9A227] mb-2">28%</div>
                            <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">EBITDA Margin Target</div>
                        </div>
                    </div>
                `;
            }} else if (id === 'cdmo') {{
                contentDiv.className = 'bg-white border border-[#E1D2DA] rounded-xl p-8 shadow-sm transition-all duration-300';
                contentDiv.innerHTML = `
                    <h3 class="text-2xl font-bold text-[#5B0F2E] mb-3">Secondary Option: Leverage CDMO Capabilities</h3>
                    <p class="text-[#4A3F44] leading-relaxed mb-6 text-lg">
                        As a secondary pathway, Emergent can utilize its existing manufacturing and fill-finish capabilities to act as a CDMO for mid-tier challengers. This avoids the upfront plasma collection CAPEX while capturing solid margin downstream.
                    </p>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                        <div class="bg-[#FAF5F7] rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm">
                            <div class="text-3xl font-extrabold text-[#A45A7B] mb-2">0.45</div>
                            <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">Serviceable Base (%)</div>
                        </div>
                        <div class="bg-[#FAF5F7] rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm">
                            <div class="text-3xl font-extrabold text-[#A45A7B] mb-2">$99.1 Mn</div>
                            <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">Est. 2035 Rev Potential</div>
                        </div>
                        <div class="bg-[#FAF5F7] rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm">
                            <div class="text-3xl font-extrabold text-[#A45A7B] mb-2">22%</div>
                            <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">EBITDA Margin Target</div>
                        </div>
                    </div>
                `;
            }} else if (id === 'direct') {{
                contentDiv.className = 'bg-[#FAF5F7] border border-[#9F1D35]/30 rounded-xl p-8 shadow-sm transition-all duration-300';
                contentDiv.innerHTML = `
                    <h3 class="text-2xl font-bold text-[#9F1D35] mb-3">Strategic Warning: Avoid Direct Core Entry</h3>
                    <p class="text-[#4A3F44] leading-relaxed mb-6 text-lg">
                        Entering the core pooled-IVIG space directly is ill-advised. It requires scaling plasma collection centers against entrenched leaders. The capability gap is too wide, and the payback period too long for a viable ROI without a massive transformative acquisition.
                    </p>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                        <div class="bg-white rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm opacity-80">
                            <div class="text-3xl font-extrabold text-[#9F1D35] mb-2">$1.6 Bn+</div>
                            <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">Est. Base CAPEX</div>
                        </div>
                        <div class="bg-white rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm opacity-80">
                            <div class="text-3xl font-extrabold text-[#9F1D35] mb-2">Low</div>
                            <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">Strategic Fit</div>
                        </div>
                        <div class="bg-white rounded-lg p-5 border border-[#E1D2DA] text-center shadow-sm opacity-80">
                            <div class="text-3xl font-extrabold text-[#9F1D35] mb-2">Very High</div>
                            <div class="text-xs text-[#5B0F2E] uppercase font-bold tracking-wider">Execution Risk</div>
                        </div>
                    </div>
                `;
            }}
        }}
    </script>
</body>
</html>
"""

# Insert logo safely if exists
final_html = HTML_CONTENT.replace("LOGO_PLACEHOLDER", html_logo)

# Render HTML inside Streamlit container
components.html(final_html, height=1400, scrolling=True)
