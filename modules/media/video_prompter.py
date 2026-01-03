
import random

class VideoPrompter:
    def __init__(self):
        print("🎬 Initializing Cinematic Architect (Video Prompt Engine)...")
        # Style Presets
        self.styles = {
            "cinematic_commercial": "shot on 35mm, Arri Alexa, anamorphic lens, golden hour lighting, cinematic film grain, 4k, hyper-realistic, shallow depth of field, slow motion 60fps",
            "modern_saas": "clean minimalism, bright studio lighting, white background, tech aesthetic, 4k, sharp focus, smooth camera pan, corporate memphis 3d style",
            "viral_ugc": "shot on iPhone 15 Pro, vertical 9:16, handheld camera shake, authentic lighting, raw footage style, POV perspective, social media aesthetic"
        }
        
    def generate_prompt(self, concept, vibe="cinematic_commercial"):
        """
        Transforms a raw concept into a Hollywood-grade prompt.
        """
        modifier_string = self.styles.get(vibe, self.styles["cinematic_commercial"])
        
        # Structure the prompt for Video AI (Subject + Action + Environment + Camera + Lighting + Style)
        final_prompt = f"{concept}. {modifier_string}."
        
        return final_prompt

    def batch_generate(self, ad_concepts, vibe="cinematic_commercial"):
        """
        Takes a list of concepts and returns formatted prompts.
        """
        print(f"\n🎬 GENERATING BATCH ({vibe}):")
        prompts = []
        for concept in ad_concepts:
            p = self.generate_prompt(concept, vibe)
            prompts.append(p)
            print(f"   [SCENE]: {concept}")
            print(f"   [PROMPT]: {p}\n")
        
        return prompts

if __name__ == "__main__":
    architect = VideoPrompter()
    
    # Test Concepts (HVAC)
    concepts = [
        "A branded white HVAC van driving through a stormy suburban neighborhood with palm trees bending in the wind",
        "Close up of an old rusted AC unit dripping water in slow motion",
        "A happy family sitting in a cool living room drinking iced tea, safe from the heat"
    ]
    
    architect.batch_generate(concepts, vibe="cinematic_commercial")
