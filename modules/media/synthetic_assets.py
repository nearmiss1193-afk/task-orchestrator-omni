
from PIL import Image, ImageDraw, ImageFont
import os

def create_synthetic_ui(title, metric, metric_val, filename):
    """Generates a high-quality 'Glass' UI Mockup"""
    w, h = 1920, 1080
    
    # Background: Dark Gradient (Dark Slate to Black)
    img = Image.new('RGB', (w, h), color='#0f172a')
    draw = ImageDraw.Draw(img)
    
    # Draw Background Grid
    for i in range(0, w, 100):
        draw.line([(i, 0), (i, h)], fill='#1e293b', width=1)
    for i in range(0, h, 100):
        draw.line([(0, i), (w, i)], fill='#1e293b', width=1)

    # Draw "Graph" (Green for Money)
    points = [(0, h), (400, 800), (800, 600), (1200, 500), (1600, 300), (1920, 200)]
    draw.polygon(points + [(1920, 1080), (0, 1080)], fill='#064e3b') # Dark Green fill
    draw.line(points, fill='#10b981', width=12) # Emerald Line
    
    # Draw "Card" Container
    card_w, card_h = 900, 600
    card_x, card_y = (w - card_w) // 2, (h - card_h) // 2
    
    # Card Shadow
    draw.rectangle([card_x+20, card_y+20, card_x + card_w+20, card_y + card_h+20], fill='#000000')
    
    # Card Body
    draw.rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        fill='#1e293b', outline='#334155', width=4
    )
    
    # Font Selection
    try:
        # Try to find a nice font on Linux/Standard paths
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if not os.path.exists(font_path):
            font_path = "arial.ttf" # Windows fallback
        
        font_lg = ImageFont.truetype(font_path, 100)
        font_xl = ImageFont.truetype(font_path, 160)
        font_sm = ImageFont.truetype(font_path, 50)
    except:
        font_lg = ImageFont.load_default()
        font_xl = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    # Content
    # Title
    draw.text((card_x + 80, card_y + 80), title, fill='white', font=font_lg)
    
    # Metric Label
    draw.text((card_x + 80, card_y + 250), metric, fill='#94a3b8', font=font_sm)
    
    # Metric Value (The Hero)
    draw.text((card_x + 80, card_y + 320), metric_val, fill='#22d3ee', font=font_xl)
    
    # Button Mockup
    draw.rectangle([card_x + 80, card_y + 480, card_x + 400, card_y + 570], fill='#3b82f6')
    draw.text((card_x + 130, card_y + 505), "VIEW REPORT", fill='white', font=font_sm)

    # Status Indicator
    draw.ellipse([card_x + card_w - 100, card_y + 80, card_x + card_w - 60, card_y + 120], fill='#10b981')
    draw.text((card_x + card_w - 220, card_y + 85), "Active", fill='#10b981', font=font_sm)

    os.makedirs("assets/generated", exist_ok=True)
    path = f"assets/generated/{filename}"
    img.save(path)
    print(f"🎨 Asset Created: {path}")

if __name__ == "__main__":
    create_synthetic_ui("Missed Call Recovery", "Revenue Saved", "$4,200 / mo", "dashboard_recovery.png")
