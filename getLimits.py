from pynput import mouse, keyboard

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse clicked at ({x}, {y})")

def on_press(key):
    if key == keyboard.Key.esc:
        # Stop the mouse listener when 'Esc' is pressed
        print("Escape key pressed. Exiting...")
        listener.stop()
        return False  # Stop the keyboard listener

# Start the mouse listener
listener = mouse.Listener(on_click=on_click)
listener.start()

# Start the keyboard listener
with keyboard.Listener(on_press=on_press) as keyboard_listener:
    keyboard_listener.join()