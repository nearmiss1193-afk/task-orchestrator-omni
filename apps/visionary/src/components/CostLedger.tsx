
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import React from 'react';
import { CostLedgerData } from '../types';
import { XMarkIcon, TrendingUpIcon, ArrowPathIcon } from './icons';

interface CostLedgerProps {
  data: CostLedgerData;
  onClose: () => void;
  onReset: () => void;
}

const CostLedger: React.FC<CostLedgerProps> = ({ data, onClose, onReset }) => {
  return (
    <div className="fixed top-0 right-0 w-[28rem] h-full bg-[#050505] border-l border-white/10 z-[100] p-8 flex flex-col animate-in slide-in-from-right duration-500 shadow-[-50px_0_100px_rgba(0,0,0,1)]">
      <div className="flex justify-between items-center mb-10">
        <div>
          <h3 className="text-xl font-black text-white italic tracking-tighter">COST LEDGER</h3>
          <p className="text-[9px] text-gray-600 font-bold uppercase tracking-widest">Real-Time Production Burn</p>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
          <XMarkIcon className="w-6 h-6 text-gray-500" />
        </button>
      </div>

      <div className="bg-indigo-600/5 border border-indigo-500/20 rounded-[2rem] p-8 mb-10 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10">
           <TrendingUpIcon className="w-24 h-24 text-indigo-500" />
        </div>
        <div className="relative z-10">
          <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2">Total Accumulated Spend</p>
          <div className="text-5xl font-black text-white italic tracking-tighter mb-4">
            ${data.totalBurn.toFixed(2)}
            <span className="text-xs text-indigo-400/50 ml-2 not-italic font-mono uppercase">USD</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-1.5 flex-grow bg-white/5 rounded-full overflow-hidden">
               <div className="h-full bg-indigo-500 shadow-[0_0_10px_#6366f1]" style={{ width: `${Math.min((data.totalBurn / 100) * 100, 100)}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-grow flex flex-col min-h-0">
        <div className="flex justify-between items-center mb-4">
           <span className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Transaction History</span>
           <button 
             onClick={onReset}
             className="text-[9px] font-black text-gray-700 hover:text-red-500 uppercase tracking-widest flex items-center gap-1 transition-colors"
           >
             <ArrowPathIcon className="w-3 h-3" /> Reset Ledger
           </button>
        </div>

        <div className="flex-grow overflow-y-auto custom-scrollbar pr-2 space-y-3">
          {data.history.length > 0 ? (
            data.history.map((entry) => (
              <div key={entry.id} className="bg-white/[0.02] border border-white/5 rounded-2xl p-4 flex justify-between items-center group hover:border-white/10 transition-colors">
                <div>
                  <div className="text-[11px] font-black text-white uppercase tracking-tight">{entry.projectName}</div>
                  <div className="text-[9px] text-gray-600 font-mono mt-0.5">
                    {entry.duration}S SEQUENCE • {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                <div className="text-sm font-black text-indigo-400 font-mono">
                  +${entry.cost.toFixed(2)}
                </div>
              </div>
            ))
          ) : (
            <div className="flex flex-col items-center justify-center h-40 text-center opacity-20">
               <TrendingUpIcon className="w-12 h-12 mb-4" />
               <p className="text-[10px] font-bold uppercase tracking-widest">No Transactions Logged</p>
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 pt-8 border-t border-white/5">
         <div className="p-4 bg-yellow-500/5 border border-yellow-500/10 rounded-xl">
            <p className="text-[9px] text-yellow-500/80 font-bold uppercase leading-relaxed">
              *Approximate calculation based on $0.10/second generation fee. Actual GCP billing may vary based on token overhead.
            </p>
         </div>
      </div>
    </div>
  );
};

export default CostLedger;
