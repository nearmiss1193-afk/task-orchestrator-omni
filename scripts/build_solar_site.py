
"""
Script: Build Solar AI Landing Page
Mission: Generate a high-performance landing page for Solar Companies.
"""
import os
import sys

# Ensure path visibility
sys.path.insert(0, os.getcwd())

from modules.constructor.wiring import WiringTech
from modules.constructor.funnel_forge import FunnelForge

def build_solar_asset():
    print("☀️ IGNITING SOLAR VERTICAL ASSET GENERATION...")
    
    forge = FunnelForge()
    
    # SOLAR SPECIFIC COPY (The "Pain & Cure")
    niche = "Solar"
    headline = "Your Leads Are Cooling Down. <span class='text-amber-500'>Heat Them Up.</span>"
    pain_points = """
    <ul class='text-left max-w-lg mx-auto space-y-4 mb-8 text-gray-700'>
        <li class='flex items-center'><span class='text-red-500 mr-2'>❌</span> <strong>Speed to Lead Failure:</strong> 5 minutes delay = 400% drop in closing.</li>
        <li class='flex items-center'><span class='text-red-500 mr-2'>❌</span> <strong>Voicemail Tag:</strong> You call, they don't answer. They call back, you're busy.</li>
        <li class='flex items-center'><span class='text-red-500 mr-2'>❌</span> <strong>Expensive CPL:</strong> You pay $50/lead just to lose them in the cracks.</li>
    </ul>
    """
    
    solution = """
    <div class='bg-blue-50 p-8 rounded-2xl border border-blue-100 my-10'>
        <h3 class='text-2xl font-bold text-blue-900 mb-4'>The AI Service Co Solution</h3>
        <div class='grid md:grid-cols-2 gap-6 text-left'>
            <div>
                <h4 class='font-bold text-lg'>🚀 Instant SMS Strike</h4>
                <p class='text-sm text-gray-600'>Lead fills form -> AI text sent in 30 seconds. "Hey [Name], saw you looked at solar. Quick question?"</p>
            </div>
            <div>
                <h4 class='font-bold text-lg'>📞 24/7 Receptionist</h4>
                <p class='text-sm text-gray-600'>Missed calls are answered by AI who can book appointments on your calendar instantly.</p>
            </div>
        </div>
    </div>
    """
    
    # Trigger Link (Simulated for Speed)
    trigger_link = "https://calendly.com/aiserviceco/solar-audit"
    
    # Custom HTML Construction using Forge Logic manually for maximum customization
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI For Solar - Stop Losing Deals</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;800&display=swap" rel="stylesheet">
    <style>body {{ font-family: 'Outfit', sans-serif; }}</style>
</head>
<body class="bg-white text-slate-900">

    <!-- NAV -->
    <nav class="flex justify-between items-center px-8 py-6 max-w-6xl mx-auto">
        <div class="font-black text-2xl tracking-tighter">AI Service Co.</div>
        <a href="{trigger_link}" class="bg-slate-900 text-white px-6 py-2 rounded-lg font-bold hover:bg-slate-700 transition">Book Demo</a>
    </nav>

    <!-- HERO -->
    <section class="text-center py-20 px-6">
        <h1 class="text-5xl md:text-7xl font-black mb-6 leading-tight">{headline}</h1>
        <p class="text-xl text-gray-500 mb-12 max-w-2xl mx-auto">
            Automate your Solar Sales Follow-up. Close 2x more deals without hiring another SDR.
        </p>
        
        {pain_points}
        
        <a href="{trigger_link}" class="inline-block bg-amber-500 text-white font-bold text-xl py-5 px-12 rounded-full shadow-lg hover:shadow-amber-500/50 hover:-translate-y-1 transition transform">
            Get My Free AI Audit &rarr;
        </a>
    </section>

    <!-- SOLUTION -->
    <section class="max-w-5xl mx-auto px-6">
        {solution}
    </section>

    <!-- SOCIAL PROOF -->
    <section class="bg-slate-900 text-white py-24 mt-20 text-center">
        <h2 class="text-3xl font-bold mb-12">Results from Solar Pros</h2>
        <div class="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto px-6">
            <div class="p-6 bg-slate-800 rounded-xl">
                <div class="text-4xl mb-4">☀️</div>
                <p class="mb-4">"Our connection rate went from 12% to 45% in week one."</p>
                <p class="font-bold text-amber-500">- SunRun Franchisee</p>
            </div>
            <div class="p-6 bg-slate-800 rounded-xl">
                <div class="text-4xl mb-4">💰</div>
                <p class="mb-4">"The AI booked 14 appointments while my team was at lunch."</p>
                <p class="font-bold text-amber-500">- Apex Energy</p>
            </div>
            <div class="p-6 bg-slate-800 rounded-xl">
                <div class="text-4xl mb-4">📉</div>
                <p class="mb-4">"Reduced our Cost Per Acquisition by 30%. It's a no brainer."</p>
                <p class="font-bold text-amber-500">- BrightSky Solar</p>
            </div>
        </div>
    </section>
    
    <footer class="text-center py-10 text-gray-400 text-sm">
        &copy; 2024 AI Service Co. | Built by Empire Constructors
    </footer>

</body>
</html>
    """
    
    # Save
    fname = "output/solar_ai_lander.html"
    os.makedirs("output", exist_ok=True)
    with open(fname, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"✅ SOLAR ASSET BUILT: {fname}")

if __name__ == "__main__":
    build_solar_asset()
