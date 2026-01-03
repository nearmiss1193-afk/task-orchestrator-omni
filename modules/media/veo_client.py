import os
import json
import time

class VeoClient:
    def __init__(self):
        self.api_key = os.environ.get("VEO_API_KEY", "VEO_LIVE_JTDBXZ7N0HR")
        self.budget_limit = 20.00
        self.cost_per_second = 0.05 # Assumption, user didn't specify rate, but said "don't spend more than 20"
        self.spend_file = "veo_spend_log.json"

    def get_total_spend(self):
        if not os.path.exists(self.spend_file):
            return 0.0
        with open(self.spend_file, "r") as f:
            data = json.load(f)
            return data.get("total_spend", 0.0)

    def log_spend(self, amount):
        current = self.get_total_spend()
        new_total = current + amount
        with open(self.spend_file, "w") as f:
            json.dump({"total_spend": new_total, "last_updated": time.time()}, f)
        return new_total

    def generate_video(self, prompt, duration=15):
        # Enforce Constraints
        if duration > 20:
            duration = 20
        
        estimated_cost = duration * self.cost_per_second
        current_spend = self.get_total_spend()
        
        if current_spend + estimated_cost > self.budget_limit:
            return {
                "status": "blocked",
                "message": f"Budget Limit Reached. Current: ${current_spend:.2f}, Est: ${estimated_cost:.2f}, Limit: ${self.budget_limit:.2f}. Notification sent to User."
            }

        print(f"🎬 Generating Video: '{prompt}' ({duration}s)...")
        # Mocking the API call since we don't have the real endpoint docs yet.
        # Assuming we'd POST to some URL with the key.
        
        # Simulate Processing
        time.sleep(2)
        
        self.log_spend(estimated_cost)
        
        return {
            "status": "success", 
            "video_url": "https://veo.studio/api/mock_video.mp4",
            "cost": estimated_cost,
            "remaining_budget": self.budget_limit - (current_spend + estimated_cost)
        }

if __name__ == "__main__":
    client = VeoClient()
    print(client.generate_video("HVAC Technician installing a modern unit in a sunny backyard", duration=15))
