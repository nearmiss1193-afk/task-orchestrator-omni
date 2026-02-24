import modal
from modal.client import Client
import asyncio

async def list_apps():
    client = await Client.from_env()
    print("Fetching active apps for current workspace...")
    apps = await client.list_apps()
    for app in apps:
        print(f"App: {app.name}, ID: {app.app_id}, Workspace: {app.workspace_username}")
        
    print("\nAttempting to query recent logs for 'ghl-omni-automation'...")

if __name__ == "__main__":
    asyncio.run(list_apps())
