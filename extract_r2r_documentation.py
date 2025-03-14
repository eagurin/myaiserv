#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

try:
    import html2text
except ImportError:
    html2text = None

url = "https://r2r-docs.sciphi.ai/introduction"
response = requests.get(url)
if response.status_code != 200:
    print("Failed to fetch documentation, status code:", response.status_code)
    exit(1)

html_content = response.text
soup = BeautifulSoup(html_content, "html.parser")

# Remove unnecessary elements
for tag in soup(["script", "style"]):
    tag.decompose()

# Attempt to convert HTML to Markdown if html2text is available, else fallback to plain text
if html2text:
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    markdown = converter.handle(html_content)
else:
    markdown = soup.get_text(separator="\n")

# Write the output to a markdown file in the docs directory
with open("docs/r2r_documentation.md", "w") as f:
    f.write(markdown)

print("Documentation saved to docs/r2r_documentation.md")
