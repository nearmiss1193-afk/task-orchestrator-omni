
import random
import json

class AdExecutive:
    def __init__(self, niche="HVAC"):
        self.niche = niche
        self.pain_points = [
            "Missing calls while under a house",
            "Losing leads to competitors at 2 AM",
            "Paying for leads that go to voicemail",
            "Scheduling headaches consuming your evening"
        ]
        self.solutions = [
            "AI Receptionist that never sleeps",
            "Instant text-back for every missed call",
            "Auto-booking directly into your calendar",
            "Qualifying leads before you even speak to them"
        ]

    def generate_ad_pack(self, angle_type="pain_focused"):
        if angle_type == "pain_focused":
            headline = f"Stop Losing {self.niche} Jobs to Missed Calls."
            primary_text = (
                f"You're stuck in an attic fixing a unit. Your phone rings. You can't answer.\n\n"
                f"That was a $12,000 install. And they just called your competitor.\n\n"
                f"Stop bleeding revenue. Our AI Office Manager answers every call, 24/7, books appointments, "
                f"and qualifies leads while you work.\n\n"
                f"✅ 0 Missed Calls\n✅ Instant ROI\n✅ No Sick Days\n\n"
                f"Click below to hear a live demo."
            )
            image_prompt = (
                f"Hyper-realistic photo of a stressed {self.niche} technician crawling in a dark, tight attic space, "
                f"looking at his ringing smartphone which is just out of reach. High contrast, gritty, cinematic lighting. "
                f"Text overlay in red neon style: 'MISSED CALL = LOST MONEY'"
            )
        
        elif angle_type == "logic_focused":
            headline = f"Hire a 24/7 Receptionist for $3/Day."
            primary_text = (
                f"Hiring a human office manager: $45,000/year + Benefits + Training.\n"
                f"Hiring our AI Receptionist: A fraction of the cost. Zero drama.\n\n"
                f"It answers phones, texts back instantly, and integrates with your CRM. "
                f"Scale your {self.niche} business without increasing overhead.\n\n"
                f"Try it risk-free for 7 days."
            )
            image_prompt = (
                f"Split screen comparison. Left side: Stressed office desk piled with paper, dark lighting. "
                f"Right side: Sleek, glowing blue futuristic AI interface visualization on a clean desk, bright lighting. "
                f"Text overlay: 'OLD WAY vs NEW WAY'"
            )

        elif angle_type == "urgent_offer":
            headline = "Free 'Missed Call' Audit for HVAC Owners."
            primary_text = (
                f"How many leads did you miss last month? We'll tell you.\n\n"
                f"We are giving away 10 free audits this week to {self.niche} owners in [City]. "
                f"See exactly how much revenue you're leaving on the table.\n\n"
                f"Plus, get a free 7-day trial of the AI that fixes it."
            )
            image_prompt = (
                f"Close up realistic shot of a smartphone screen showing a list of 'Missed Calls' in red. "
                f"Background is a blurred HVAC van. "
                f"Overlay text: 'STOP THE BLEEDING'"
            )

        return {
            "angle": angle_type,
            "headline": headline,
            "primary_text": primary_text,
            "image_prompt": image_prompt
        }

if __name__ == "__main__":
    agent = AdExecutive()
    campaign = [
        agent.generate_ad_pack("pain_focused"),
        agent.generate_ad_pack("logic_focused"),
        agent.generate_ad_pack("urgent_offer")
    ]
    print(json.dumps(campaign, indent=2))
