import os
from pathlib import Path

def get_directory_stats(root_dir):
    print(f"Scanning {root_dir}...")
    root_path = Path(root_dir)
    dir_stats = []

    try:
        # Scan top-level directories in the scratch folder
        for item in root_path.iterdir():
            if item.is_dir() and item.name not in ['.git', '.gemini', 'empire-unified-bloat', 'node_modules']:
                total_size = 0
                file_count = 0
                try:
                    for root, dirs, files in os.walk(item):
                        file_count += len(files)
                        for f in files:
                            fp = os.path.join(root, f)
                            if not os.path.islink(fp):
                                total_size += os.path.getsize(fp)
                    
                    dir_stats.append({
                        'name': item.name,
                        'size_mb': total_size / (1024 * 1024),
                        'files': file_count
                    })
                except Exception as e:
                    print(f"Error scanning {item.name}: {e}")

        # Sort by size
        dir_stats.sort(key=lambda x: x['size_mb'], reverse=True)
        
        print(f"{'Directory':<40} | {'Size (MB)':<10} | {'Files':<10}")
        print("-" * 65)
        for stat in dir_stats:
            print(f"{stat['name']:<40} | {stat['size_mb']:<10.2f} | {stat['files']:<10}")

    except Exception as e:
        print(f"Global error: {e}")

if __name__ == "__main__":
    get_directory_stats(".")
