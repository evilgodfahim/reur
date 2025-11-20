import sys
import os
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

HTML_FILE = "opinion.html"
XML_FILE = "articles.xml"

# Load HTML
if not os.path.exists(HTML_FILE):
    print("HTML not found")
    sys.exit(1)

with open(HTML_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# Parse article entries
articles = []

# Pattern: <a href="..."> around each article card/lead/list-block
for a in soup.select("a[href*='/opinion/article/']"):
    url = a.get("href")

    # Title extraction
    h1 = a.select_one("h1")
    h3 = a.select_one("h3")
    title = None
    if h1:
        title = h1.get_text(strip=True)
    elif h3:
        title = h3.get_text(strip=True)
    else:
        continue

    # Description
    desc_tag = a.select_one("p")
    desc = desc_tag.get_text(strip=True) if desc_tag else ""

    # Publish time
    pub = ""
    t = a.select_one(".publishTime")
    if t:
        pub = t.get_text(strip=True)

    # Image
    img = ""
    img_tag = a.select_one("img")
    if img_tag:
        img = img_tag.get("src", "")

    articles.append({
        "url": url,
        "title": title,
        "desc": desc,
        "pub": pub,
        "img": img
    })

# Load previous XML or create new
if os.path.exists(XML_FILE):
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
else:
    root = ET.Element("articles")

# Collect existing URLs
existing = set()
for item in root.findall("item"):
    u = item.find("url")
    if u is not None:
        existing.add(u.text.strip())

# Append new unique articles
for art in articles:
    if art["url"] in existing:
        continue

    item = ET.SubElement(root, "item")

    e_url = ET.SubElement(item, "url")
    e_url.text = art["url"]

    e_title = ET.SubElement(item, "title")
    e_title.text = art["title"]

    e_desc = ET.SubElement(item, "description")
    e_desc.text = art["desc"]

    e_pub = ET.SubElement(item, "publishTime")
    e_pub.text = art["pub"]

    e_img = ET.SubElement(item, "image")
    e_img.text = art["img"]

# Trim to last 500
items = root.findall("item")
if len(items) > 500:
    for extra in items[:-500]:
        root.remove(extra)

# Save XML
tree = ET.ElementTree(root)
tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)