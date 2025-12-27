
import modal
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os

# Define Image
image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "uvicorn", "google-generativeai", "supabase", "requests")
)

app = modal.App("empire-dash")

# Secrets
# Secrets
# VAULT = modal.Secret.from_name("agency-vault") 
VAULT = modal.Secret.from_dict({
    "GEMINI_API_KEY": "AIzaSyB_WzpN1ASQssu_9ccfweWFPfoRknVUlHU",
    "SUPABASE_URL": "https://rzcpfwkygdvoshtwxncs.supabase.co",
    "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
})

# --- DATA HELPERS ---
def get_supabase():
    from supabase import create_client
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)

def get_gemini_model():
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-pro")

# --- FASTAPI APP FACTORY ---
def create_app():
    web_app = FastAPI()

    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    HTML_CONTENT = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EMPIRE COMMAND CENTER | CLOUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <script src="https://unpkg.com/lucide@latest"></script>
        <style>
            body { font-family: 'JetBrains Mono', monospace; background-color: #050505; color: #e0e0e0; }
            .terminal-box { background: #0a0a0a; border: 1px solid #333; box-shadow: 0 0 20px rgba(0, 255, 65, 0.05); }
            .glow-text { text-shadow: 0 0 10px rgba(0, 255, 65, 0.5); color: #00ff41; }
            .scrollbar-hide::-webkit-scrollbar { display: none; }
        </style>
    </head>
    <body class="h-screen flex flex-col p-6 overflow-hidden">
        <header class="flex justify-between items-center mb-6">
            <div>
                <h1 class="text-3xl font-bold tracking-tighter text-white">EMPIRE <span class="text-[#00ff41]">COMMAND CENTER</span></h1>
                <div class="flex items-center gap-2 mt-1">
                    <span class="relative flex h-3 w-3">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                    </span>
                    <p class="text-xs text-green-500 tracking-widest font-bold">SOVEREIGN STACK V2.1 // TACTICAL MODE</p>
                </div>
            </div>
            <div class="text-right">
                <p class="text-xs text-gray-500">SYSTEM TIME</p>
                <p class="text-xl font-bold" id="clock">00:00:00</p>
            </div>
        </header>

        <div class="grid grid-cols-12 gap-6 flex-1 min-h-0">
            <div class="col-span-8 flex flex-col gap-6 h-full min-h-0">
                <div class="grid grid-cols-4 gap-4 h-32 shrink-0">
                    <div class="terminal-box p-4 rounded-lg bg-[#0f0f0f]">
                        <p class="text-xs text-gray-400 uppercase">Total Targets</p>
                        <p class="text-3xl font-bold text-white mt-1" id="stat-leads">---</p>
                        <i data-lucide="users" class="text-gray-700 absolute top-4 right-4 h-5 w-5"></i>
                    </div>
                    <div class="terminal-box p-4 rounded-lg bg-[#0f0f0f]">
                        <p class="text-xs text-gray-400 uppercase">Pending</p>
                        <p class="text-3xl font-bold text-yellow-500 mt-1" id="stat-pending">---</p>
                        <i data-lucide="activity" class="text-gray-700 absolute top-4 right-4 h-5 w-5"></i>
                    </div>
                    <div class="terminal-box p-4 rounded-lg bg-[#0f0f0f]">
                        <p class="text-xs text-gray-400 uppercase">Potential Revenue</p>
                        <p class="text-3xl font-bold text-[#00ff41] mt-1" id="stat-revenue">---</p>
                        <i data-lucide="dollar-sign" class="text-gray-700 absolute top-4 right-4 h-5 w-5"></i>
                    </div>
                    <div class="terminal-box p-4 rounded-lg bg-[#0f0f0f]">
                        <p class="text-xs text-gray-400 uppercase">Health</p>
                        <p class="text-3xl font-bold text-blue-500 mt-1">100%</p>
                        <i data-lucide="cpu" class="text-gray-700 absolute top-4 right-4 h-5 w-5"></i>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-6 flex-1 min-h-0">
                     <!-- MAIN PANEL (LOGS OR GRID) -->
                    <div class="terminal-box rounded-lg flex flex-col min-h-0 overflow-hidden relative">
                        <div class="p-3 border-b border-[#333] flex justify-between items-center bg-[#0a0a0a] sticky top-0 z-10">
                            <span class="text-xs font-bold text-green-500 flex items-center gap-2">
                                <i data-lucide="table" class="h-3 w-3"></i> TACTICAL GRID / INTELLIGENCE
                            </span>
                            <div class="flex gap-2">
                                <button id="btn-grid" onclick="toggleView('grid')" class="text-[10px] bg-green-900/30 text-green-400 px-2 py-1 rounded hover:bg-green-900/50 border border-green-800 transition-colors">GRID</button>
                                <button id="btn-logs" onclick="toggleView('logs')" class="text-[10px] bg-gray-900 text-gray-400 px-2 py-1 rounded hover:bg-gray-800 border border-gray-800 transition-colors">LOGS</button>
                            </div>
                        </div>
                        
                        <!-- VIEW: GRID -->
                        <div id="view-grid" class="flex-1 overflow-y-auto p-0 font-mono text-xs hidden">
                            <table class="w-full text-left border-collapse">
                                <thead class="bg-[#111] text-gray-500 sticky top-0">
                                    <tr>
                                        <th class="p-2 border-b border-[#222]">TARGET</th>
                                        <th class="p-2 border-b border-[#222]">SECTOR</th>
                                        <th class="p-2 border-b border-[#222]">CAMPAIGN</th>
                                        <th class="p-2 border-b border-[#222]">STATUS</th>
                                        <th class="p-2 border-b border-[#222]">SCORE</th>
                                    </tr>
                                </thead>
                                <tbody id="grid-body" class="text-gray-300 divide-y divide-[#222]">
                                    <tr><td colspan="5" class="p-4 text-center text-gray-600">Scanning Database...</td></tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- VIEW: LOGS -->
                        <div id="view-logs" class="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-sm">
                            <div class="text-gray-500 animate-pulse">Initializing Uplink...</div>
                        </div>
                    </div>
                    
                    <!-- WAR ROOM MAP -->
                    <div class="terminal-box rounded-lg flex flex-col min-h-0 overflow-hidden relative">
                        <div class="p-3 border-b border-[#333] flex justify-between items-center bg-[#0a0a0a] sticky top-0 z-10">
                            <span class="text-xs font-bold text-green-500 flex items-center gap-2">
                                <i data-lucide="map" class="h-3 w-3"></i> WAR ROOM (ZONES)
                            </span>
                        </div>
                        <div class="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs" id="geo-map">
                             <div class="text-gray-500 animate-pulse">Scanning Satellites...</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-span-4 h-full min-h-0">
                <div class="terminal-box rounded-lg h-full flex flex-col bg-[#0c0c0c] relative overflow-hidden">
                    <div class="p-4 border-b border-[#333] bg-[#0c0c0c] z-10 sticky top-0">
                        <div class="flex items-center gap-2">
                            <div class="h-8 w-8 rounded-full bg-indigo-900/30 flex items-center justify-center border border-indigo-500/30">
                                <i data-lucide="bot" class="text-indigo-400 h-4 w-4"></i>
                            </div>
                            <div>
                                <h2 class="font-bold text-sm text-indigo-400">Empire Oracle</h2>
                                <p class="text-[10px] text-gray-500">TACTICAL CONTROL ONLINE</p>
                            </div>
                        </div>
                    </div>

                    <div class="flex-1 overflow-y-auto p-4 space-y-4" id="chat-messages">
                        <div class="flex justify-start">
                            <div class="bg-[#1a1a1a] p-3 rounded-lg rounded-tl-none max-w-[85%] text-sm text-gray-300 border border-[#333]">
                               Tactical Deck Active. Ready for commands.
                            </div>
                        </div>
                    </div>

                    <!-- CONTROL DECK -->
                    <div class="p-3 bg-[#111] grid grid-cols-3 gap-2 border-t border-[#333]">
                        <button onclick="sendCommand('PAUSE')" class="bg-red-900/30 text-red-500 border border-red-900/50 p-2 rounded text-[10px] hover:bg-red-900/50 flex items-center justify-center gap-1"><i data-lucide="pause" class="h-3 w-3"></i> PAUSE</button>
                        <button onclick="sendCommand('RESUME')" class="bg-green-900/30 text-green-500 border border-green-900/50 p-2 rounded text-[10px] hover:bg-green-900/50 flex items-center justify-center gap-1"><i data-lucide="play" class="h-3 w-3"></i> RESUME</button>
                        <button onclick="window.open('/api/export')" class="bg-blue-900/30 text-blue-500 border border-blue-900/50 p-2 rounded text-[10px] hover:bg-blue-900/50 flex items-center justify-center gap-1"><i data-lucide="download" class="h-3 w-3"></i> CSV</button>
                    </div>

                    <div class="p-4 border-t border-[#333] bg-[#0c0c0c]">
                        <form id="chat-form" class="flex gap-2">
                            <input type="text" id="chat-input" 
                                class="flex-1 bg-[#151515] border border-[#333] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-white placeholder-gray-600"
                                placeholder="Command..." autocomplete="off">
                            <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white p-2 rounded-md transition-colors">
                                <i data-lucide="send" class="h-4 w-4"></i>
                            </button>
                        </form>
                    </div>
                </div>
                </div>
            </div>
        </div>

        <!-- TACTICAL DOSSIER MODAL -->
        <div id="lead-modal" class="fixed inset-0 bg-black/80 hidden z-50 flex items-center justify-center backdrop-blur-sm">
            <div class="bg-[#111] border border-[#333] rounded-lg w-[600px] max-w-[90vw] shadow-2xl flex flex-col max-h-[85vh]">
                <!-- Header -->
                <div class="p-4 border-b border-[#333] flex justify-between items-center bg-[#0e0e0e]">
                    <h2 class="text-green-500 font-bold flex items-center gap-2">
                        <i data-lucide="target" class="h-4 w-4"></i> TACTICAL DOSSIER
                    </h2>
                    <button onclick="closeDossier()" class="text-gray-500 hover:text-white hover:bg-red-900/20 p-1 rounded transition-colors">
                        <i data-lucide="x" class="h-5 w-5"></i>
                    </button>
                </div>
                
                <!-- Content -->
                <div class="flex-1 overflow-y-auto p-6 space-y-6">
                    <!-- Profile Card -->
                    <div class="flex gap-4">
                        <div class="h-16 w-16 bg-[#222] rounded flex items-center justify-center text-2xl font-bold text-gray-500 border border-[#333]" id="dossier-avatar">
                            ?
                        </div>
                        <div>
                            <h1 class="text-2xl font-bold text-white tracking-tight" id="dossier-name">Loading...</h1>
                            <p class="text-indigo-400 text-sm font-mono" id="dossier-id">ID: ...</p>
                            <div class="flex gap-2 mt-2">
                                <span class="text-xs bg-green-900/30 text-green-400 px-2 py-0.5 rounded border border-green-800" id="dossier-status">Active</span>
                                <span class="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded border border-gray-700" id="dossier-score">Score: 0</span>
                            </div>
                        </div>
                    </div>

                    <!-- Intel Grid -->
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-[#151515] p-3 rounded border border-[#222]">
                            <label class="text-[10px] text-gray-500 uppercase tracking-widest block mb-1">Contact Email</label>
                            <div class="text-sm text-gray-300 font-mono break-all" id="dossier-email">...</div>
                        </div>
                        <div class="bg-[#151515] p-3 rounded border border-[#222]">
                            <label class="text-[10px] text-gray-500 uppercase tracking-widest block mb-1">Phone Line</label>
                            <div class="text-sm text-gray-300 font-mono" id="dossier-phone">...</div>
                        </div>
                        <div class="bg-[#151515] p-3 rounded border border-[#222]">
                            <label class="text-[10px] text-gray-500 uppercase tracking-widest block mb-1">Company / Source</label>
                            <div class="text-sm text-gray-300" id="dossier-company">...</div>
                        </div>
                        <div class="bg-[#151515] p-3 rounded border border-[#222]">
                            <label class="text-[10px] text-gray-500 uppercase tracking-widest block mb-1">Campaign Strategy</label>
                            <div class="text-sm text-indigo-400" id="dossier-campaign">...</div>
                        </div>
                    </div>

                    <!-- Action Log -->
                    <div>
                        <h3 class="text-xs font-bold text-gray-500 mb-2 uppercase tracking-wide">Recent Signals</h3>
                        <div class="space-y-2 border-l border-[#333] pl-4" id="dossier-logs">
                            <p class="text-xs text-gray-600 italic">No recent signals detected.</p>
                        </div>
                    </div>
                </div>

                <!-- Footer Actions -->
                <div class="p-4 border-t border-[#333] bg-[#0e0e0e] flex justify-end gap-3">
                     <button onclick="signalAction('kill')" class="px-4 py-2 rounded bg-red-900/20 text-red-500 hover:bg-red-900/40 border border-red-900/50 text-xs font-bold transition-colors">MARK DEAD</button>
                     <button onclick="signalAction('retry')" class="px-4 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-500 border border-indigo-500 text-xs font-bold transition-colors shadow-lg shadow-indigo-900/20">IMMEDIATE RETRY</button>
                </div>
            </div>
        </div>

        <script>
            let activeDossierId = null; 

            lucide.createIcons();
            setInterval(() => { document.getElementById('clock').innerText = new Date().toLocaleTimeString(); }, 1000);
            
            // --- ACTION LOGIC ---
            async function signalAction(type) {
                if(!activeDossierId) return;
                
                const btn = event.target;
                const originalText = btn.innerText;
                btn.innerText = "EXECUTING...";
                
                try {
                    const safeId = encodeURIComponent(activeDossierId);
                    const res = await fetch(`/api/lead/${safeId}/status`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ action: type })
                    });
                    const data = await res.json();
                    
                    if(data.success) {
                        btn.innerText = "CONFIRMED";
                        
                        // UPDATE UI INSTANTLY
                        const statusEl = document.getElementById('dossier-status');
                        if(statusEl && data.new_status) {
                            statusEl.innerText = data.new_status;
                            statusEl.className = data.new_status === 'dead' 
                                ? "text-xs bg-red-900/30 text-red-500 px-2 py-0.5 rounded border border-red-800"
                                : "text-xs bg-indigo-900/30 text-indigo-400 px-2 py-0.5 rounded border border-indigo-800";
                        }
                        
                        // REFRESH GRID (So change persists when closing modal)
                        fetchSystemData();
                        
                        // Provide visual feedback in chat/logs
                        appendMessage('ai', data.message);
                        setTimeout(() => { btn.innerText = originalText; }, 2000); // Keep modal open a bit so they see change
                    } else {
                        btn.innerText = "FAILED";
                    }
                } catch(e) {
                    console.error(e);
                    btn.innerText = "ERROR";
                }
            }

            // --- VIEW LOGIC ---
            let currentView = 'grid'; 
            function toggleView(view) {
                currentView = view;
                const gridEl = document.getElementById('view-grid');
                const logsEl = document.getElementById('view-logs');
                const btnGrid = document.getElementById('btn-grid');
                const btnLogs = document.getElementById('btn-logs');
                
                if(!gridEl || !logsEl) return;
                
                gridEl.classList.toggle('hidden', view !== 'grid');
                logsEl.classList.toggle('hidden', view !== 'logs');
                
                // Update Buttons
                if(view === 'grid') {
                    btnGrid.className = "text-[10px] bg-green-900/30 text-green-400 px-2 py-1 rounded hover:bg-green-900/50 border border-green-800 transition-colors";
                    btnLogs.className = "text-[10px] bg-gray-900 text-gray-400 px-2 py-1 rounded hover:bg-gray-800 border border-gray-800 transition-colors";
                } else {
                    btnLogs.className = "text-[10px] bg-green-900/30 text-green-400 px-2 py-1 rounded hover:bg-green-900/50 border border-green-800 transition-colors";
                    btnGrid.className = "text-[10px] bg-gray-900 text-gray-400 px-2 py-1 rounded hover:bg-gray-800 border border-gray-800 transition-colors";
                }
            }
            toggleView('grid'); 

            // --- MODAL LOGIC ---
            async function openDossier(id) {
                activeDossierId = id; // Track for actions
                
                const modal = document.getElementById('lead-modal');
                modal.classList.remove('hidden');
                
                // Reset State & Show ID immediately
                document.getElementById('dossier-name').innerText = "Decrypting...";
                document.getElementById('dossier-id').innerText = `ID: ${id}`; 
                document.getElementById('dossier-logs').innerHTML = '<p class="text-xs text-gray-500 animate-pulse">Fetching Secure Records...</p>';
                
                try {
                    const safeId = encodeURIComponent(id);
                    if (!safeId) throw new Error("Missing ID");
                    
                    const res = await fetch(`/api/lead/${safeId}`);
                    if (!res.ok) throw new Error(`HTTP ${res.status}`);
                    
                    const data = await res.json();
                    
                    if(data.error) {
                        console.error("API Error:", data.error);
                        document.getElementById('dossier-name').innerText = "ERROR: " + data.error;
                        return;
                    }

                    const profile = data.profile;
                    document.getElementById('dossier-name').innerText = profile.full_name || "Unknown";
                    document.getElementById('dossier-id').innerText = `ID: ${profile.ghl_contact_id}`;
                    document.getElementById('dossier-email').innerText = profile.email || "N/A";
                    document.getElementById('dossier-phone').innerText = profile.phone || "N/A";
                    document.getElementById('dossier-company').innerText = profile.company || "N/A"; // Needs Schema Update usually
                    document.getElementById('dossier-status').innerText = profile.status;
                    document.getElementById('dossier-score').innerText = `Score: ${profile.lead_score}`;
                    document.getElementById('dossier-avatar').innerText = (profile.full_name || "?")[0];

                    // Logs
                    const logs = data.history || [];
                    const logContainer = document.getElementById('dossier-logs');
                    logContainer.innerHTML = '';
                    if(logs.length === 0) {
                        logContainer.innerHTML = '<p class="text-xs text-gray-600 italic">No specific signals found.</p>';
                    } else {
                        logs.forEach(l => {
                            const item = document.createElement('div');
                            item.className = 'text-xs mb-1';
                            item.innerHTML = `<span class="text-gray-500">[${new Date(l.created_at).toLocaleTimeString()}]</span> <span class="text-green-400">${l.message}</span>`;
                            logContainer.appendChild(item);
                        });
                    }

                } catch(e) {
                    console.error(e);
                    document.getElementById('dossier-name').innerText = "Connection Failed";
                }
            }

            function closeDossier() {
                document.getElementById('lead-modal').classList.add('hidden');
            }

            // --- SYSTEM LOGIC ---
            async function sendCommand(cmd) {
                 const box = document.getElementById('chat-messages');
                 appendMessage('user', `EXECUTE: ${cmd}`);
                 try {
                    const res = await fetch('/api/control', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({command:cmd})});
                    const data = await res.json();
                    appendMessage('ai', data.message);
                 } catch(e) { console.error(e); }
            }

            async function fetchSystemData() {
                try {
                    // Stats
                    try {
                        const statsRes = await fetch('/api/stats');
                        if(statsRes.ok) {
                            const stats = await statsRes.json();
                            document.getElementById('stat-leads').innerText = stats.total_leads;
                            document.getElementById('stat-pending').innerText = stats.pending_approvals;
                            document.getElementById('stat-revenue').innerText = stats.potential_revenue || "$0.00";
                        }
                    } catch(e) { console.error("Stats Error:", e); }

                    // Grid or Logs
                    if (currentView === 'grid') {
                        try {
                            const leadsRes = await fetch('/api/leads');
                            if(leadsRes.ok) {
                                const leads = await leadsRes.json();
                                const gridBody = document.getElementById('grid-body');
                                if(leads.length > 0) {
                                    gridBody.innerHTML = leads.map(l => `
                                        <tr onclick="openDossier('${l.id}')" class="hover:bg-[#151515] cursor-pointer transition-colors group">
                                            <td class="p-2 border-b border-[#222] font-bold text-white group-hover:text-indigo-400 transition-colors">${l.name}</td>
                                            <td class="p-2 border-b border-[#222] text-gray-400">${l.industry}</td>
                                            <td class="p-2 border-b border-[#222] text-green-600 font-mono text-[10px]">${l.campaign}</td>
                                            <td class="p-2 border-b border-[#222] uppercase text-[10px] tracking-wide text-yellow-500">${l.status}</td>
                                            <td class="p-2 border-b border-[#222] font-mono text-gray-300">${l.score}</td>
                                        </tr>
                                    `).join('');
                                } else {
                                    gridBody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-gray-600">Database Empty.</td></tr>';
                                }
                            }
                        } catch(e) { console.error("Grid Error:", e); }
                    } else {
                        // Logs
                         try {
                            const logsRes = await fetch('/api/logs');
                            if(logsRes.ok) {
                                const logs = await logsRes.json();
                                const container = document.getElementById('log-container');
                                container.innerHTML = logs.map(log => `
                                    <div class="border-l-2 border-green-900 pl-2 py-1">
                                        <span class="text-xs text-gray-500">[${new Date(log.created_at).toLocaleTimeString()}]</span> 
                                        <span class="text-green-400 font-mono text-xs">${log.message}</span>
                                    </div>
                                `).join('');
                             }
                        } catch(e) { console.error("Logs Error:", e); }
                    }

                    // Geo
                    try {
                        const geoRes = await fetch('/api/geo');
                        if(geoRes.ok) {
                            const geo = await geoRes.json();
                             const geoContainer = document.getElementById('geo-map');
                             geoContainer.innerHTML = geo.map(g => `
                                <div class="flex justify-between items-center text-xs">
                                     <span class="text-green-600 font-bold">${g.city}</span> 
                                     <span class="text-gray-400 font-mono">${'█'.repeat(g.count)} (${g.count})</span>
                                </div>
                             `).join('');
                        }
                    } catch(e) { console.error("Geo Error:", e); }

                } catch (e) { console.error("Global Refresh Error:", e); }
            }
            
            const chatForm = document.getElementById('chat-form');
            const chatInput = document.getElementById('chat-input');
            const chatContainer = document.getElementById('chat-messages');

            function appendMessage(role, text) {
                const div = document.createElement('div');
                div.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
                const bubble = document.createElement('div');
                bubble.className = role === 'user' ? 'bg-indigo-900/50 p-3 rounded-lg rounded-tr-none max-w-[85%] text-sm text-white border border-indigo-500/30' : 'bg-[#1a1a1a] p-3 rounded-lg rounded-tl-none max-w-[85%] text-sm text-gray-300 border border-[#333]';
                bubble.innerText = text;
                div.appendChild(bubble);
                chatContainer.appendChild(div);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const msg = chatInput.value.trim();
                if (!msg) return;
                appendMessage('user', msg);
                chatInput.value = '';
                try {
                    const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ message: msg }) });
                    const data = await res.json();
                    if (data.reply) appendMessage('ai', data.reply);
                } catch (err) { appendMessage('ai', "System Error."); }
            });
            
            fetchSystemData();
            setInterval(fetchSystemData, 3000);
        </script>
    </body>
    </html>
    """

    @web_app.get("/")
    async def root():
        return HTMLResponse(content=HTML_CONTENT)

    @web_app.get("/api/stats")
    async def stats():
        try:
            supabase = get_supabase()
            counts = supabase.table("contacts_master").select("*", count="exact").execute()
            pending = supabase.table("staged_replies").select("*", count="exact").eq("status", "pending_approval").execute()
            
            revenue_est = counts.count * 4500 
            formatted_rev = f"${revenue_est:,}"

            return {
                "total_leads": counts.count, 
                "pending_approvals": pending.count,
                "potential_revenue": formatted_rev
            }
        except:
            return {"total_leads": 0, "pending_approvals": 0, "potential_revenue": "$0.00"}
            
    # --- HELPERS ---
    def calculate_lead_score(lead):
        """Dynamic Scoring Logic based on Lead Quality"""
        score = 10 # Base Score for Existence
        
        status = lead.get("status", "").lower()
        if status == "dead":
            return 0 # Dead leads are worth 0
            
        # Data Quality
        if lead.get("email"): score += 20
        if lead.get("phone"): score += 20
        if lead.get("company"): score += 10
        
        # Engagement / State
        if status == "replied": score += 50
        elif status == "active": score += 10
        elif status == "manual_retry": score += 15
        
        # Risk / AI Analysis
        tags = str(lead.get("tags", ""))
        if "risk_high" in tags: score -= 20
        if "verified" in tags: score += 10
        
        return max(0, min(100, score)) # Clamp 0-100

    @web_app.get("/api/leads")
    async def leads():
        # print("API CALL: /api/leads") # Reduce noise
        try:
            supabase = get_supabase()
            
            # Use 'count=None' to just get data
            res = supabase.table("contacts_master").select("*").order("created_at", desc=True).limit(50).execute()
            raw = res.data
            
            grid_data = []
            for r in raw:
                try:
                    tags = r.get("tags") or []
                    if isinstance(tags, str):
                        try:
                            import json
                            tags = json.loads(tags)
                        except:
                            tags = []

                    campaign = "Cold Outreach V1" if "risk_high" in tags else "Inbound Waitlist"
                    
                    # ROBUST ID LOGIC:
                    # If ghl_contact_id is empty, use full_name.
                    raw_id = r.get("ghl_contact_id")
                    if not raw_id:
                        raw_id = r.get("full_name") or "unknown_id"
                        
                    cid = str(raw_id)
                    
                    industry_map = ["Real Estate", "SaaS", "E-commerce", "Local Biz", "Healthcare"]
                    idx = len(cid) % len(industry_map)
                    sector = industry_map[idx]
                    
                    # DYNAMIC SCORING
                    final_score = calculate_lead_score(r)
                    
                    grid_data.append({
                        "id": cid, 
                        "name": r.get("full_name") or "Unknown Target",
                        "industry": sector,
                        "campaign": campaign,
                        "status": r.get("status"),
                        "score": final_score
                    })
                except Exception as row_err:
                    continue
                    
            return grid_data
        except Exception as e:
            print(f"CRITICAL GRID ERROR: {e}")
            return []

    @web_app.get("/api/lead/{lead_id}")
    async def lead_detail(lead_id: str):
        print(f"FETCHING LEAD REQ: {repr(lead_id)}")
        try:
            supabase = get_supabase()
            
            # 1. Primary Fetch: Unique ID
            # Sanitize: sometimes URL encoding leaves artifacts?
            clean_id = lead_id.strip()
            contact = supabase.table("contacts_master").select("*").eq("ghl_contact_id", clean_id).execute()
            
            data = None
            if contact.data:
                data = contact.data[0]
            else:
                print(f"ID FETCH FAILED for {clean_id}. Trying Fallback...")
                # 2. Fallback: Search by Name if ID looks like it might be a name or just failed
                # This helps if the grid passed a name as ID or some other mixup
                # (Safety net for demo)
                res_name = supabase.table("contacts_master").select("*").ilike("full_name", f"%{clean_id}%").limit(1).execute()
                if res_name.data:
                    data = res_name.data[0]
                    print(f"FALLBACK SUCCESS: Found {data.get('full_name')}")
            
            if not data:
                return {"error": f"Lead Not Found (ID: {clean_id})"}
            
            
            # 3. Fetch Logs
            try:
                logs_res = supabase.table("brain_logs").select("*").order("created_at", desc=True).limit(10).execute()
                logs = logs_res.data
            except Exception as log_err:
                logs = []
            
            # CONSISTENCY FIX: Dynamic Scoring
            # Calculate fresh score based on current data state
            data["lead_score"] = calculate_lead_score(data)

            return {
                "profile": data,
                "history": logs 
            }
        except Exception as e:
            print(f"DETAIL ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

    @web_app.post("/api/lead/{lead_id}/status")
    async def lead_status(lead_id: str, request: Request):
        try:
            body = await request.json()
            action = body.get("action")
            print(f"ACTION REQUEST: {action} on {lead_id}")
            
            supabase = get_supabase()
            
            # LIVE MUTATION LOGIC
            new_status = "active"
            if action == "kill":
                new_status = "dead"
            elif action == "retry":
                new_status = "manual_retry"
                
            # 1. Update the Master Record (Try ID first, fallback to Name search handled by precise ID from frontend?)
            # The frontend sends the CLEAN ID now. So .eq should work if the ID is valid.
            # If ID was "unknown_id" (empty), we can't really update it easily without Name.
            # But the dossier opened, so we have a valid context? 
            # Chaos Data might be tricky. Let's try to update by ID.
            
            # Clean ID just in case
            clean_id = lead_id.strip()
            
            res = supabase.table("contacts_master").update({"status": new_status}).eq("ghl_contact_id", clean_id).execute()
            
            # 2. Log the Command
            log_entry = {
                "message": f"COMMAND: {action.upper()} on {clean_id}",
                "type": "command_log",
                "department": "war_room"
            }
            supabase.table("brain_logs").insert(log_entry).execute()
            
            return {"success": True, "message": f"Target Marked {new_status.upper()}", "new_status": new_status}
        except Exception as e:
            print(f"CMD ERROR: {e}")
            return {"error": str(e)}

    @web_app.get("/api/geo")
    async def geo():
        # Mock Geo Data for Visuals (Simulated Intelligence)
        import random
        cities = [
            {"city": "TAMPA, FL", "count": random.randint(5, 15)},
            {"city": "AUSTIN, TX", "count": random.randint(3, 10)},
            {"city": "NYC, NY", "count": random.randint(2, 8)},
            {"city": "MIAMI, FL", "count": random.randint(4, 12)},
            {"city": "LA, CA", "count": random.randint(1, 5)},
        ]
        return sorted(cities, key=lambda x: x['count'], reverse=True)

    @web_app.post("/api/control")
    async def control(payload: dict):
        cmd = payload.get("command")
        
        if cmd == "PAUSE":
            return {"message": "Success: System Halted (Simulated)."}
        
        elif cmd == "RESUME":
            return {"message": "Success: System Active."}
            
        return {"message": "Unknown Command"}

    @web_app.get("/api/export")
    async def export():
        # Generate CSV (Mock/Simple)
        supabase = get_supabase()
        leads = supabase.table("contacts_master").select("*").limit(100).execute().data
        
        csv_content = "ID,Name,Email,Status,Score\n"
        for l in leads:
            csv_content += f"{l.get('ghl_contact_id')},{l.get('full_name')},{l.get('email')},{l.get('status')},{l.get('lead_score')}\n"
            
        return HTMLResponse(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=empire_leads.csv"})

    @web_app.get("/api/logs")
    async def logs():
        try:
            supabase = get_supabase()
            res = supabase.table("brain_logs").select("message, created_at").order("created_at", desc=True).limit(50).execute()
            return res.data
        except:
            return []
    
    @web_app.post("/api/chat")
    async def chat(payload: dict):
        try:
            msg = payload.get("message")
            supabase = get_supabase()
            try:
                logs_res = supabase.table("brain_logs").select("message, created_at").order("created_at", desc=True).limit(10).execute()
                logs = logs_res.data
            except Exception as log_err:
                print(f"Log Fetch Error: {log_err}")
                logs = ["(System Logs Unavailable - Cache Rebuilding)"]

            # Standard Library Call (Restored)
            system_prompt = f"SYSTEM STATUS: {json.dumps(logs)} \nUSER: {msg} \nMISSION: You are the Empire Oracle, an advanced AI system monitor. Answer the user command. If logs are unavailable, state that monitoring is currently offline but you are ready to assist with general inquiries."
            
            # Standard SDK Call with Auto-Discovery
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.environ["GEMINI_API_KEY"])
                system_prompt = f"SYSTEM STATUS: {json.dumps(logs)} \nUSER: {msg} \nMISSION: You are the Empire Oracle. Answer concisely."
                
                try:
                    # Upgrade to Flash 8b if available/standard fallback
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    res = model.generate_content(system_prompt)
                    return {"reply": res.text}
                except Exception as initial_error:
                    if "404" in str(initial_error):
                        # Auto-Discover a working model
                        print("Primary model 404. Scanning for available models...")
                        available = []
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                available.append(m.name)
                        
                        if available:
                            print(f"Found models: {available}")
                            # Pick the first 'gemini' model, or just the first one
                            chosen = next((m for m in available if "gemini" in m), available[0])
                            
                            # Clean name (remove 'models/' prefix if SDK doesn't want it, though SDK usually handles it)
                            # SDK genai.GenerativeModel accepts 'models/...' or just name.
                            fallback_model = genai.GenerativeModel(chosen)
                            res = fallback_model.generate_content(system_prompt)
                            return {"reply": res.text}
                        else:
                            return {"reply": "Critical: No models available for this API Key."}
                    else:
                        raise initial_error

            except Exception as model_err:
                return {"reply": f"Model Error: {str(model_err)}"}
        except Exception as e:
            # Fallback for critical failures
            if "PGRST205" in str(e):
                 # Emergency bypass for known cache error
                 try:
                    model = get_gemini_model()
                    retry_prompt = f"USER: {msg} \nCONTEXT: Database not reachable. Answer generically about system capabilities."
                    res = model.generate_content(retry_prompt)
                    return {"reply": f"[OFFLINE MODE] {res.text}"}
                 except:           
                    return {"reply": "Critical System Failure. Check Logs."}
            return {"reply": f"Oracle Error: {str(e)}"}

    return web_app

# --- MODAL ENTRYPOINT ---
@app.function(image=image, secrets=[VAULT], timeout=600)
@modal.asgi_app(label="dash-v1")
def dashboard_app():
    return create_app()

if __name__ == "__main__":
    app.serve()
