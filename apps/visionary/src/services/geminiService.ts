
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import {
  GoogleGenAI,
  Type,
  Video,
  VideoGenerationReferenceImage,
  VideoGenerationReferenceType,
  Modality,
} from '@google/genai';
import {GenerateVideoParams, GenerationMode, NarrativePlan, VoiceProfile, EmotionalTone} from '../types';

function decodeBase64(base64: string) {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

async function decodeAudioData(
  data: Uint8Array,
  ctx: AudioContext,
  sampleRate: number,
  numChannels: number,
): Promise<AudioBuffer> {
  const dataInt16 = new Int16Array(data.buffer);
  const frameCount = dataInt16.length / numChannels;
  const buffer = ctx.createBuffer(numChannels, frameCount, sampleRate);

  for (let channel = 0; channel < numChannels; channel++) {
    const channelData = buffer.getChannelData(channel);
    for (let i = 0; i < frameCount; i++) {
      channelData[i] = dataInt16[i * numChannels + channel] / 32768.0;
    }
  }
  return buffer;
}

export const generateSpeech = async (
  text: string, 
  voice: VoiceProfile = VoiceProfile.KORE,
  tone: EmotionalTone = EmotionalTone.PROFESSIONAL
): Promise<AudioBuffer> => {
  const ai = new GoogleGenAI({apiKey: process.env.API_KEY});
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-preview-tts",
    contents: [{ 
      parts: [{ 
        text: `Deliver this narrative with a ${tone.toLowerCase()} and professional executive persona. Tone: ${tone}. Narrative: ${text}` 
      }] 
    }],
    config: {
      responseModalities: [Modality.AUDIO],
      speechConfig: {
        voiceConfig: {
          prebuiltVoiceConfig: { voiceName: voice },
        },
      },
    },
  });

  const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
  if (!base64Audio) throw new Error("Failed to generate synthesized narrative.");

  const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)({sampleRate: 24000});
  const audioData = decodeBase64(base64Audio);
  return await decodeAudioData(audioData, audioCtx, 24000, 1);
};

export const brainstormIdeas = async (context: { capabilities: string, ideas: string }): Promise<string> => {
  const ai = new GoogleGenAI({apiKey: process.env.API_KEY});
  const prompt = `You are an elite Global Creative Director and Strategic Consultant. 
  Based on these Core Capabilities: "${context.capabilities}" 
  and these Strategic Objectives: "${context.ideas}", 
  architect 3 distinct visual narratives for high-fidelity cinema assets (7-21 seconds each) and 2 high-impact executive taglines. 
  Focus on brand authority, strategic scalability, and multi-dimensional storytelling for a global professional audience.
  Format the response clearly in professional Markdown.`;

  const response = await ai.models.generateContent({
    model: 'gemini-3-pro-preview',
    contents: prompt,
  });

  return response.text || "Failed to synthesize strategic insights.";
};

export const refinePrompt = async (currentPrompt: string, context: { capabilities: string, ideas: string }): Promise<string> => {
  const ai = new GoogleGenAI({apiKey: process.env.API_KEY});
  const prompt = `Refine this visual objective for Veo: "${currentPrompt}". 
  Strategic Context: "${context.capabilities}". Brand Objectives: "${context.ideas}".
  Elevate the language to a professional cinematic standard. Specify lighting (chiaroscuro, corporate minimalism, architectural lighting), camera movement (precision dolly, expansive panoramic, micro-focal tracking), and texture.
  The output should be ONLY the refined prompt text, no meta-commentary.`;

  const response = await ai.models.generateContent({
    model: 'gemini-3-flash-preview',
    contents: prompt,
  });

  return response.text?.trim() || currentPrompt;
};

export const generateNarrativeOptions = async (text: string, targetDuration: number): Promise<NarrativePlan[]> => {
  const ai = new GoogleGenAI({apiKey: process.env.API_KEY});
  const sceneCount = Math.max(2, Math.floor(targetDuration / 7));
  
  const response = await ai.models.generateContent({
    model: 'gemini-3-pro-preview',
    contents: `Analyze these strategic assets and objectives: "${text}". 
    Architect 3 distinct high-fidelity cinematic storyboard directions for a ${targetDuration}s visual asset (${sceneCount} segments each).
    Direction 1: "Monolithic Excellence" - Minimalist, high-contrast, corporate authority.
    Direction 2: "Dynamic Evolution" - High-energy, fluid, expansive growth.
    Direction 3: "Human-Centric Vision" - Emotional resonance, authentic detail, professional depth.
    
    Each direction must include a projectName, styleName, and ${sceneCount} segments with visualPrompt, narrationScript, and description.`,
    config: {
      responseMimeType: 'application/json',
      responseSchema: {
        type: Type.ARRAY,
        items: {
          type: Type.OBJECT,
          properties: {
            projectName: { type: Type.STRING },
            styleName: { type: Type.STRING },
            estimatedCost: { type: Type.NUMBER, description: "Resource burn in USD ($0.10 per second)" },
            totalDuration: { type: Type.NUMBER },
            scenes: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  id: { type: Type.NUMBER },
                  title: { type: Type.STRING },
                  visualPrompt: { type: Type.STRING },
                  narrationScript: { type: Type.STRING },
                  description: { type: Type.STRING }
                },
                required: ["id", "title", "visualPrompt", "narrationScript", "description"]
              }
            }
          },
          required: ["projectName", "styleName", "scenes", "totalDuration", "estimatedCost"]
        }
      }
    }
  });

  const data = JSON.parse(response.text || '[]');
  return data.map((plan: any) => ({
    ...plan,
    totalDuration: targetDuration,
    estimatedCost: targetDuration * 0.10 
  }));
};

export const generateVideo = async (
  params: GenerateVideoParams,
): Promise<{objectUrl: string; blob: Blob; uri: string; video: Video}> => {
  const ai = new GoogleGenAI({apiKey: process.env.API_KEY});
  const config: any = { numberOfVideos: 1, resolution: params.resolution };
  if (params.mode !== GenerationMode.EXTEND_VIDEO) { 
    config.aspectRatio = params.aspectRatio; 
  }

  if (params.endFrame) {
    config.lastFrame = {
      imageBytes: params.endFrame.base64,
      mimeType: params.endFrame.file.type || 'image/png',
    };
  }

  if (params.referenceImages && params.referenceImages.length > 0) {
    config.referenceImages = params.referenceImages.map(img => ({
      image: {
        imageBytes: img.base64,
        mimeType: img.file.type || 'image/png'
      },
      referenceType: VideoGenerationReferenceType.ASSET,
    }));
  }

  const payload: any = { model: params.model, config: config };
  
  let finalPrompt = params.prompt;
  if (params.mode === GenerationMode.AVATAR_SYNC) {
    finalPrompt = `Synthesize a high-fidelity talking avatar from this reference image. The avatar should articulately speak with natural lip-sync, expressive facial micro-movements, and consistent character integrity: ${params.prompt}`;
  }
  if (finalPrompt) payload.prompt = finalPrompt;

  if (params.startFrame) {
    payload.image = {
      imageBytes: params.startFrame.base64,
      mimeType: params.startFrame.file.type || 'image/png',
    };
  }

  if (params.mode === GenerationMode.EXTEND_VIDEO) {
    if (params.inputVideoObject) {
      payload.video = params.inputVideoObject;
    } else {
      throw new Error('Visual extension requires a primary asset source.');
    }
  }

  let operation = await ai.models.generateVideos(payload);
  
  let pollCount = 0;
  const MAX_POLLS = 90; // Strictly capped at 15 minutes (90 * 10s)
  
  while (!operation.done) {
    pollCount++;
    if (pollCount > MAX_POLLS) {
      throw new Error('Synthesis Timeout: The production node exceeded the 15-minute time limit. This may be due to high server load.');
    }

    await new Promise((resolve) => setTimeout(resolve, 10000));
    
    try {
      operation = await ai.operations.getVideosOperation({operation: operation});
    } catch (pollError) {
      console.warn('Network interruption during polling. Retrying connection...', pollError);
      continue; // Silently retry polling if it's just a network hiccup
    }
    
    // Check for explicit server-side failures returned in the operation object
    if (operation.error) {
      throw new Error(`Production Fault [${operation.error.code}]: ${operation.error.message || 'The synthesis encountered a critical error on the server.'}`);
    }
  }

  const videoObject = operation.response?.generatedVideos?.[0]?.video;
  if (videoObject && videoObject.uri) {
    const res = await fetch(`${videoObject.uri}&key=${process.env.API_KEY}`);
    if (!res.ok) throw new Error('Asset Access Denied: Failed to retrieve synthesized content from the secure storage node.');
    const videoBlob = await res.blob();
    return {objectUrl: URL.createObjectURL(videoBlob), blob: videoBlob, uri: videoObject.uri, video: videoObject};
  }
  
  throw new Error('Response Null: The synthesis operation completed but returned no visual assets.');
};
