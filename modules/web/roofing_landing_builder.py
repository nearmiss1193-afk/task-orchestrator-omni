# modules/web/roofing_landing_builder.py

def get_roofing_landing_html(calendly_url="#", form_url="#"):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Empire Roofing - Storm Revenue Recovery</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Outfit', sans-serif; }}
        .glass {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }}
        .animate-in {{ animation: fadeIn 0.6s ease-out; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
</head>
<body class="bg-slate-950 text-white overflow-x-hidden">

    <!-- HERO -->
    <section class="relative min-h-screen flex items-center justify-center p-4">
        <!-- Background Overlay -->
        <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1628135804068-19045cb21429?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center opacity-20"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent"></div>

        <div class="relative z-10 grid lg:grid-cols-2 gap-12 max-w-7xl mx-auto items-center">
            
            <!-- Left Content -->
            <div class="space-y-8 text-center lg:text-left animate-in">
                <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-red-400 text-sm font-bold uppercase tracking-wider">
                    <i data-lucide="siren"></i> Storm Season Alert
                </div>
                <h1 class="text-5xl md:text-7xl font-extrabold leading-tight">
                    Don't Let Storm Jobs <span class="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500">Slip Away</span>
                </h1>
                <p class="text-xl text-slate-400">
                    The "Storm Sentinel" AI instantly texts back missed calls, booking inspections before your competition even picks up the phone.
                </p>
                <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                    <a href="#calculator" class="px-8 py-4 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold text-lg transition-all transform hover:scale-105 shadow-lg shadow-red-600/20">
                        Calculate Lost Revenue
                    </a>
                    <a href="#demo" class="px-8 py-4 glass hover:bg-white/10 text-white rounded-xl font-bold text-lg transition-all">
                        View Live Demo
                    </a>
                </div>
                <div class="flex items-center gap-4 justify-center lg:justify-start text-sm text-slate-500 pt-4">
                    <span class="flex items-center gap-1"><i data-lucide="check-circle" class="w-4 h-4 text-green-500"></i> Hail Verified</span>
                    <span class="flex items-center gap-1"><i data-lucide="check-circle" class="w-4 h-4 text-green-500"></i> &lt;30s Response</span>
                    <span class="flex items-center gap-1"><i data-lucide="check-circle" class="w-4 h-4 text-green-500"></i> GHL Integrated</span>
                </div>
            </div>

            <!-- Right Calculator (Glass Card) -->
            <div id="calculator" class="glass p-8 rounded-2xl shadow-2xl animate-in" style="animation-delay: 0.2s;">
                <div id="calc-step-1">
                    <h3 class="text-2xl font-bold mb-6 text-center">How many calls do you miss per week?</h3>
                    <div class="grid gap-4">
                        <button onclick="nextStep(5)" class="p-6 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl text-left transition-all hover:border-red-500 group">
                            <span class="text-xl font-bold block group-hover:text-red-400 transition-colors">1 - 5 Calls</span>
                            <span class="text-slate-400 text-sm">I'm a solo operator or small crew</span>
                        </button>
                        <button onclick="nextStep(15)" class="p-6 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl text-left transition-all hover:border-red-500 group">
                            <span class="text-xl font-bold block group-hover:text-red-400 transition-colors">6 - 20 Calls</span>
                            <span class="text-slate-400 text-sm">We get slammed during storms</span>
                        </button>
                        <button onclick="nextStep(30)" class="p-6 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl text-left transition-all hover:border-red-500 group">
                            <span class="text-xl font-bold block group-hover:text-red-400 transition-colors">20+ Calls</span>
                            <span class="text-slate-400 text-sm">I need major automation ASAP</span>
                        </button>
                    </div>
                </div>

                <div id="calc-step-2" class="hidden text-center space-y-6">
                    <div class="w-16 h-16 mx-auto bg-red-500/20 text-red-500 rounded-full flex items-center justify-center">
                        <i data-lucide="trending-down" class="w-8 h-8"></i>
                    </div>
                    <h3 class="text-3xl font-bold">You're Bleeding Revenue</h3>
                    <div class="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-600">
                        $<span id="revenue-loss">0</span>
                    </div>
                    <p class="text-slate-400">Potential monthly loss in missed roof installs.</p>
                    <button class="w-full py-4 bg-red-600 hover:bg-red-700 rounded-xl font-bold text-lg shadow-lg shadow-red-600/20 animate-pulse">
                        Plug The Hole &rarr;
                    </button>
                </div>
            </div>

        </div>
    </section>

    <!-- JS Logic -->
    <script>
        lucide.createIcons();
        function nextStep(calls) {{
            const avgTicket = 15000;
            const closeRate = 0.2;
            const loss = calls * 4 * avgTicket * closeRate; // Monthly
            
            document.getElementById('calc-step-1').classList.add('hidden');
            document.getElementById('revenue-loss').innerText = loss.toLocaleString();
            document.getElementById('calc-step-2').classList.remove('hidden');
        }}
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    print(get_roofing_landing_html())
