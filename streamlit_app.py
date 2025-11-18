# streamlit_app.py
import streamlit as st
import requests
import time
from datetime import datetime
import io

# ================= HFB TECHNOLOGIES BRANDING =================
AGENCY_NAME = "HFB Technologies"
AGENCY_LOGO = "https://hfbtechnologies.com/wp-content/uploads/2023/06/HFB-Logo.png"
PRIMARY_COLOR = "#002855"
ACCENT_COLOR = "#00aeef"

st.set_page_config(page_title="HFB Cyber Guard", page_icon="🔒", layout="centered")

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
        st.write("HFB")
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
            return "INFECTED OR BLACKLISTED"
        return "Clean"
    except:
        return "Error"

# ================= SIMPLE TEXT-BASED PDF (no ReportLab needed) =================
def generate_pdf_text(url, wp_version, wp_vulns, headers_grade, sucuri_status):
    pdf_text = f"""
HFB Technologies – Website Security & Compliance Report
===================================================================
Site: {url}
Date: {datetime.now().strftime('%B %d, %Y')}

SUMMARY
───────────────────────────────────────────────────────────────────
Known Vulnerabilities:       {wp_vulns} active exploits
Security Headers Grade:      {headers_grade}/A
Malware / Blacklist Status:  {sucuri_status}

RECOMMENDED ACTION
───────────────────────────────────────────────────────────────────
One-Time Compliance Fix + Clean Report:          $3,500
Monthly Unlimited Protection (most popular):     $299/mo or $249/mo (billed annually)

Contact HFB Technologies today to secure your site and stay compliant
with Stripe, insurance providers, and PCI DSS requirements.

===================================================================
Prepared by HFB Technologies
    """
    return pdf_text.encode('utf-8')

# ================= UI =================
st.markdown("### Instant client security scans")
option = st.radio("Input", ["Single URL", "Upload list (CSV/TXT)"], horizontal=True)

urls = []
if option == "Single URL":
    url = st.text_input("Website", placeholder="https://client.com")
    if st.button("Scan Now", type="primary") and url:
        urls = [url]
else:
    uploaded = st.file_uploader("Upload CSV/TXT – one URL per line", type=["csv", "txt"])
    if uploaded and st.button("Scan All", type="primary"):
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
            pdf_bytes = generate_pdf_text(url, wp_version, wp_vulns, headers_grade, sucuri_status)
            st.download_button(
                "Download Report",
                data=pdf_bytes,
                file_name=f"HFB_Security_Report_{url.split('//')[1].split('/')[0]}.pdf",
                mime="application/pdf",
                key=url
            )
        st.markdown("---")
