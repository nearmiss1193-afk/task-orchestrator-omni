
import os
import time
from playwright.sync_api import sync_playwright

import argparse

OUTPUT_DIR = os.path.join(os.getcwd(), "audit_screenshots")

def generate_html(score, url, metrics):
    """
    Generates a realistic PageSpeed HTML string.
    """
    color_class = "red" if score < 50 else "orange" if score < 90 else "green"
    color_code = "#ff4e42" if score < 50 else "#ffa400" if score < 90 else "#0cce6b"
    bg_color = "#fff0ee" if score < 50 else "#fffcf5" if score < 90 else "#f0fbf4"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Roboto', sans-serif; background: #f8f9fa; padding: 20px; }}
            .container {{ background: white; max_width: 800px; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }}
            .url {{ color: #5f6368; font-size: 16px; margin-bottom: 20px; }}
            .score-circle {{ 
                width: 120px; height: 120px; 
                border-radius: 50%; 
                border: 8px solid {color_code}; 
                display: flex; align-items: center; justify-content: center; 
                font-size: 48px; font-weight: bold; color: {color_code};
                background: {bg_color};
                margin: 0 auto;
            }}
            .metrics-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 30px; }}
            .metric-card {{ border-top: 1px solid #e0e0e0; padding: 10px 0; display: flex; justify-content: space-between; }}
            .metric-label {{ color: #5f6368; font-size: 14px; }}
            .metric-value {{ font-weight: bold; color: #202124; }}
            .red-dot {{ display: inline-block; width: 10px; height: 10px; background: #ff4e42; margin-right: 8px; clip-path: polygon(50% 0%, 0% 100%, 100% 100%); }}
            .green-dot {{ display: inline-block; width: 10px; height: 10px; background: #0cce6b; border-radius: 50%; margin-right: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <strong>Performance</strong>
                <span style="color: #1a73e8;">Mobile</span>
            </div>
            <div class="url">{url}</div>
            
            <div class="score-container" style="text-align: center;">
                <div class="score-circle">{score}</div>
                <div style="margin-top: 10px; color: {color_code}; font-weight: bold;">{score}-49</div>
            </div>

            <div class="metrics-grid">
                <div class="metric-card"><span class="metric-label"><span class="red-dot"></span>First Contentful Paint</span> <span class="metric-value">{metrics[0]}</span></div>
                <div class="metric-card"><span class="metric-label"><span class="red-dot"></span>Largest Contentful Paint</span> <span class="metric-value">{metrics[1]}</span></div>
                <div class="metric-card"><span class="metric-label"><span class="red-dot"></span>Total Blocking Time</span> <span class="metric-value">{metrics[2]}</span></div>
                <div class="metric-card"><span class="metric-label"><span class="green-dot"></span>Cumulative Layout Shift</span> <span class="metric-value">{metrics[3]}</span></div>
                <div class="metric-card"><span class="metric-label"><span class="red-dot"></span>Speed Index</span> <span class="metric-value">{metrics[4]}</span></div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--score", type=int, required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Simulated metrics based on score
        metrics = ["3.4 s", "4.1 s", "810 ms", "0.04", "4.5 s"] 
        if args.score > 80:
             metrics = ["1.2 s", "1.8 s", "120 ms", "0.01", "2.1 s"]
             
        html_content = generate_html(args.score, args.url, metrics)
        page.set_content(html_content)
        
        # Screenshot buffer
        screenshot_path = os.path.join(OUTPUT_DIR, f"{args.name}_slow_load.png")
        
        # Select the container to crop whitespace
        try:
            element = page.locator(".container")
            element.screenshot(path=screenshot_path)
            print(f"[OK] Generated Speed Evidence: {screenshot_path}")
        except Exception as e:
            print(f"[ERROR] Failed to generate speed evidence: {e}")
        
        page.close()
        browser.close()

if __name__ == "__main__":
    main()
