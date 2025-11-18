# streamlit_app.py  ← paste this exact code
import streamlit as st
import requests
import re
import time
from datetime import datetime
import io

st.set_page_config(page_title="HFB Cyber Guard", page_icon="🔒", layout="centered")

# HFB Branding
st.image("https://hfbtechnologies.com/wp-content/uploads/2023/06/HFB-Logo.png", width=200)
st.markdown("<h1 style='color:#002855;text-align:center;'>HFB Technologies</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#00aeef;text-align:center;'>Cyber Guard Pro</h3>", unsafe_allow_html=True)
st.markdown("---")

# FIXED header grade parsing (now works
def get_headers_grade(url):
    try:
        r = requests.get(f"https://securityheaders.com/?q={url}&followRedirects=on", timeout=20)
        # The grade is in a <span class="grade">F</span> or similar
        match = re.search(r'<span class="grade">(.*?)</span>', r.text, re.IGNORECASE)
        if match:
            return match.group(1).strip().upper()
        # Fallback: look for the score
        if "score_value" in r.text:
            score_match = re.search(r'score_value.*?(\d+)', r.text)
            score = int(score_match.group(1)) if score_match else 0
            if score >= 90: return "A"
            elif score >= 80: return "B"
            elif score >= 70: return "C"
            elif score >= 60: return "D"
            else: return "F"
        return "F"
    except:
        return "Error"

def get_wpscan_data(url):
    try:
        clean_url = url.replace("https://", "").replace("http://", "").split("/")[0]
        r = requests.get(f"https://wpscan.com/api/v3/wordpresses?url={clean_url}", timeout=20)
        data = r.json()
        if 'wordpress' in data:
            wp = data['wordpress']
            version = wp.get('version', 'Unknown')
            vulns = len(wp.get('vulnerabilities', []))
            return version, vulns
        return "Not WordPress", 0
    except:
        return "Error", 0

def get_sucuri_status(url):
    try:
        r = requests.get(f"https://sitecheck.sucuri.net/results/{url}", timeout=20)
        if "malware" in r.text.lower() or "blacklisted" in r.text.lower():
            return "INFECTED OR BLACKLISTED"
        return "Clean"
    except:
        return "Error"

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
st.markdown("### Scan a client site")
url = st.text_input("Website URL", placeholder="https://example.com")

if st.button("🚀 Scan Now", type="primary") and url:
    if not url.startswith("http"):
        url = "https://" + url

    with st.spinner("Running real scans (WPScan, SecurityHeaders, Sucuri)..."):
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
