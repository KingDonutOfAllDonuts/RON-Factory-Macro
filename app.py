import os
import time
from pynput import keyboard, mouse
import pydirectinput
import bettercam
from ultralytics import YOLO
import torch
import tkinter as tk

THRESHOLD = 0.5
MIN_X = 180 #later just make it click on corner
MIN_Y = 120
MAX_Y = 952

FACTORY_X = 77
FACTORY_Y = {
  "civilian": 610,
  "motor": 643,
  "fertilizer": 679,
  "steel": 719,
  "electronics": 757
}

BUILDING_X = 326
BUILDING_Y = 783
pydirectinput.PAUSE = 0.04

class FactoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Factory Macro")
        self.factories = {
            "civilian": tk.IntVar(),
            "motor": tk.IntVar(),
            "fertilizer": tk.IntVar(),
            "steel": tk.IntVar(),
            "electronics": tk.IntVar(),
        }
        self.current_hotkey = None
        self.listener = None
        self.stack_factories = tk.BooleanVar(value=False)

        self.create_widgets()

    
    def moveMouse(self, x, y):
      pydirectinput.moveTo(x+1, y+1)
      pydirectinput.moveTo(x, y) #update game
    
    def entryValidationCallback(self, P):
      if str.isdigit(P) or P == "":
          return True
      else:
          return False
    
    def create_widgets(self):
        row = 0
        for factory, var in self.factories.items():
            label = tk.Label(self.root, text=f"{factory.capitalize()} Factories:")
            label.grid(row=row, column=0, padx=10, pady=5)
            
            vcmd = (self.root.register(self.entryValidationCallback))
            entry = tk.Entry(self.root, textvariable=var, validate='all', validatecommand=(vcmd, '%P'))
            entry.grid(row=row, column=1, padx=10, pady=5)
            
            def deselect_entry(event):
              entry.selection_clear()
            entry.bind("<FocusOut>", deselect_entry)
            
            row += 1

        # Checkbox for stacking factories
        self.stack_checkbox = tk.Checkbutton(
            self.root, text="Stack Factories", variable=self.stack_factories
        )
        self.stack_checkbox.grid(row=row, columnspan=2, pady=5)
        
        row += 1
        
        self.status_label = tk.Label(self.root, text="WAITING FOR COMMAND", fg="blue")
        self.status_label.grid(row=row, columnspan=2, pady=5)
        
        row += 1
        
        self.create_button = tk.Button(self.root, text="Create Factories", command=self.create_factories)
        self.create_button.grid(row=row, columnspan=2, pady=10)

        self.hotkey_label = tk.Label(self.root, text="Press 'Set Hotkey' to define a hotkey", fg="blue")
        self.hotkey_label.grid(row=row + 1, columnspan=2, pady=10)
        
        self.set_hotkey_button = tk.Button(self.root, text="Set Hotkey", command=self.set_hotkey)
        self.set_hotkey_button.grid(row=row + 2, columnspan=2, pady=10)

    def create_factories(self):
      # Take a screenshot
      screenshot = camera.grab(region=(0, 0, 1920, 1080))
      if screenshot is None:
        print("fail")
        return

      # Use YOLO model to detect objects
      results = model(screenshot, device=device, verbose=False, conf=THRESHOLD)[0]
      stackFactories = self.stack_factories.get()
      factories = {
            "civilian": self.factories["civilian"].get(),
            "motor": self.factories["motor"].get(),
            "fertilizer": self.factories["fertilizer"].get(),
            "steel": self.factories["steel"].get(),
            "electronics": self.factories["electronics"].get(),
        }
      it = iter(factories.keys())
      
      detections = []

      for result in results.boxes.data.tolist():
          x1, y1, x2, y2, score, class_id = result
          center_x = int((x1 + x2) / 2)
          center_y = int((y1 + y2) / 2)
          
          detections.append((center_x, center_y))
      # Click on all detected objects with a 0.1-second interval
      for (center_x, center_y) in detections:
          if center_y>MIN_Y & center_y<MIN_X:
            self.moveMouse(center_x, center_y)
            
            pydirectinput.keyDown('shift') 
            pydirectinput.click() 
            pydirectinput.keyUp('shift')
            time.sleep(.1)
            
            #click factories
            empty=True
            for name in factories:
              if factories[name] != 0:
                empty = False
                break
            if empty:
              break
            self.moveMouse(BUILDING_X, BUILDING_Y)
            time.sleep(.2)
            pydirectinput.click()
            if stackFactories:    
              for _ in factories:
                factory = next(it, None)
                if factories[factory] > 0:
                  self.moveMouse(FACTORY_X, FACTORY_Y[factory])
                  time.sleep(.15)
                  pydirectinput.click()
                  factories[factory]-=1
              it = iter(factories.keys())
            else:
              factory = next(it, "")
              while (factory == "" or factories[factory] <= 0):
                if (factory == ""):
                  it = iter(factories.keys())
                factory = next(it, "")
              self.moveMouse(FACTORY_X, FACTORY_Y[factory])
              time.sleep(.15)
              pydirectinput.click()
              factories[factory]-=1 
            
            
            # no pop up
            self.moveMouse(1920, 1080)
            pydirectinput.click()
            time.sleep(0.05)  # delay wait for game to react
      if (len(detections) > 0):
        last = detections[len(detections)-1]
        pydirectinput.moveTo(last[0], last[1])
      
    def set_hotkey(self):
        self.hotkey_label.config(text="Press a key to set it as your hotkey...")

        # Temporarily disable the Set Hotkey button to prevent multiple clicks
        self.set_hotkey_button.config(state=tk.DISABLED)

        def on_press(key):
            try:
                # Store the key as a string
                self.current_hotkey = key.char if hasattr(key, 'char') else key.name
                self.hotkey_label.config(text=f"Hotkey set to: '{self.current_hotkey}'")

            except Exception as e:
                self.hotkey_label.config(text=f"Error: {str(e)}")
                print(f"Error: {str(e)}")

            if self.listener:
                self.listener.stop()  # Stop the listener to avoid multiple instances
            
            self.set_hotkey_button.config(state=tk.NORMAL)  # Re-enable the button
            self.create_hotkey_listener()
            return False  # Stop listener after setting hotkey

        # Start a listener to capture the hotkey
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def on_activate(self):
        self.create_factories()
        
    def create_hotkey_listener(self):
        if self.listener:
            self.listener.stop()

        # Check if the hotkey is set before creating GlobalHotKeys listener
        if self.current_hotkey:
            try:
                hotkey_format = f'<{self.current_hotkey}>' if len(self.current_hotkey) > 1 else self.current_hotkey
                self.listener = keyboard.GlobalHotKeys({
                    hotkey_format: self.on_activate
                })
                self.listener.start()
                self.hotkey_label.config(text=f"Hotkey '{self.current_hotkey}' is active. Press it to create factories.")
            except Exception as e:
                self.hotkey_label.config(text=f"Error setting hotkey: {e}")
                print(f"Error setting hotkey: {e}")
    def on_closing(self):
        if self.listener:
            self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    
    # Load the YOLO model
    model_path = os.path.join('.', 'models', 'square_detector.pt')
    model = YOLO(model_path)

    camera = bettercam.create(output_color="BGR")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
  
    root = tk.Tk()
    app = FactoryApp(root) 
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()