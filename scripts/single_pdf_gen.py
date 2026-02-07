
import sys
import os
import json
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_pdf(facts_file, output_path, industry="Business"):
    with open(facts_file, "r") as f:
        facts = json.load(f)
    
    # Simple mapping
    term_map = {
        "HVAC": "homeowner",
        "Plumbing": "homeowner",
        "Roofing": "homeowner", 
        "Dental": "patient",
        "Medical": "patient"
    }
    client_term = term_map.get(industry, "client")

    
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkblue)
    c.drawString(50, height - 50, "STRATEGIC SOLUTIONS PROPOSAL")
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(50, height - 80, f"Prepared for: Locally-Owned Business | {facts.get('site_title', 'Client')}")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 100, f"We act as your technical shield and growth engine. Below are the specific services available")
    c.drawString(50, height - 115, f"to fix your current liabilities and accelerate {client_term} acquisition.")
    
    # Section 1: Liability Shield
    y = height - 160
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "1. LIABILITY & PERFORMANCE SHIELD")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Immediate technical remediation to protect the practice:")
    y -= 20
    
    # Bullets
    c.drawString(60, y, "•  TCPA Compliance Guard: Installation of mandated consent checkboxes on all forms.")
    y -= 15
    c.drawString(60, y, "•  Legal Safe Harbor: Drafting and hosting of Terms of Use & Privacy Policy.")
    y -= 15
    c.drawString(60, y, "•  Mobile Velocity Fix: Code optimization to achieve < 3s load times (Google Core Web Vitals).")
    
    # Section 2: Acquisition Engines
    y -= 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"2. {client_term.upper()} ACQUISITION ENGINES")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Automated systems to capture 100% of demand:")
    y -= 20
    
    c.drawString(60, y, "•  24/7 AI Receptionist: Answers calls day & night, answers questions, and books appointments.")
    y -= 15
    c.drawString(60, y, f"•  Map-Pack Domination: Local SEO protocols to rank #1 for '{industry} near me'.")
    y -= 15
    c.drawString(60, y, "•  Client Reactivation: Automated newsletter campaigns with a verified 30% rebooking rate.")
    
    # Footer
    y -= 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "NEXT STEPS:")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "All systems above can be deployed within 48 hours. Reply 'YES' to the email to schedule a 10-minute")
    c.drawString(50, y - 15, "demo.")
    
    c.save()
    print(f"✅ PDF Generated: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--facts", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--industry", default="Business")
    args = parser.parse_args()
    
    generate_pdf(args.facts, args.output, args.industry)
