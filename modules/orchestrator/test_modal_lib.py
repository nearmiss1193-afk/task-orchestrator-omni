import modal
try:
    print(f"Modal version: {modal.__version__}")
    print(f"App exists: {hasattr(modal, 'App')}")
    print(f"Mount exists: {hasattr(modal, 'Mount')}")
    print(f"Secret exists: {hasattr(modal, 'Secret')}")
except Exception as e:
    print(f"Error checking modal: {e}")
