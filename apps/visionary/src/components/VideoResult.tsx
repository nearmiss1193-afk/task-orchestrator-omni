
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import React, { useEffect, useRef, useState } from 'react';
import {ArrowPathIcon, PlusIcon, SparklesIcon, FilmIcon, DownloadIcon, ShieldCheckIcon, ShareIcon} from './icons';
import { NarrativeScene } from '../types';

interface VideoResultProps {
  videoUrl: string;
  videoBlob: Blob | null;
  onRetry: () => void;
  onNewVideo: () => void;
  onExtend: () => void;
  canExtend: boolean;
  nextScene?: NarrativeScene;
  currentScene?: NarrativeScene;
  completedScenesCount: number;
  totalScenesCount: number;
  isFinished?: boolean;
  projectName?: string;
  isAutoMode?: boolean;
  onArchive?: () => void;
}

const VideoResult: React.FC<VideoResultProps> = ({
  videoUrl,
  videoBlob,
  onRetry,
  onNewVideo,
  onExtend,
  canExtend,
  nextScene,
  currentScene,
  completedScenesCount,
  totalScenesCount,
  isFinished = false,
  projectName = "Professional_Production",
  isAutoMode = false,
  onArchive
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [archiveStatus, setArchiveStatus] = useState<'idle' | 'saving' | 'persisted'>('idle');
  const [shareStatus, setShareStatus] = useState<'idle' | 'sharing' | 'shared'>('idle');
  const [downloading, setDownloading] = useState(false);
  
  const totalDuration = totalScenesCount * 7;

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play()
        .then(() => setIsPlaying(true))
        .catch(() => setIsPlaying(false));
    }
  }, [videoUrl]);

  const togglePlay = () => {
    if (videoRef.current) {
      if (videoRef.current.paused) {
        videoRef.current.play();
        setIsPlaying(true);
      } else {
        videoRef.current.pause();
        setIsPlaying(false);
      }
    }
  };

  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!videoBlob || downloading) return;
    
    setDownloading(true);
    try {
      const url = URL.createObjectURL(videoBlob);
      const a = document.createElement('a');
      a.href = url;
      const timestamp = new Date().getTime();
      const sanitizedProjectName = projectName?.toUpperCase().replace(/\s+/g, '_') || "STRATEGIC_ASSET";
      const fileName = isFinished 
        ? `MASTER_REEL_${sanitizedProjectName}_${timestamp}.mp4` 
        : `SCENE_0${completedScenesCount}_${timestamp}.mp4`;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } finally {
      setTimeout(() => setDownloading(false), 1000);
    }
  };

  const handlePersistToLibrary = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onArchive && archiveStatus === 'idle') {
      setArchiveStatus('saving');
      // Simulated delay for UI feedback
      setTimeout(() => {
        onArchive();
        setArchiveStatus('persisted');
        // Status resets after a visual confirmation period
        setTimeout(() => setArchiveStatus('idle'), 5000);
      }, 800);
    }
  };

  const handleShare = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (shareStatus !== 'idle') return;

    setShareStatus('sharing');
    await new Promise(resolve => setTimeout(resolve, 1500));
    const uniqueId = Math.random().toString(36).substring(2, 10).toUpperCase();
    const simulatedLink = `https://veovisionary.studio/v/${uniqueId}`;
    
    try {
      await navigator.clipboard.writeText(simulatedLink);
      setShareStatus('shared');
      setTimeout(() => setShareStatus('idle'), 3000);
    } catch (err) {
      console.error('Failed to copy share link:', err);
      setShareStatus('idle');
    }
  };

  const productionId = `PRD-${projectName.substring(0, 3).toUpperCase()}-${new Date().getTime().toString().slice(-6)}`;

  if (isFinished) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center animate-in fade-in duration-1000 overflow-y-auto custom-scrollbar p-10">
        <div className="w-full max-w-6xl flex flex-col items-center gap-10">
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-4">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_#22c55e]"></div>
              <span className="text-[10px] font-black text-green-500 uppercase tracking-[0.5em]">Synthesis Finalized • Master Ready</span>
            </div>
            <h2 className="text-5xl md:text-8xl font-black text-white italic tracking-tighter mb-4">{projectName?.toUpperCase()}</h2>
            <div className="flex items-center justify-center gap-6 text-[10px] font-mono text-gray-500 tracking-widest uppercase">
              <span>Ref ID: {productionId}</span>
              <span className="w-1 h-1 bg-gray-800 rounded-full"></span>
              <span>Runtime: {totalDuration}s</span>
              <span className="w-1 h-1 bg-gray-800 rounded-full"></span>
              <span>Codec: H.264 High-Profile</span>
            </div>
          </div>

          <div className="relative w-full aspect-video bg-black rounded-[2.5rem] overflow-hidden shadow-[0_0_120px_rgba(0,0,0,1)] border-2 border-white/10 cursor-pointer group" onClick={togglePlay}>
            <video ref={videoRef} src={videoUrl} loop className="w-full h-full object-contain" playsInline />
            {!isPlaying && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm group-hover:bg-black/20 transition-all">
                 <div className="w-24 h-24 bg-white text-black rounded-full flex items-center justify-center shadow-2xl transition-transform hover:scale-110">
                    <div className="w-0 h-0 border-t-[14px] border-t-transparent border-l-[24px] border-l-black border-b-[14px] border-b-transparent ml-2"></div>
                 </div>
              </div>
            )}
          </div>

          <div className="w-full flex flex-col lg:flex-row items-center justify-between gap-8 bg-white/[0.03] p-10 rounded-[3rem] border-2 border-white/10 shadow-2xl">
            <div className="text-left flex-grow">
               <h3 className="text-3xl font-black text-white italic mb-2 uppercase tracking-tighter">Export Control</h3>
               <p className="text-gray-400 text-[10px] max-w-sm uppercase font-bold tracking-[0.2em] leading-relaxed">Persist your high-fidelity asset to the Strategic Vault or export for global distribution.</p>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 w-full lg:w-auto shrink-0">
               <button 
                 onClick={handlePersistToLibrary} 
                 disabled={archiveStatus !== 'idle'}
                 className={`flex items-center justify-center gap-3 px-8 py-5 rounded-2xl text-[11px] font-black uppercase tracking-widest transition-all border-2 ${archiveStatus === 'persisted' ? 'bg-green-500 text-black border-green-500 shadow-[0_0_30px_rgba(34,197,94,0.3)]' : 'bg-black text-white border-white/20 hover:border-white hover:bg-white hover:text-black'}`}
               >
                 <ShieldCheckIcon className={`w-5 h-5 ${archiveStatus === 'saving' ? 'animate-pulse' : ''}`} />
                 {archiveStatus === 'saving' ? 'Persisting...' : archiveStatus === 'persisted' ? 'Saved to Vault' : 'Save to Library'}
               </button>
               
               <button 
                 onClick={handleShare}
                 disabled={shareStatus === 'sharing'}
                 className={`flex items-center justify-center gap-3 px-8 py-5 rounded-2xl text-[11px] font-black uppercase tracking-widest transition-all border-2 ${shareStatus === 'shared' ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/40' : 'bg-black text-white border-white/20 hover:border-white hover:bg-white hover:text-black'}`}
               >
                 <ShareIcon className={`w-5 h-5 ${shareStatus === 'sharing' ? 'animate-spin' : ''}`} />
                 {shareStatus === 'sharing' ? 'Linking...' : shareStatus === 'shared' ? 'Link Copied' : 'Share Link'}
               </button>

               <button 
                 onClick={handleDownload} 
                 disabled={downloading}
                 className="flex items-center justify-center gap-4 px-12 py-5 bg-indigo-600 hover:bg-indigo-500 text-white font-black rounded-2xl transition-all shadow-[0_0_40px_rgba(99,102,241,0.4)] border-2 border-indigo-400/30"
               >
                 <DownloadIcon className={`w-6 h-6 ${downloading ? 'animate-bounce' : ''}`} />
                 {downloading ? 'Exporting...' : 'Download Master'}
               </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl flex flex-col items-center justify-center gap-8 animate-in fade-in zoom-in duration-700 p-6 overflow-y-auto custom-scrollbar">
      <div className="w-full flex justify-between items-end px-2">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
             <div className="w-2.5 h-2.5 rounded-full animate-pulse bg-indigo-500 shadow-[0_0_12px_#6366f1]"></div>
             <span className="text-[11px] font-black text-indigo-500 uppercase tracking-widest">
               {isAutoMode ? 'Strategic Processing Node Active' : 'Sequence Node Ready'}
             </span>
          </div>
          <h2 className="text-4xl font-black text-white italic tracking-tighter uppercase">SCENE 0{completedScenesCount} SYNTHESIZED</h2>
        </div>
        <div className="text-right">
           <div className="text-[10px] font-black text-gray-500 mb-2 uppercase tracking-widest">Global Pipeline: {completedScenesCount} / {totalScenesCount}</div>
           <div className="h-2 w-56 bg-white/10 rounded-full overflow-hidden border border-white/5">
             <div className="h-full bg-indigo-500 shadow-[0_0_10px_#6366f1] transition-all duration-1000" style={{ width: `${(completedScenesCount / totalScenesCount) * 100}%` }}></div>
           </div>
        </div>
      </div>

      <div className="relative w-full aspect-video bg-black rounded-[3rem] overflow-hidden shadow-[0_0_100px_rgba(0,0,0,1)] border-2 border-white/10 cursor-pointer group" onClick={togglePlay}>
        <video ref={videoRef} src={videoUrl} loop className="w-full h-full object-contain" playsInline />
        {!isPlaying && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/40 group-hover:bg-black/20 transition-all">
             <div className="w-20 h-20 bg-white/10 backdrop-blur-md rounded-full flex items-center justify-center border-2 border-white/20">
                <div className="w-0 h-0 border-t-[10px] border-t-transparent border-l-[18px] border-l-white border-b-[10px] border-b-transparent ml-1"></div>
             </div>
          </div>
        )}
        {isAutoMode && (
          <div className="absolute top-10 right-10 px-6 py-3 bg-indigo-600 border-2 border-indigo-400/40 rounded-2xl text-[11px] font-black text-white animate-pulse uppercase tracking-widest shadow-2xl">
            Auto-Processing Next Segment...
          </div>
        )}
      </div>

      {!isAutoMode && (
        <div className="w-full grid grid-cols-1 md:grid-cols-4 gap-6">
           <div className="md:col-span-3 bg-[#0a0a0c] p-10 rounded-[2.5rem] border-2 border-white/10 flex items-center justify-between shadow-2xl">
              <div>
                 <p className="text-[11px] text-gray-600 font-black uppercase mb-1 tracking-widest">Strategic Halt</p>
                 <p className="text-2xl text-white font-black italic uppercase tracking-tighter">Initiate Segment 0{completedScenesCount + 1}?</p>
              </div>
              <div className="flex gap-4">
                 <button 
                  onClick={handlePersistToLibrary}
                  disabled={archiveStatus !== 'idle'}
                  className={`flex items-center gap-2 px-6 py-4 rounded-xl transition-all text-[10px] font-black uppercase tracking-widest border-2 ${archiveStatus === 'persisted' ? 'bg-green-500 text-black border-green-500' : 'bg-white/5 hover:bg-white hover:text-black text-gray-400 border-white/10'}`}
                 >
                   <ShieldCheckIcon className="w-4 h-4" /> {archiveStatus === 'persisted' ? 'Persisted' : 'Persist'}
                 </button>
                 <button onClick={handleDownload} className="flex items-center gap-3 px-8 py-4 bg-indigo-600/10 hover:bg-indigo-600 text-indigo-400 hover:text-white rounded-xl transition-all border-2 border-indigo-500/30 text-[11px] font-black uppercase tracking-widest shadow-lg shadow-indigo-600/10">
                   <DownloadIcon className="w-5 h-5" /> Download
                 </button>
              </div>
           </div>
           <div className="flex flex-col gap-3">
              <button onClick={onNewVideo} className="flex-grow p-5 bg-white text-black hover:bg-gray-200 rounded-2xl border-2 border-white text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-2 transition-all shadow-xl">
                 <PlusIcon className="w-4 h-4" /> New Vision
              </button>
              <button onClick={onRetry} className="flex-grow p-5 bg-black text-gray-500 hover:text-white border-2 border-white/10 hover:border-white/40 rounded-2xl text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-2 transition-all">
                 <ArrowPathIcon className="w-4 h-4" /> Re-Synthesize
              </button>
           </div>
        </div>
      )}
    </div>
  );
};

export default VideoResult;
