
import pyautogui
import time

class InputModule:
    """
    Handles physical inputs (Mouse/Keyboard).
    Includes FAILSAFE: Slam mouse to top-left to abort.
    """
    pyautogui.FAILSAFE = True
    
    @staticmethod
    def move_mouse(x, y, duration=0.5):
        print(f"🖱️ Moving Mouse to ({x}, {y})...")
        pyautogui.moveTo(x, y, duration=duration)
        
    @staticmethod
    def type_text(text, interval=0.05):
        print(f"kB Typing: {text}")
        pyautogui.write(text, interval=interval)
        
    @staticmethod
    def click():
        pyautogui.click()
        
    @staticmethod
    def take_screenshot(path="screenshot.png"):
        print(f"📸 Taking Screenshot -> {path}")
        try:
            shot = pyautogui.screenshot()
            shot.save(path)
            return path
        except Exception as e:
            print(f"❌ Screenshot Failed: {e}")
            return None

if __name__ == "__main__":
    # Test
    print("Testing Input Module in 3 seconds (Abort: Slam Mouse Top-Left)...")
    time.sleep(3)
    InputModule.move_mouse(100, 100)
    InputModule.take_screenshot("test_shot.png")
