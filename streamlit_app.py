# streamlit_app.py   ← name the file exactly this
# Deploy this to Streamlit Cloud – it will work instantly

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

# ================= HFB TECHNOLOGIES BRANDING =================
AGENCY_NAME = "HFB Technologies"
AGENCY_LOGO = "https://hfbtechnologies.com/wp-content/uploads/2023/06/HFB-Logo.png"
PRIMARY_COLOR = "#002855"   # Deep navy
ACCENT_COLOR = "#00aeef"    # Bright blue

st.set_page_config(page_title="HFB Cyber Guard", page_icon="🔒", layout="centered")

# Custom CSS
st.markdown(f"""
<style>
    .stButton>button {{ background-color: {ACCENT_COLOR}; color: white; border: none; }}
    h1, h2, h3 {{ color: {PRIMARY_COLOR}; }}
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([1, 5])
with col1:
    try:
        st.image(AGENCY_LOGO, width=160)
    except:
        st.write("🔒")
with col2:
    st.markdown(f"<h1 style='color:{PRIMARY_COLOR};'>{AGENCY_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{ACCENT_COLOR};'>Cyber Guard Pro – Security & Compliance Auditor</h3>", unsafe_allow_html=True)

st.markdown("---")

# ================= SCAN FUNCTIONS =================
@st.cache_data(ttl=3600)
def scan_wpscan(url):
    try:
        r = requests.get(f"https://wpscan.com/api/v3/wordpresses?url={url}", timeout=20)
        data = r.json()
        if 'wordpress' in data:
            wp = data['wordpress']
            version = wp.get('version', 'Unknown')
            vulns = len(wp.get('vulnerabilities', []))
            return version, vulns
        return "Not WordPress", 0
    except:
        return "Error", 0

@st.cache_data(ttl=3600)
def scan_headers(url):
    try:
        r = requests.get(f"https://securityheaders.com/?q={url}&followRedirects=on", timeout=15)
        text = r.text
        if "A+" in text or "A-" in text: return "A"
        if "B" in text: return "B"
        if "C" in text: return "C"
        if "D" in text: return "D"
        return "F"
    except:
        return "Error"

@st.cache_data(ttl=3600)
def scan_sucuri(url):
    try:
        r = requests.get(f"https://sitecheck.sucuri.net/results/{url}", timeout=15)
        if "malware" in r.text.lower() or "blacklist" in r.text.lower():
            return "🚨 INFECTED"
        return "✅ Clean"
    except:
        return "⚠️ Error"

# ================= PDF GENERATOR (fixed line 119) =================
def generate_pdf(url, wp_version, wp_vulns, headers_grade, sucuri_status):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=100)
    styles = getSampleStyleSheet()
    story = []

    # Logo
    try:
        img = ImageReader(AGENCY_LOGO)
        logo = RLImage(img, width=220, height=90)
        logo.hAlign = 'CENTER'
        story.append(logo)
    except:
        pass
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<font size=22 color='{PRIMARY_COLOR}'><b>WEBSITE SECURITY & COMPLIANCE REPORT</b></font>", styles['Title']))
    story.append(Paragraph(f"<font size=14>{url}</font>", styles['Heading2']))
    story.append(Paragraph(f"Prepared by <b>{AGENCY_NAME}</b> • {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))

    # Summary table – FIXED LINE HERE
    data = [
        ["Assessment", "Result", "Risk"],
        ["Known Vulnerabilities", f"{wp_vulns} exploits", "CRITICAL" if wp_vulns > 0 else "Low"],
        ["Security Headers Grade", headers_grade, "HIGH" if headers_grade in ["F","D","C"] else "Low"],
        ["Malware / Blacklist", sucuri_status.replace("🚨 ","").replace("✅ ",""), "CRITICAL" if "INFECTED" in sucuri_status else "Clean"],
    ]
    table = Table(data, colWidths=[220, 160, 110])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(PRIMARY_COLOR)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1.5, colors.HexColor("#002855")),  # ← fixed comma + dot
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f5f8ff")),
    ]))
    story.append(table)
    story.append(Spacer(1, 40))

    # Call to action
    story.append(Paragraph(f"<font color='{ACCENT_COLOR}' size=16><b>Next Steps</b></font>", styles['Heading2']))
    story.append(Paragraph(
        "• One-Time Compliance Fix + Clean Report: <b>$3,500</b><br/>"
        "• Monthly Unlimited Protection: <b>$299/mo</b> or <b>$249/mo annual</b>",
        styles['Normal']
    ))

    doc.build(story)
    return buffer.getvalue()

# ================= UI =================
st.markdown("### Scan client sites")
option = st.radio("Input", ["Single URL", "Upload list"], horizontal=True)

urls = []
if option == "Single URL":
    url = st.text_input("Website", placeholder="https://client.com")
    if st.button("🚀 Scan Now", type="primary") and url:
        urls = [url]
else:
    uploaded = st.file_uploader("Upload CSV/TXT – one URL per line", type=["csv", "txt"])
    if uploaded and st.button("🚀 Scan All", type="primary"):
        text = uploaded.read().decode()
        urls = [u.strip() for u in text.splitlines() if u.strip() and u.startswith("http")]

if urls:
    for url in urls:
        if not url.startswith("http"):
            url = "https://" + url
        with st.spinner(f"Scanning {url}..."):
            time.sleep(1)
            wp_version, wp_vulns = scan_wpscan(url)
            headers_grade = scan_headers(url)
            sucuri_status = scan_sucuri(url)

        st.success(f"{url}")
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            st.metric("Vulnerabilities", wp_vulns)
            st.metric("Headers Grade", headers_grade)
        with c2:
            st.write(f"**Malware:** {sucuri_status}")
        with c3:
            pdf = generate_pdf(url, wp_version, wp_vulns, headers_grade, sucuri_status)
            st.download_button(
                "📥 Download Report",
                data=pdf,
                file_name=f"HFB_Security_Report_{url.split('//')[1].split('/')[0]}.pdf",
                mime="application/pdf",
                key=url
            )
        st.markdown("---")
