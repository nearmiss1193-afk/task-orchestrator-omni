
import modal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = modal.App("empire-roofing-v1")

image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "uvicorn")
)

@app.function(image=image, secrets=[modal.Secret.from_name("agency-vault")])
@modal.web_endpoint(method="GET")
def entry():
    from modules.constructor.workflow_architect import WorkflowArchitect
    
    # 1. CONSTRUCTOR LOGIC (Self-Wiring)
    arch = WorkflowArchitect()
    # Try to find a specific roofing form, or fallback to the master default
    form_id = arch.find_form("Roofing Intake") or "7TTJ1CUAFjhON69ZsOZK"
    
    print(f"🏗️ Deployment using Form ID: {form_id}")

    html_content = r'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Empire Roofing - Storm Revenue Recovery</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/lucide@latest"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; }
            .animate-in { animation: fadeIn 0.5s ease-out; }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        </style>
    </head>
    <body class="min-h-screen bg-slate-900 text-white">

        <!-- CALCULATOR SECTION -->
        <div id="calculator-container" class="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <div class="w-full max-w-2xl p-8 md:p-12 bg-slate-800 border-red-600 border-2 shadow-2xl rounded-xl">
                
                <!-- STEP 0 -->
                <div id="step-0" class="space-y-6 animate-in">
                    <h2 class="text-2xl md:text-3xl font-bold text-white text-center">
                        How many <span class="text-red-500">Roof Replacements</span> are you losing to missed calls?
                    </h2>
                    <div class="grid gap-4 mt-8">
                        <button onclick="setMissedCalls('1-3')" class="h-16 text-xl bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-md w-full font-bold transition-transform hover:scale-105">
                            1-3 missed jobs / mo
                        </button>
                        <button onclick="setMissedCalls('4-8')" class="h-16 text-xl bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-md w-full font-bold transition-transform hover:scale-105">
                            4-8 missed jobs / mo
                        </button>
                        <button onclick="setMissedCalls('9+')" class="h-16 text-xl bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-md w-full font-bold transition-transform hover:scale-105">
                            9+ missed jobs / mo
                        </button>
                    </div>
                </div>

                <!-- STEP 1 -->
                <div id="step-1" class="space-y-6 animate-in hidden">
                    <h2 class="text-2xl md:text-3xl font-bold text-white text-center">
                        Average Ticket Value (Storm/Retail)?
                    </h2>
                    <div class="mt-8">
                        <div class="relative">
                            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-3xl text-slate-400">$</span>
                            <input type="number" id="ticketValue" value="18000" placeholder="18000" class="w-full h-20 text-3xl pl-12 bg-slate-700 border-slate-600 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
                        </div>
                        <button onclick="calculateRevenue()" class="w-full h-16 mt-6 text-xl bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 rounded-md font-bold flex items-center justify-center transition-transform hover:scale-105">
                            Calculate Lost Revenue <i data-lucide="chevron-right" class="ml-2"></i>
                        </button>
                    </div>
                </div>

                <!-- STEP 2 (LOADING) -->
                <div id="step-2-loading" class="space-y-6 animate-in text-center hidden">
                    <div class="w-20 h-20 mx-auto border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
                    <p class="text-xl text-slate-300">Analyzing Market Data...</p>
                </div>

                <!-- STEP 2 (RESULT) -->
                <div id="step-2-result" class="space-y-6 animate-in text-center hidden">
                    <h2 class="text-2xl md:text-3xl font-bold text-white">
                        You're Bleeding Approximately
                    </h2>
                    <div id="lostRevenueDisplay" class="text-6xl md:text-7xl font-bold text-red-500">
                        $0
                    </div>
                    <p class="text-xl text-slate-300">per month in missed installs</p>
                    <button onclick="scrollToContact()" class="w-full h-16 text-xl bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 mt-8 rounded-md font-bold flex items-center justify-center transition-transform hover:scale-105">
                        Recover This Revenue Now <i data-lucide="chevron-right" class="ml-2"></i>
                    </button>
                </div>

            </div>
        </div>

        <!-- HERO SECTION -->
        <section id="contact-section" class="min-h-screen flex items-center justify-center p-4 md:p-8 bg-gradient-to-br from-slate-900 to-slate-800">
            <div class="w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
                <div class="space-y-6">
                    <h1 class="text-4xl md:text-6xl font-bold text-white leading-tight">
                        Don't Let Storm Jobs <span class="text-red-500">Slip Away</span>
                    </h1>
                    <p class="text-xl md:text-2xl text-slate-300">
                        The "Storm Sentinel" AI instantly texts back missed calls, booking inspections before your competition even picks up the phone.
                    </p>
                    <div class="flex flex-wrap gap-4 text-slate-300">
                        <div class="flex items-center gap-2">
                            <i data-lucide="shield-check" class="text-green-500"></i>
                            <span>Hail Damage Verified</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <i data-lucide="zap" class="text-red-500"></i>
                            <span>< 30s Response Time</span>
                        </div>
                    </div>
                </div>
                
                <div class="p-6 bg-slate-800 border-2 border-red-600 rounded-xl shadow-lg">
                    <h3 class="text-2xl font-bold text-white mb-4">Secure Your Territory</h3>
                    <!-- DYNAMIC FORM INJECTION -->
                    <iframe 
                        src="https://links.aiserviceco.com/widget/form/{{FORM_ID}}" 
                        style="width:100%; height:500px; border:none; border-radius:8px;" 
                        id="inline-{{FORM_ID}}" 
                        data-form-id="{{FORM_ID}}">
                    </iframe>
                    <div class="mt-4 p-3 bg-slate-700 rounded text-xs text-slate-300">
                        By submitting, you agree to receive automated texts. Reply STOP to opt-out.
                    </div>
                </div>
            </div>
        </section>

        <!-- STACK SECTION -->
        <section class="py-20 px-4 md:px-8 bg-slate-800">
            <div class="max-w-6xl mx-auto">
                <h2 class="text-4xl md:text-5xl font-bold text-white text-center mb-16">
                    The <span class="text-red-500">Roofing Dominance</span> Stack
                </h2>
                
                <div class="grid md:grid-cols-2 gap-8">
                    <!-- Storm Sentinel -->
                    <div class="p-8 bg-gradient-to-br from-slate-700 to-slate-800 border-2 border-red-600 hover:scale-105 transition-transform rounded-xl">
                        <div class="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center mb-6">
                            <i data-lucide="cloud-lightning" class="w-8 h-8 text-white"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-white mb-4">Storm Sentinel</h3>
                        <p class="text-slate-300 mb-4">Missed Call Text-Back for Storm Chasers</p>
                        <ul class="space-y-2 text-slate-300">
                            <li class="flex items-start gap-2"><i data-lucide="check" class="text-red-500 mt-1"></i> <span>Beats knockers to the appointment</span></li>
                            <li class="flex items-start gap-2"><i data-lucide="check" class="text-red-500 mt-1"></i> <span>Auto-books inspections 24/7</span></li>
                        </ul>
                    </div>

                    <!-- Warranty Watchdog -->
                    <div class="p-8 bg-gradient-to-br from-slate-700 to-slate-800 border-2 border-blue-500 hover:scale-105 transition-transform rounded-xl">
                        <div class="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mb-6">
                            <i data-lucide="clipboard-check" class="w-8 h-8 text-white"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-white mb-4">Warranty Watchdog</h3>
                        <p class="text-slate-300 mb-4">Long-Term Maintenance Automation</p>
                        <ul class="space-y-2 text-slate-300">
                            <li class="flex items-start gap-2"><i data-lucide="check" class="text-blue-500 mt-1"></i> <span>Annual inspection reminders</span></li>
                            <li class="flex items-start gap-2"><i data-lucide="check" class="text-blue-500 mt-1"></i> <span>Referral generation on auto-pilot</span></li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <script>
            lucide.createIcons();
            let missedCalls = null;
            let ticketValue = 18000;

            function setMissedCalls(val) {
                missedCalls = val;
                document.getElementById('step-0').classList.add('hidden');
                document.getElementById('step-1').classList.remove('hidden');
            }

            function calculateRevenue() {
                const input = document.getElementById('ticketValue').value;
                if(input) ticketValue = input;
                
                document.getElementById('step-1').classList.add('hidden');
                document.getElementById('step-2-loading').classList.remove('hidden');

                setTimeout(() => {
                    document.getElementById('step-2-loading').classList.add('hidden');
                    document.getElementById('step-2-result').classList.remove('hidden');
                    
                    let multiplier = 2; // conservative for 1-3
                    if(missedCalls === '4-8') multiplier = 6;
                    if(missedCalls === '9+') multiplier = 10;
                    
                    const lost = multiplier * parseFloat(ticketValue);
                    document.getElementById('lostRevenueDisplay').innerText = '$' + lost.toLocaleString();
                }, 1500);
            }

            function scrollToContact() {
                document.getElementById('contact-section').scrollIntoView({ behavior: 'smooth' });
            }
        </script>
    </body>
    </html>
    '''.replace("{{FORM_ID}}", form_id)
    
    return HTMLResponse(content=html_content)
