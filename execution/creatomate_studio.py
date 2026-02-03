"""
Creatomate Studio - Cloud Video Editing API
============================================

Replaces Descript with Creatomate for easier API automation.
Features: Templates, text-to-video, auto-captions, cloud rendering.

Part of the Content Engine & Social Command Center.
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Self-annealing integration
try:
    from annealing_engine import self_annealing, log_annealing_event
    ANNEALING_ENABLED = True
except ImportError:
    ANNEALING_ENABLED = False
    def self_annealing(func):
        return func

# Configuration
CREATOMATE_API_BASE = "https://api.creatomate.com/v1"
CONTENT_LIBRARY_DIR = Path(__file__).parent.parent / "content_library"

# Export presets for different platforms
EXPORT_PRESETS = {
    "youtube": {"width": 1920, "height": 1080, "aspect_ratio": "16:9"},
    "instagram_feed": {"width": 1080, "height": 1080, "aspect_ratio": "1:1"},
    "instagram_reels": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
    "tiktok": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
    "twitter": {"width": 1280, "height": 720, "aspect_ratio": "16:9"},
    "linkedin": {"width": 1920, "height": 1080, "aspect_ratio": "16:9"},
    "facebook": {"width": 1080, "height": 1080, "aspect_ratio": "1:1"},
}


class CreatomateStudio:
    """
    Cloud video editing using Creatomate API.
    
    Much easier to automate than Descript - simple REST API with templates.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Creatomate Studio.
        
        Args:
            api_key: Creatomate API key. Falls back to CREATOMATE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("CREATOMATE_API_KEY")
        
        if not self.api_key:
            print("[CREATOMATE] Warning: CREATOMATE_API_KEY not set")
        
        CONTENT_LIBRARY_DIR.mkdir(exist_ok=True)
        self.renders = []
    
    def _headers(self) -> Dict[str, str]:
        """Get API headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @self_annealing
    def render_from_template(
        self,
        template_id: str,
        modifications: Dict[str, Any],
        output_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Render video from a Creatomate template.
        
        Args:
            template_id: Creatomate template ID
            modifications: Dynamic content to insert
            output_name: Custom output filename
        
        Returns:
            Render status with URL
        """
        if not self.api_key:
            return {"success": False, "error": "CREATOMATE_API_KEY not configured"}
        
        print(f"[CREATOMATE] Rendering template: {template_id}")
        
        try:
            response = requests.post(
                f"{CREATOMATE_API_BASE}/renders",
                headers=self._headers(),
                json={
                    "template_id": template_id,
                    "modifications": modifications
                }
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                render_id = result[0].get("id") if isinstance(result, list) else result.get("id")
                
                print(f"[CREATOMATE] Render started: {render_id}")
                
                # Poll for completion
                return self._wait_for_render(render_id, output_name)
            else:
                return {"success": False, "error": f"API error: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @self_annealing
    def render_from_json(
        self,
        source: Dict[str, Any],
        output_format: str = "mp4",
        platform: str = "youtube"
    ) -> Dict[str, Any]:
        """
        Render video from JSON definition (no template needed).
        
        Args:
            source: JSON video definition
            output_format: Output format (mp4, gif, etc.)
            platform: Target platform for sizing
        
        Returns:
            Render result
        """
        if not self.api_key:
            return {"success": False, "error": "CREATOMATE_API_KEY not configured"}
        
        preset = EXPORT_PRESETS.get(platform, EXPORT_PRESETS["youtube"])
        
        # Add dimensions to source
        source["width"] = preset["width"]
        source["height"] = preset["height"]
        source["output_format"] = output_format
        
        print(f"[CREATOMATE] Rendering for {platform}: {preset['width']}x{preset['height']}")
        
        try:
            response = requests.post(
                f"{CREATOMATE_API_BASE}/renders",
                headers=self._headers(),
                json={"source": source}
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                render_id = result[0].get("id") if isinstance(result, list) else result.get("id")
                return self._wait_for_render(render_id)
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _wait_for_render(
        self,
        render_id: str,
        output_name: Optional[str] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Wait for render to complete.
        
        Args:
            render_id: Render job ID
            output_name: Custom output filename
            timeout: Max wait time in seconds
        
        Returns:
            Final render result
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f"{CREATOMATE_API_BASE}/renders/{render_id}",
                    headers=self._headers()
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    
                    if status == "succeeded":
                        video_url = result.get("url")
                        
                        # Save metadata
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_name = output_name or f"creatomate_{timestamp}"
                        
                        metadata = {
                            "id": f"creatomate_{timestamp}",
                            "type": "video",
                            "source": "creatomate",
                            "render_id": render_id,
                            "video_url": video_url,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        metadata_path = CONTENT_LIBRARY_DIR / f"{output_name}.json"
                        with open(metadata_path, "w") as f:
                            json.dump(metadata, f, indent=2)
                        
                        self.renders.append(metadata)
                        
                        print(f"[CREATOMATE] ✅ Render complete: {video_url[:50]}...")
                        
                        return {
                            "success": True,
                            "render_id": render_id,
                            "video_url": video_url,
                            "metadata": metadata
                        }
                    
                    elif status == "failed":
                        return {
                            "success": False,
                            "error": result.get("error_message", "Render failed")
                        }
                    
                    # Still processing
                    print(f"[CREATOMATE] Status: {status}...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"[CREATOMATE] Poll error: {e}")
                time.sleep(5)
        
        return {"success": False, "error": "Render timeout"}
    
    @self_annealing
    def create_text_video(
        self,
        text: str,
        duration: float = 5.0,
        background_color: str = "#000000",
        text_color: str = "#FFFFFF",
        platform: str = "instagram_reels"
    ) -> Dict[str, Any]:
        """
        Create a simple text video (no template needed).
        
        Args:
            text: Text to display
            duration: Video duration in seconds
            background_color: Background hex color
            text_color: Text hex color
            platform: Target platform for sizing
        
        Returns:
            Render result
        """
        preset = EXPORT_PRESETS.get(platform, EXPORT_PRESETS["instagram_reels"])
        
        source = {
            "output_format": "mp4",
            "width": preset["width"],
            "height": preset["height"],
            "elements": [
                {
                    "type": "composition",
                    "duration": duration,
                    "elements": [
                        {
                            "type": "shape",
                            "width": "100%",
                            "height": "100%",
                            "fill_color": background_color
                        },
                        {
                            "type": "text",
                            "text": text,
                            "width": "80%",
                            "x": "50%",
                            "y": "50%",
                            "x_anchor": "50%",
                            "y_anchor": "50%",
                            "fill_color": text_color,
                            "font_size": "8 vmin",
                            "font_weight": "700",
                            "text_align": "center"
                        }
                    ]
                }
            ]
        }
        
        return self.render_from_json(source, platform=platform)
    
    @self_annealing
    def create_video_with_caption(
        self,
        video_url: str,
        caption_text: str,
        caption_style: str = "bottom",
        platform: str = "instagram_reels"
    ) -> Dict[str, Any]:
        """
        Add captions/text overlay to existing video.
        
        Args:
            video_url: URL to source video
            caption_text: Caption text
            caption_style: "bottom", "top", or "center"
            platform: Target platform
        
        Returns:
            Render result with captioned video
        """
        preset = EXPORT_PRESETS.get(platform, EXPORT_PRESETS["instagram_reels"])
        
        y_position = {"bottom": "90%", "top": "10%", "center": "50%"}
        
        source = {
            "output_format": "mp4",
            "width": preset["width"],
            "height": preset["height"],
            "elements": [
                {
                    "type": "video",
                    "source": video_url,
                    "width": "100%",
                    "height": "100%"
                },
                {
                    "type": "text",
                    "text": caption_text,
                    "width": "90%",
                    "x": "50%",
                    "y": y_position.get(caption_style, "90%"),
                    "x_anchor": "50%",
                    "y_anchor": "50%",
                    "fill_color": "#FFFFFF",
                    "stroke_color": "#000000",
                    "stroke_width": "1.5 vmin",
                    "font_size": "5 vmin",
                    "font_weight": "700",
                    "text_align": "center"
                }
            ]
        }
        
        return self.render_from_json(source, platform=platform)
    
    def list_templates(self) -> Dict[str, Any]:
        """List available templates."""
        if not self.api_key:
            return {"success": False, "error": "API key not configured"}
        
        try:
            response = requests.get(
                f"{CREATOMATE_API_BASE}/templates",
                headers=self._headers()
            )
            
            if response.status_code == 200:
                return {"success": True, "templates": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def render_for_all_platforms(
        self,
        template_id: str,
        modifications: Dict[str, Any],
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Render same content for multiple platforms.
        
        Args:
            template_id: Template ID
            modifications: Dynamic content
            platforms: Target platforms (default: main social)
        
        Returns:
            Results per platform
        """
        platforms = platforms or ["youtube", "instagram_reels", "tiktok", "twitter"]
        results = {}
        
        for platform in platforms:
            print(f"[CREATOMATE] Rendering for {platform}...")
            
            # Add platform-specific dimensions
            preset = EXPORT_PRESETS.get(platform, EXPORT_PRESETS["youtube"])
            mods = {
                **modifications,
                "width": preset["width"],
                "height": preset["height"]
            }
            
            result = self.render_from_template(
                template_id, 
                mods, 
                output_name=f"creatomate_{platform}_{datetime.now().strftime('%H%M%S')}"
            )
            results[platform] = result
            
            time.sleep(1)  # Rate limiting
        
        return {
            "success": all(r.get("success") for r in results.values()),
            "renders": results
        }


# Convenience functions
def quick_text_video(text: str, platform: str = "instagram_reels") -> Dict[str, Any]:
    """Create a quick text video."""
    studio = CreatomateStudio()
    return studio.create_text_video(text, platform=platform)


def add_captions(video_url: str, caption: str) -> Dict[str, Any]:
    """Add captions to a video."""
    studio = CreatomateStudio()
    return studio.create_video_with_caption(video_url, caption)


if __name__ == "__main__":
    print("[CREATOMATE] Creatomate Studio - Cloud Video Editing")
    print("=" * 55)
    
    api_key = os.getenv("CREATOMATE_API_KEY")
    if api_key:
        print(f"[CREATOMATE] API Key: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("[CREATOMATE] ⚠️ CREATOMATE_API_KEY not set")
        print("[CREATOMATE] Get your key at: https://creatomate.com")
    
    print()
    print("[CREATOMATE] Available export presets:")
    for platform, preset in EXPORT_PRESETS.items():
        print(f"  - {platform}: {preset['width']}x{preset['height']}")
    
    print()
    print(f"[CREATOMATE] Content Library: {CONTENT_LIBRARY_DIR}")
