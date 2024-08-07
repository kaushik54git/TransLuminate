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
            exit()

        control_window.protocol("WM_DELETE_WINDOW", on_closing)

    def make_window_click_through(self):
        self.hwnd = win32gui.GetParent(self.winfo_id())

        # Set window style to layered and transparent
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        
        # Set initial transparency
        self.update_transparency(self.transparency_value)

    def update_transparency(self, value):
        self.transparency_value = int(value)
        if self.transparency_value <= 210:
            self.error_shown = False  # Reset error flag
            win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(0, 0, 0), self.transparency_value, win32con.LWA_ALPHA)
        else:
            if not self.error_shown:
                self.error_shown = True
                messagebox.showerror("Too Dim", "It's going to be too dim, you may not be able to see the screen")
                self.slider.set(200)
                self.transparency_value = 200
                self.after(100, self.reset_error_flag)
                win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(0, 0, 0), self.transparency_value, win32con.LWA_ALPHA)

    def choose_color(self):
        color = askcolor()[1]
        if color:
            self.bg_color = color
            self.configure(bg=self.bg_color)
            self.update_color()

    def update_color(self):
        r, g, b = self.winfo_rgb(self.bg_color)
        color_key = win32api.RGB(r // 256, g // 256, b // 256)
        win32gui.SetLayeredWindowAttributes(self.hwnd, color_key, self.transparency_value, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)

def main():
    app = TransparentWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
