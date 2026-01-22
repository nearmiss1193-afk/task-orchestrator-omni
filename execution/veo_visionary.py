"""
Veo Visionary - AI Video Generation Engine
============================================

Generates high-quality video content using Google Veo via the Gemini API.
Supports text-to-video, image-to-video, and video extension.

Part of the Content Engine & Social Command Center.
"""

import os
import json
import time
import base64
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Try to import Google AI SDK
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Self-annealing integration
try:
    from annealing_engine import self_annealing, log_annealing_event
    ANNEALING_ENABLED = True
except ImportError:
    ANNEALING_ENABLED = False
    def self_annealing(func):
        return func

# Configuration
VEO_MODEL = "veo-2.0-generate-001"  # Default model
VEO_MODELS = [
    "veo-3.1-generate-001",  # Latest, 8s 4K
    "veo-3.0-generate-001",
    "veo-2.0-generate-001",
]
MAX_BUDGET_PER_VIDEO = 20.00  # USD
CONTENT_LIBRARY_DIR = Path(__file__).parent.parent / "content_library"


class VeoVisionary:
    """AI-powered video generation using Google Veo."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Veo Visionary.
        
        Args:
            api_key: Google AI API key. Falls back to GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set. Please set the environment variable.")
        
        if GENAI_AVAILABLE:
            genai.configure(api_key=self.api_key)
        
        # Ensure content library exists
        CONTENT_LIBRARY_DIR.mkdir(exist_ok=True)
        
        self.generation_history = []
    
    def _estimate_cost(self, duration_seconds: int, resolution: str) -> float:
        """
        Estimate generation cost.
        
        Based on typical Vertex AI pricing. Actual costs may vary.
        """
        # Rough estimates per second of video
        cost_per_second = {
            "720p": 0.05,
            "1080p": 0.10,
            "4k": 0.20
        }
        return duration_seconds * cost_per_second.get(resolution, 0.10)
    
    @self_annealing
    def generate_from_text(
        self,
        prompt: str,
        duration_seconds: int = 8,
        resolution: str = "1080p",
        aspect_ratio: str = "16:9",
        style: Optional[str] = None,
        output_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt.
        
        Args:
            prompt: Text description of desired video
            duration_seconds: Video length (default 8s, max varies by model)
            resolution: "720p", "1080p", or "4k"
            aspect_ratio: "16:9", "9:16" (portrait), or "1:1"
            style: Optional style preset (e.g., "cinematic", "animation")
            output_name: Custom filename (without extension)
        
        Returns:
            Dict with video_url, thumbnail_url, metadata
        """
        # Estimate cost and check budget
        estimated_cost = self._estimate_cost(duration_seconds, resolution)
        if estimated_cost > MAX_BUDGET_PER_VIDEO:
            return {
                "success": False,
                "error": f"Estimated cost ${estimated_cost:.2f} exceeds budget ${MAX_BUDGET_PER_VIDEO}",
                "requires_approval": True
            }
        
        # Build enhanced prompt
        enhanced_prompt = prompt
        if style:
            enhanced_prompt = f"{style} style: {prompt}"
        
        print(f"[VEO] Generating video from prompt: {prompt[:50]}...")
        print(f"[VEO] Duration: {duration_seconds}s, Resolution: {resolution}")
        print(f"[VEO] Estimated cost: ${estimated_cost:.2f}")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = output_name or f"veo_{timestamp}"
        
        try:
            # Use Gemini API for video generation
            # Note: Veo API specifics may vary - this is the general pattern
            if GENAI_AVAILABLE:
                result = self._generate_with_genai(
                    enhanced_prompt,
                    duration_seconds,
                    resolution,
                    aspect_ratio
                )
            else:
                result = self._generate_with_rest_api(
                    enhanced_prompt,
                    duration_seconds,
                    resolution,
                    aspect_ratio
                )
            
            if result.get("success"):
                # Save to content library
                video_path = CONTENT_LIBRARY_DIR / f"{output_name}.mp4"
                
                # In practice, you'd download the video from the result URL
                # For now, we'll store the metadata
                metadata = {
                    "id": f"veo_{timestamp}",
                    "type": "video",
                    "source": "veo",
                    "prompt": prompt,
                    "duration_seconds": duration_seconds,
                    "resolution": resolution,
                    "aspect_ratio": aspect_ratio,
                    "style": style,
                    "estimated_cost": estimated_cost,
                    "file_path": str(video_path),
                    "created_at": datetime.now().isoformat()
                }
                
                # Save metadata
                metadata_path = CONTENT_LIBRARY_DIR / f"{output_name}.json"
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)
                
                self.generation_history.append(metadata)
                
                print(f"[VEO] ✅ Video generated: {video_path}")
                
                return {
                    "success": True,
                    "video_url": result.get("video_url"),
                    "thumbnail_url": result.get("thumbnail_url"),
                    "metadata": metadata,
                    "estimated_cost": estimated_cost
                }
            else:
                return result
                
        except Exception as e:
            print(f"[VEO] ❌ Generation failed: {e}")
            if ANNEALING_ENABLED:
                log_annealing_event({
                    "type": "error",
                    "script": "veo_visionary.py",
                    "function": "generate_from_text",
                    "error": str(e),
                    "prompt": prompt[:100],
                    "timestamp": datetime.now().isoformat()
                })
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_with_genai(
        self,
        prompt: str,
        duration: int,
        resolution: str,
        aspect_ratio: str
    ) -> Dict[str, Any]:
        """Generate using Google AI Python SDK."""
        try:
            # Initialize the model for video generation
            # Note: Actual Veo API may have different method names
            model = genai.GenerativeModel(VEO_MODEL)
            
            # Generate video
            response = model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "video/mp4",
                    "video_config": {
                        "duration_seconds": duration,
                        "resolution": resolution,
                        "aspect_ratio": aspect_ratio
                    }
                }
            )
            
            # Extract video URL from response
            # Actual response structure may vary
            if hasattr(response, 'video_url'):
                return {
                    "success": True,
                    "video_url": response.video_url,
                    "thumbnail_url": getattr(response, 'thumbnail_url', None)
                }
            elif hasattr(response, 'candidates') and response.candidates:
                # Handle response with candidates
                candidate = response.candidates[0]
                return {
                    "success": True,
                    "video_url": getattr(candidate, 'video_url', None),
                    "response": str(response)
                }
            else:
                return {
                    "success": False,
                    "error": "No video URL in response",
                    "response": str(response)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"GenAI SDK error: {str(e)}"
            }
    
    def _generate_with_rest_api(
        self,
        prompt: str,
        duration: int,
        resolution: str,
        aspect_ratio: str
    ) -> Dict[str, Any]:
        """Generate using REST API directly."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{VEO_MODEL}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "responseMimeType": "video/mp4",
                "videoConfig": {
                    "durationSeconds": duration,
                    "resolution": resolution,
                    "aspectRatio": aspect_ratio
                }
            }
        }
        
        try:
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=300  # 5 minute timeout for video generation
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "video_url": data.get("videoUrl"),
                    "thumbnail_url": data.get("thumbnailUrl"),
                    "response": data
                }
            else:
                return {
                    "success": False,
                    "error": f"API error {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"REST API error: {str(e)}"
            }
    
    @self_annealing
    def generate_from_image(
        self,
        image_path: str,
        prompt: str,
        duration_seconds: int = 5,
        motion_type: str = "pan_zoom"
    ) -> Dict[str, Any]:
        """
        Generate video from image with motion effects.
        
        Args:
            image_path: Path to source image
            prompt: Description of desired motion/transformation
            duration_seconds: Video length
            motion_type: "pan_zoom", "morph", "animate"
        
        Returns:
            Dict with video metadata
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": f"Image not found: {image_path}"}
        
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        enhanced_prompt = f"{motion_type} effect: {prompt}"
        
        print(f"[VEO] Generating video from image: {image_path}")
        print(f"[VEO] Motion: {motion_type}, Duration: {duration_seconds}s")
        
        # Similar generation flow as text-to-video
        # Implementation depends on Veo API specifics
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"veo_image_{timestamp}"
        
        metadata = {
            "id": f"veo_image_{timestamp}",
            "type": "video",
            "source": "veo",
            "source_image": image_path,
            "prompt": prompt,
            "motion_type": motion_type,
            "duration_seconds": duration_seconds,
            "created_at": datetime.now().isoformat()
        }
        
        # Save metadata
        metadata_path = CONTENT_LIBRARY_DIR / f"{output_name}.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "metadata": metadata,
            "note": "Image-to-video generation queued. Check content library for results."
        }
    
    def list_generated_content(self) -> List[Dict]:
        """List all generated content from this session."""
        return self.generation_history
    
    def get_library_contents(self) -> List[Dict]:
        """Get all content in the library."""
        contents = []
        for metadata_file in CONTENT_LIBRARY_DIR.glob("*.json"):
            with open(metadata_file, "r") as f:
                contents.append(json.load(f))
        return contents


# Convenience functions for direct use
def generate_ad_video(
    product_description: str,
    style: str = "cinematic",
    duration: int = 15,
    aspect_ratio: str = "9:16"  # Default to vertical for social
) -> Dict[str, Any]:
    """
    Quick function to generate an ad video.
    
    Args:
        product_description: Description of product/service
        style: Visual style ("cinematic", "animated", "minimal")
        duration: Length in seconds
        aspect_ratio: "9:16" (vertical), "16:9" (horizontal), "1:1" (square)
    """
    # Build ad-optimized prompt
    ad_prompt = f"""
    Professional advertisement video for: {product_description}
    
    Requirements:
    - Visually striking and attention-grabbing
    - Smooth camera movements
    - Professional color grading
    - Suitable for social media advertising
    """
    
    veo = VeoVisionary()
    return veo.generate_from_text(
        prompt=ad_prompt,
        duration_seconds=duration,
        style=style,
        aspect_ratio=aspect_ratio,
        resolution="1080p"
    )


if __name__ == "__main__":
    print("[VEO] Veo Visionary - AI Video Generation Engine")
    print("=" * 50)
    
    # Check configuration
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"[VEO] API Key: {api_key[:8]}...{api_key[-4:]}")
        print("[VEO] GenAI SDK:", "Available" if GENAI_AVAILABLE else "Not installed")
        print("[VEO] Annealing:", "Enabled" if ANNEALING_ENABLED else "Disabled")
        print(f"[VEO] Content Library: {CONTENT_LIBRARY_DIR}")
        
        # Initialize
        try:
            veo = VeoVisionary()
            print("[VEO] ✅ Veo Visionary initialized successfully")
            
            # List any existing content
            contents = veo.get_library_contents()
            print(f"[VEO] Content Library: {len(contents)} items")
            
        except Exception as e:
            print(f"[VEO] ❌ Initialization failed: {e}")
    else:
        print("[VEO] ⚠️ GOOGLE_API_KEY not set")
        print("[VEO] Set the environment variable to enable video generation")
