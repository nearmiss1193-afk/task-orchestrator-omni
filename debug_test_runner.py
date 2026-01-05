
import subprocess
import sys

def run_tests():
    print("Running tests/test_inbound_logic.py ...")
    result = subprocess.run([sys.executable, "tests/test_inbound_logic.py"], capture_output=True, text=True)
    
    with open("debug_output.log", "w", encoding="utf-8") as f:
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)
        
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

if __name__ == "__main__":
    run_tests()
