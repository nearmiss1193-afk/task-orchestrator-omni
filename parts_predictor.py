"""
PARTS PREDICTOR
===============
Predict parts needed based on call description.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')

# Common parts inventory
COMMON_PARTS = {
    "hvac": {
        "capacitor": {"price": 45, "in_stock": 15},
        "contactor": {"price": 65, "in_stock": 8},
        "fan_motor": {"price": 185, "in_stock": 4},
        "compressor": {"price": 850, "in_stock": 2},
        "thermostat": {"price": 95, "in_stock": 12},
        "refrigerant_r410a": {"price": 75, "in_stock": 20},
        "filter": {"price": 25, "in_stock": 50},
    },
    "plumbing": {
        "faucet": {"price": 85, "in_stock": 10},
        "garbage_disposal": {"price": 150, "in_stock": 5},
        "water_heater_element": {"price": 45, "in_stock": 8},
        "pex_tubing_100ft": {"price": 120, "in_stock": 6},
        "p_trap": {"price": 15, "in_stock": 25},
    }
}


def predict_parts(issue_description: str, service_type: str = "hvac") -> dict:
    """Predict parts needed based on issue description"""
    
    prompt = f"""Based on this service issue, predict which parts will likely be needed:

Issue: {issue_description}
Service Type: {service_type}

Available parts: {list(COMMON_PARTS.get(service_type, {}).keys())}

Return JSON:
{{
    "likely_parts": [
        {{"part": "part_name", "probability": 0.0-1.0, "reason": "why"}}
    ],
    "estimated_repair_time_hours": 0.0,
    "difficulty": "easy/medium/hard",
    "notes": "any special considerations"
}}"""

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-3-mini",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            prediction = json.loads(response.json()['choices'][0]['message']['content'])
            
            # Add inventory info
            inventory = COMMON_PARTS.get(service_type, {})
            for part in prediction.get('likely_parts', []):
                part_name = part['part']
                if part_name in inventory:
                    part['price'] = inventory[part_name]['price']
                    part['in_stock'] = inventory[part_name]['in_stock']
            
            return prediction
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
    
    return {"error": "Prediction failed"}


def check_inventory(parts: list, service_type: str = "hvac") -> dict:
    """Check if predicted parts are in stock"""
    inventory = COMMON_PARTS.get(service_type, {})
    
    results = []
    total_cost = 0
    all_in_stock = True
    
    for part in parts:
        part_name = part.get('part', '')
        if part_name in inventory:
            in_stock = inventory[part_name]['in_stock'] > 0
            results.append({
                "part": part_name,
                "in_stock": in_stock,
                "quantity": inventory[part_name]['in_stock'],
                "price": inventory[part_name]['price']
            })
            total_cost += inventory[part_name]['price']
            if not in_stock:
                all_in_stock = False
    
    return {
        "parts": results,
        "estimated_parts_cost": total_cost,
        "all_in_stock": all_in_stock
    }


if __name__ == "__main__":
    test_issue = "AC unit is not cooling. Hears clicking sound when trying to start. Unit is 12 years old."
    
    prediction = predict_parts(test_issue, "hvac")
    print("Parts Prediction:")
    print(json.dumps(prediction, indent=2))
