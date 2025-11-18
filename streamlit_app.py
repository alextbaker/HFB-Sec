import streamlit as st
import requests
import re
import time
from datetime import datetime

st.set_page_config(page_title="HFB Cyber Guard", page_icon="🔒", layout="centered")

# === PUT YOUR FREE WPSCAN KEY HERE (from wpscan.com) ===
WPSCAN_KEY = st.secrets.get("wpscan_key", "PUT_YOUR_KEY_HERE")  # or just paste it directly below

# HFB Branding
st.image("https://hfbtechnologies.com/wp-content/uploads/2023/06/HFB-Logo.png", width=220)
st.markdown("<h1 style='color:#002855;text-align:center;'>HFB Technologies</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#00aeef;text-align:center;'>Cyber Guard Pro</h3>", unsafe_allow_html=True)
st.markdown("---")

# === REAL SCANS ===
def get_wpscan(url):
    try:
        clean = url.replace("https://", "").replace("http://", "").split("/")[0]
        headers = {"Authorization": f"Token token={WPSCAN_KEY}"}
        r = requests.get(f"https://wpscan.com/api/v3/wordpresses?url={clean}", headers=headers, timeout=25)
        data = r.json()
        if 'wordpress' in data:
            vulns = len(data['wordpress'].get('vulnerabilities', []))
            ver = data['wordpress'].get('version', 'Unknown')
            return ver, vulns
        return "Not WP", 0
    except:
        return "Error", 0

def get_headers_grade(url):
    try:
        r = requests.get(f"https://securityheaders.com/?q={url}&followRedirects=on", timeout=25)
        match = re.search(r'<span class="grade">([A-F])[\+\-]?', r.text)
        return match.group(1) if match else "F"
    except:
        return "Error"

def get_sucuri(url):
    try:
        r = requests.get(f"https://sitecheck.sucuri.net/results/{url}", timeout=25)
        if any(x in r.text.lower() for x in ["malware", "blacklist", "spam", "suspicious"]):
            return "INFECTED / BLACKLISTED"
        return "Clean"
    except:
        return "Error"

def make_pdf(url, ver, vulns, grade, sucuri):
    text = f"""
HFB Technologies – Website Security Report
══════════════════════════════════════════════════════════
Site: {url}
Date: {datetime.now().strftime('%B %d, %Y')}

SECURITY SUMMARY
──────────────────────────────────────────────────────────
WordPress Version:               {ver}
Known Vulnerabilities:           {vulns} active exploits
Security Headers Grade:          {grade} (F = critical missing protections)
Malware / Blacklist Status:      {sucuri}

RECOMMENDED ACTION
──────────────────────────────────────────────────────────
One-Time Full Fix + Clean Report:        $3,500
Monthly Unlimited Protection:            $299/mo or $249/mo (annual)

Contact HFB Technologies today – avoid hacks, Stripe freezes, and insurance denials.

══════════════════════════════════════════════════════════
HFB Technologies | Keeping Your Business Safe Online
    """.strip()
    return text.encode('utf-8')

# UI
st.markdown("### Instant client security scan")
url = st.text_input("Website URL", placeholder="https://client.com")

if st.button("🚀 Scan Now", type="primary") and url:
    if not url.startswith("http"):
        url = "https://" + url

    with st.spinner("Running real scans..."):
        time.sleep(2)
        ver, vulns = get_wpscan(url)
        grade = get_headers_grade(url)
        sucuri = get_sucuri(url)

    st.success("Scan complete!")

    c1, c2, c3 = st.columns(3)
    c1.metric("Vulnerabilities", vulns, delta=vulns if vulns > 0 else None)
    c2.metric("Headers Grade", grade)
    c3.metric("Malware", sucuri)

    pdf = make_pdf(url, ver, vulns, grade, sucuri)
    st.download_button(
        "📥 Download HFB Security Report",
        data=pdf,
        file_name=f"HFB_Security_Report_{url.split('//')[1].split('/')[0]}.pdf",
        mime="application/pdf"
    )
