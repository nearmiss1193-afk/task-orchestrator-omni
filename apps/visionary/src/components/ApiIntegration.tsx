
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import React, { useState } from 'react';
import { XMarkIcon, CodeIcon, DownloadIcon, ExternalLinkIcon, ShieldCheckIcon } from './icons';

interface ApiIntegrationProps {
  onClose: () => void;
}

const ApiIntegration: React.FC<ApiIntegrationProps> = ({ onClose }) => {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const generateKey = () => {
    const key = `VEO_LIVE_${Math.random().toString(36).substring(2, 15).toUpperCase()}`;
    setApiKey(key);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const integrationCode = `
// VEO STUDIO BRIDGE CLIENT
// Use this to trigger video generations from your external app or IDE

const generateVideo = async (prompt) => {
  const response = await fetch('https://api.veostudio.cloud/v1/generate', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ${apiKey || 'YOUR_API_KEY'}',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt: prompt,
      model: 'veo-3.1-fast-generate-preview',
      resolution: '720p'
    })
  });
  return await response.json();
};
  `.trim();

  return (
    <div className="fixed top-0 right-0 w-[32rem] h-full bg-[#000000] border-l-2 border-white/20 z-[110] p-10 flex flex-col animate-in slide-in-from-right duration-500 shadow-[-100px_0_150px_rgba(0,0,0,1)]">
      <div className="flex justify-between items-center mb-12">
        <div>
          <h3 className="text-2xl font-black text-white italic tracking-tighter">DEVELOPER BRIDGE</h3>
          <p className="text-[10px] text-indigo-400 font-bold uppercase tracking-[0.3em]">External API Integration</p>
        </div>
        <button onClick={onClose} className="p-3 hover:bg-white/10 rounded-full transition-colors border border-transparent hover:border-white/10">
          <XMarkIcon className="w-6 h-6 text-white" />
        </button>
      </div>

      <div className="flex-grow space-y-8 overflow-y-auto custom-scrollbar pr-4">
        <section>
          <label className="text-[11px] font-black text-white uppercase tracking-widest block mb-4">1. Project Access Token</label>
          <div className="p-6 bg-[#0a0a0c] border-2 border-white/10 rounded-2xl flex flex-col gap-4">
            {apiKey ? (
              <div className="flex items-center justify-between gap-4">
                <code className="text-indigo-400 font-mono text-sm break-all font-bold">{apiKey}</code>
                <button 
                  onClick={() => copyToClipboard(apiKey)}
                  className="px-4 py-2 bg-white text-black text-[10px] font-black uppercase rounded-lg hover:bg-gray-200 transition-colors shrink-0"
                >
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
            ) : (
              <button 
                onClick={generateKey}
                className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-black uppercase tracking-widest text-[11px] rounded-xl transition-all shadow-lg shadow-indigo-600/20"
              >
                Generate Production Key
              </button>
            )}
            <p className="text-[9px] text-gray-500 font-bold uppercase tracking-tight">
              Use this key to authorize requests from Antigravity, VS Code, or custom web apps.
            </p>
          </div>
        </section>

        <section>
          <div className="flex justify-between items-center mb-4">
            <label className="text-[11px] font-black text-white uppercase tracking-widest">2. Code Snippet (Javascript)</label>
            <button 
              onClick={() => copyToClipboard(integrationCode)}
              className="text-[9px] font-black text-indigo-400 hover:text-white uppercase tracking-widest flex items-center gap-1"
            >
              <CodeIcon className="w-3 h-3" /> Copy Snippet
            </button>
          </div>
          <div className="relative group">
            <pre className="p-6 bg-black border-2 border-white/10 rounded-2xl overflow-x-auto text-[11px] font-mono text-gray-400 leading-relaxed custom-scrollbar">
              {integrationCode}
            </pre>
          </div>
        </section>

        <section>
          <label className="text-[11px] font-black text-white uppercase tracking-widest block mb-4">3. Webhook Endpoints</label>
          <div className="space-y-3">
             {[
               { name: "Trigger Render", type: "POST", endpoint: "/v1/generate" },
               { name: "Fetch Status", type: "GET", endpoint: "/v1/status/:id" },
               { name: "Stream Content", type: "WEBSOCKET", endpoint: "/v1/live" }
             ].map((node, i) => (
               <div key={i} className="flex items-center justify-between p-4 bg-white/[0.03] border border-white/5 rounded-xl">
                 <div>
                    <div className="text-[9px] text-gray-500 font-black uppercase mb-0.5">{node.name}</div>
                    <code className="text-[10px] font-bold text-white font-mono">{node.endpoint}</code>
                 </div>
                 <div className="text-[8px] font-black px-2 py-1 bg-white/10 text-white rounded uppercase">{node.type}</div>
               </div>
             ))}
          </div>
        </section>
      </div>

      <div className="mt-auto pt-8 border-t-2 border-white/10 space-y-4">
         <button className="w-full flex items-center justify-center gap-3 py-5 bg-white text-black font-black uppercase tracking-[0.2em] text-[11px] rounded-2xl hover:bg-gray-200 transition-all">
           <ExternalLinkIcon className="w-4 h-4" /> View Documentation
         </button>
         <div className="flex items-center justify-center gap-2 text-[10px] text-gray-600 font-bold uppercase tracking-widest">
            <ShieldCheckIcon className="w-3 h-3 text-green-500" /> Secure SSL Connection Enabled
         </div>
      </div>
    </div>
  );
};

export default ApiIntegration;
