
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import {Video} from '@google/genai';

export enum AppState {
  IDLE,
  RESEARCH,    
  DIAGNOSTICS, 
  ANALYZING, 
  CHOOSING, 
  LOADING,
  SUCCESS,
  ERROR,
  PLANNING,
  FINISHED,
  API_INTEGRATION,
}

export enum VeoModel {
  VEO_FAST = 'veo-3.1-fast-generate-preview',
  VEO = 'veo-3.1-generate-preview',
}

export enum AspectRatio {
  LANDSCAPE = '16:9',
  PORTRAIT = '9:16',
}

export enum Resolution {
  P720 = '720p',
  P1080 = '1080p',
}

export enum VoiceProfile {
  KORE = 'Kore',
  PUCK = 'Puck',
  CHARON = 'Charon',
  FENRIR = 'Fenrir',
  ZEPHYR = 'Zephyr',
}

export enum EmotionalTone {
  AUTHORITATIVE = 'Authoritative',
  INSPIRATIONAL = 'Inspirational',
  WARM = 'Warm',
  URGENT = 'Urgent',
  PROFESSIONAL = 'Professional',
  CINEMATIC = 'Cinematic',
}

export enum GenerationMode {
  TEXT_TO_VIDEO = 'Text to Video',
  FRAMES_TO_VIDEO = 'Frames to Video',
  REFERENCES_TO_VIDEO = 'References to Video',
  EXTEND_VIDEO = 'Extend Video',
  AVATAR_SYNC = 'Avatar Sync',
}

export interface ImageFile {
  file: File;
  base64: string;
}

export interface VideoFile {
  file: File;
  base64: string;
}

export interface CharacterProfile {
  id: string;
  name: string;
  image: ImageFile;
  voice: VoiceProfile;
  tone: EmotionalTone;
  timestamp: number;
}

export interface NarrativeScene {
  id: number;
  title: string;
  visualPrompt: string;
  description: string;
  narrationScript: string;
}

export interface NarrativePlan {
  projectName: string;
  styleName: string;
  scenes: NarrativeScene[];
  estimatedCost: number;
  totalDuration: number;
}

export interface GenerateVideoParams {
  prompt: string;
  model: VeoModel;
  aspectRatio: AspectRatio;
  resolution: Resolution;
  mode: GenerationMode;
  duration?: number;
  voiceProfile?: VoiceProfile;
  emotionalTone?: EmotionalTone;
  startFrame?: ImageFile | null;
  endFrame?: ImageFile | null;
  referenceImages?: ImageFile[];
  styleImage?: ImageFile | null;
  inputVideo?: VideoFile | null;
  inputVideoObject?: Video | null;
  isLooping?: boolean;
}

export interface NotepadData {
  ideas: string;
  prompts: string;
  capabilities: string;
}

export interface CostEntry {
  id: string;
  projectName: string;
  duration: number;
  cost: number;
  timestamp: number;
}

export interface CostLedgerData {
  totalBurn: number;
  history: CostEntry[];
}
