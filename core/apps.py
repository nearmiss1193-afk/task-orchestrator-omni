import modal

# SINGLE SOURCE OF TRUTH FOR MODAL APPS
# All files MUST import these instances to avoid serialization conflicts.
engine_app = modal.App("ghl-omni-automation")
# portal_app = modal.App("ghl-omni-portal") # Temporarily disabled to unblock engine deploy
