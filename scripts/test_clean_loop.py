import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from workers.outreach import auto_outreach_loop

class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")
        
    def write(self, message):
        self.log.write(message)
        
    def flush(self):
        self.log.flush()

if __name__ == "__main__":
    sys.stdout = Logger("clean_loop_output.txt")
    
    print("Testing auto_outreach_loop locally...")
    try:
        auto_outreach_loop()
    except Exception as e:
        import traceback
        print("EXCEPTION IN LOOP:")
        traceback.print_exc()
        
    print("Done")
