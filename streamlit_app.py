import streamlit as st
import requests
import re
import time
from datetime import datetime

st.set_page_config(page_title="HFB Cyber Guard", page_icon="🔒", layout="centered")

# Your free WPScan key (from secrets or paste directly)
WPSCAN_KEY = st.secrets["wpscan_key"] if "wpscan_key" in st.secrets else "ADD_YOUR_KEY_HERE"

# Branding
st.image("https://hfbtechnologies.com/wp-content/uploads/2023/06/HFB-Logo.png", width=220)
st.markdown("<h1 style='color:#002855;text-align:center;'>HFB Technologies</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#00aeef;text-align:center;'>Cyber Guard Pro</h3>", unsafe_allow_html=True)
st.markdown("---")

if WPSCAN_KEY == "ADD_YOUR_KEY_HERE":
    st.error("⚠️ Add your free WPScan API key in Secrets (Manage app → Settings → Secrets) for real vulnerability scans!")

# Scans
def get_wpscan(url):
    if not WPSCAN_KEY or WPSCAN_KEY == "ADD_YOUR_KEY_HERE":
        return "Add key", 0
    try:
        clean = url.replace("https://", "").replace("http://", "").rstrip("/")
        headers = {"Authorization": f"Token token={WPSCAN_KEY}"}
        r = requests.get(f"https://wpscan.com/api/v3/wordpresses?url={clean}", headers=headers, timeout=30)
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
        r = requests.get(f"https://securityheaders.com/?q={url}&followRedirects=on", timeout=30)
        match = re.search(r'grade-[A-F]', r.text)
        if match:
            return match.group(0)[-1]
        return "F"
    except:
        return "Error"

def get_sucuri(url):
    try:
        r = requests.get(f"https://sitecheck.sucuri.net/results/{url}", timeout=30)
        text = r.text.lower()
        if any(word in text for word in ["malware", "blacklist", "suspicious", "spam"]):
            return "INFECTED / BLACKLISTED"
        if "no issues detected" in text or "clean" in text:
            return "Clean"
        return "Unknown"
    except:
        return "Error"

def make_pdf(url, ver, vulns, grade, sucuri):
    text = f"""
HFB Technologies Security Report
Site: {url}
Date: {datetime.now().strftime('%B %d, %Y')}

Vulnerabilities: {vulns}
Headers Grade: {grade}
Malware: {sucuri}

One-Time Fix: $3,500
Monthly Protection: $299/mo ($249 annual)

Contact HFB Technologies
    """.strip()
    return text.encode('utf-8')

st.markdown("### Scan client site")
url = st.text_input("URL", placeholder="https://example.com")

if st.button("Scan Now", type="primary") and url:
    if not url.startswith("http"):
        url = "https://" + url

    with st.spinner("Scanning..."):
        time.sleep(2)
        ver, vulns = get_wpscan(url)
        grade = get_headers_grade(url)
        sucuri = get_sucuri(url)

    st.success("Done!")
    c1, c2, c3 = st.columns(3)
    c1.metric("Vulnerabilities", vulns)
    c2.metric("Headers Grade", grade)
    c3.metric("Malware", sucuri)

    pdf = make_pdf(url, ver, vulns, grade, sucuri)
    st.download_button("Download Report", pdf, f"HFB_Report_{url.split('//')[1].split('/')[0]}.pdf", "application/pdf")
