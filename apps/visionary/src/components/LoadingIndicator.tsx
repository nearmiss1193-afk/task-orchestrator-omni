
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import React, { useState, useEffect } from 'react';

const loadingMessages = [
  "Synthesizing visual narrative...",
  "Calibrating brand alignment...",
  "Optimizing cinematic resolution...",
  "Consulting the strategic intelligence node...",
  "Rendering high-fidelity assets...",
  "Applying professional color grading...",
  "This operation requires significant computational logic...",
  "Synthesizing stakeholder value...",
  "Polishing the executive narrative...",
  "Finalizing production architecture...",
  "Reviewing creative coherence...",
  "Compiling multi-dimensional data...",
  "Enhancing aesthetic precision...",
  "Structuring global vision...",
  "Authenticating creative integrity...",
  "Ensuring narrative fluidity..."
];

const technicalInsights = [
  "PRO-TIP: Narrative extension preserves lighting and texture consistency.",
  "VEONTOLOGY: Fast models optimize for speed without compromising resolution.",
  "ARCHITECTURE: Each 7s segment contains hundreds of unique generated frames.",
  "STRATEGY: Using a starting frame (Selfie) anchors the character biometric.",
  "SYSTEM: Global synthesis time varies based on concurrent cloud render load.",
];

interface LoadingIndicatorProps {
  message?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ message }) => {
  const [messageIndex, setMessageIndex] = useState(0);
  const [insightIndex, setInsightIndex] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [lastPing, setLastPing] = useState<string | null>(null);
  const [heartbeat, setHeartbeat] = useState<string[]>([]);

  useEffect(() => {
    const msgInterval = setInterval(() => {
      setMessageIndex((prevIndex) => (prevIndex + 1) % loadingMessages.length);
      setInsightIndex((prev) => (prev + 1) % technicalInsights.length);
    }, 5000);

    const timeInterval = setInterval(() => {
      setElapsed(prev => prev + 1);
      
      // Update heartbeat log every 10 seconds to show active polling
      if ((elapsed + 1) % 10 === 0) {
        const now = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        setLastPing(now);
        setHeartbeat(prev => [`[${now}] Pinging Node... Operation Pending.`, ...prev].slice(0, 3));
      }
    }, 1000);

    return () => {
      clearInterval(msgInterval);
      clearInterval(timeInterval);
    };
  }, [elapsed]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col items-center justify-center p-16 bg-black rounded-[4rem] border-2 border-white/10 shadow-[0_0_120px_rgba(0,0,0,1)] max-w-xl w-full">
      <div className="relative w-32 h-32 mb-8">
        <div className="absolute inset-0 border-8 border-indigo-500/5 rounded-full"></div>
        <div className="absolute inset-0 border-8 border-t-indigo-500 rounded-full animate-spin shadow-[0_0_25px_#6366f1]"></div>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
           <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Elapsed</span>
           <span className="text-sm font-black text-white font-mono tracking-tighter">{formatTime(elapsed)}</span>
        </div>
      </div>
      
      <div className="text-center w-full mb-10">
        <h2 className="text-4xl font-black text-white tracking-tighter italic uppercase mb-3">
          {message || "Processing Synthesis"}
        </h2>
        <div className="h-1 w-32 bg-indigo-500/20 mx-auto rounded-full overflow-hidden mb-8">
           <div className="h-full bg-indigo-500 animate-[progress_15s_infinite] shadow-[0_0_10px_#6366f1]"></div>
        </div>
        <div className="h-10">
          <p className="text-[10px] text-indigo-400 font-black uppercase tracking-[0.4em] animate-pulse-indigo">
            {loadingMessages[messageIndex]}
          </p>
        </div>
      </div>

      <div className="w-full space-y-4">
        <div className="p-6 bg-white/[0.03] border border-white/10 rounded-2xl flex flex-col gap-3">
           <div className="flex justify-between items-center text-[9px] font-black uppercase tracking-widest text-gray-500 border-b border-white/5 pb-3">
              <span>Production Console</span>
              <span className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                Connection Live
              </span>
           </div>
           <div className="flex flex-col gap-2 font-mono text-[9px] text-gray-600 uppercase tracking-tighter overflow-hidden h-12">
              {heartbeat.length > 0 ? (
                heartbeat.map((log, i) => (
                  <div key={i} className={i === 0 ? "text-indigo-400 font-bold" : "opacity-40"}>{log}</div>
                ))
              ) : (
                <div className="animate-pulse">Initializing primary handshake with synthesis node...</div>
              )}
           </div>
        </div>

        <div className="p-4 bg-indigo-600/10 border border-indigo-500/20 rounded-xl">
           <p className="text-[9px] text-gray-400 font-black uppercase tracking-widest leading-relaxed text-center">
             <span className="text-indigo-500 mr-2">INSIGHT:</span>
             {technicalInsights[insightIndex]}
           </p>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;
