
import modal

app = modal.App("hvac-campaign-standalone")

# Minimal image
image = modal.Image.debian_slim().pip_install("fastapi")

def get_html_content(calendly_url, stripe_url):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stop Losing AC Repair Jobs | Polk County HVAC Automation</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .ken-burns-bg {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('https://images.unsplash.com/photo-1581094794329-cd1361ddee2f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
            animation: kenBurns 20s infinite alternate;
            z-index: -1;
            filter: brightness(0.3);
        }}
        @keyframes kenBurns {{
            from {{ transform: scale(1); }}
            to {{ transform: scale(1.1); }}
        }}
        .glass {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
    </style>
</head>
<body class="bg-gray-900 text-white h-screen flex flex-col overflow-hidden relative">

    <div class="ken-burns-bg"></div>

    <nav class="w-full p-6 flex justify-between items-center z-10">
        <div class="text-2xl font-bold tracking-tighter text-blue-400">Empire<span class="text-white">Cooling</span></div>
        <a href="#demo" class="px-5 py-2 rounded-full border border-gray-500 hover:border-white transition text-sm">Member Login</a>
    </nav>

    <main class="flex-grow flex flex-col justify-center items-center text-center px-4 z-10 max-w-4xl mx-auto">
        <div class="mb-4 inline-block px-4 py-1 rounded-full bg-blue-600/20 border border-blue-500/50 text-blue-300 text-xs tracking-widest uppercase animate-pulse">
            For Polk County HVAC Owners Only
        </div>
        <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
            Stop Losing AC Jobs to <br> <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">Missed Calls.</span>
        </h1>
        <p class="text-gray-300 text-lg md:text-xl max-w-2xl mb-10">
            If you don't answer instantly, they call the next guy on Google.
            Our AI texts them back in 3 seconds to book the appointment automatically.
        </p>
        <div class="w-full max-w-3xl aspect-video bg-black/50 rounded-xl border border-gray-700 shadow-2xl mb-10 flex items-center justify-center relative group cursor-pointer overflow-hidden">
            <div class="absolute inset-0 bg-blue-500/10 group-hover:bg-blue-500/5 transition"></div>
            <div class="w-16 h-16 rounded-full bg-white/10 backdrop-blur flex items-center justify-center border border-white/20 group-hover:scale-110 transition duration-300">
                <svg class="w-6 h-6 text-white ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            </div>
            <span class="absolute bottom-4 text-sm text-gray-400">Watch the 60s Demo</span>
        </div>
        <div class="flex flex-col md:flex-row gap-4 w-full max-w-md">
            <a href="{stripe_url}" class="flex-1 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-bold py-4 rounded-lg shadow-lg transform hover:-translate-y-1 transition border border-blue-400/20 flex items-center justify-center">
                Start Free 14-Day Trial
            </a>
            <a href="{calendly_url}" class="flex-1 glass hover:bg-white/10 text-white font-semibold py-4 rounded-lg transition border border-white/20 flex items-center justify-center">
                Get a Live Demo
            </a>
        </div>
        <p class="mt-6 text-gray-500 text-xs">
            No credit card required for demo. FTSA Compliant.
        </p>
    </main>

    <footer class="p-6 text-center text-gray-600 text-xs z-10">
        &copy; 2025 Empire Unified. All rights reserved.
    </footer>
</body>
</html>
"""

@app.function(image=image)
@modal.fastapi_endpoint()
def hvac_landing():
    from fastapi.responses import HTMLResponse
    html = get_html_content(
        calendly_url="https://calendly.com/aiserviceco/demo",
        stripe_url="https://buy.stripe.com/test_hvac"
    )
    return HTMLResponse(content=html, status_code=200)
