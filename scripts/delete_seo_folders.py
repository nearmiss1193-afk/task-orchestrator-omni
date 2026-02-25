import os
import shutil

base_dir = r'C:/Users/nearm/.gemini/antigravity/scratch/empire-unified/apps/portal/src/app'

# Safety checks: only delete directories that have hyphens and specific SEO prefixes
valid_prefixes = [
    'ai-phone-agent-for-',
    'ai-receptionist-for-',
    'automated-booking-system-for-',
    'voice-ai-for-',
    'ai-secretary-for-'
]

deleted_count = 0

for item in os.listdir(base_dir):
    full_path = os.path.join(base_dir, item)
    
    if os.path.isdir(full_path):
        # Check against prefixes
        is_seo_folder = any(item.startswith(prefix) for prefix in valid_prefixes)
        
        if is_seo_folder:
            shutil.rmtree(full_path)
            deleted_count += 1
            if deleted_count % 100 == 0:
                print(f"Deleted {deleted_count} SEO folders...")

print(f"✅ Cleanup Complete! Masterfully purged {deleted_count} static SEO folders from the codebase.")
