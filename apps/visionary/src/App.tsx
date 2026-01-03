
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import {Video} from '@google/genai';
import React, {useCallback, useEffect, useRef, useState} from 'react';
import ApiKeyDialog from './components/ApiKeyDialog';
import LoadingIndicator from './components/LoadingIndicator';
import PromptForm from './components/PromptForm';
import VideoResult from './components/VideoResult';
import NarrativePanel from './components/NarrativePanel';
import ResearchBrief from './components/ResearchBrief';
import Notepad from './components/Notepad';
import CostLedger from './components/CostLedger';
import ApiIntegration from './components/ApiIntegration';
import {generateVideo, generateNarrativeOptions, generateSpeech} from './services/geminiService';
import {
  AppState,
  GenerateVideoParams,
  GenerationMode,
  Resolution,
  VideoFile,
  NarrativePlan,
  VeoModel,
  AspectRatio,
  NotepadData,
  CostLedgerData,
  CostEntry,
  VoiceProfile,
  EmotionalTone,
  CharacterProfile,
} from './types';

interface FinishedArchive {
  url: string;
  blobBase64?: string;
  projectName: string;
  timestamp: number;
}

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>(AppState.IDLE);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastConfig, setLastConfig] = useState<GenerateVideoParams | null>(null);
  const [lastVideoObject, setLastVideoObject] = useState<Video | null>(null);
  const [lastVideoBlob, setLastVideoBlob] = useState<Blob | null>(null);
  const [showApiKeyDialog, setShowApiKeyDialog] = useState(false);
  
  const [vault, setVault] = useState<FinishedArchive[]>([]);
  const [characterVault, setCharacterVault] = useState<CharacterProfile[]>([]);
  const [notepad, setNotepad] = useState<NotepadData>({ ideas: '', prompts: '', capabilities: '' });
  const [showNotepad, setShowNotepad] = useState(false);
  const [showApiPanel, setShowApiPanel] = useState(false);

  // Financial tracking
  const [costLedger, setCostLedger] = useState<CostLedgerData>({ totalBurn: 0, history: [] });
  const [showLedger, setShowLedger] = useState(false);

  const audioContextRef = useRef<AudioContext | null>(null);
  const narrationBufferRef = useRef<AudioBuffer | null>(null);
  const musicSourceRef = useRef<AudioBufferSourceNode | null>(null);
  const narrationSourceRef = useRef<AudioBufferSourceNode | null>(null);

  const [narrativeOptions, setNarrativeOptions] = useState<NarrativePlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<NarrativePlan | null>(null);
  const [currentSceneIndex, setCurrentSceneIndex] = useState<number>(-1);
  const [completedSceneIds, setCompletedSceneIds] = useState<number[]>([]);
  const isAutoProcessingRef = useRef(false);
  const isGeneratingRef = useRef(false);

  useEffect(() => {
    const savedVault = localStorage.getItem('veo_vault');
    if (savedVault) try { setVault(JSON.parse(savedVault)); } catch (e) {}
    
    const savedCharVault = localStorage.getItem('veo_char_vault');
    if (savedCharVault) try { 
      const parsed = JSON.parse(savedCharVault);
      setCharacterVault(parsed); 
    } catch (e) {}

    const savedNotepad = localStorage.getItem('veo_notepad');
    if (savedNotepad) try { setNotepad(JSON.parse(savedNotepad)); } catch (e) {}

    const savedLedger = localStorage.getItem('veo_cost_ledger');
    if (savedLedger) try { setCostLedger(JSON.parse(savedLedger)); } catch (e) {}

    const checkApiKey = async () => {
      if (window.aistudio) {
        try { if (!(await window.aistudio.hasSelectedApiKey())) setShowApiKeyDialog(true); } 
        catch (error) { setShowApiKeyDialog(true); }
      }
    };
    checkApiKey();
    audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({sampleRate: 24000});
    return () => { if (audioContextRef.current) audioContextRef.current.close(); };
  }, []);

  useEffect(() => {
    localStorage.setItem('veo_notepad', JSON.stringify(notepad));
  }, [notepad]);

  useEffect(() => {
    localStorage.setItem('veo_cost_ledger', JSON.stringify(costLedger));
  }, [costLedger]);

  useEffect(() => {
    localStorage.setItem('veo_vault', JSON.stringify(vault));
  }, [vault]);

  useEffect(() => {
    localStorage.setItem('veo_char_vault', JSON.stringify(characterVault));
  }, [characterVault]);

  const recordCost = (duration: number, projectName: string) => {
    const cost = duration * 0.10;
    const newEntry: CostEntry = {
      id: Math.random().toString(36).substring(7),
      projectName: projectName,
      duration: duration,
      cost: cost,
      timestamp: Date.now()
    };
    setCostLedger(prev => ({
      totalBurn: prev.totalBurn + cost,
      history: [newEntry, ...prev.history].slice(0, 50)
    }));
  };

  const handleSaveToVault = async () => {
    if (!lastVideoBlob) return;
    const name = selectedPlan?.projectName || vault[0]?.projectName || "Strategic_Synthesis";
    
    const reader = new FileReader();
    reader.readAsDataURL(lastVideoBlob);
    reader.onloadend = () => {
      const base64data = reader.result as string;
      const newEntry: FinishedArchive = {
        url: URL.createObjectURL(lastVideoBlob),
        blobBase64: base64data,
        projectName: name,
        // FIX: Removed invalid 'number =' from timestamp assignment which caused a syntax error.
        timestamp: Date.now(),
      };
      
      setVault(prev => {
        const filtered = prev.filter(e => e.projectName !== name);
        return [newEntry, ...filtered].slice(0, 5);
      });
    };
  };

  const handleSaveCharacter = (char: CharacterProfile) => {
    setCharacterVault(prev => {
      const filtered = prev.filter(p => p.id !== char.id);
      return [char, ...filtered].slice(0, 10);
    });
  };

  const handleRestoreFromVault = async (entry: FinishedArchive) => {
    try {
      if (entry.blobBase64) {
        const response = await fetch(entry.blobBase64);
        const blob = await response.blob();
        const objectUrl = URL.createObjectURL(blob);
        setVideoUrl(objectUrl);
        setLastVideoBlob(blob);
        setAppState(AppState.FINISHED);
        setSelectedPlan(prev => prev ? { ...prev, projectName: entry.projectName } : null);
      }
    } catch (e) {
      console.error("Critical failure during asset restoration:", e);
      setErrorMessage("The requested asset could not be synthesized from persistent storage.");
    }
  };

  const stopAllAudio = () => {
    if (musicSourceRef.current) { try { musicSourceRef.current.stop(); } catch(e) {} musicSourceRef.current = null; }
    if (narrationSourceRef.current) { try { narrationSourceRef.current.stop(); } catch(e) {} narrationSourceRef.current = null; }
  };

  const playNarrativeAudio = async () => {
    if (!audioContextRef.current || !narrationBufferRef.current) return;
    const ctx = audioContextRef.current;
    if (ctx.state === 'suspended') await ctx.resume();
    stopAllAudio();
    const narrationSource = ctx.createBufferSource();
    const narrationGain = ctx.createGain();
    narrationSource.buffer = narrationBufferRef.current;
    narrationGain.gain.value = 1.0;
    narrationSource.connect(narrationGain).connect(ctx.destination);
    narrationSource.start(ctx.currentTime + 0.2);
    narrationSourceRef.current = narrationSource;
  };

  const handleGenerate = useCallback(async (params: GenerateVideoParams, sceneIndexOverride?: number) => {
    if (isGeneratingRef.current) return;
    isGeneratingRef.current = true;
    
    setAppState(AppState.LOADING);
    setErrorMessage(null);
    setLastConfig(params);

    const activeIndex = sceneIndexOverride !== undefined ? sceneIndexOverride : currentSceneIndex;

    try {
      const videoPromise = generateVideo(params);
      let ttsPromise: Promise<AudioBuffer | null> = Promise.resolve(null);
      
      if (selectedPlan && activeIndex >= 0) {
        const scene = selectedPlan.scenes[activeIndex];
        if (scene) {
          ttsPromise = generateSpeech(
            scene.narrationScript,
            params.voiceProfile,
            params.emotionalTone
          ).catch(() => null);
        }
      }

      const [videoResult, audioBuffer] = await Promise.all([videoPromise, ttsPromise]);
      
      setVideoUrl(videoResult.objectUrl);
      setLastVideoBlob(videoResult.blob);
      setLastVideoObject(videoResult.video);
      narrationBufferRef.current = audioBuffer;
      
      const duration = params.duration || 7;
      const pName = selectedPlan?.projectName || "Professional Production";
      recordCost(duration, pName);

      // Revised Transition Logic
      if (selectedPlan && activeIndex >= 0) {
        setCompletedSceneIds(prev => {
          const currentId = selectedPlan?.scenes[activeIndex]?.id;
          if (currentId === undefined) return prev;
          const next = Array.from(new Set([...prev, currentId]));
          
          const isActuallyFinished = selectedPlan && next.length === selectedPlan.scenes.length;
          
          if (isActuallyFinished) {
            setAppState(AppState.FINISHED);
            isAutoProcessingRef.current = false;
          } else {
            setAppState(AppState.SUCCESS);
            if (isAutoProcessingRef.current) {
              setTimeout(() => triggerNextExtension(videoResult.blob, videoResult.video, next.length, params), 2000);
            }
          }
          return next;
        });
      } else {
        // One-off generation path
        setAppState(AppState.SUCCESS);
      }
      
      playNarrativeAudio();
    } catch (error) {
      const msg = error instanceof Error ? error.message : 'Unknown Synthesis Fault';
      setErrorMessage(msg);
      setAppState(AppState.ERROR);
      isAutoProcessingRef.current = false;
    } finally {
      isGeneratingRef.current = false;
    }
  }, [selectedPlan, currentSceneIndex]);

  const triggerNextExtension = (prevBlob: Blob, prevVideo: Video, nextIdx: number, originalParams: GenerateVideoParams) => {
    if (!selectedPlan || !isAutoProcessingRef.current) return;
    const nextScene = selectedPlan.scenes[nextIdx];
    if (!nextScene) {
       setAppState(AppState.FINISHED);
       isAutoProcessingRef.current = false;
       return;
    }
    setCurrentSceneIndex(nextIdx);
    handleGenerate({
      prompt: nextScene.visualPrompt,
      model: VeoModel.VEO_FAST,
      aspectRatio: originalParams.aspectRatio || AspectRatio.LANDSCAPE,
      resolution: Resolution.P720,
      mode: GenerationMode.EXTEND_VIDEO,
      inputVideo: { file: new File([prevBlob], 'last.mp4'), base64: '' },
      inputVideoObject: prevVideo,
      duration: 7,
      voiceProfile: originalParams.voiceProfile,
      emotionalTone: originalParams.emotionalTone
    }, nextIdx);
  };

  const handleAnalyzeCapabilities = async (text: string, duration: number) => {
    setAppState(AppState.ANALYZING);
    try {
      const options = await generateNarrativeOptions(text, duration);
      setNarrativeOptions(options);
      setAppState(AppState.CHOOSING);
    } catch (error) {
      setErrorMessage("Strategic analysis node failed to respond.");
      setAppState(AppState.ERROR);
    }
  };

  const handleSelectPlan = (plan: NarrativePlan) => {
    setSelectedPlan(plan);
    setCompletedSceneIds([]);
    setCurrentSceneIndex(0);
    isAutoProcessingRef.current = true;
    
    handleGenerate({
      prompt: plan.scenes[0].visualPrompt,
      model: VeoModel.VEO_FAST,
      aspectRatio: AspectRatio.LANDSCAPE, 
      resolution: Resolution.P720, 
      mode: GenerationMode.TEXT_TO_VIDEO,
      duration: 7,
      voiceProfile: VoiceProfile.KORE,
      emotionalTone: EmotionalTone.PROFESSIONAL
    }, 0);
  };

  const handleEmergencyReset = () => {
    isGeneratingRef.current = false;
    isAutoProcessingRef.current = false;
    setAppState(AppState.IDLE);
    setErrorMessage(null);
  };

  return (
    <div className="h-screen bg-[#000000] text-white flex flex-col font-sans overflow-hidden">
      {showApiKeyDialog && <ApiKeyDialog onContinue={() => { setShowApiKeyDialog(false); window.aistudio?.openSelectKey(); }} />}
      
      <header className="py-6 flex justify-between items-center px-12 relative z-[110] border-b-2 border-white/10 bg-black shadow-2xl">
        <h1 className="text-3xl font-black tracking-tighter italic">
          VEO VISIONARY <span className="text-indigo-500 font-black ml-4 tracking-[0.4em] text-[11px] uppercase not-italic border-l-2 border-white/20 pl-6">Strategic Suite v3.2</span>
        </h1>
        <div className="flex items-center gap-8">
          <button 
            onClick={() => setShowApiPanel(!showApiPanel)}
            className="px-6 py-2.5 bg-white text-black border-2 border-white rounded-full text-[10px] font-black uppercase tracking-[0.3em] hover:bg-transparent hover:text-white transition-all flex items-center gap-2"
          >
            Developer Bridge
          </button>
          <button 
            onClick={() => setShowLedger(!showLedger)}
            className="px-6 py-2.5 bg-black border-2 border-white/20 rounded-full text-[10px] text-white font-black uppercase tracking-[0.3em] hover:border-indigo-500 hover:text-indigo-400 transition-all flex items-center gap-3"
          >
            <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full shadow-[0_0_15px_#6366f1]"></div>
            Capital Allocation: ${costLedger.totalBurn.toFixed(2)}
          </button>
          <button 
            onClick={() => setAppState(AppState.RESEARCH)}
            className="px-6 py-2.5 bg-indigo-600 border-2 border-indigo-500 rounded-full text-[10px] text-white font-black uppercase tracking-[0.3em] hover:bg-indigo-500 transition-all"
          >
            Executive Briefing
          </button>
          <button 
            onClick={() => setShowNotepad(!showNotepad)}
            className="px-6 py-2.5 bg-black border-2 border-white/20 rounded-full text-[10px] text-white font-black uppercase tracking-[0.3em] hover:bg-white hover:text-black transition-all"
          >
            {showNotepad ? 'Exit Strategy' : 'Strategy Vault'}
          </button>
        </div>
      </header>

      <main className="relative flex-grow flex overflow-hidden bg-[#000000]">
        {showNotepad && <Notepad data={notepad} onChange={setNotepad} onClose={() => setShowNotepad(false)} />}
        {showLedger && <CostLedger data={costLedger} onClose={() => setShowLedger(false)} onReset={() => setCostLedger({ totalBurn: 0, history: [] })} />}
        {showApiPanel && <ApiIntegration onClose={() => setShowApiPanel(false)} />}
        
        <div className={`flex-grow flex flex-col overflow-hidden transition-all duration-700 ${appState === AppState.FINISHED ? 'p-0' : 'max-w-7xl mx-auto w-full'}`}>
          <div className="flex-grow flex flex-col min-h-0">
            {appState === AppState.RESEARCH && <ResearchBrief onProceed={() => setAppState(AppState.IDLE)} />}
            
            {appState === AppState.ANALYZING && <div className="flex-grow flex items-center justify-center"><LoadingIndicator message="Synthesizing Visual Narrative..." /></div>}
            
            {(appState === AppState.IDLE || appState === AppState.CHOOSING) && !selectedPlan && appState !== AppState.RESEARCH && (
              <NarrativePanel 
                onSubmit={handleAnalyzeCapabilities} 
                vault={vault}
                onRestore={handleRestoreFromVault}
                options={narrativeOptions}
                onSelectOption={handleSelectPlan}
                isChoosing={appState === AppState.CHOOSING}
              />
            )}

            {(appState === AppState.LOADING || appState === AppState.SUCCESS || appState === AppState.FINISHED || appState === AppState.ERROR) && appState !== AppState.RESEARCH && (
              <div className={`flex-grow flex flex-col items-center justify-center overflow-y-auto custom-scrollbar ${appState === AppState.FINISHED ? 'bg-black w-full' : ''}`}>
                {appState === AppState.LOADING && (
                  <div className="flex flex-col items-center gap-8">
                    <LoadingIndicator message={`Synthesizing Segment 0${currentSceneIndex + 1}`} />
                    <button 
                      onClick={handleEmergencyReset}
                      className="px-6 py-3 bg-white/5 border border-white/10 hover:border-red-500/40 text-[10px] font-black text-gray-500 hover:text-red-500 uppercase tracking-widest rounded-full transition-all"
                    >
                      Emergency Production Reset
                    </button>
                  </div>
                )}
                {(appState === AppState.SUCCESS || appState === AppState.FINISHED) && videoUrl && (
                  <VideoResult
                    videoUrl={videoUrl} videoBlob={lastVideoBlob}
                    onRetry={() => handleGenerate(lastConfig!)}
                    onNewVideo={() => { setAppState(AppState.IDLE); setSelectedPlan(null); isAutoProcessingRef.current = false; isGeneratingRef.current = false; }}
                    onExtend={() => {}} 
                    canExtend={false} 
                    nextScene={selectedPlan?.scenes[currentSceneIndex + 1]}
                    currentScene={selectedPlan?.scenes[currentSceneIndex]}
                    completedScenesCount={completedSceneIds.length}
                    totalScenesCount={selectedPlan?.scenes.length || 1}
                    isFinished={appState === AppState.FINISHED}
                    projectName={selectedPlan?.projectName || vault[0]?.projectName || "Strategic_Synthesis"}
                    isAutoMode={isAutoProcessingRef.current}
                    onArchive={handleSaveToVault}
                  />
                )}
                {appState === AppState.ERROR && (
                   <div className="bg-black/80 p-12 rounded-[3rem] border-2 border-red-500/20 text-center max-w-xl">
                      <h2 className="text-4xl font-black text-red-500 mb-6 italic uppercase tracking-tighter">Production Fault</h2>
                      <p className="text-gray-400 mb-10 text-sm font-bold uppercase tracking-widest leading-relaxed">{errorMessage}</p>
                      <div className="flex gap-4 justify-center">
                        <button onClick={() => handleGenerate(lastConfig!)} className="px-10 py-4 bg-white text-black font-black rounded-xl uppercase tracking-widest hover:bg-gray-200 transition-all">Retry Synthesis</button>
                        <button onClick={handleEmergencyReset} className="px-10 py-4 bg-black border-2 border-white/20 text-white font-black rounded-xl uppercase tracking-widest hover:border-white transition-all">Abort</button>
                      </div>
                   </div>
                )}
                {appState === AppState.IDLE && (
                  <div className="w-full h-full flex items-center justify-center p-12">
                    <div className="w-full max-w-2xl bg-white/[0.03] p-16 rounded-[4rem] border-2 border-white/10 text-center shadow-[0_0_100px_rgba(255,255,255,0.05)]">
                      <div className="text-[11px] font-black text-indigo-400 uppercase tracking-[0.6em] mb-8">Production Node: Optimized & Ready</div>
                      <h2 className="text-5xl font-black italic mb-12 uppercase tracking-tighter leading-none">Creative Director is Ready</h2>
                      <PromptForm 
                        onGenerate={handleGenerate} 
                        notepadContext={notepad} 
                        characterVault={characterVault}
                        onSaveCharacter={handleSaveCharacter}
                      />
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
