print("Hello from test_print.py")
import sys
sys.stdout.flush()
with open("test_output_check.txt", "w") as f:
    f.write("File write worked")
print("File write completed")
