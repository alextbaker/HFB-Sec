
### Updated Script (adds full vulnerability list + fixes in the PDF)


import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="HFB Cyber Guard", page_icon="🔒", layout="centered")

WPSCAN_KEY = st.secrets["wpscan_key"]   # ← your key from Secrets

st.image("https://hfbtechnologies.com/wp-content/uploads/2023/06/HFB-Logo.png", width=220)
st.markdown("<h1 style='color:#002855;text-align:center;'>HFB Technologies</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#00aeef;text-align:center;'>Cyber Guard Pro</h3>", unsafe_allow_html=True)
st.markdown("---")

def get_full_wpscan(url):
    try:
        clean = url.replace("https://", "").replace("http://", "").split("/")[0]
        headers = {"Authorization": f"Token token={WPSCAN_KEY}"}
        r = requests.get(f"https://wpscan.com/api/v3/wordpresses?url={clean}", headers=headers, timeout=30)
        data = r.json()
        if 'wordpress' in data:
            wp = data['wordpress']
            version = wp.get('version', 'Unknown')
            vulns = wp.get('vulnerabilities', [])
            return version, vulns
        return "Not WordPress", []
    except:
        return "Error", []

def get_headers_grade(url):
    try:
        r = requests.get(f"https://securityheaders.com/?q={url}&followRedirects=on", timeout=30)
        match = re.search(r'grade-[A-F]', r.text)
        return match.group(0)[-1] if match else "F"
    except:
        return "Error"

def get_sucuri(url):
    try:
        r = requests.get(f"https://sitecheck.sucuri.net/results/{url}", timeout=30)
        text = r.text.lower()
        if any(word in text for word in ["malware", "blacklist", "suspicious"]):
            return "INFECTED / BLACKLISTED"
        return "Clean"
    except:
        return "Error"

def make_detailed_pdf(url, version, vulns_list, grade, sucuri):
    lines = [
        "HFB Technologies – Detailed Security Report",
        "="*60,
        f"Site: {url}",
        f"Date: {datetime.now().strftime('%B %d, %Y')}",
        "",
        f"WordPress Version: {version}",
        f"Security Headers Grade: {grade}",
        f"Malware Status: {sucuri}",
        "",
        f"KNOWN VULNERABILITIES ({len(vulns_list)} found)",
        "-"*60
    ]
    for v in vulns_list[:20]:  # limit to 20 for PDF size
        title = v.get('title', 'Unknown vulnerability')
        fix = v.get('fixed_in', 'Update required')
        lines.append(f"• {title}")
        lines.append(f"  Fix: Update to version {fix} or higher")
        lines.append("")

    lines += [
        "RECOMMENDED ACTION",
        "-"*60,
        "One-Time Full Fix + Clean Report: $3,500",
        "Monthly Unlimited Protection: $299/mo or $249/mo annual",
        "",
        "Contact HFB Technologies today",
        "="*60
    ]
    return "\n".join(lines).encode('utf-8')

st.markdown("### Client Security Scan")
url = st.text_input("Website URL", placeholder="https://client.com")

if st.button("Scan Now", type="primary") and url:
    if not url.startswith("http"):
        url = "https://" + url

    with st.spinner("Running full vulnerability scan..."):
        version, vulns_list = get_full_wpscan(url)
        grade = get_headers_grade(url)
        sucuri = get_sucuri(url)

    st.success("Scan complete!")
    st.metric("Known Vulnerabilities", len(vulns_list), delta=len(vulns_list) if len(vulns_list) > 0 else None)
    st.metric("Headers Grade", grade)
    st.metric("Malware Status", sucuri)

    if vulns_list:
        st.subheader("Vulnerabilities Found")
        for v in vulns_list[:15]:
            title = v.get('title', 'Unknown')
            fix = v.get('fixed_in', 'Update required')
            st.write(f"• **{title}** → Fix: Update to {fix} or higher")

    pdf = make_detailed_pdf(url, version, vulns_list, grade, sucuri)
    st.download_button(
        "📥 Download Detailed HFB Report",
        data=pdf,
        file_name=f"HFB_Detailed_Report_{url.split('//')[1].split('/')[0]}.pdf",
        mime="application/pdf"
    )
