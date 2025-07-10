import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import messagebox
import win32api
import win32gui
import win32con
from sys import exit

class TransparentWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.transparency_value = 128
        self.bg_color = '#000000'
        self.error_shown = False  # Initialize error_shown
        self.initUI()

    def initUI(self):
        self.title("Transparent Click-Through Window")

        # Configure window background color
        self.configure(bg=self.bg_color)

        # Maximize the window and remove the title bar
        self.attributes('-fullscreen', True)
        self.wm_attributes('-topmost', 1)  # Make the window stay on top
        self.overrideredirect(1)  # Remove title bar and borders

        # Schedule the click-through setup to run after the main loop starts
        self.after(100, self.make_window_click_through)

        # Create a separate control window
        self.create_control_window()

    def create_control_window(self):
        control_window = tk.Toplevel(self)
        control_window.title("Control Panel")

        # Transparency slider
        self.slider = tk.Scale(control_window, from_=0, to=255, orient=tk.HORIZONTAL, label='Transparency', command=self.update_transparency)
        self.slider.set(self.transparency_value)
        self.slider.pack(fill=tk.X)

        # Color palette button
        self.color_button = tk.Button(control_window, text='Choose Color', command=self.choose_color)
        self.color_button.pack(fill=tk.X)

        def on_closing():
            self.quit() # Use self.quit() for cleaner Tkinter exit
            exit() # Ensure process exits if quit isn't enough

        control_window.protocol("WM_DELETE_WINDOW", on_closing)

    def make_window_click_through(self):
        self.hwnd = win32gui.GetParent(self.winfo_id())

        # Set window style to layered and transparent
        current_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE,
                               current_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

        # Set initial transparency using LWA_ALPHA.
        # The color key (second param, 0) is ignored when LWA_ALPHA is used alone.
        win32gui.SetLayeredWindowAttributes(self.hwnd, 0, self.transparency_value, win32con.LWA_ALPHA)

    def reset_error_flag(self):
        self.error_shown = False

    def update_transparency(self, value_str): # Scale command passes string value
        value = int(value_str)
        if not hasattr(self, 'hwnd') or not self.hwnd:
            # This can happen if the slider is moved before make_window_click_through completes
            # Or if make_window_click_through fails. Store value, will be applied when hwnd is ready.
            self.transparency_value = value
            return

        if value <= 210:
            self.transparency_value = value
            # If error was shown, and now value is OK, reset flag if it's not scheduled by 'after'
            # No, this is not quite right. reset_error_flag should be called by the 'after' if messagebox was shown.
            # If user manually slides back to <=210, error_shown should be reset.
            if self.error_shown and value <= 200: # If it was set to 200 by error, and user goes lower
                 self.error_shown = False

            win32gui.SetLayeredWindowAttributes(self.hwnd, 0, self.transparency_value, win32con.LWA_ALPHA)
        else: # value > 210
            if not self.error_shown:
                self.error_shown = True # Set flag immediately
                messagebox.showerror("Too Dim", "It's going to be too dim, you may not be able to see the screen")
                # User acknowledged the error. Set slider and transparency to a safe value.
                self.transparency_value = 200
                self.slider.set(200) # This will trigger update_transparency again with 200

                # Call SetLayeredWindowAttributes here for immediate effect for 200,
                # as slider.set might be asynchronous or delayed in its callback.
                win32gui.SetLayeredWindowAttributes(self.hwnd, 0, self.transparency_value, win32con.LWA_ALPHA)

                # Schedule reset_error_flag to allow re-showing error if user goes >210 again quickly
                # This might not be necessary if we allow error to show every time it goes >210 and not self.error_shown
                self.after(100, self.reset_error_flag) # Reset after a short delay
            else:
                # Error is already shown (e.g. from a previous drag).
                # If they are still trying to drag above 210, the slider.set(200) in the previous
                # block should eventually correct them. We don't want to show stacked message boxes.
                # We can just cap the value here if necessary, but slider.set should handle it.
                # To be safe, ensure current applied transparency doesn't exceed cap if user is fast.
                if self.transparency_value > 200: # If somehow it got set higher despite error
                    self.transparency_value = 200
                    win32gui.SetLayeredWindowAttributes(self.hwnd, 0, self.transparency_value, win32con.LWA_ALPHA)


    def choose_color(self):
        color_code = askcolor(title="Choose overlay color")[1] # askcolor returns a tuple (rgb, hex) or (None, None)
        if color_code:
            self.bg_color = color_code
            self.configure(bg=self.bg_color)
            # The existing LWA_ALPHA transparency will apply to the new background color.
            # No need to call SetLayeredWindowAttributes or a separate update_color method here.

    # update_color method is removed as it's no longer needed.

def main():
    app = TransparentWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
