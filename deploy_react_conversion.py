
import modal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = modal.App("empire-hvac-v3")

image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "uvicorn")
)

@app.function(image=image)
@modal.web_endpoint(method="GET")
def entry():
    html_content = r'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Service Co - Stop Losing Jobs</title>
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
            <div class="w-full max-w-2xl p-8 md:p-12 bg-slate-800 border-orange-500 border-2 shadow-2xl rounded-xl">
                
                <!-- STEP 0 -->
                <div id="step-0" class="space-y-6 animate-in">
                    <h2 class="text-2xl md:text-3xl font-bold text-white text-center">
                        How many jobs are you losing per month to missed calls?
                    </h2>
                    <div class="grid gap-4 mt-8">
                        <button onclick="setMissedCalls('1-5')" class="h-16 text-xl bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-md w-full font-bold transition-transform hover:scale-105">
                            1-5 missed calls per month
                        </button>
                        <button onclick="setMissedCalls('6-10')" class="h-16 text-xl bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-md w-full font-bold transition-transform hover:scale-105">
                            6-10 missed calls per month
                        </button>
                        <button onclick="setMissedCalls('11+')" class="h-16 text-xl bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-md w-full font-bold transition-transform hover:scale-105">
                            11+ missed calls per month
                        </button>
                    </div>
                </div>

                <!-- STEP 1 -->
                <div id="step-1" class="space-y-6 animate-in hidden">
                    <h2 class="text-2xl md:text-3xl font-bold text-white text-center">
                        What is your average job ticket value?
                    </h2>
                    <div class="mt-8">
                        <div class="relative">
                            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-3xl text-slate-400">$</span>
                            <input type="number" id="ticketValue" placeholder="5000" class="w-full h-20 text-3xl pl-12 bg-slate-700 border-slate-600 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500">
                        </div>
                        <button onclick="calculateRevenue()" class="w-full h-16 mt-6 text-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 rounded-md font-bold flex items-center justify-center transition-transform hover:scale-105">
                            Calculate My Lost Revenue <i data-lucide="chevron-right" class="ml-2"></i>
                        </button>
                    </div>
                </div>

                <!-- STEP 2 (LOADING) -->
                <div id="step-2-loading" class="space-y-6 animate-in text-center hidden">
                    <div class="w-20 h-20 mx-auto border-4 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
                    <p class="text-xl text-slate-300">Calculating your lost revenue...</p>
                </div>

                <!-- STEP 2 (RESULT) -->
                <div id="step-2-result" class="space-y-6 animate-in text-center hidden">
                    <h2 class="text-2xl md:text-3xl font-bold text-white">
                        You're Losing Approximately
                    </h2>
                    <div id="lostRevenueDisplay" class="text-6xl md:text-7xl font-bold text-orange-500">
                        $0
                    </div>
                    <p class="text-xl text-slate-300">per month in missed opportunities</p>
                    <button onclick="scrollToContact()" class="w-full h-16 text-xl bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 mt-8 rounded-md font-bold flex items-center justify-center transition-transform hover:scale-105">
                        AI Service Co Can Recover This For You <i data-lucide="chevron-right" class="ml-2"></i>
                    </button>
                </div>

            </div>
        </div>

        <!-- HERO SECTION -->
        <section id="contact-section" class="min-h-screen flex items-center justify-center p-4 md:p-8 bg-gradient-to-br from-slate-900 to-slate-800">
            <div class="w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
                <div class="space-y-6">
                    <h1 class="text-4xl md:text-6xl font-bold text-white leading-tight">
                        Stop Losing Jobs to <span class="text-orange-500">Missed Calls</span>
                    </h1>
                    <p class="text-xl md:text-2xl text-slate-300">
                        AI Service Co automates your customer follow-ups, social media, and operations so you can focus on the work that pays.
                    </p>
                    <div class="flex flex-wrap gap-4 text-slate-300">
                        <div class="flex items-center gap-2">
                            <i data-lucide="shield" class="text-cyan-500"></i>
                            <span>Florida SMS Compliant</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <i data-lucide="zap" class="text-orange-500"></i>
                            <span>Instant Response AI</span>
                        </div>
                    </div>
                </div>
                
                <div class="p-6 bg-slate-800 border-2 border-cyan-500 rounded-xl shadow-lg">
                    <h3 class="text-2xl font-bold text-white mb-4">Get Started Now</h3>
                    <!-- Form Placeholder: Using a styled div as we don't have the widget script local context or iframe constraints might apply -->
                    <iframe 
                        src="https://links.aiserviceco.com/widget/form/7TTJ1CUAFjhON69ZsOZK" 
                        style="width:100%; height:500px; border:none; border-radius:8px;" 
                        id="inline-7TTJ1CUAFjhON69ZsOZK" 
                        data-form-id="7TTJ1CUAFjhON69ZsOZK">
                    </iframe>
                    <div class="mt-4 p-3 bg-slate-700 rounded text-xs text-slate-300">
                        By submitting your information, you provide express written consent to AI Service Co to contact you via SMS or phone call using automated technology.
                    </div>
                </div>
            </div>
        </section>

        <!-- STACK SECTION -->
        <section class="py-20 px-4 md:px-8 bg-slate-800">
            <div class="max-w-6xl mx-auto">
                <h2 class="text-4xl md:text-5xl font-bold text-white text-center mb-16">
                    The <span class="text-orange-500">AI Service Co</span> Automation Stack
                </h2>
                
                <div class="grid md:grid-cols-2 gap-8">
                    <!-- The Voice Nexus -->
                    <div class="p-8 bg-gradient-to-br from-slate-700 to-slate-800 border-2 border-orange-500 hover:scale-105 transition-transform rounded-xl">
                        <div class="w-16 h-16 bg-orange-500 rounded-full flex items-center justify-center mb-6">
                            <i data-lucide="phone" class="w-8 h-8 text-white"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-white mb-4">The Voice Nexus</h3>
                        <p class="text-slate-300 mb-4">AI Missed Call Text-Back - "The Closer"</p>
                        <ul class="space-y-2 text-slate-300">
                            <li class="flex items-start gap-2"><i data-lucide="chevron-right" class="text-orange-500 mt-1"></i> <span>Instantly texts back missed calls</span></li>
                            <li class="flex items-start gap-2"><i data-lucide="chevron-right" class="text-orange-500 mt-1"></i> <span>AI-powered conversation booking</span></li>
                            <li class="flex items-start gap-2"><i data-lucide="chevron-right" class="text-orange-500 mt-1"></i> <span>Works 24/7</span></li>
                        </ul>
                    </div>

                    <!-- Social Siege -->
                    <div class="p-8 bg-gradient-to-br from-slate-700 to-slate-800 border-2 border-cyan-500 hover:scale-105 transition-transform rounded-xl">
                        <div class="w-16 h-16 bg-cyan-500 rounded-full flex items-center justify-center mb-6">
                            <i data-lucide="message-square" class="w-8 h-8 text-white"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-white mb-4">Social Siege</h3>
                        <p class="text-slate-300 mb-4">Instagram/LinkedIn Omni-Presence Automation</p>
                        <ul class="space-y-2 text-slate-300">
                            <li class="flex items-start gap-2"><i data-lucide="chevron-right" class="text-cyan-500 mt-1"></i> <span>Automated posting schedule</span></li>
                            <li class="flex items-start gap-2"><i data-lucide="chevron-right" class="text-cyan-500 mt-1"></i> <span>DM automation for lead gen</span></li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <!-- FOOTER -->
        <footer class="bg-slate-950 py-12 px-4 md:px-8 border-t-2 border-orange-500">
            <div class="max-w-6xl mx-auto text-center">
                <h3 class="text-2xl font-bold text-white mb-4">AI Service Co</h3>
                <p class="text-slate-400">Automation solutions for blue-collar businesses</p>
                <div class="pt-8 border-t border-slate-800 mt-8">
                    <p class="text-xs text-slate-600">© 2024 AI Service Co. All rights reserved.</p>
                </div>
            </div>
        </footer>

        <script>
            // Initialize Icons
            lucide.createIcons();

            // Logic
            let missedCalls = null;
            let ticketValue = 0;

            function setMissedCalls(val) {
                missedCalls = val;
                document.getElementById('step-0').classList.add('hidden');
                document.getElementById('step-1').classList.remove('hidden');
            }

            function calculateRevenue() {
                const input = document.getElementById('ticketValue').value;
                if(!input) return;
                ticketValue = input;
                
                document.getElementById('step-1').classList.add('hidden');
                document.getElementById('step-2-loading').classList.remove('hidden');

                // Simulate calculation
                setTimeout(() => {
                    document.getElementById('step-2-loading').classList.add('hidden');
                    document.getElementById('step-2-result').classList.remove('hidden');
                    
                    // Calculation Logic from React code
                    // (missedCalls === '1-5' ? 3 : missedCalls === '6-10' ? 8 : 15) * parseFloat(ticketValue)
                    let multiplier = 3;
                    if(missedCalls === '6-10') multiplier = 8;
                    if(missedCalls === '11+') multiplier = 15;
                    
                    const lost = multiplier * parseFloat(ticketValue);
                    document.getElementById('lostRevenueDisplay').innerText = '$' + lost.toLocaleString();
                }, 2000);
            }

            function scrollToContact() {
                document.getElementById('contact-section').scrollIntoView({ behavior: 'smooth' });
            }
        </script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)
