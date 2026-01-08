"""
DISPATCH OPTIMIZER
==================
AI routes jobs to closest available tech.
"""
import os
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict

# Sample technicians (in production, from database)
TECHNICIANS = [
    {"id": "tech1", "name": "Mike Johnson", "lat": 27.95, "lng": -82.46, "skills": ["hvac", "electrical"], "available": True, "current_jobs": 1},
    {"id": "tech2", "name": "Dave Wilson", "lat": 28.02, "lng": -82.52, "skills": ["hvac", "plumbing"], "available": True, "current_jobs": 0},
    {"id": "tech3", "name": "Chris Brown", "lat": 27.89, "lng": -82.39, "skills": ["plumbing", "roofing"], "available": True, "current_jobs": 2},
    {"id": "tech4", "name": "James Lee", "lat": 28.10, "lng": -82.61, "skills": ["hvac", "plumbing", "electrical"], "available": False, "current_jobs": 3},
]


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points in miles"""
    R = 3959  # Earth radius in miles
    
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def find_best_tech(job: dict, technicians: List[dict] = None) -> dict:
    """Find the best technician for a job"""
    
    if technicians is None:
        technicians = TECHNICIANS
    
    job_lat = job.get('lat', 27.95)
    job_lng = job.get('lng', -82.46)
    required_skill = job.get('skill_required', 'hvac')
    urgency = job.get('urgency', 'normal')  # normal, urgent, emergency
    
    candidates = []
    
    for tech in technicians:
        # Skip unavailable techs (unless emergency)
        if not tech['available'] and urgency != 'emergency':
            continue
        
        # Check skill match
        if required_skill not in tech['skills']:
            continue
        
        # Calculate distance
        distance = haversine_distance(job_lat, job_lng, tech['lat'], tech['lng'])
        
        # Calculate score (lower is better)
        score = distance * 1.0  # Base: distance
        score += tech['current_jobs'] * 3  # Penalty for busy techs
        
        if urgency == 'emergency':
            score -= 10  # Prioritize emergencies
        
        candidates.append({
            "tech": tech,
            "distance": round(distance, 1),
            "score": round(score, 2),
            "eta_minutes": round(distance * 3 + 10)  # Rough ETA
        })
    
    if not candidates:
        return {"error": "No available technicians with required skills"}
    
    # Sort by score
    candidates.sort(key=lambda x: x['score'])
    best = candidates[0]
    
    return {
        "assigned_tech": best['tech']['name'],
        "tech_id": best['tech']['id'],
        "distance_miles": best['distance'],
        "eta_minutes": best['eta_minutes'],
        "score": best['score'],
        "alternatives": [{"name": c['tech']['name'], "eta": c['eta_minutes']} for c in candidates[1:3]]
    }


def optimize_route(tech_id: str, jobs: List[dict]) -> List[dict]:
    """Optimize route for a tech with multiple jobs"""
    
    # Simple nearest-neighbor algorithm
    optimized = []
    remaining = jobs.copy()
    current_lat, current_lng = 27.95, -82.46  # Start at office
    
    while remaining:
        # Find closest job
        closest = min(remaining, key=lambda j: haversine_distance(
            current_lat, current_lng, j.get('lat', 27.95), j.get('lng', -82.46)
        ))
        
        optimized.append(closest)
        current_lat, current_lng = closest.get('lat', 27.95), closest.get('lng', -82.46)
        remaining.remove(closest)
    
    # Calculate total distance
    total_distance = 0
    prev_lat, prev_lng = 27.95, -82.46
    for job in optimized:
        total_distance += haversine_distance(prev_lat, prev_lng, job.get('lat', 27.95), job.get('lng', -82.46))
        prev_lat, prev_lng = job.get('lat', 27.95), job.get('lng', -82.46)
    
    return {
        "tech_id": tech_id,
        "optimized_route": optimized,
        "total_distance_miles": round(total_distance, 1),
        "estimated_time_hours": round(total_distance / 20 + len(optimized) * 1.5, 1)  # Rough estimate
    }


if __name__ == "__main__":
    test_job = {
        "customer": "John Smith",
        "address": "123 Main St, Tampa, FL",
        "lat": 27.98,
        "lng": -82.48,
        "skill_required": "hvac",
        "urgency": "normal",
        "description": "AC not cooling"
    }
    
    result = find_best_tech(test_job)
    print("Best Tech Assignment:")
    print(json.dumps(result, indent=2))
