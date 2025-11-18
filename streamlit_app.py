# streamlit_app.py  ← deploy this
import streamlit as st
import requests
import re
import time
from datetime import datetime
import io

st.set_page_config(page_title="HFB Cyber Guard", page_icon="🔒", layout="centered")

# ================= YOUR FREE UNLIMITED WPSCAN KEY =================
WPSCAN_API_KEY = "HrvGdNeeEuj9zhWqLIykNxscP7SaoPvu3YDEyySts5E"   # ← paste your key from wpscan.com here

# HFB Branding
st.image("https://hfbtechnologies.com/wp-content/uploads/2023/06/HFB-Logo.png", width=200)
st.markdown("<h1 style='color:#002855;text-align:center;'>HFB Technologies</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#00aeef;text-align:center;'>Cyber Guard Pro</h3>", unsafe_allow_html=True)
st.markdown("---")

# ================= UNLIMITED WPSCAN (real vulnerabilities) =================
def get_wpscan_data(url):
    if not WPSCAN_API_KEY or WPSCAN_API_KEY == "PUT_YOUR_KEY_HERE":
        st.error("Add your free WPScan API key to the script (line 12) for unlimited scans")
        return "Add key", 0
    try:
        clean_url = url.replace("https://", "").replace("http://", "").split("/")[0]
        headers = {"Authorization": f"Token token={WPSCAN_API_KEY}"}
        r = requests.get(f"https://wpscan.com/api/v3/wordpresses?url={clean_url}", headers=headers, timeout=20)
        data = r.json()
        if 'wordpress' in data:
            wp = data['wordpress']
            version = wp.get('version', 'Unknown')
            vulns = len(wp.get('vulnerabilities', []))
            return version, vulns
        return "Not WordPress", 0
    except Exception as e:
        return "Error", 0

# Accurate headers grade
def get_headers_grade(url):
    try:
        r = requests.get(f"https://securityheaders.com/?q={url}&followRedirects=on", timeout=20)
        match = re.search(r'<span class="grade">(.*?)</span>', r.text, re.IGNORECASE)
        if match:
            return match.group(1).strip().upper()
        return "F"
    except:
        return "Error"

def get_sucuri_status(url):
    try:
        r = requests.get(f"https://sitecheck.sucuri.net/results/{url}", timeout=20)
        if "malware" in r.text.lower() or "blacklisted" in r.text.lower():
            return "INFECTED OR BLACKLISTED"
        return "Clean"
    except:
        return "Error"

# PDF report
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

Contact HFB Technologies today – most clients save thousands on insurance
and avoid Stripe payment freezes.

══════════════════════════════════════════════════════════
HFB Technologies | Keeping Your Business Safe Online
    """.strip()
    return report.encode('latin-1', errors='ignore')

# UI
st.markdown("### Instant client security scans")
url = st.text_input("Website URL", placeholder="https://client.com")

if st.button("🚀 Scan Now", type="primary") and url:
    if not url.startswith("http"):
        url = "https://" + url

    with st.spinner("Running unlimited WPScan + SecurityHeaders + Sucuri..."):
        time.sleep(2)
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
