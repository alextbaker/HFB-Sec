# hfb_cyber_guard_pro_branding_fixed.py
# Install: pip install streamlit reportlab requests pandas pillow
# Run: streamlit run hfb_cyber_guard_pro_branding_fixed.py

import streamlit as st
import requests
import time
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io

# ================= HFB TECHNOLOGIES EXACT BRANDING =================
AGENCY_NAME = "HFB Technologies"
AGENCY_LOGO = "https://hfbtechnologies.com/wp-content/uploads/2023/06/HFB-Logo.png"
PRIMARY_COLOR = "#002855"   # Deep navy from your site
ACCENT_COLOR = "#00aeef"    # Bright blue accent/buttons

st.set_page_config(page_title="HFB Cyber Guard", page_icon="🔒", layout="centered")

# Custom CSS to match your site exactly
st.markdown(f"""
<style>
    .report-section {{ background-color: #f8f9fa; padding: 20px; border-radius: 10px; }}
    .stButton>button {{ background-color: {ACCENT_COLOR}; color: white; }}
    .stButton> Tropical: {ACCENT_COLOR}; color: white; }}
    h1, h2, h3 {{ color: {PRIMARY_COLOR}; }}
</style>
""", unsafe_allow_html=True)

# Header with logo
col1, col2 = st.columns([1, 5])
with col1:
    try:
        st.image(AGENCY_LOGO, width=160)
    except:
        st.markdown(f"<h1 style='color:{PRIMARY_COLOR};'>HFB</h1>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<h1 style='color:{PRIMARY_COLOR};'>{AGENCY_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{ACCENT_COLOR};'>Cyberengineered Cyber Guard Pro</h3>", unsafe_allow_html=True)
    st.markdown("**Security & Compliance Auditing for Your Clients**")

st.markdown("---")

# Rest of the scan functions (same as before - unchanged for performance)
@st.cache_data(ttl=3600)
def scan_wpscan(url):
    try:
        r = requests.get(f"https://wpscan.com/api/v3/wordpresses?url={url}", timeout=20)
        data = r.json()
        if 'wordpress' in data:
            wp = data['wordpress']
            version = wp.get('version', 'Unknown')
            vulns = len(wp.get('vulnerabilities', []))
            return version, vulns, wp.get('vulnerabilities', [])
        return "Not detected", 0, []
    except:
        return "Error", 0, []

@st.cache_data(ttl=3600)
def scan_headers(url):
    try:
        r = requests.get(f"https://securityheaders.com/?q={url}&followRedirects=on", timeout=15)
        text = r.text
        if "A+" in text or "A-" in text: return "A", "Excellent"
        if "B" in text: return "B", "Good"
        if "C" in text: return "C", "Fair"
        if "D" in text: return "D", "Needs Work"
        return "F", "Critical Issues"
    except:
        return "Error", "Failed"

@st.cache_data(ttl=3600)
def scan_sucuri(url):
    try:
        r = requests.get(f"https://sitecheck.sucuri.net/results/{url}", timeout=15)
        if "malware" in r.text.lower() or "blacklist" in r.text.lower():
            return "🚨 INFECTED OR BLACKLISTED"
        return "✅ Clean"
    except:
        return "⚠️ Scan error"

# PDF with exact HFB colors
def generate_hfb_pdf(url, wp_version, wp_vulns, vulns_list, headers_grade, sucuri_status):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=100)
    styles = getSampleStyleSheet()
    story = []

    # Logo at top
    try:
        img = ImageReader(AGENCY_LOGO)
        logo = RLImage(img, width=200, height=80)
        logo.hAlign = 'CENTER'
        story.append(logo)
    except:
        pass
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<font size=22 color='{PRIMARY_COLOR}'><b>WEBSITE SECURITY & COMPLIANCE REPORT</b></font>", styles['Title']))
    story.append(Paragraph(f"<font size=14>{url}</font>", styles['Heading2']))
    story.append(Paragraph(f"Prepared by <b>HFB Technologies</b> • {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))

    # Summary table with HFB colors
    data = [
        ["Assessment", "Result", "Risk Level"],
        ["Known Vulnerabilities", f"{wp_vulns} exploits found", "CRITICAL" if wp_vulns > 0 else "Low"],
        ["Security Headers", headers_grade, "HIGH" if headers_grade in ['F','D','C'] else "Low"],
        ["Malware Status", sucuri_status.replace("🚨 ","").replace("✅ ",""), "CRITICAL" if "INFECTED" in sucuri_status else "Clean"],
    ]
    table = Table(data, colWidths=[220, 160, 110])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(PRIMARY_COLOR)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1.5, colors HexColor("#002855")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f5f8ff"))
    ]))
    story.append(table)
    story.append(Spacer(1, 40))

    # Call to action in accent color
    story.append(Paragraph(f"<font color='{ACCENT_COLOR}' size=16><b>Next Steps – Get Compliant Today</b></font>", styles['Heading2']))
    story.append(Paragraph(
        "• <b>One-Time Fix + Clean Report:</b> $3,500<br/>"
        "• <b>Monthly Protection Plan:</b> $299/mo or $249/mo annual<br/>"
        "<i>Contact HFB Technologies to secure your site and stay Stripe/insurance compliant.</i>",
        styles['Normal']
    ))

    doc.build(story)
    return buffer.getvalue()

# UI (same powerful functionality)
st.markdown("### Scan client websites instantly")
option = st.radio("Input", ["Single site", "Upload list (CSV/TXT)"], horizontal=True)

urls = []
if option == "Single site":
    url = st.text_input("Website URL", placeholder="https://client.com")
    if st.button("🚀 Scan Now", type="primary") and url:
        urls = [url]
else:
    uploaded = st.file_uploader("Upload file – one URL per line", type=["csv", "txt"])
    if uploaded and st.button("🚀 Scan All", type="primary"):
        text = uploaded.read().decode()
        urls = [u.strip() for u in text.splitlines() if u.strip() and "http" in u]

if urls:
    for url in urls:
        if not url.startswith("http"):
            url = "https://" + url
        with st.spinner(f"Analyzing {url}..."):
            time.sleep(1)
            wp_version, wp_vulns, _ = scan_wpscan(url)
            headers_grade, _ = scan_headers(url)
            sucuri_status = scan_sucuri(url)

        st.success(f"Complete: {url}")
        c1, c2, c3 = st.columns([2,2,2])
        with c1:
            st.metric("Vulnerabilities Found", wp_vulns, delta=wp_vulns if wp_vulns > 0 else None)
            st.metric("Headers Grade", headers_grade)
        with c2:
            st.write(f"**Malware:** {sucuri_status}")
        with c3:
            pdf = generate_hfb_pdf(url, wp_version, wp_vulns, [], headers_grade, sucuri_status)
            st.download_button(
                "📥 Download HFB Report",
                data=pdf,
                file_name=f"HFB_Security_Report_{url.split('//')[1].split('/')[0]}.pdf",
                mime="application/pdf",
                key=url
            )
        st.markdown("---")
