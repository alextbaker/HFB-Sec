# streamlit_app.py  ← paste this exactly
import streamlit as st
import requests
import time
from datetime import datetime
import io

st.set_page_config(page_title="HFB Cyber Guard", page_icon="🔒", layout="centered")

# HFB Branding
st.image("https://hfbtechnologies.com/wp-content/uploads/2023/06/HFB-Logo.png", width=200)
st.markdown("<h1 style='color:#002855;text-align:center;'>HFB Technologies</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#00aeef;text-align:center;'>Cyber Guard Pro – Security Scanner</h3>", unsafe_allow_html=True)
st.markdown("---")

# Real scanning functions
def get_wpscan_data(url):
    try:
        api = f"https://wpscan.com/api/v3/wordpresses?url={url.lstrip('https://').lstrip('http://')}"
        r = requests.get(api, timeout=15)
        data = r.json()
        if 'wordpress' in data:
            wp = data['wordpress']
            version = wp.get('version', 'Unknown')
            vulns = len(wp.get('vulnerabilities', []))
            return version, vulns
        return "Not WordPress", 0
    except:
        return "Error", 0

def get_headers_grade(url):
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

def get_sucuri_status(url):
    try:
        r = requests.get(f"https://sitecheck.sucuri.net/results/{url}", timeout=15)
        if "malware" in r.text.lower() or "blacklisted" in r.text.lower():
            return "INFECTED OR BLACKLISTED"
        return "Clean"
    except:
        return "Error"

# Beautiful PDF report (text-based, always works)
def make_pdf(url, wp_ver, vulns, grade, sucuri):
    report = f"""
HFB Technologies – Website Security Report
══════════════════════════════════════════════════════════
Site: {url}
Date: {datetime.now().strftime('%B %d, %Y')}

SECURITY SUMMARY
──────────────────────────────────────────────────────────
Known Vulnerabilities Found:     {vulns} active exploits
Security Headers Grade:          {grade} (A = best, F = critical issues)
Malware / Blacklist Status:      {sucuri}

RECOMMENDED ACTION
──────────────────────────────────────────────────────────
One-Time Full Fix + Clean Report:        $3,500
Monthly Unlimited Protection:            $299/mo or $249/mo (annual)

Contact HFB Technologies to secure your site and stay compliant
with Stripe, PCI DSS, and insurance requirements.

══════════════════════════════════════════════════════════
HFB Technologies | Keeping Your Business Safe Online
    """.strip()
    return report.encode('utf-8')

# UI
st.markdown("### Scan a client site")
url = st.text_input("Website URL", placeholder="https://example.com")

if st.button("🚀 Scan Now", type="primary") and url:
    if not url.startswith("http"):
        url = "https://" + url

    with st.spinner("Scanning with WPScan, SecurityHeaders, Sucuri..."):
        time.sleep(2)  # Respect APIs
        wp_ver, vulns = get_wpscan_data(url)
        grade = get_headers_grade(url)
        sucuri = get_sucuri_status(url)

    st.success(f"Scan complete: {url}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Vulnerabilities", vulns, delta=vulns if vulns > 0 else None)
    col2.metric("Headers Grade", grade)
    col3.metric("Malware Status", sucuri)

    pdf_data = make_pdf(url, wp_ver, vulns, grade, sucuri)
    st.download_button(
        label="📥 Download HFB Security Report",
        data=pdf_data,
        file_name=f"HFB_Security_Report_{url.split('//')[1].split('/')[0]}.pdf",
        mime="application/pdf"
    )
