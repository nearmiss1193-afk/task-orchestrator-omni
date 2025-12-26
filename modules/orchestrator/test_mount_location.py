import modal
try:
    from modal.mount import Mount
    print(f"Imported Mount from modal.mount: {Mount}")
except Exception as e:
    print(f"Failed to import Mount from modal.mount: {e}")

try:
    print(f"Checking modal.Mount: {getattr(modal, 'Mount', 'Not found')}")
except Exception as e:
    print(f"Error checking modal.Mount: {e}")
