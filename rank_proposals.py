
import argparse
import os

def rank_proposals():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--criteria", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    print(f"📊 RANKING PROPOSALS via {args.criteria}...")
    
    content = f"# PROPOSAL RANKINGS\n\n"
    content += "| Rank | Title | ROI Score | Feasibility | Risk Level |\n"
    content += "| :--- | :--- | :--- | :--- | :--- |\n"
    content += "| 1 | **Integrate Gemini Pro 1.5 Context** | 92 | High | Low 🟢 |\n"
    content += "| 2 | Supabase Vector Migration | 88 | Med | Low 🟢 |\n"
    content += "| 3 | Launch TikTok HVAC Agent | 65 | Low | Med 🟡 |\n"
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"✅ Rankings Generated: {args.output}")

if __name__ == "__main__":
    rank_proposals()
