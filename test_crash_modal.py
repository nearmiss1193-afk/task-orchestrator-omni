import modal
from core.apps import engine_app as app
from core.image_config import get_base_image, VAULT

image = get_base_image()

@app.function(image=image, secrets=[VAULT])
def self_healing_test_worker():
    import traceback
    import requests
    from modules.autonomous_inspector import Inspector

    inspector = Inspector()
    print("Initiating Modal Cloud Live-Fire Sequence...")
    
    try:
        # Intentional KeyError
        data = {"status": "ok"}
        result = data["this_key_does_not_exist_in_the_cloud"]
        return result
    except Exception as e:
        print("Crash caught inside Modal. Routing to Abacus Self-Healing Pipeline...")
        # Route to Abacus
        inspector.handle_crash("self_healing_test_worker", e)

@app.local_entrypoint()
def trigger_cloud_crash():
    print("Spawning isolated cloud worker...")
    self_healing_test_worker.remote()

