
import os
import shutil
import time
from datetime import datetime, timedelta

class Archivist:
    """
    The 'Archivist' creates order from chaos.
    It moves stale logs and temp files to the Long-Term Archive.
    """
    def __init__(self, root_dir=None):
        if root_dir is None:
            self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        else:
            self.root_dir = root_dir
            
        self.logs_dir = os.path.join(self.root_dir, "logs")
        self.archive_dir = os.path.join(self.root_dir, "modules", "knowledge", "archive", "logs")
        
        # Ensure archive exists
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)

    def archive_stale_logs(self, days_threshold=7):
        """Moves files older than X days from /logs to /archive"""
        print(f"📦 Archivist: Scanning {self.logs_dir} for files older than {days_threshold} days...")
        
        if not os.path.exists(self.logs_dir):
            print("   -> No /logs directory found. Nothing to archive.")
            return

        cutoff_time = time.time() - (days_threshold * 86400)
        moved_count = 0

        for filename in os.listdir(self.logs_dir):
            file_path = os.path.join(self.logs_dir, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
                
            # Check modification time
            if os.path.getmtime(file_path) < cutoff_time:
                target_path = os.path.join(self.archive_dir, filename)
                try:
                    shutil.move(file_path, target_path)
                    print(f"   -> Archived: {filename}")
                    moved_count += 1
                except Exception as e:
                    print(f"   ❌ Error moving {filename}: {e}")

        if moved_count == 0:
            print("   -> No stale logs found. The workspace is clean.")
        else:
            print(f"   ✅ Archived {moved_count} files to {self.archive_dir}")

if __name__ == "__main__":
    archivist = Archivist()
    # Test run with 0 days (force archive active logs for demo, or set to 7 for prod)
    # Using 1 day for safety in verification
    archivist.archive_stale_logs(days_threshold=1)
