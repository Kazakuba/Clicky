import pyautogui
import subprocess
import time

class AutomationService:
    def execute_action(self, action):
        try:
            if action.action_type == "click":
                pyautogui.click(action.params["x"], action.params["y"], clicks=action.params["clicks"])
            elif action.action_type == "hold":
                pyautogui.mouseDown(action.params["x"], action.params["y"])
                time.sleep(action.params["duration"])
                pyautogui.mouseUp()
            elif action.action_type == "scroll":
                pyautogui.click(action.params["x"], action.params["y"])
                pyautogui.scroll(action.params["amount"], x=action.params["x"], y=action.params["y"])
            elif action.action_type == "drag":
                pyautogui.moveTo(action.params["x1"], action.params["y1"])
                pyautogui.dragTo(action.params["x2"], action.params["y2"], button='left')
            elif action.action_type == "keyboard":
                pyautogui.write(action.params["keys"])
            elif action.action_type == "script":
                subprocess.run(action.params["command"], shell=True, check=True)
            elif action.action_type == "wait for":
                time.sleep(action.params["time"])
            elif action.action_type == "press key":
                pyautogui.press(action.params["key"])
            elif action.action_type == "move mouse to":
                pyautogui.moveTo(action.params["x"], action.params["y"])
        except Exception as e:
            raise RuntimeError(f"Action '{action.action_type}' failed: {e}")

    def execute_workflow(self, workflow):
        for action in workflow.actions:
            self.execute_action(action)
            time.sleep(0.5)