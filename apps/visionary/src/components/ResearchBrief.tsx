
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import React from 'react';
import { SparklesIcon, TvIcon, ShieldCheckIcon, TrendingUpIcon } from './icons';

interface ResearchBriefProps {
  onProceed: () => void;
}

const ResearchBrief: React.FC<ResearchBriefProps> = ({ onProceed }) => {
  return (
    <div className="flex-grow flex flex-col items-center justify-center p-8 animate-in fade-in duration-1000 overflow-y-auto custom-scrollbar">
      <div className="max-w-5xl w-full py-12">
        <div className="mb-16 text-center">
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-indigo-500/10 border border-indigo-500/20 rounded-full mb-8">
            <SparklesIcon className="w-4 h-4 text-indigo-400" />
            <span className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em]">Strategic Intelligence Node</span>
          </div>
          <h2 className="text-6xl md:text-8xl font-black text-white italic tracking-tighter mb-6 leading-none">EXECUTIVE BRIEFING</h2>
          <p className="text-gray-500 text-xs max-w-2xl mx-auto uppercase tracking-[0.4em] font-black">
            Asset Scaling • Market Penetration • Vision Synthesis
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {/* Tier 1 */}
          <div className="bg-black border-2 border-white/5 p-10 rounded-[3rem] hover:border-white/20 transition-all flex flex-col">
            <div className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest">Model Alpha</div>
            <h3 className="text-3xl font-black text-white italic mb-2 uppercase tracking-tighter">Core Asset</h3>
            <p className="text-4xl font-black text-white mb-8">$199<span className="text-xs text-gray-700 font-black tracking-widest ml-2">/UNIT</span></p>
            <ul className="space-y-4 mb-10 flex-grow">
              <li className="text-[11px] text-gray-400 font-black uppercase flex gap-3">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 shrink-0"></div>
                Rapid Visual Synthesis (7s)
              </li>
              <li className="text-[11px] text-gray-400 font-black uppercase flex gap-3">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 shrink-0"></div>
                High-Impact Narrative
              </li>
              <li className="text-[11px] text-gray-400 font-black uppercase flex gap-3">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 shrink-0"></div>
                Standard API Gateway
              </li>
            </ul>
          </div>

          {/* Tier 2 */}
          <div className="bg-indigo-600/5 border-2 border-indigo-500/30 p-10 rounded-[3rem] relative overflow-hidden shadow-[0_0_100px_rgba(99,102,241,0.1)] flex flex-col">
            <div className="absolute top-0 right-0 px-6 py-2 bg-indigo-500 text-[9px] font-black text-white uppercase tracking-[0.2em]">Priority Tier</div>
            <div className="text-[10px] font-black text-indigo-400 uppercase mb-4 tracking-widest">Model Sigma</div>
            <h3 className="text-3xl font-black text-white italic mb-2 uppercase tracking-tighter">Enterprise</h3>
            <p className="text-4xl font-black text-white mb-8">$499<span className="text-xs text-gray-600 font-black tracking-widest ml-2">/MONTH</span></p>
            <ul className="space-y-4 mb-10 flex-grow">
              <li className="text-[11px] text-white font-black uppercase flex gap-3">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 shrink-0"></div>
                Extended Narrative Reels (49s)
              </li>
              <li className="text-[11px] text-white font-black uppercase flex gap-3">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 shrink-0"></div>
                Director-Level Autopilot
              </li>
              <li className="text-[11px] text-white font-black uppercase flex gap-3">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 shrink-0"></div>
                Premium Rendering Queue
              </li>
            </ul>
          </div>

          {/* Tier 3 */}
          <div className="bg-black border-2 border-white/5 p-10 rounded-[3rem] hover:border-white/20 transition-all flex flex-col">
            <div className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest">Model Omega</div>
            <h3 className="text-3xl font-black text-white italic mb-2 uppercase tracking-tighter">Global</h3>
            <p className="text-4xl font-black text-white mb-8">$1.2k<span className="text-xs text-gray-700 font-black tracking-widest ml-2">/MONTH</span></p>
            <ul className="space-y-4 mb-10 flex-grow">
              <li className="text-[11px] text-gray-400 font-black uppercase flex gap-3">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 shrink-0"></div>
                Unlimited Sequence Synthesis
              </li>
              <li className="text-[11px] text-gray-400 font-black uppercase flex gap-3">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 shrink-0"></div>
                Custom Neural Voice Cloning
              </li>
              <li className="text-[11px] text-gray-400 font-black uppercase flex gap-3">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 shrink-0"></div>
                Strategic Support Dedicated
              </li>
            </ul>
          </div>
        </div>

        <div className="bg-white/[0.02] p-10 rounded-[3rem] border-2 border-white/10 mb-16 shadow-inner">
          <h4 className="text-[11px] font-black text-indigo-400 uppercase tracking-[0.4em] mb-8 text-center">Executive Value Pillars</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
             {[
               { icon: <ShieldCheckIcon />, title: "Brand Integrity", desc: "Ensure visual consistency and professional authority across all stakeholders." },
               { icon: <TrendingUpIcon />, title: "Market Agility", desc: "Synthesize high-fidelity responses to market shifts in real-time." },
               { icon: <TvIcon />, title: "Strategic Synthesis", desc: "Transform complex enterprise logic into compelling cinematic narratives." }
             ].map((item, i) => (
               <div key={i} className="flex flex-col items-center text-center gap-4">
                 <div className="text-indigo-500 w-12 h-12 flex items-center justify-center bg-indigo-500/10 rounded-2xl mb-2">{item.icon}</div>
                 <div className="text-sm font-black text-white uppercase tracking-tight">{item.title}</div>
                 <p className="text-[10px] text-gray-500 leading-relaxed font-bold uppercase">{item.desc}</p>
               </div>
             ))}
          </div>
        </div>

        <button 
          onClick={onProceed}
          className="w-full py-10 bg-white hover:bg-gray-100 text-black font-black rounded-[3rem] text-3xl transition-all shadow-2xl border-b-[12px] border-gray-300 active:border-b-0 active:translate-y-3 uppercase tracking-tighter italic"
        >
          Initialize Strategic Suite
        </button>
      </div>
    </div>
  );
};

export default ResearchBrief;
