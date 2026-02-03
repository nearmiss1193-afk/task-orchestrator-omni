
import sys
import json
from datetime import datetime

def generate_report(data_json):
    """
    Deterministic report generation logic.
    Layer 3: Reliable, fast, testable.
    """
    try:
        data = json.loads(data_json)
        funnels = data.get('funnels', [])
        pipelines = data.get('pipelines', [])
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_funnels": len(funnels),
                "total_pipelines": len(pipelines)
            },
            "funnel_list": funnels,
            "pipeline_list": pipelines,
            "status": "DETERMINISTIC_SUCCESS"
        }
        return json.dumps(report, indent=2)
    except Exception as e:
        return json.dumps({"status": "ERROR", "message": str(e)})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(generate_report(sys.argv[1]))
    else:
        print(json.dumps({"status": "ERROR", "message": "No data provided"}))
