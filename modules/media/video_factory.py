
import os
try:
    from moviepy.editor import ImageClip, CompositeVideoClip
except ImportError:
    print("MoviePy not installed. Run: pip install moviepy")

def create_ken_burns_loop(image_path, output_filename, duration=5.0):
    """
    Turns a static screenshot into a premium 5-second silent loop 
    with a 'Ken Burns' zoom effect.
    Text overlays are handled by CSS on the frontend for maximum sharpness.
    """
    if not os.path.exists(image_path):
        print(f"⚠️ Image not found: {image_path}")
        return None

    try:
        # 1. Load Image
        # Resize to ensuring it's large enough (e.g. 1080p width base)
        # Note: In a real serverless env, we'd need to handle aspect ratios carefully.
        img = ImageClip(image_path)
        w, h = img.size
        
        # 2. The Zoom Effect
        # We resize it from 1.0 to 1.05 over 'duration' seconds
        # 'resize' with logic requires a lambda t: factor
        # We start at 1.0 (original) and grow to 1.05 (5% zoom)
        # We set the position to center to zoom into the middle
        zoomed_clip = (img
                       .resize(lambda t: 1 + 0.05 * (t / duration)) 
                       .set_position('center')
                       .set_duration(duration))

        # 3. Export
        # We use a lower crf for quality, but preset ultrafast for speed
        zoomed_clip.write_videofile(
            output_filename, 
            fps=24, 
            codec='libx264', 
            audio=False, 
            preset='medium',
            threads=4
        )
        print(f"✅ Generated Commercial Loop: {output_filename}")
        return output_filename

    except Exception as e:
        print(f"❌ Video Generation Failed: {e}")
        return None

if __name__ == "__main__":
    # Test Run
    # Assume we have a placeholder image
    pass
