
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import React, { useState } from 'react';
import { SparklesIcon, FilmIcon, DownloadIcon, TvIcon, RectangleStackIcon } from './icons';
import { NarrativePlan } from '../types';

interface FinishedArchive {
  url: string;
  blobBase64?: string;
  projectName: string;
  timestamp: number;
}

interface NarrativePanelProps {
  onSubmit: (text: string, duration: number) => void;
  vault: FinishedArchive[];
  onRestore: (entry: FinishedArchive) => void;
  options: NarrativePlan[];
  onSelectOption: (plan: NarrativePlan) => void;
  isChoosing: boolean;
}

const NarrativePanel: React.FC<NarrativePanelProps> = ({ 
  onSubmit, 
  vault, 
  onRestore, 
  options, 
  onSelectOption, 
  isChoosing 
}) => {
  const [text, setText] = useState('');
  const [duration, setDuration] = useState(21);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) onSubmit(text, duration);
  };

  const estimatedTotalCost = duration * 0.10;

  if (isChoosing) {
    return (
      <div className="flex-grow flex flex-col items-center justify-start w-full p-4 md:p-12 animate-in fade-in slide-in-from-bottom-8 duration-700 overflow-y-auto custom-scrollbar">
        <div className="text-center mb-16 mt-8">
          <div className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.5em] mb-4 animate-pulse">Select Production Track</div>
          <h2 className="text-6xl md:text-7xl font-black text-white italic tracking-tighter mb-4">ORCHESTRATE YOUR VISION</h2>
          <p className="text-gray-400 text-xs max-w-md mx-auto uppercase tracking-widest font-bold leading-relaxed">
            Pick a storyboard direction below. Once selected, the Auto-Pilot will chain render all segments.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-7xl pb-20">
          {options.map((option, i) => (
            <div 
              key={i}
              onClick={() => onSelectOption(option)}
              className="group relative bg-[#0a0a0c] border-2 border-white/10 rounded-[3rem] p-10 cursor-pointer hover:border-indigo-500 hover:bg-white/[0.03] transition-all hover:-translate-y-3 shadow-[0_0_80px_rgba(0,0,0,1)] flex flex-col"
            >
              <div className="absolute top-10 right-10 text-indigo-500/10 group-hover:text-indigo-500/40 transition-colors">
                <RectangleStackIcon className="w-16 h-16" />
              </div>

              <div className="mb-10">
                <div className="text-[9px] font-black text-indigo-400 uppercase tracking-[0.4em] mb-3">Direction 0{i+1}</div>
                <h3 className="text-3xl font-black text-white italic mb-2 uppercase tracking-tighter leading-none">{option.styleName}</h3>
                <div className="flex items-center gap-4 mt-4">
                   <span className="text-[11px] text-white font-mono font-black bg-white/10 px-3 py-1 rounded-full uppercase">COST: ${option.estimatedCost.toFixed(2)}</span>
                   <span className="w-1 h-1 bg-gray-700 rounded-full"></span>
                   <span className="text-[11px] text-gray-400 font-mono font-bold uppercase">BUILD: ~4 MIN</span>
                </div>
              </div>

              <div className="flex-grow space-y-6 mb-12">
                {option.scenes.map((s, si) => (
                  <div key={si} className="flex gap-4 p-5 bg-black border border-white/10 rounded-2xl group-hover:border-white/30 transition-colors">
                    <div className="text-[10px] font-black text-indigo-500 mt-0.5">0{si+1}</div>
                    <div className="text-[12px] text-gray-300 leading-snug">
                      <span className="text-white font-black uppercase block mb-1 tracking-tight">{s.title}</span>
                      {s.description.substring(0, 90)}...
                    </div>
                  </div>
                ))}
              </div>

              <button className="w-full py-6 bg-white text-black font-black uppercase tracking-[0.2em] text-[11px] rounded-2xl group-hover:bg-indigo-600 group-hover:text-white transition-all shadow-xl active:scale-95">
                Initialize Sequence
              </button>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex-grow flex flex-col items-center justify-start max-w-6xl mx-auto w-full p-4 md:p-12 animate-in fade-in duration-1000 overflow-y-auto custom-scrollbar">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-20 w-full items-start mt-8 pb-20">
        
        {/* COMMAND CENTER */}
        <div className="md:col-span-3 flex flex-col">
          <div className="mb-12">
            <div className="inline-flex items-center gap-3 px-5 py-3 bg-indigo-600 text-white rounded-full border-2 border-indigo-500 mb-8 shadow-[0_0_20px_rgba(99,102,241,0.4)]">
              <div className="w-2.5 h-2.5 bg-white rounded-full animate-pulse"></div>
              <span className="text-[10px] font-black uppercase tracking-[0.2em]">Master Production Engine v3.1</span>
            </div>
            <h2 className="text-7xl md:text-8xl font-black text-white mb-6 tracking-tighter italic leading-[0.8]">Build Your<br/>Master Reel</h2>
            <p className="text-white text-xs leading-relaxed max-w-sm uppercase tracking-widest font-black opacity-100 bg-white/5 p-4 rounded-xl border border-white/10">Drop your system capabilities below. Gemini will architect 3 cinematic directions before delivery.</p>
          </div>

          <form onSubmit={handleSubmit} className="w-full space-y-8">
            <div className="relative group">
               <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-white rounded-[2.5rem] blur opacity-10 group-focus-within:opacity-40 transition-opacity"></div>
               <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="PASTE SYSTEM CAPABILITIES HERE..."
                className="relative w-full h-72 bg-[#000000] border-4 border-white/10 rounded-[2rem] p-10 text-white focus:border-indigo-500 focus:outline-none resize-none transition-all placeholder:text-gray-800 text-2xl font-mono leading-relaxed"
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div className="bg-[#0a0a0c] p-10 rounded-[2rem] border-2 border-white/10 shadow-inner">
                  <div className="flex justify-between items-center mb-8">
                     <span className="text-[11px] font-black text-white uppercase tracking-widest">Runtime Target</span>
                     <span className="text-sm font-black text-black bg-white px-4 py-1.5 rounded-full font-mono">{duration}s</span>
                  </div>
                  <input 
                    type="range" min="7" max="49" step="7" 
                    value={duration} 
                    onChange={(e) => setDuration(parseInt(e.target.value))} 
                    className="w-full h-2 bg-white/10 rounded-full accent-indigo-500 cursor-pointer appearance-none"
                  />
                  <div className="flex justify-between text-[10px] text-white font-black uppercase mt-6 tracking-tighter">
                     <span>Teaser (7s)</span>
                     <span>Master (49s)</span>
                  </div>
               </div>

               <div className="bg-indigo-600 p-10 rounded-[2rem] flex flex-col justify-center shadow-2xl border-2 border-indigo-400/30">
                  <span className="text-[11px] font-black text-white/70 uppercase tracking-widest mb-2">Estimated Delivery</span>
                  <div className="text-5xl font-black text-white italic tracking-tighter">${estimatedTotalCost.toFixed(2)} USD</div>
                  <div className="text-[10px] text-white/50 font-black uppercase mt-4 tracking-widest">Authorized via Billing Key</div>
               </div>
            </div>

            <button
              type="submit"
              disabled={!text.trim()}
              className="group relative w-full py-10 bg-white hover:bg-gray-100 disabled:bg-gray-900 disabled:text-gray-800 text-black font-black rounded-[3rem] text-3xl transition-all shadow-[0_30px_60px_rgba(255,255,255,0.1)] border-b-[12px] border-gray-300 active:border-b-0 active:translate-y-3 uppercase tracking-tighter italic"
            >
              Analyze Production Paths
              <SparklesIcon className="inline w-8 h-8 ml-6 group-hover:rotate-12 transition-transform" />
            </button>
          </form>
        </div>

        {/* VAULT / SIDEBAR */}
        <div className="md:col-span-2 flex flex-col gap-10 h-full">
          <div className="flex flex-col gap-6">
             <div className="text-[11px] font-black text-white uppercase tracking-[0.3em] px-2 flex items-center justify-between">
                <span>Recent Productions</span>
                <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_#22c55e]"></span>
             </div>
             {vault.length > 0 ? (
               <div className="space-y-4">
                 {vault.map((entry, idx) => (
                   <div 
                     key={idx}
                     onClick={() => onRestore(entry)}
                     className="group bg-[#0a0a0c] border-2 border-white/10 rounded-[2.5rem] p-7 cursor-pointer hover:bg-white hover:border-white transition-all flex items-center gap-6"
                   >
                     <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center border border-white/5 group-hover:bg-black group-hover:border-black transition-all">
                        <FilmIcon className="w-8 h-8 text-gray-500 group-hover:text-indigo-500 transition-colors" />
                     </div>
                     <div className="flex-grow min-w-0">
                        <h4 className="text-md font-black text-white group-hover:text-black uppercase truncate italic">{entry.projectName}</h4>
                        <p className="text-[10px] text-gray-600 group-hover:text-gray-400 font-black uppercase mt-1 tracking-widest">{new Date(entry.timestamp).toLocaleDateString()}</p>
                     </div>
                   </div>
                 ))}
               </div>
             ) : (
               <div className="bg-black border-4 border-white/5 border-dashed rounded-[3rem] p-16 text-center flex flex-col items-center justify-center">
                  <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mb-8">
                    <FilmIcon className="w-10 h-10 text-gray-800" />
                  </div>
                  <h3 className="text-white font-black uppercase tracking-[0.3em] text-[11px] mb-3">Vault Offline</h3>
                  <p className="text-[10px] text-gray-700 max-w-[180px] font-black uppercase tracking-widest leading-relaxed">No completed Master Reels in current cache.</p>
               </div>
             )}
          </div>

          <div className="bg-[#0a0a0c] border-2 border-white/10 rounded-[2.5rem] p-10 mt-auto shadow-inner">
             <h4 className="text-[11px] font-black text-white uppercase tracking-[0.3em] mb-8 border-b border-white/10 pb-4">Live Pipeline Nodes</h4>
             <div className="space-y-8">
                {[
                  { label: "Visual core", value: "VEO 3.1 Fast", status: "ONLINE" },
                  { label: "Logic node", value: "GEMINI 3 PRO", status: "ONLINE" },
                  { label: "Vocal synth", value: "GEMINI TTS", status: "ONLINE" }
                ].map((item, i) => (
                  <div key={i} className="flex justify-between items-center group">
                    <div>
                      <div className="text-[9px] text-gray-600 font-black uppercase mb-1.5 tracking-widest">{item.label}</div>
                      <div className="text-[12px] text-white font-mono font-black group-hover:text-indigo-400 transition-colors uppercase">{item.value}</div>
                    </div>
                    <div className="text-[9px] px-4 py-1.5 bg-green-500/10 text-green-500 rounded-full font-black tracking-[0.2em] shadow-[0_0_15px_rgba(34,197,94,0.1)] border border-green-500/20">{item.status}</div>
                  </div>
                ))}
             </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default NarrativePanel;
