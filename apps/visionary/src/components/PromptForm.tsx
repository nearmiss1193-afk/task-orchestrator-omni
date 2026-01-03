
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import {Video} from '@google/genai';
import React, {useCallback, useEffect, useRef, useState} from 'react';
import { refinePrompt } from '../services/geminiService';
import {
  AspectRatio,
  GenerateVideoParams,
  GenerationMode,
  ImageFile,
  Resolution,
  VeoModel,
  VideoFile,
  NotepadData,
  VoiceProfile,
  EmotionalTone,
  CharacterProfile,
} from '../types';
import {
  ArrowRightIcon,
  ChevronDownIcon,
  FilmIcon,
  FramesModeIcon,
  PlusIcon,
  RectangleStackIcon,
  ReferencesModeIcon,
  SlidersHorizontalIcon,
  SparklesIcon,
  TextModeIcon,
  TvIcon,
  XMarkIcon,
  CameraIcon,
  UserIcon,
} from './icons';

const aspectRatioDisplayNames: Record<AspectRatio, string> = {
  [AspectRatio.LANDSCAPE]: 'Landscape (16:9)',
  [AspectRatio.PORTRAIT]: 'Portrait (9:16)',
};

const modeIcons: Record<GenerationMode, React.ReactNode> = {
  [GenerationMode.TEXT_TO_VIDEO]: <TextModeIcon className="w-5 h-5" />,
  [GenerationMode.FRAMES_TO_VIDEO]: <FramesModeIcon className="w-5 h-5" />,
  [GenerationMode.REFERENCES_TO_VIDEO]: (
    <ReferencesModeIcon className="w-5 h-5" />
  ),
  [GenerationMode.EXTEND_VIDEO]: <FilmIcon className="w-5 h-5" />,
  [GenerationMode.AVATAR_SYNC]: <UserIcon className="w-5 h-5" />,
};

const fileToBase64 = <T extends {file: File; base64: string}>(
  file: File,
): Promise<T> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = (reader.result as string).split(',')[1];
      if (base64) {
        resolve({file, base64} as T);
      } else {
        reject(new Error('Failed to read file as base64.'));
      }
    };
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
};
const fileToImageFile = (file: File): Promise<ImageFile> =>
  fileToBase64<ImageFile>(file);
const fileToVideoFile = (file: File): Promise<VideoFile> =>
  fileToBase64<VideoFile>(file);

const CustomSelect: React.FC<{
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  icon: React.ReactNode;
  children: React.ReactNode;
  disabled?: boolean;
}> = ({label, value, onChange, icon, children, disabled = false}) => (
  <div className="flex-grow">
    <label
      className={`text-[9px] font-black uppercase tracking-widest block mb-2 ${
        disabled ? 'text-gray-600' : 'text-gray-400'
      }`}>
      {label}
    </label>
    <div className="relative">
      <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
        {icon}
      </div>
      <select
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="w-full bg-black/40 border border-white/10 rounded-xl pl-10 pr-8 py-2.5 appearance-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-700/50 disabled:border-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed text-xs font-bold uppercase tracking-tight">
        {children}
      </select>
      <ChevronDownIcon
        className={`w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none ${
          disabled ? 'text-gray-600' : 'text-gray-400'
        }`}
      />
    </div>
  </div>
);

const ImageUpload: React.FC<{
  onSelect: (image: ImageFile) => void;
  onRemove?: () => void;
  image?: ImageFile | null;
  label: React.ReactNode;
  allowCamera?: boolean;
}> = ({onSelect, onRemove, image, label, allowCamera = false}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      try {
        const imageFile = await fileToImageFile(file);
        onSelect(imageFile);
      } catch (error) {
        console.error('Error converting file:', error);
      }
    }
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
       const imageFile = await fileToImageFile(file);
       onSelect(imageFile);
    }
  };

  const startCamera = async () => {
    setIsCameraActive(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 1280, height: 720 } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Camera access denied:', err);
      setIsCameraActive(false);
    }
  };

  const captureCamera = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Biometric mirroring
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(videoRef.current, 0, 0);
      }
      canvas.toBlob(async (blob) => {
        if (blob) {
          const file = new File([blob], 'biometric_selfie.png', { type: 'image/png' });
          const imageFile = await fileToImageFile(file);
          onSelect(imageFile);
          stopCamera();
        }
      }, 'image/png');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
    }
    setIsCameraActive(false);
  };

  if (isCameraActive) {
    return (
      <div className="relative w-[30rem] h-80 bg-black border-2 border-indigo-500 rounded-3xl overflow-hidden group shadow-[0_0_60px_rgba(99,102,241,0.3)] z-50">
        <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover scale-x-[-1]" />
        <div className="absolute inset-0 border-[30px] border-black/30 pointer-events-none"></div>
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
           <div className="w-48 h-64 border-2 border-dashed border-indigo-500/50 rounded-[4rem] animate-pulse"></div>
        </div>
        <div className="absolute top-6 left-6 flex items-center gap-2">
           <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
           <span className="text-[10px] font-black text-white uppercase tracking-widest">Biometric Viewfinder</span>
        </div>
        <div className="absolute bottom-6 left-0 right-0 flex justify-center gap-4">
           <button onClick={captureCamera} className="px-8 py-3 bg-white text-black text-[11px] font-black uppercase rounded-xl hover:bg-gray-200 transition-all shadow-xl">Capture Selfie</button>
           <button onClick={stopCamera} className="px-8 py-3 bg-black/60 text-white text-[11px] font-black uppercase rounded-xl hover:bg-black/80 transition-all">Cancel</button>
        </div>
      </div>
    );
  }

  if (image) {
    return (
      <div className="relative w-32 h-24 group">
        <img
          src={URL.createObjectURL(image.file)}
          alt="preview"
          className="w-full h-full object-cover rounded-xl border-2 border-indigo-500/40 shadow-lg"
        />
        <div className="absolute inset-0 bg-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-xl pointer-events-none"></div>
        <button
          type="button"
          onClick={onRemove}
          className="absolute -top-2 -right-2 w-8 h-8 bg-black border border-white/10 hover:bg-red-600 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-all"
          aria-label="Remove image">
          <XMarkIcon className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div 
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`relative flex flex-col items-center justify-center gap-3 ${isDragging ? 'scale-110' : ''} transition-all`}
    >
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className={`w-32 h-24 ${isDragging ? 'bg-indigo-600/20 border-indigo-500' : 'bg-gray-700/20 hover:bg-gray-700/40 border-gray-600'} border-2 border-dashed rounded-xl flex flex-col items-center justify-center text-gray-400 hover:text-white transition-all`}>
        <PlusIcon className="w-6 h-6" />
        <span className="text-[9px] font-black uppercase mt-2 px-2 text-center leading-tight tracking-widest">{label}</span>
      </button>
      {allowCamera && (
        <button 
          type="button"
          onClick={startCamera}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white border border-indigo-400/30 rounded-full text-[9px] font-black hover:bg-indigo-500 transition-all uppercase tracking-[0.2em] shadow-lg shadow-indigo-600/20"
        >
          <CameraIcon className="w-4 h-4" /> Initialize Selfie
        </button>
      )}
      <input
        type="file"
        ref={inputRef}
        onChange={handleFileChange}
        accept="image/*"
        className="hidden"
      />
    </div>
  );
};

const VideoUpload: React.FC<{
  onSelect: (video: VideoFile) => void;
  onRemove?: () => void;
  video?: VideoFile | null;
  label: React.ReactNode;
}> = ({onSelect, onRemove, video, label}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      try {
        const videoFile = await fileToVideoFile(file);
        onSelect(videoFile);
      } catch (error) {
        console.error('Error converting file:', error);
      }
    }
  };

  if (video) {
    return (
      <div className="relative w-48 h-28 group">
        <video
          src={URL.createObjectURL(video.file)}
          muted
          loop
          className="w-full h-full object-cover rounded-lg"
        />
        <button
          type="button"
          onClick={onRemove}
          className="absolute top-1 right-1 w-6 h-6 bg-black/60 hover:bg-black/80 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity"
          aria-label="Remove video">
          <XMarkIcon className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={() => inputRef.current?.click()}
      className="w-48 h-28 bg-gray-700/50 hover:bg-gray-700 border-2 border-dashed border-gray-600 rounded-lg flex flex-col items-center justify-center text-gray-400 hover:text-white transition-colors text-center">
      <PlusIcon className="w-6 h-6" />
      <span className="text-xs mt-1 px-2">{label}</span>
      <input
        type="file"
        ref={inputRef}
        onChange={handleFileChange}
        accept="video/*"
        className="hidden"
      />
    </button>
  );
};

interface PromptFormProps {
  onGenerate: (params: GenerateVideoParams) => void;
  initialValues?: GenerateVideoParams | null;
  notepadContext?: NotepadData;
  characterVault: CharacterProfile[];
  onSaveCharacter: (char: CharacterProfile) => void;
}

const PromptForm: React.FC<PromptFormProps> = ({
  onGenerate,
  initialValues,
  notepadContext,
  characterVault,
  onSaveCharacter,
}) => {
  const [prompt, setPrompt] = useState(initialValues?.prompt ?? '');
  const [model, setModel] = useState<VeoModel>(
    initialValues?.model ?? VeoModel.VEO_FAST,
  );
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>(
    initialValues?.aspectRatio ?? AspectRatio.LANDSCAPE,
  );
  const [resolution, setResolution] = useState<Resolution>(
    initialValues?.resolution ?? Resolution.P720,
  );
  const [generationMode, setGenerationMode] = useState<GenerationMode>(
    initialValues?.mode ?? GenerationMode.TEXT_TO_VIDEO,
  );
  const [duration, setDuration] = useState<number>(initialValues?.duration ?? 21);
  
  const [voiceProfile, setVoiceProfile] = useState<VoiceProfile>(
    initialValues?.voiceProfile ?? VoiceProfile.KORE
  );
  const [emotionalTone, setEmotionalTone] = useState<EmotionalTone>(
    initialValues?.emotionalTone ?? EmotionalTone.PROFESSIONAL
  );

  const [startFrame, setStartFrame] = useState<ImageFile | null>(
    initialValues?.startFrame ?? null,
  );
  const [endFrame, setEndFrame] = useState<ImageFile | null>(
    initialValues?.endFrame ?? null,
  );
  const [referenceImages, setReferenceImages] = useState<ImageFile[]>(
    initialValues?.referenceImages ?? [],
  );
  const [styleImage, setStyleImage] = useState<ImageFile | null>(
    initialValues?.styleImage ?? null,
  );
  const [inputVideo, setInputVideo] = useState<VideoFile | null>(
    initialValues?.inputVideo ?? null,
  );
  const [inputVideoObject, setInputVideoObject] = useState<Video | null>(
    initialValues?.inputVideoObject ?? null,
  );
  const [isLooping, setIsLooping] = useState(initialValues?.isLooping ?? false);

  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isModeSelectorOpen, setIsModeSelectorOpen] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [showProfileVault, setShowProfileVault] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const modeSelectorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (initialValues) {
      setPrompt(initialValues.prompt ?? '');
      setModel(initialValues.model ?? VeoModel.VEO_FAST);
      setAspectRatio(initialValues.aspectRatio ?? AspectRatio.LANDSCAPE);
      setResolution(initialValues.resolution ?? Resolution.P720);
      setGenerationMode(initialValues.mode ?? GenerationMode.TEXT_TO_VIDEO);
      setDuration(initialValues.duration ?? 21);
      setVoiceProfile(initialValues.voiceProfile ?? VoiceProfile.KORE);
      setEmotionalTone(initialValues.emotionalTone ?? EmotionalTone.PROFESSIONAL);
      setStartFrame(initialValues.startFrame ?? null);
      setEndFrame(initialValues.endFrame ?? null);
      setReferenceImages(initialValues.referenceImages ?? []);
      setStyleImage(initialValues.styleImage ?? null);
      setInputVideo(initialValues.inputVideo ?? null);
      setInputVideoObject(initialValues.inputVideoObject ?? null);
      setIsLooping(initialValues.isLooping ?? false);
    }
  }, [initialValues]);

  const handleRefine = async () => {
    if (!prompt || isRefining) return;
    setIsRefining(true);
    try {
      const refined = await refinePrompt(prompt, notepadContext || { capabilities: '', ideas: '', prompts: '' });
      setPrompt(refined);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRefining(false);
    }
  };

  // Local handler to save a profile to the character vault using the prop callback.
  const handleSaveProfile = () => {
    if (!startFrame) return;
    const profile: CharacterProfile = {
      id: Math.random().toString(36).substring(7),
      name: `Visionary_${voiceProfile}_${emotionalTone}`,
      image: startFrame,
      voice: voiceProfile,
      tone: emotionalTone,
      timestamp: Date.now()
    };
    onSaveCharacter(profile);
  };

  const applyProfile = (profile: CharacterProfile) => {
    setStartFrame(profile.image);
    setVoiceProfile(profile.voice);
    setEmotionalTone(profile.tone);
    setShowProfileVault(false);
  };

  useEffect(() => {
    if (generationMode === GenerationMode.REFERENCES_TO_VIDEO) {
      setModel(VeoModel.VEO);
      setAspectRatio(AspectRatio.LANDSCAPE);
      setResolution(Resolution.P720);
    } else if (generationMode === GenerationMode.EXTEND_VIDEO) {
      setResolution(Resolution.P720);
    } else if (generationMode === GenerationMode.AVATAR_SYNC) {
      setAspectRatio(AspectRatio.PORTRAIT);
      setResolution(Resolution.P720);
    }
  }, [generationMode]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [prompt]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        modeSelectorRef.current &&
        !modeSelectorRef.current.contains(event.target as Node)
      ) {
        setIsModeSelectorOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      onGenerate({
        prompt,
        model,
        aspectRatio,
        resolution,
        mode: generationMode,
        duration,
        voiceProfile,
        emotionalTone,
        startFrame,
        endFrame,
        referenceImages,
        styleImage,
        inputVideo,
        inputVideoObject,
        isLooping,
      });
    },
    [
      prompt,
      model,
      aspectRatio,
      resolution,
      generationMode,
      duration,
      voiceProfile,
      emotionalTone,
      startFrame,
      endFrame,
      referenceImages,
      styleImage,
      inputVideo,
      inputVideoObject,
      onGenerate,
      isLooping,
    ],
  );

  const handleSelectMode = (mode: GenerationMode) => {
    setGenerationMode(mode);
    setIsModeSelectorOpen(false);
    setStartFrame(null);
    setEndFrame(null);
    setReferenceImages([]);
    setStyleImage(null);
    setInputVideo(null);
    setInputVideoObject(null);
    setIsLooping(false);
  };

  const promptPlaceholder = {
    [GenerationMode.TEXT_TO_VIDEO]: 'Describe the visual narrative objectives...',
    [GenerationMode.FRAMES_TO_VIDEO]: 'Describe movement and transition logic...',
    [GenerationMode.REFERENCES_TO_VIDEO]: 'Describe a sequence using reference assets...',
    [GenerationMode.EXTEND_VIDEO]: 'Define the tactical evolution of this scene...',
    [GenerationMode.AVATAR_SYNC]: 'Provide the biometric narration or script for the avatar...',
  }[generationMode];

  const selectableModes = [
    GenerationMode.TEXT_TO_VIDEO,
    GenerationMode.FRAMES_TO_VIDEO,
    GenerationMode.REFERENCES_TO_VIDEO,
    GenerationMode.AVATAR_SYNC,
  ];

  const renderMediaUploads = () => {
    if (generationMode === GenerationMode.AVATAR_SYNC) {
      return (
        <div className="mb-3 p-10 bg-[#0a0a0c] rounded-[3rem] border-2 border-indigo-500/20 flex flex-col items-center justify-center gap-6 shadow-[inset_0_0_80px_rgba(0,0,0,1)] relative overflow-hidden">
           <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent animate-scanline"></div>
           
           <div className="flex justify-between w-full items-center mb-4">
              <div className="text-[11px] font-black text-indigo-400 uppercase tracking-[0.4em]">Biometric Sync Interface</div>
              <button 
                onClick={() => setShowProfileVault(!showProfileVault)}
                className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-[9px] font-black text-gray-500 hover:text-white transition-all uppercase tracking-widest"
              >
                {showProfileVault ? 'Close Vault' : 'Persistent Character Vault'}
              </button>
           </div>

           {showProfileVault ? (
             <div className="w-full grid grid-cols-2 sm:grid-cols-4 gap-4 animate-in fade-in zoom-in-95 duration-500 max-h-48 overflow-y-auto custom-scrollbar p-2">
                {characterVault.length > 0 ? characterVault.map(profile => (
                  <button 
                    key={profile.id}
                    onClick={() => applyProfile(profile)}
                    className="flex flex-col items-center gap-2 p-3 bg-white/5 rounded-2xl hover:bg-white/10 border border-white/5 hover:border-indigo-500 transition-all group"
                  >
                    <img src={URL.createObjectURL(profile.image.file)} className="w-16 h-16 rounded-full object-cover border-2 border-indigo-500/20 group-hover:border-indigo-500 shadow-lg" alt="profile" />
                    <span className="text-[8px] font-black uppercase text-gray-500 group-hover:text-white truncate w-full text-center tracking-tighter">{profile.voice} Persona</span>
                  </button>
                )) : (
                  <div className="col-span-full py-10 text-center text-gray-700 font-black uppercase tracking-widest text-[10px]">Vault empty. Capture a selfie to save.</div>
                )}
             </div>
           ) : (
             <div className="flex flex-col items-center gap-6">
                <ImageUpload 
                  label="Reference Headshot" 
                  image={startFrame} 
                  onSelect={setStartFrame} 
                  onRemove={() => setStartFrame(null)}
                  allowCamera={true}
                />
                {startFrame && (
                  <button 
                    // Fixed: onClick reference changed from handleSaveCharacter to handleSaveProfile
                    onClick={handleSaveProfile}
                    className="px-8 py-3 bg-indigo-600/10 border-2 border-indigo-500/30 text-indigo-400 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] hover:bg-indigo-600 hover:text-white transition-all shadow-xl"
                  >
                    Persist to Character Vault
                  </button>
                )}
             </div>
           )}
           <p className="text-[9px] text-gray-600 uppercase tracking-widest font-bold border-t border-white/5 pt-6 w-full text-center">Biometric data is cached locally for cross-project narrative consistency.</p>
        </div>
      );
    }
    if (generationMode === GenerationMode.FRAMES_TO_VIDEO) {
      return (
        <div className="mb-3 p-4 bg-[#2c2c2e] rounded-xl border border-gray-700 flex flex-col items-center justify-center gap-4">
          <div className="flex items-center justify-center gap-4">
            <ImageUpload
              label="Start Frame"
              image={startFrame}
              onSelect={setStartFrame}
              onRemove={() => {
                setStartFrame(null);
                setIsLooping(false);
              }}
            />
            {!isLooping && (
              <ImageUpload
                label="End Frame"
                image={endFrame}
                onSelect={setEndFrame}
                onRemove={() => setEndFrame(null)}
              />
            )}
          </div>
          {startFrame && !endFrame && (
            <div className="mt-3 flex items-center">
              <input
                id="loop-video-checkbox"
                type="checkbox"
                checked={isLooping}
                onChange={(e) => setIsLooping(e.target.checked)}
                className="w-4 h-4 text-indigo-600 bg-gray-700 border-gray-600 rounded focus:ring-indigo-500 focus:ring-offset-gray-800 cursor-pointer"
              />
              <label
                htmlFor="loop-video-checkbox"
                className="ml-2 text-sm font-medium text-gray-300 cursor-pointer">
                Create a looping video
              </label>
            </div>
          )}
        </div>
      );
    }
    if (generationMode === GenerationMode.REFERENCES_TO_VIDEO) {
      return (
        <div className="mb-3 p-4 bg-[#2c2c2e] rounded-xl border border-gray-700 flex flex-wrap items-center justify-center gap-2">
          {referenceImages.map((img, index) => (
            <ImageUpload
              key={index}
              image={img}
              label=""
              onSelect={() => {}}
              onRemove={() =>
                setReferenceImages((imgs) => imgs.filter((_, i) => i !== index))
              }
            />
          ))}
          {referenceImages.length < 3 && (
            <ImageUpload
              label="Add Reference"
              onSelect={(img) => setReferenceImages((imgs) => [...imgs, img])}
            />
          )}
        </div>
      );
    }
    if (generationMode === GenerationMode.EXTEND_VIDEO) {
      return (
        <div className="mb-3 p-4 bg-[#2c2c2e] rounded-xl border border-gray-700 flex items-center justify-center gap-4">
          <VideoUpload
            label={
              <>
                Input Video
                <br />
                (must be 720p veo generated)
              </>
            }
            video={inputVideo}
            onSelect={setInputVideo}
            onRemove={() => {
              setInputVideo(null);
              setInputVideoObject(null);
            }}
          />
        </div>
      );
    }
    return null;
  };

  const isRefMode = generationMode === GenerationMode.REFERENCES_TO_VIDEO;
  const isExtendMode = generationMode === GenerationMode.EXTEND_VIDEO;
  const isAvatarMode = generationMode === GenerationMode.AVATAR_SYNC;

  let isSubmitDisabled = false;
  let tooltipText = '';

  switch (generationMode) {
    case GenerationMode.TEXT_TO_VIDEO:
      isSubmitDisabled = !prompt.trim();
      break;
    case GenerationMode.FRAMES_TO_VIDEO:
      isSubmitDisabled = !startFrame;
      break;
    case GenerationMode.AVATAR_SYNC:
      isSubmitDisabled = !startFrame || !prompt.trim();
      break;
    case GenerationMode.REFERENCES_TO_VIDEO:
      const hasNoRefs = referenceImages.length === 0;
      const hasNoPrompt = !prompt.trim();
      isSubmitDisabled = hasNoRefs || hasNoPrompt;
      break;
    case GenerationMode.EXTEND_VIDEO:
      isSubmitDisabled = !inputVideoObject;
      break;
  }

  return (
    <div className="relative w-full">
      {isSettingsOpen && (
        <div className="absolute bottom-full left-0 right-0 mb-3 p-8 bg-[#151517] rounded-[2.5rem] border-2 border-white/10 shadow-[0_0_100px_rgba(0,0,0,0.8)] space-y-8 animate-in slide-in-from-bottom-4 duration-300 z-[130]">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <CustomSelect
              label="Visual Architecture"
              value={model}
              onChange={(e) => setModel(e.target.value as VeoModel)}
              icon={<SparklesIcon className="w-4 h-4 text-indigo-400" />}
              disabled={isRefMode}>
              {Object.values(VeoModel).map((modelValue) => (
                <option key={modelValue} value={modelValue}>
                  {modelValue}
                </option>
              ))}
            </CustomSelect>
            <CustomSelect
              label="Canvas Aspect"
              value={aspectRatio}
              onChange={(e) => setAspectRatio(e.target.value as AspectRatio)}
              icon={<RectangleStackIcon className="w-4 h-4 text-indigo-400" />}
              disabled={isRefMode || isExtendMode || isAvatarMode}>
              {Object.entries(aspectRatioDisplayNames).map(([key, name]) => (
                <option key={key} value={key}>
                  {name}
                </option>
              ))}
            </CustomSelect>
            <CustomSelect
              label="Output Resolution"
              value={resolution}
              onChange={(e) => setResolution(e.target.value as Resolution)}
              icon={<TvIcon className="w-4 h-4 text-indigo-400" />}
              disabled={isRefMode || isExtendMode || isAvatarMode}>
              <option value={Resolution.P720}>720p (Production)</option>
              <option value={Resolution.P1080}>1080p (Master)</option>
            </CustomSelect>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4 border-t border-white/5">
             <div className="space-y-6">
                <CustomSelect
                  label="Narration Voice Profile"
                  value={voiceProfile}
                  onChange={(e) => setVoiceProfile(e.target.value as VoiceProfile)}
                  icon={<FilmIcon className="w-4 h-4 text-indigo-400" />}>
                  {Object.values(VoiceProfile).map((v) => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </CustomSelect>
                <CustomSelect
                  label="Emotional Tone Archetype"
                  value={emotionalTone}
                  onChange={(e) => setEmotionalTone(e.target.value as EmotionalTone)}
                  icon={<SparklesIcon className="w-4 h-4 text-indigo-400" />}>
                  {Object.values(EmotionalTone).map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </CustomSelect>
             </div>

             <div className="bg-white/[0.03] p-6 rounded-[2rem] border border-white/5">
                <div className="flex justify-between items-center mb-6">
                   <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Asset Duration Logic</span>
                   <span className="text-xs font-black text-white font-mono">{duration}s</span>
                </div>
                <input 
                  type="range" min="7" max="49" step="7" 
                  value={duration} 
                  onChange={(e) => setDuration(parseInt(e.target.value))} 
                  className="w-full h-1 bg-white/5 rounded-full accent-indigo-500 cursor-pointer appearance-none"
                />
                <div className="flex justify-between text-[8px] text-gray-700 font-black uppercase mt-4 tracking-tighter">
                   <span>7s</span>
                   <span>21s</span>
                   <span>49s</span>
                </div>
                <p className="text-[8px] text-indigo-400/50 font-black uppercase tracking-widest mt-6 leading-relaxed">
                  Longer assets require more complex synthesis nodes.
                </p>
             </div>
          </div>
        </div>
      )}
      <form onSubmit={handleSubmit} className="w-full">
        {renderMediaUploads()}
        <div className="flex items-end gap-2 bg-[#1f1f1f] border border-gray-600 rounded-3xl p-3 shadow-2xl focus-within:ring-2 focus-within:ring-indigo-500 transition-all">
          <div className="relative" ref={modeSelectorRef}>
            <button
              type="button"
              onClick={() => setIsModeSelectorOpen((prev) => !prev)}
              className="flex shrink-0 items-center gap-2 px-4 py-3 rounded-2xl hover:bg-gray-700 text-gray-300 hover:text-white transition-colors"
              aria-label="Select generation mode">
              {modeIcons[generationMode]}
              <span className="font-bold text-[10px] uppercase tracking-widest ml-1">
                {generationMode === GenerationMode.AVATAR_SYNC ? 'Avatar Sync' : generationMode}
              </span>
            </button>
            {isModeSelectorOpen && (
              <div className="absolute bottom-full mb-4 w-60 bg-[#2c2c2e] border border-gray-600 rounded-2xl shadow-2xl overflow-hidden z-20 animate-in fade-in slide-in-from-bottom-2 duration-200">
                {selectableModes.map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    onClick={() => handleSelectMode(mode)}
                    className={`w-full text-left flex items-center gap-3 p-4 hover:bg-indigo-600/50 transition-colors ${generationMode === mode ? 'bg-indigo-600/30 text-white' : 'text-gray-300'}`}>
                    {modeIcons[mode]}
                    <span className="text-[10px] uppercase font-black tracking-widest">{mode === GenerationMode.AVATAR_SYNC ? 'Avatar Sync' : mode}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          <textarea
            ref={textareaRef}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={promptPlaceholder}
            className="flex-grow bg-transparent focus:outline-none resize-none text-base text-white placeholder-gray-600 max-h-48 py-3 font-medium"
            rows={1}
          />
          <button
            type="button"
            onClick={handleRefine}
            disabled={!prompt.trim() || isRefining}
            className={`p-3.5 rounded-full hover:bg-gray-700 disabled:opacity-30 transition-all ${isRefining ? 'animate-pulse text-indigo-400' : 'text-gray-400'}`}
            title="Executive Refinement"
          >
            <SparklesIcon className="w-6 h-6" />
          </button>
          <button
            type="button"
            onClick={() => setIsSettingsOpen((prev) => !prev)}
            className={`p-3.5 rounded-full hover:bg-gray-700 transition-all ${isSettingsOpen ? 'bg-indigo-600 text-white' : 'text-gray-400'}`}
            aria-label="Toggle configurations">
            <SlidersHorizontalIcon className="w-6 h-6" />
          </button>
          <div className="relative group ml-1">
            <button
              type="submit"
              className="p-3.5 bg-indigo-600 rounded-2xl hover:bg-indigo-500 disabled:bg-gray-700 disabled:text-gray-800 disabled:cursor-not-allowed transition-all shadow-xl shadow-indigo-600/20 active:scale-95"
              aria-label="Initialize production"
              disabled={isSubmitDisabled}>
              <ArrowRightIcon className="w-6 h-6 text-white" />
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default PromptForm;
