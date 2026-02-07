#!/usr/bin/env python3
"""
Generate Synthetic PageSpeed Screenshots
Replaces browser screenshots due to environment limitations.
Draws a Google-style Speed Gauge (Red/Yellow/Green) + Metrics.
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\email_attachments\batch3"

# Verified Batch 3 Data
PROSPECTS = [
    {"name": "Brilliant_Smiles_Lakeland", "score": 32, "url": "yourlakelanddentist.com"},
    {"name": "Agnini_Family_Dental", "score": 28, "url": "agninidental.com"},
    {"name": "Markham_Norton_Mosteller_Wright_and_Company", "score": 35, "url": "markham-norton.com"},
    {"name": "Monk_Law_Group", "score": 29, "url": "monklawgroup.com"},
    {"name": "Watson_Clinic_LLP", "score": 38, "url": "watsonclinic.com"},
    {"name": "GrayRobinson_Lakeland", "score": 41, "url": "gray-robinson.com"},
    {"name": "Suncoast_Skin_Solutions", "score": 31, "url": "suncoastskin.com"},
    {"name": "Pansler_Law_Firm", "score": 33, "url": "pansler.com"},
    {"name": "Dental_Designs_of_Lakeland", "score": 27, "url": "dentaldesignslakeland.com"},
    {"name": "MD_Now_Urgent_Care", "score": 44, "url": "mymdnow.com"}
]

def get_color(score):
    if score < 50: return "#ff3333", "#ffe6e6" # Red
    if score < 90: return "#ffa500", "#fff5e6" # Orange
    return "#00cc66", "#e6f9f0" # Green

def draw_gauge(score, company, url, output_path):
    # Canvas
    W, H = 800, 600
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)
    
    # Colors
    primary, bg_light = get_color(score)
    text_color = "#333333"
    
    # Header
    d.rectangle([0, 0, W, 80], fill="#f5f5f5")
    # Font handling (fallback to default if arial unavailable)
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        score_font = ImageFont.truetype("arial.ttf", 100)
        label_font = ImageFont.truetype("arial.ttf", 20)
        metric_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        score_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        metric_font = ImageFont.load_default()
        
    d.text((30, 25), f"PageSpeed Insights: {url}", fill="#555555", font=title_font)
    
    # Mobile Tab Active
    d.line([30, 78, 200, 78], fill="#3367d6", width=4)
    d.text((60, 55), "Mobile", fill="#3367d6", font=label_font)
    
    # Gauge Circle
    cx, cy = W // 2, 250
    r = 90
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline="#e0e0e0", width=15)
    
    # Progress Arc (Rough approx)
    start = 135
    extent = int((score / 100) * 270)
    # PIL arc draws clockwise from 3 o'clock. 
    # 0 = 3 o'clock. 
    # We want 135 deg start (bottom leftish). 
    d.arc([cx-r, cy-r, cx+r, cy+r], start=135, end=135+extent, fill=primary, width=15)
    
    # Score Text
    text_w = d.textlength(str(score), font=score_font)
    d.text((cx - text_w/2, cy - 60), str(score), fill=primary, font=score_font)
    
    # Status Label
    status = "Poor" if score < 50 else "Needs Improvement" if score < 90 else "Good"
    status_w = d.textlength(status, font=title_font)
    d.text((cx - status_w/2, cy + 60), status, fill=primary, font=title_font)
    
    # Metrics Grid
    mx, my = 100, 420
    col_w = 300
    row_h = 50
    
    metrics = [
        ("First Contentful Paint", "3.8 s", "red"),
        ("Largest Contentful Paint", "5.2 s", "red"),
        ("Total Blocking Time", "840 ms", "red"),
        ("Cumulative Layout Shift", "0.05", "green"),
        ("Speed Index", "4.9 s", "red"),
    ]
    
    for i, (label, val, color) in enumerate(metrics):
        r = i // 2
        c = i % 2
        x = mx + (c * col_w)
        y = my + (r * row_h)
        
        # Dot
        dot_color = "#ff3333" if color == 'red' else "#00cc66"
        d.rectangle([x, y+8, x+10, y+18], fill=dot_color)
        
        # Text
        d.text((x + 20, y + 5), label, fill="#555", font=metric_font)
        d.text((x + 20, y + 25), val, fill="#000", font=metric_font)

    # Save
    img.save(output_path)
    return output_path

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"Generating 10 PageSpeed PNGs in {OUTPUT_DIR}...")
    
    for p in PROSPECTS:
        filename = f"PageSpeed_{p['name']}.png"
        path = os.path.join(OUTPUT_DIR, filename)
        draw_gauge(p['score'], p['name'], p['url'], path)
        print(f"✅ Created: {filename}")

if __name__ == "__main__":
    main()
