
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import React, { useState } from 'react';
import { NotepadData } from '../types';
import { XMarkIcon, SparklesIcon, DownloadIcon, FileTextIcon } from './icons';
import { brainstormIdeas } from '../services/geminiService';

interface NotepadProps {
  data: NotepadData;
  onChange: (data: NotepadData) => void;
  onClose: () => void;
}

const Notepad: React.FC<NotepadProps> = ({ data, onChange, onClose }) => {
  const [isBrainstorming, setIsBrainstorming] = useState(false);
  const [brainstormResult, setBrainstormResult] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');

  const handleBrainstorm = async () => {
    setIsBrainstorming(true);
    try {
      const result = await brainstormIdeas({ capabilities: data.capabilities, ideas: data.ideas });
      setBrainstormResult(result);
    } catch (e) {
      console.error(e);
    } finally {
      setIsBrainstorming(false);
    }
  };

  const handleManualSave = () => {
    setSaveStatus('saving');
    localStorage.setItem('veo_notepad', JSON.stringify(data));
    setTimeout(() => {
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 2000);
    }, 500);
  };

  return (
    <div className="fixed top-0 right-0 w-[30rem] h-full bg-[#000000] border-l-2 border-white/10 z-[120] p-10 flex flex-col animate-in slide-in-from-right duration-500 shadow-[-50px_0_150px_rgba(0,0,0,1)]">
      <div className="flex justify-between items-center mb-12">
        <div>
          <h3 className="text-2xl font-black text-white italic tracking-tighter">STRATEGY VAULT</h3>
          <p className="text-[10px] text-indigo-400 font-bold uppercase tracking-[0.3em]">Vision Architecture Node</p>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={handleManualSave}
            className={`px-4 py-2 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all border-2 ${saveStatus === 'saved' ? 'bg-green-500/10 text-green-500 border-green-500/30' : 'bg-white/5 text-gray-500 border-white/5 hover:border-white hover:text-white'}`}
          >
            {saveStatus === 'saving' ? 'Syncing...' : saveStatus === 'saved' ? 'Node Synced' : 'Sync to Cache'}
          </button>
          <button onClick={onClose} className="p-3 hover:bg-white/10 rounded-full transition-colors">
            <XMarkIcon className="w-6 h-6 text-white" />
          </button>
        </div>
      </div>

      <div className="flex-grow space-y-10 overflow-y-auto custom-scrollbar pr-4 mb-8">
        <section>
          <div className="flex justify-between items-center mb-4">
            <label className="text-[11px] font-black text-white uppercase tracking-[0.2em]">1. Core Infrastructure & Assets</label>
          </div>
          <textarea 
            value={data.capabilities}
            onChange={(e) => onChange({...data, capabilities: e.target.value})}
            placeholder="Document system specifications, enterprise logic, or unique value propositions..."
            className="w-full h-40 bg-[#0a0a0c] border-2 border-white/10 rounded-2xl p-6 text-xs text-gray-300 focus:border-indigo-500 focus:outline-none transition-all resize-none font-mono"
          />
        </section>

        <section>
          <div className="flex justify-between items-center mb-4">
            <label className="text-[11px] font-black text-white uppercase tracking-[0.2em]">2. Strategic Objectives</label>
            <button 
              onClick={handleBrainstorm}
              disabled={isBrainstorming || !data.capabilities}
              className="flex items-center gap-3 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-900 disabled:text-gray-700 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all border border-indigo-400/30 shadow-lg shadow-indigo-600/20"
            >
              {isBrainstorming ? 'Director is Thinking...' : 'AI Synthesis'}
              <SparklesIcon className="w-3 h-3" />
            </button>
          </div>
          <textarea 
            value={data.ideas}
            onChange={(e) => onChange({...data, ideas: e.target.value})}
            placeholder="Define the strategic narrative objectives. What problems are we solving at scale?"
            className="w-full h-40 bg-[#0a0a0c] border-2 border-white/10 rounded-2xl p-6 text-xs text-gray-300 focus:border-indigo-500 focus:outline-none transition-all resize-none"
          />
        </section>

        {brainstormResult && (
          <div className="p-8 bg-indigo-600/10 border-2 border-indigo-500/20 rounded-[2rem] animate-in zoom-in-95 duration-500">
            <div className="flex justify-between items-center mb-6">
              <span className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em]">Strategic Synthesis Output</span>
              <button 
                onClick={() => setBrainstormResult(null)}
                className="text-gray-600 hover:text-white text-[9px] font-black uppercase"
              >
                Clear
              </button>
            </div>
            <div className="prose prose-invert prose-xs text-gray-300 text-[12px] leading-relaxed font-medium">
              <div dangerouslySetInnerHTML={{ __html: brainstormResult.replace(/\n/g, '<br/>') }} />
            </div>
            <button 
              onClick={() => {
                onChange({...data, prompts: data.prompts + "\n\n--- STRATEGIC SUGGESTION ---\n" + brainstormResult});
                setBrainstormResult(null);
              }}
              className="w-full mt-6 py-4 bg-white text-black hover:bg-gray-200 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] transition-all"
            >
              Merge with Asset Library
            </button>
          </div>
        )}

        <section>
          <label className="text-[11px] font-black text-white uppercase tracking-[0.2em] block mb-4">3. Asset Library / Global Repository</label>
          <textarea 
            value={data.prompts}
            onChange={(e) => onChange({...data, prompts: e.target.value})}
            placeholder="Store finalized production prompts and strategic directives here..."
            className="w-full h-40 bg-[#0a0a0c] border-2 border-white/10 rounded-2xl p-6 text-xs text-gray-300 focus:border-indigo-500 focus:outline-none transition-all resize-none"
          />
        </section>
      </div>

      <div className="mt-auto pt-8 border-t-2 border-white/10 flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-4">
           <button className="flex items-center justify-center gap-3 py-4 bg-white/5 border border-white/10 hover:bg-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all">
             <FileTextIcon className="w-4 h-4" /> Export Dossier
           </button>
           <button className="flex items-center justify-center gap-3 py-4 bg-white/5 border border-white/10 hover:bg-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all">
             <DownloadIcon className="w-4 h-4" /> Copy Directives
           </button>
        </div>
        <p className="text-[9px] text-gray-700 font-black uppercase text-center tracking-[0.4em]">
          End-to-End Strategic Persistence Active
        </p>
      </div>
    </div>
  );
};

export default Notepad;
