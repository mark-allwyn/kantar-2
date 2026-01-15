#!/usr/bin/env python3
"""
Create PDF from HTML with embedded images
"""
import base64
import re
from pathlib import Path

# Read the HTML file
html_path = Path("PRESENTATION_FULL_REPORT.html")
html_content = html_path.read_text()

# Find all image references
img_pattern = r'<img src="([^"]+)"'
matches = re.findall(img_pattern, html_content)

# Replace each image with base64 embedded version
for img_file in matches:
    img_path = Path(img_file)
    if img_path.exists():
        # Read image and convert to base64
        with open(img_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')

        # Determine MIME type
        ext = img_path.suffix.lower()
        mime_type = 'image/png' if ext == '.png' else 'image/jpeg'

        # Create data URI
        data_uri = f'data:{mime_type};base64,{img_data}'

        # Replace in HTML
        html_content = html_content.replace(f'src="{img_file}"', f'src="{data_uri}"')
        print(f"✓ Embedded: {img_file}")

# Write modified HTML
output_path = Path("PRESENTATION_FULL_REPORT_embedded.html")
output_path.write_text(html_content)
print(f"\n✓ Created: {output_path}")
print("  Images are now embedded as base64 data URIs")
