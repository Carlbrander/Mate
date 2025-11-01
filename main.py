import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk
import pyperclip
import pyautogui
import time
import math
import os
from PIL import Image, ImageTk

import signal
import sys
from anthropic import Anthropic
import config
import ctypes
import re

def show_study_topic_dialog():
    """Show startup dialog to ask user what they're studying"""
    # Set DPI awareness before creating any windows (Windows only)
    dpi_scale = 1.0
    try:
        from ctypes import windll
        user32 = windll.user32
        # Get the DPI scaling factor
        # Standard DPI is 96, so scaling = actual_dpi / 96
        try:
            # Try to get DPI for the primary monitor
            hdc = user32.GetDC(0)
            dpi = windll.gdi32.GetDeviceCaps(hdc, 88)  # 88 = LOGPIXELSX
            user32.ReleaseDC(0, hdc)
            dpi_scale = dpi / 96.0
            print(f"Detected DPI: {dpi} (scale factor: {dpi_scale})")
        except:
            pass
        user32.SetProcessDPIAware()
    except:
        pass
    
    # Create a dedicated CTk window for the dialog
    dialog = ctk.CTk()
    
    # Remove title bar for clean rounded corner window
    dialog.overrideredirect(True)
    
    # Set transparent background color
    transparent_color = "#010101"  # Near-black color to make transparent
    dialog.configure(fg_color=transparent_color)
    dialog.wm_attributes('-transparentcolor', transparent_color)
    
    # Center the window on screen - get actual screen dimensions
    window_width = 500
    window_height = 280
    
    # Update window to ensure proper screen dimension detection
    dialog.update_idletasks()
    
    # Get screen dimensions - use tkinter's coordinate system
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    
    print(f"Tkinter screen dimensions: {screen_width}x{screen_height}")
    print(f"DPI scale factor: {dpi_scale}")
    print(f"Dialog window size: {window_width}x{window_height}")
    
    # Calculate center position accounting for DPI scaling
    # The window will be DPI scaled, so we need to account for the actual rendered size
    actual_window_width = int(window_width * dpi_scale)
    actual_window_height = int(window_height * dpi_scale)
    
    print(f"Window will be DPI scaled to: {actual_window_width}x{actual_window_height}")
    
    # Calculate position using the ACTUAL (scaled) window size
    x = (screen_width - actual_window_width) // 2
    y = (screen_height - actual_window_height) // 2
    
    # Verify centering with actual scaled dimensions
    window_center_x = x + (actual_window_width // 2)
    window_center_y = y + (actual_window_height // 2)
    screen_center_x = screen_width // 2
    screen_center_y = screen_height // 2
    
    print(f"Window top-left at: ({x}, {y})")
    print(f"Expected window center: ({window_center_x}, {window_center_y})")
    print(f"Screen center: ({screen_center_x}, {screen_center_y})")
    print(f"Expected center offset: ({window_center_x - screen_center_x}, {window_center_y - screen_center_y})")
    
    # Set window size and position
    dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Force update to apply geometry
    dialog.update_idletasks()
    
    # Verify actual position after setting
    dialog.update()
    actual_x = dialog.winfo_x()
    actual_y = dialog.winfo_y()
    actual_width = dialog.winfo_width()
    actual_height = dialog.winfo_height()
    
    print(f"\n=== WINDOW POSITIONING DEBUG ===")
    print(f"Requested position: ({x}, {y})")
    print(f"Actual position: ({actual_x}, {actual_y})")
    print(f"Requested size: {window_width}x{window_height}")
    print(f"Actual size reported by winfo: {actual_width}x{actual_height}")
    
    # Calculate where the window actually is on screen
    actual_center_x = actual_x + (actual_width // 2)
    actual_center_y = actual_y + (actual_height // 2)
    print(f"Actual window center: ({actual_center_x}, {actual_center_y})")
    print(f"Screen center: ({screen_width // 2}, {screen_height // 2})")
    print(f"Visual center offset: ({actual_center_x - screen_width // 2}, {actual_center_y - screen_height // 2})")
    
    # Check for DPI scaling affecting window size
    if actual_width != window_width or actual_height != window_height:
        print(f"WARNING: Window size mismatch! Window may be DPI scaled.")
        size_scale_x = actual_width / window_width if window_width > 0 else 1
        size_scale_y = actual_height / window_height if window_height > 0 else 1
        print(f"Window size scale factors: x={size_scale_x:.2f}, y={size_scale_y:.2f}")
    
    # Check if position matches what we requested
    if abs(actual_x - x) > 5 or abs(actual_y - y) > 5:
        print(f"WARNING: Window position mismatch by more than 5 pixels!")
        print(f"  Difference: ({actual_x - x}, {actual_y - y})")
        
        # Try to correct by adjusting for the difference
        corrected_x = x - (actual_x - x)
        corrected_y = y - (actual_y - y)
        print(f"Attempting correction to: ({corrected_x}, {corrected_y})")
        dialog.geometry(f"+{corrected_x}+{corrected_y}")
        dialog.update()
        final_x = dialog.winfo_x()
        final_y = dialog.winfo_y()
        print(f"Position after correction: ({final_x}, {final_y})")
        
        # Check final center position
        final_center_x = final_x + (dialog.winfo_width() // 2)
        final_center_y = final_y + (dialog.winfo_height() // 2)
        print(f"Final window center: ({final_center_x}, {final_center_y})")
        print(f"Final center offset: ({final_center_x - screen_width // 2}, {final_center_y - screen_height // 2})")
    
    print(f"=== END DEBUG ===\n")
    
    # Ensure window is on top
    dialog.attributes('-topmost', True)
    
    # Variable to store the result
    study_topic = tk.StringVar()
    dialog_closed = tk.BooleanVar(value=False)
    
    # Define close handler early so it can be used by close button
    def on_closing():
        dialog_closed.set(True)
        dialog.quit()  # Exit mainloop
    
    # Main container with rounded corners
    main_container = ctk.CTkFrame(
        dialog,
        fg_color="white",
        corner_radius=15,
        border_width=2,
        border_color="#e0e0e0"
    )
    main_container.pack(fill='both', expand=True, padx=0, pady=0)
    
    # Close button (X) in top-right corner
    close_button = ctk.CTkButton(
        main_container,
        text="✕",
        font=("Segoe UI", 16),
        width=30,
        height=30,
        corner_radius=15,
        fg_color="transparent",
        text_color="#999999",
        hover_color="#f0f0f0",
        command=lambda: on_closing()
    )
    close_button.place(x=window_width - 50, y=10)
    
    # Title
    title_label = ctk.CTkLabel(
        main_container,
        text="What are you studying today?",
        font=("Segoe UI", 18, "bold"),
        text_color="#333333"
    )
    title_label.pack(pady=(30, 10))
    
    # Subtitle
    subtitle_label = ctk.CTkLabel(
        main_container,
        text="This helps me tailor explanations to your learning context",
        font=("Segoe UI", 11),
        text_color="#666666"
    )
    subtitle_label.pack(pady=(0, 20))
    
    # Frame for input and checkmark
    input_frame = ctk.CTkFrame(
        main_container,
        fg_color="white"
    )
    input_frame.pack(pady=20, padx=40, fill='x')
    
    # Text entry with rounded corners
    text_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="e.g., Machine Learning, Spanish, Guitar...",
        font=("Segoe UI", 14),
        height=45,
        corner_radius=10,
        border_width=2,
        border_color="#667eea",
        fg_color="white",
        text_color="#333333"
    )
    text_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
    text_entry.focus()  # Focus on the text entry
    
    def submit_topic():
        """Save the topic and close the dialog"""
        topic = text_entry.get().strip()
        if topic:
            study_topic.set(topic)
        dialog_closed.set(True)
        dialog.quit()  # Exit mainloop
    
    # Checkmark button
    checkmark_button = ctk.CTkButton(
        input_frame,
        text="✓",
        font=("Segoe UI", 24, "bold"),
        width=45,
        height=45,
        corner_radius=10,
        fg_color="#667eea",
        hover_color="#764ba2",
        command=submit_topic
    )
    checkmark_button.pack(side='right')
    
    # Bind Enter key to submit
    text_entry.bind('<Return>', lambda e: submit_topic())
    
    # Wait for dialog to close
    dialog.mainloop()
    
    # Get the result before destroying
    result = study_topic.get() if dialog_closed.get() else ""
    
    # Hide the window immediately (user won't see cleanup delay)
    dialog.withdraw()
    
    # Process all pending events and cancel remaining callbacks
    try:
        # Update multiple times to process all pending events
        for _ in range(10):
            dialog.update_idletasks()
            dialog.update()
    except:
        pass
    
    # Wait for all scheduled callbacks to complete
    time.sleep(0.2)
    
    # Force quit any remaining tkinter operations
    try:
        dialog.quit()
    except:
        pass
    
    # Now destroy the dialog - wrap in try/except to suppress any errors
    try:
        import sys
        import io
        # Temporarily redirect stderr to suppress CustomTkinter cleanup errors
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        
        dialog.destroy()
        
        # Restore stderr
        sys.stderr = old_stderr
    except:
        sys.stderr = old_stderr
    
    # Return the study topic (or empty string if none entered)
    return result

class ELI5Overlay:
    def __init__(self):
        # Main transparent window with button
        self.root = tk.Tk()
        self.root.title("Mate")
        
        # Make window transparent and always on top
        self.root.attributes('-topmost', True)  # Always on top
        
        # Remove window decorations and set transparent color
        self.root.overrideredirect(True)
        # Use a specific color for transparency on Windows
        transparent_color = '#010101'  # Near-black color to make transparent
        self.root.config(bg=transparent_color)
        self.root.wm_attributes('-transparentcolor', transparent_color)
        
        # Position more towards center-right
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = screen_width - config.BUTTON_SIZE - 100  # More towards center
        y_position = screen_height - config.BUTTON_SIZE - 150  # Higher up
        
        # Window size needs to accommodate canvas with extra space for hover, additional buttons, and pomodoro controls
        # We need space for 3 buttons above the main button AND space for pomodoro control dots (35+18=53px on each side)
        window_width = int(config.BUTTON_SIZE * 1.15) + 120  # Extra space for pomodoro controls
        window_height = int(config.BUTTON_SIZE * 5)  # Space for 4 buttons total
        # Adjust x_position to keep button centered
        x_position = x_position - 60  # Shift left by half the extra width
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position - (window_height - int(config.BUTTON_SIZE * 1.15))}")
        
        # Make window not steal focus on Windows using WinAPI
        self.root.update_idletasks()  # Ensure window is created
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            # Set WS_EX_NOACTIVATE extended window style
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_NOACTIVATE)
        except Exception as e:
            print(f"Note: Could not set no-activate style: {e}")
        
        # Create circular button using Canvas - add extra space for hover growth, additional buttons, and pomodoro controls
        canvas_width = int(config.BUTTON_SIZE * 1.15) + 120  # Wider to accommodate pomodoro controls
        canvas_height = int(config.BUTTON_SIZE * 5)
        self.canvas = tk.Canvas(
            self.root,
            width=canvas_width,
            height=canvas_height,
            bg=transparent_color,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Calculate positions - main button at bottom of canvas, centered horizontally
        self.main_button_size = config.BUTTON_SIZE
        self.small_button_size = int(config.BUTTON_SIZE * 0.75)  # 75% of main button
        self.button_spacing = int(config.BUTTON_SIZE * 1.1)  # Space between button centers
        # When extending downward, first button needs to account for half of main + half of small + gap
        self.first_button_offset_down = int(config.BUTTON_SIZE * 0.5 + self.small_button_size * 0.5 + config.BUTTON_SIZE * 0.1)
        
        # Main button position (at bottom, centered in wider canvas)
        main_button_y = canvas_height - int(config.BUTTON_SIZE * 1.15)
        padding = (int(config.BUTTON_SIZE * 1.15) - config.BUTTON_SIZE) // 2
        # Center the button horizontally in the wider canvas
        horizontal_offset = 60  # Half of the extra 120px width
        
        # Draw main circular button (centered in canvas)
        button_left = horizontal_offset + padding
        button_right = horizontal_offset + int(config.BUTTON_SIZE * 1.15) - padding
        self.button_circle = self.canvas.create_oval(
            button_left, main_button_y + padding, 
            button_right, main_button_y + int(config.BUTTON_SIZE * 1.15) - padding,
            fill='#667eea',  # Modern purple-blue gradient
            outline='',
            width=0
        )
        
        # Add image centered in main button
        try:
            # Load the mate.png image
            mate_image = Image.open("mate.png")
            # Resize to fit in button (about 1/3 of button size)
            image_size = int(config.BUTTON_SIZE * 0.4)
            mate_image = mate_image.resize((image_size, image_size), Image.Resampling.LANCZOS)
            self.mate_photo = ImageTk.PhotoImage(mate_image)
            self.mate_image_original = mate_image  # Store original for resizing
            
            self.button_text = self.canvas.create_image(
                horizontal_offset + int(config.BUTTON_SIZE * 1.15) // 2,
                main_button_y + int(config.BUTTON_SIZE * 1.15) // 2,
                image=self.mate_photo
            )
            self.is_image = True
        except Exception as e:
            # Fallback to text if image not found
            print(f"Could not load mate.png: {e}, using text fallback")
            self.original_font_size = 12
            self.button_text = self.canvas.create_text(
                horizontal_offset + int(config.BUTTON_SIZE * 1.15) // 2,
                main_button_y + int(config.BUTTON_SIZE * 1.15) // 2,
                text=config.BUTTON_TEXT,
                font=('Segoe UI', self.original_font_size, 'bold'),
                fill='white'
            )
            self.is_image = False
        
        # Create 3 additional smaller buttons (initially hidden at main button position)
        self.extra_buttons = []
        self.extra_button_icons = []
        button_colors = ['#764ba2', '#f093fb', '#4facfe']  # Different gradient colors
        button_icons = ['➕', '🔍', '🍅']  # Icons: plus, magnifier, tomato (pomodoro)
        
        for i in range(3):
            # Initially position at main button location (centered perfectly on main button center)
            # Center the small button on the main button's center point
            main_center_x = horizontal_offset + int(config.BUTTON_SIZE * 1.15) // 2
            main_center_y = main_button_y + int(config.BUTTON_SIZE * 1.15) // 2
            
            small_button_left = main_center_x - self.small_button_size // 2
            small_button_top = main_center_y - self.small_button_size // 2
            
            button = self.canvas.create_oval(
                small_button_left,
                small_button_top,
                small_button_left + self.small_button_size,
                small_button_top + self.small_button_size,
                fill=button_colors[i],
                outline='',
                width=0,
                state='hidden'  # Initially hidden
            )
            
            icon = self.canvas.create_text(
                main_center_x,
                main_center_y,
                text=button_icons[i],
                font=('Segoe UI', 14),
                fill='white',
                state='hidden'  # Initially hidden
            )
            
            self.extra_buttons.append(button)
            self.extra_button_icons.append(icon)
        
        # Animation tracking
        self.animation_running = False
        self.animation_direction = None  # 'up' or 'down'
        self.buttons_visible = False  # Track if extra buttons are shown
        self.buttons_expand_direction = 'up'  # Track if buttons expand 'up' or 'down'
        self.current_layout = 'bottom'  # Track if main button is at 'bottom' or 'top' of canvas
        
        # Bind drag events to make main button draggable across screen
        # Click and drag on the mate button to move it anywhere
        self.canvas.tag_bind(self.button_circle, '<Button-1>', self.start_drag)
        self.canvas.tag_bind(self.button_circle, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.button_circle, '<ButtonRelease-1>', self.on_button_click)
        self.canvas.tag_bind(self.button_text, '<Button-1>', self.start_drag)
        self.canvas.tag_bind(self.button_text, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.button_text, '<ButtonRelease-1>', self.on_button_click)
        
        # Hover effects - only bind to main button elements
        self.canvas.tag_bind(self.button_circle, '<Enter>', self.on_hover)
        self.canvas.tag_bind(self.button_circle, '<Leave>', self.check_leave)
        self.canvas.tag_bind(self.button_text, '<Enter>', self.on_hover)
        self.canvas.tag_bind(self.button_text, '<Leave>', self.check_leave)
        
        # Bind hover events to extra buttons to prevent closing when hovering over them
        # Also add hover effects (grow on hover)
        for i, (button, icon) in enumerate(zip(self.extra_buttons, self.extra_button_icons)):
            # Hover enter - grow the button and keep menu open
            enter_handler = lambda e, idx=i: self.on_extra_button_hover(e, idx)
            self.canvas.tag_bind(button, '<Enter>', enter_handler)
            self.canvas.tag_bind(icon, '<Enter>', enter_handler)
            
            # Hover leave - shrink back and check if leaving menu
            leave_handler = lambda e, idx=i: self.on_extra_button_leave(e, idx)
            self.canvas.tag_bind(button, '<Leave>', leave_handler)
            self.canvas.tag_bind(icon, '<Leave>', leave_handler)
        
        # Bind click events to extra buttons
        for i, (button, icon) in enumerate(zip(self.extra_buttons, self.extra_button_icons)):
            # Create a lambda with default argument to capture current i value
            click_handler = lambda e, index=i: self.on_extra_button_click(index)
            self.canvas.tag_bind(button, '<Button-1>', click_handler)
            self.canvas.tag_bind(icon, '<Button-1>', click_handler)
        
        # Initialize Anthropic client
        try:
            self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        except Exception as e:
            print(f"Warning: Could not initialize Anthropic client. Please check your API key. Error: {e}")
            self.client = None
        
        # Explanation window (initially hidden)
        self.explanation_window = None
        
        # Drag tracking
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self.is_hovered = False
        self.leave_timer = None  # For delayed leave detection
        
        # Extra button hover state tracking
        self.extra_button_hover_state = [False, False, False]
        self.extra_button_shrink_timers = [None, None, None]
        
        # Pomodoro timer state
        self.pomodoro_active = False
        self.pomodoro_running = False
        self.pomodoro_is_break = False
        self.pomodoro_seconds = 25 * 60  # 25 minutes for work
        self.pomodoro_timer_id = None
        self.pomodoro_control_dots = []  # Will store control dot canvas items
    
    def ease_out_cubic(self, t):
        """Easing function for smooth deceleration"""
        return 1 - pow(1 - t, 3)
    
    def reposition_to_top_layout(self):
        """Move main button to top of canvas to make room for buttons below"""
        canvas_height = int(config.BUTTON_SIZE * 5)
        canvas_width = int(config.BUTTON_SIZE * 1.15) + 120  # Wider canvas
        
        # Calculate current and target positions
        current_main_button_y = canvas_height - int(config.BUTTON_SIZE * 1.15)
        target_main_button_y = 0
        
        # Calculate offset to move canvas elements
        offset_y = target_main_button_y - current_main_button_y
        
        # Delete pomodoro controls first (will be recreated after move)
        controls_were_visible = self.buttons_visible if self.pomodoro_active and self.pomodoro_control_dots else False
        if self.pomodoro_control_dots:
            for dot in self.pomodoro_control_dots:
                self.canvas.delete(dot)
            self.pomodoro_control_dots = []
        
        # Move all canvas elements (except pomodoro controls which we deleted)
        self.canvas.move(self.button_circle, 0, offset_y)
        self.canvas.move(self.button_text, 0, offset_y)
        for button in self.extra_buttons:
            self.canvas.move(button, 0, offset_y)
        for icon in self.extra_button_icons:
            self.canvas.move(icon, 0, offset_y)
        
        # Adjust window position to keep button in same screen location
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        window_width = int(config.BUTTON_SIZE * 1.15) + 120  # Wider window for pomodoro controls
        window_height = int(config.BUTTON_SIZE * 5)
        # Move window down by the same offset so button stays in place
        new_y = current_y - offset_y
        self.root.geometry(f"{window_width}x{window_height}+{current_x}+{new_y}")
        
        # Clear stored coordinates so they're recalculated
        if hasattr(self, 'button_initial_coords'):
            delattr(self, 'button_initial_coords')
            delattr(self, 'icon_initial_coords')
        
        # Don't create controls here - they'll be created after animation completes
        # This ensures they're positioned relative to the pomodoro button's FINAL position
    
    def reposition_to_bottom_layout(self):
        """Move main button back to bottom of canvas (default layout)"""
        canvas_height = int(config.BUTTON_SIZE * 5)
        canvas_width = int(config.BUTTON_SIZE * 1.15) + 120  # Wider canvas
        
        # Calculate current and target positions
        current_main_button_y = 0
        target_main_button_y = canvas_height - int(config.BUTTON_SIZE * 1.15)
        
        # Calculate offset to move canvas elements
        offset_y = target_main_button_y - current_main_button_y
        
        # Delete pomodoro controls first (will be recreated after move)
        controls_were_visible = self.buttons_visible if self.pomodoro_active and self.pomodoro_control_dots else False
        if self.pomodoro_control_dots:
            for dot in self.pomodoro_control_dots:
                self.canvas.delete(dot)
            self.pomodoro_control_dots = []
        
        # Move all canvas elements (except pomodoro controls which we deleted)
        self.canvas.move(self.button_circle, 0, offset_y)
        self.canvas.move(self.button_text, 0, offset_y)
        for button in self.extra_buttons:
            self.canvas.move(button, 0, offset_y)
        for icon in self.extra_button_icons:
            self.canvas.move(icon, 0, offset_y)
        
        # Adjust window position to keep button in same screen location
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        window_width = int(config.BUTTON_SIZE * 1.15) + 120  # Wider window for pomodoro controls
        window_height = int(config.BUTTON_SIZE * 5)
        # Move window up by the same offset so button stays in place
        new_y = current_y - offset_y
        self.root.geometry(f"{window_width}x{window_height}+{current_x}+{new_y}")
        
        # Clear stored coordinates so they're recalculated
        if hasattr(self, 'button_initial_coords'):
            delattr(self, 'button_initial_coords')
            delattr(self, 'icon_initial_coords')
        
        # Don't create controls here - they'll be created after animation completes
        # This ensures they're positioned relative to the pomodoro button's FINAL position
    
    def animate_extra_buttons(self, direction, frame=0, max_frames=20):
        """Animate extra buttons show/hide with easing, respecting expand direction"""
        if frame == 0:
            self.animation_running = True
            self.animation_direction = direction
            
            # Make buttons visible when showing
            if direction == 'show':
                for button in self.extra_buttons:
                    self.canvas.itemconfig(button, state='normal')
                    self.canvas.tag_raise(button)  # Bring to front when showing
                for icon in self.extra_button_icons:
                    self.canvas.itemconfig(icon, state='normal')
                    self.canvas.tag_raise(icon)  # Bring to front when showing
            elif direction == 'hide':
                # Move extra buttons behind the main button when hiding
                for button in self.extra_buttons:
                    self.canvas.tag_lower(button, self.button_circle)
                for icon in self.extra_button_icons:
                    self.canvas.tag_lower(icon, self.button_circle)
        
        if frame >= max_frames:
            self.animation_running = False
            # Hide buttons if finished hiding and update state
            if direction == 'hide':
                for button in self.extra_buttons:
                    self.canvas.itemconfig(button, state='hidden')
                for icon in self.extra_button_icons:
                    self.canvas.itemconfig(icon, state='hidden')
                self.buttons_visible = False
            elif direction == 'show':
                self.buttons_visible = True
                # Create pomodoro controls if pomodoro is active
                # Always recreate them to ensure correct position relative to pomodoro button
                if self.pomodoro_active:
                    # Delete existing controls if any (they might be in wrong position)
                    if self.pomodoro_control_dots:
                        for dot in self.pomodoro_control_dots:
                            self.canvas.delete(dot)
                        self.pomodoro_control_dots = []
                    # Create controls at correct position (after buttons are in final position)
                    self.create_pomodoro_controls()
            return
        
        # Calculate eased progress
        progress = self.ease_out_cubic(frame / max_frames)
        
        # Calculate movement distance for each button
        for i, (button, icon) in enumerate(zip(self.extra_buttons, self.extra_button_icons)):
            # Each button moves to a position based on expand direction
            # Negative offset = up, positive offset = down
            # Use same spacing for both directions for consistency
            if self.buttons_expand_direction == 'up':
                target_offset = -self.button_spacing * (i + 1)  # Negative = move up
            else:  # down
                # For downward, use same spacing as upward (just positive)
                target_offset = self.button_spacing * (i + 1)  # Positive = move down
            
            if direction == 'show':
                # Move from 0 to target_offset
                current_offset = target_offset * progress
            else:  # hide
                # Move from target_offset back to 0
                current_offset = target_offset * (1 - progress)
            
            # Calculate position for this frame
            if frame == 0:
                # Store initial position
                if not hasattr(self, 'button_initial_coords'):
                    self.button_initial_coords = []
                    self.icon_initial_coords = []
                    for btn, icn in zip(self.extra_buttons, self.extra_button_icons):
                        self.button_initial_coords.append(self.canvas.coords(btn))
                        self.icon_initial_coords.append(self.canvas.coords(icn))
            
            # Set position based on offset from initial position
            if hasattr(self, 'button_initial_coords'):
                btn_coords = self.button_initial_coords[i]
                icon_coords = self.icon_initial_coords[i]
                
                self.canvas.coords(button, 
                    btn_coords[0], btn_coords[1] + current_offset,
                    btn_coords[2], btn_coords[3] + current_offset)
                self.canvas.coords(icon,
                    icon_coords[0], icon_coords[1] + current_offset)
        
        # Schedule next frame
        self.root.after(16, lambda: self.animate_extra_buttons(direction, frame + 1, max_frames))
    
    def cancel_leave(self, event):
        """Cancel any pending leave timer"""
        if self.leave_timer:
            self.root.after_cancel(self.leave_timer)
            self.leave_timer = None
    
    def check_leave(self, event):
        """Check if mouse really left all button areas (delayed check)"""
        # Cancel any existing timer
        if self.leave_timer:
            self.root.after_cancel(self.leave_timer)
        
        # Schedule leave check after a longer delay (200ms to allow moving between buttons)
        # This is especially important for the Pomodoro control buttons
        self.leave_timer = self.root.after(200, self.on_leave)
    
    def on_hover(self, event):
        """Button hover effect - grow size and show extra buttons"""
        # Cancel any pending leave
        self.cancel_leave(event)
        
        if not self.is_hovered:
            # Determine if buttons should expand up or down based on screen position FIRST
            screen_height = self.root.winfo_screenheight()
            button_y = self.root.winfo_y()
            space_above = button_y
            space_needed = self.button_spacing * 3  # Space needed for 3 buttons
            
            # If not enough space above, expand downward
            if space_above < space_needed:
                self.buttons_expand_direction = 'down'
                # Reposition button layout to top of canvas if needed
                if self.current_layout == 'bottom':
                    self.reposition_to_top_layout()
                    self.current_layout = 'top'
            else:
                self.buttons_expand_direction = 'up'
                # Reposition button layout to bottom of canvas if needed
                if self.current_layout == 'top':
                    self.reposition_to_bottom_layout()
                    self.current_layout = 'bottom'
            
            self.is_hovered = True
            
            # Scale up the button by 10% from center (calculate position based on current layout)
            canvas_height = int(config.BUTTON_SIZE * 5)
            horizontal_offset = 60  # Horizontal centering offset
            
            if self.current_layout == 'top':
                main_button_y = 0
            else:
                main_button_y = canvas_height - int(config.BUTTON_SIZE * 1.15)
            
            # Center point is offset by the horizontal centering
            center_x = horizontal_offset + int(config.BUTTON_SIZE * 1.15) // 2
            center_y = main_button_y + int(config.BUTTON_SIZE * 1.15) // 2
            self.canvas.scale(self.button_circle, center_x, center_y, 1.1, 1.1)
            
            # Scale up text or image
            if self.is_image:
                # Scale up image
                new_size = int(config.BUTTON_SIZE * 0.4 * 1.1)
                scaled_image = self.mate_image_original.resize((new_size, new_size), Image.Resampling.LANCZOS)
                self.mate_photo = ImageTk.PhotoImage(scaled_image)
                self.canvas.itemconfig(self.button_text, image=self.mate_photo)
            else:
                # Make text bigger by increasing font size
                new_font_size = int(self.original_font_size * 1.1)
                self.canvas.itemconfig(self.button_text, font=('Segoe UI', new_font_size, 'bold'))
            self.root.config(cursor='hand2')
            
            # Animate extra buttons only if they're not already visible and not animating
            if not self.buttons_visible and not self.animation_running:
                self.animate_extra_buttons('show')
    
    def on_leave(self):
        """Button leave effect - shrink back and hide extra buttons"""
        # Clear the timer reference
        self.leave_timer = None
        
        if self.is_hovered:
            self.is_hovered = False
            
            # Scale button back down to original size (calculate position based on current layout)
            canvas_height = int(config.BUTTON_SIZE * 5)
            horizontal_offset = 60  # Horizontal centering offset
            
            if self.current_layout == 'top':
                main_button_y = 0
            else:
                main_button_y = canvas_height - int(config.BUTTON_SIZE * 1.15)
            
            # Center point is offset by the horizontal centering
            center_x = horizontal_offset + int(config.BUTTON_SIZE * 1.15) // 2
            center_y = main_button_y + int(config.BUTTON_SIZE * 1.15) // 2
            self.canvas.scale(self.button_circle, center_x, center_y, 1/1.1, 1/1.1)
            
            # Scale down text or image to original size
            if self.is_image:
                # Scale down image
                original_size = int(config.BUTTON_SIZE * 0.4)
                scaled_image = self.mate_image_original.resize((original_size, original_size), Image.Resampling.LANCZOS)
                self.mate_photo = ImageTk.PhotoImage(scaled_image)
                self.canvas.itemconfig(self.button_text, image=self.mate_photo)
            else:
                # Restore text to original font size
                self.canvas.itemconfig(self.button_text, font=('Segoe UI', self.original_font_size, 'bold'))
            self.root.config(cursor='')
            
            # Hide pomodoro controls when menu collapses
            self.hide_pomodoro_controls_visibility()
            
            # Animate extra buttons back to hidden position
            if self.buttons_visible and not self.animation_running:
                self.animate_extra_buttons('hide')
    
    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = False
        self.root.config(cursor='fleur')  # Change cursor to move cursor
        
        # Delete pomodoro controls at start of drag - they'll be recreated on next hover
        if self.pomodoro_control_dots:
            for dot in self.pomodoro_control_dots:
                self.canvas.delete(dot)
            self.pomodoro_control_dots = []
    
    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")
        self.is_dragging = True
        
        # Move the entire button menu, keeping extra buttons in sync if visible
        # The canvas coordinates are relative, so they move automatically with the window
    
    def on_extra_button_hover(self, event, index):
        """Handle hover enter on extra buttons - grow the button and keep menu open"""
        # IMPORTANT: Keep the menu open by canceling pending leave
        self.cancel_leave(event)
        
        # Cancel any pending shrink for this button
        if not hasattr(self, 'extra_button_shrink_timers'):
            self.extra_button_shrink_timers = [None, None, None]
        
        if self.extra_button_shrink_timers[index]:
            self.root.after_cancel(self.extra_button_shrink_timers[index])
            self.extra_button_shrink_timers[index] = None
        
        # Track hover state to prevent multiple scaling
        if not hasattr(self, 'extra_button_hover_state'):
            self.extra_button_hover_state = [False, False, False]
        
        # Only scale if not already scaled
        if not self.extra_button_hover_state[index]:
            self.extra_button_hover_state[index] = True
            
            button = self.extra_buttons[index]
            icon = self.extra_button_icons[index]
            
            # Get button center
            coords = self.canvas.coords(button)
            center_x = (coords[0] + coords[2]) / 2
            center_y = (coords[1] + coords[3]) / 2
            
            # Scale button (smaller effect - 5% instead of 10%)
            self.canvas.scale(button, center_x, center_y, 1.05, 1.05)
            
            # Scale icon (slightly increase font size)
            # For Pomodoro button with active timer, keep the font smaller
            if index == 2 and self.pomodoro_active:
                self.canvas.itemconfig(icon, font=('Segoe UI', 9, 'bold'))  # 8 -> 9 (timer text)
            else:
                self.canvas.itemconfig(icon, font=('Segoe UI', 15))  # 14 -> 15 (regular icons)
    
    def on_extra_button_leave(self, event, index):
        """Handle hover leave on extra buttons - shrink back and check if leaving menu"""
        # IMPORTANT: Check if we're leaving the entire menu area
        self.check_leave(event)
        
        if not hasattr(self, 'extra_button_hover_state'):
            self.extra_button_hover_state = [False, False, False]
            return
        
        if not hasattr(self, 'extra_button_shrink_timers'):
            self.extra_button_shrink_timers = [None, None, None]
        
        # Don't do anything if not currently hovered
        if not self.extra_button_hover_state[index]:
            return
        
        # Delayed check to see if we really left
        def check_and_shrink():
            # Reset timer reference
            self.extra_button_shrink_timers[index] = None
            
            # Shrink the button
            self.extra_button_hover_state[index] = False
            
            button = self.extra_buttons[index]
            icon = self.extra_button_icons[index]
            
            # Get button center
            coords = self.canvas.coords(button)
            if not coords:  # Button might be hidden
                return
                
            center_x = (coords[0] + coords[2]) / 2
            center_y = (coords[1] + coords[3]) / 2
            
            # Scale button back (1/1.05)
            self.canvas.scale(button, center_x, center_y, 1/1.05, 1/1.05)
            
            # Restore icon font size
            # For Pomodoro button with active timer, restore smaller font
            if index == 2 and self.pomodoro_active:
                self.canvas.itemconfig(icon, font=('Segoe UI', 8, 'bold'))  # Timer text
            else:
                self.canvas.itemconfig(icon, font=('Segoe UI', 14))  # Regular icons
        
        # Schedule shrink with delay - this will be cancelled if we re-enter
        self.extra_button_shrink_timers[index] = self.root.after(150, check_and_shrink)
    
    def on_extra_button_click(self, index):
        """Handle clicks on extra buttons"""
        print(f"Extra button {index} clicked")
        
        if index == 0:
            # First button (➕) - Plus functionality (placeholder)
            print("Plus button - not yet implemented")
        elif index == 1:
            # Second button (🔍) - Magnifier: ELI5 text explanation
            self.explain_selected_text()
        elif index == 2:
            # Third button (🍅) - Pomodoro timer
            if not self.pomodoro_active:
                print("Starting Pomodoro timer...")
                self.start_pomodoro()
            else:
                # If already active, toggle play/pause
                self.toggle_pomodoro()
    
    def explain_selected_text(self):
        """Copy selected text and get ELI5 explanation from Claude"""
        print("Magnifier button clicked - getting explanation...")
        
        # Store old clipboard content to detect changes
        old_clipboard = ""
        try:
            old_clipboard = pyperclip.paste()
            print(f"\nClipboard BEFORE Ctrl+C: '{old_clipboard}'")
        except:
            pass
        
        # Small delay to ensure click is processed
        time.sleep(0.05)
        
        # Simulate Ctrl+C to copy selected text
        print("Simulating Ctrl+C...")
        pyautogui.hotkey('ctrl', 'c')
        
        # Wait longer for clipboard to update
        time.sleep(0.2)
        
        # Get text from clipboard
        try:
            selected_text = pyperclip.paste()
            print(f"Clipboard AFTER Ctrl+C: '{selected_text}'\n")
        except Exception as e:
            # Silently fail - don't show error
            print(f"Could not get clipboard content: {e}")
            return
        
        # If no text selected or clipboard unchanged, silently do nothing
        if not selected_text or selected_text.strip() == "" or selected_text == old_clipboard:
            print("No new text selected - ignoring click")
            return
        
        # Check if API key is set
        if not self.client or config.ANTHROPIC_API_KEY == "your-api-key-here":
            print("API key not configured - please set your API key in config.py")
            return
        
        # Show loading message
        self.show_explanation("Generating explanation...", loading=True)
        
        # Call Claude API
        try:
            explanation = self.get_eli5_explanation(selected_text)
            self.show_explanation(explanation)
        except Exception as e:
            self.show_explanation(f"Error calling Claude API: {str(e)}")
    
    def start_pomodoro(self):
        """Start the Pomodoro timer integrated into the button"""
        self.pomodoro_active = True
        self.pomodoro_running = True
        self.pomodoro_is_break = False
        self.pomodoro_seconds = 25 * 60
        
        # Change tomato icon to timer text with smaller font
        self.canvas.itemconfig(
            self.extra_button_icons[2], 
            text=self.format_pomodoro_time(),
            font=('Segoe UI', 8, 'bold')
        )
        
        # Create control dots
        self.create_pomodoro_controls()
        
        # Start countdown
        self.update_pomodoro()
    
    def format_pomodoro_time(self):
        """Format seconds as MM:SS for display"""
        minutes = self.pomodoro_seconds // 60
        seconds = self.pomodoro_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def create_pomodoro_controls(self):
        """Create three small control dots around the tomato button"""
        # Get tomato button position
        tomato_coords = self.canvas.coords(self.extra_buttons[2])
        if not tomato_coords:
            return
        
        # Calculate center position
        button_center_x = (tomato_coords[0] + tomato_coords[2]) / 2
        button_center_y = (tomato_coords[1] + tomato_coords[3]) / 2
        button_radius = (tomato_coords[2] - tomato_coords[0]) / 2
        
        # Control dot properties
        dot_radius = 22  # Even bigger buttons
        dot_distance = button_radius + 35  # Further distance from button center
        hover_area_radius = 28  # Even bigger invisible hover area
        
        # Position dots based on expand direction
        # When expanding UP: controls go ABOVE pomodoro (negative Y = angles 210, 270, 330)
        # When expanding DOWN: controls go BELOW pomodoro (positive Y = angles 30, 90, 150)
        if self.buttons_expand_direction == 'up':
            # Buttons expand upward, so pomodoro is at top - controls go above (negative Y offset)
            angles = [210, 270, 330]  # Top-left, top, top-right
        else:  # down
            # Buttons expand downward, so pomodoro is at bottom - controls go below (positive Y offset)
            angles = [30, 90, 150]  # Bottom-right, bottom, bottom-left
        
        # Colors matching the app theme (similar to other buttons)
        colors = ['#667eea', '#764ba2', '#f093fb']  # Blue, Purple, Pink
        icons = ['▶', '❚❚', '↻']  # Play, Pause (vertical bars), Reset (circular arrow)
        
        for i, angle in enumerate(angles):
            rad = math.radians(angle)
            x = button_center_x + dot_distance * math.cos(rad)
            y = button_center_y + dot_distance * math.sin(rad)
            
            # Create invisible larger hover area (captures hover between buttons)
            hover_area = self.canvas.create_oval(
                x - hover_area_radius, y - hover_area_radius,
                x + hover_area_radius, y + hover_area_radius,
                fill='',
                outline='',
                width=0,
                state='normal'
            )
            
            # Create button circle (no border)
            dot = self.canvas.create_oval(
                x - dot_radius, y - dot_radius,
                x + dot_radius, y + dot_radius,
                fill=colors[i],
                outline='',
                width=0,
                state='normal'
            )
            
            # Create icon text (smaller font, with adjustments for centering)
            icon_x = x
            icon_y = y
            icon_font_size = 6  # Reduced all icons size
            
            # Adjust play icon position slightly for perfect centering
            if i == 0:  # Play icon
                icon_x = x + 1  # Slight right shift for visual centering
            elif i == 1:  # Pause icon - make smaller due to visual weight
                icon_font_size = 4
            
            icon = self.canvas.create_text(
                icon_x, icon_y,
                text=icons[i],
                font=('Segoe UI', icon_font_size, 'bold'),
                fill='white',
                state='normal'
            )
            
            # Raise visible elements above hover area
            self.canvas.tag_raise(dot)
            self.canvas.tag_raise(icon)
            
            self.pomodoro_control_dots.append(hover_area)
            self.pomodoro_control_dots.append(dot)
            self.pomodoro_control_dots.append(icon)
            
            # Bind hover events to all elements (hover area, circle, and icon)
            for element in [hover_area, dot, icon]:
                self.canvas.tag_bind(element, '<Enter>', self.cancel_leave)
                self.canvas.tag_bind(element, '<Leave>', self.check_leave)
            
            # Bind clicks to control dots (circle, icon, and hover area for maximum coverage)
            # Use default arguments to capture current i value
            if i == 0:  # Play/Resume
                click_handler = lambda e, func=self.pomodoro_play: func()
            elif i == 1:  # Pause
                click_handler = lambda e, func=self.pomodoro_pause: func()
            elif i == 2:  # Reset
                click_handler = lambda e, func=self.pomodoro_reset: func()
            else:
                click_handler = None
            
            if click_handler:
                self.canvas.tag_bind(hover_area, '<Button-1>', click_handler)
                self.canvas.tag_bind(dot, '<Button-1>', click_handler)
                self.canvas.tag_bind(icon, '<Button-1>', click_handler)
    
    def hide_pomodoro_controls_visibility(self):
        """Hide control dots (but don't delete them)"""
        for element in self.pomodoro_control_dots:
            self.canvas.itemconfig(element, state='hidden')
    
    def show_pomodoro_controls_visibility(self):
        """Show control dots if pomodoro is active"""
        if self.pomodoro_active and self.pomodoro_control_dots:
            for element in self.pomodoro_control_dots:
                self.canvas.itemconfig(element, state='normal')
    
    def hide_pomodoro_controls(self):
        """Hide and remove control dots"""
        for dot in self.pomodoro_control_dots:
            self.canvas.delete(dot)
        self.pomodoro_control_dots = []
    
    def update_pomodoro(self):
        """Update the Pomodoro timer countdown"""
        if self.pomodoro_running and self.pomodoro_seconds > 0:
            self.pomodoro_seconds -= 1
            self.canvas.itemconfig(self.extra_button_icons[2], text=self.format_pomodoro_time())
            self.pomodoro_timer_id = self.root.after(1000, self.update_pomodoro)
        elif self.pomodoro_seconds == 0:
            # Timer finished
            self.pomodoro_timer_finished()
    
    def pomodoro_timer_finished(self):
        """Handle Pomodoro timer completion"""
        if not self.pomodoro_is_break:
            # Work session finished, start break
            self.pomodoro_is_break = True
            self.pomodoro_seconds = 5 * 60  # 5 minute break
            self.pomodoro_running = True
            
            # Change button color to green
            self.canvas.itemconfig(self.extra_buttons[2], fill='#4CAF50')
            
            # Update display and continue
            self.canvas.itemconfig(self.extra_button_icons[2], text=self.format_pomodoro_time())
            self.update_pomodoro()
        else:
            # Break finished, reset to work session but don't start
            self.pomodoro_is_break = False
            self.pomodoro_seconds = 25 * 60
            self.pomodoro_running = False
            
            # Change button color back
            self.canvas.itemconfig(self.extra_buttons[2], fill='#4facfe')
            
            # Update display
            self.canvas.itemconfig(self.extra_button_icons[2], text=self.format_pomodoro_time())
    
    def toggle_pomodoro(self):
        """Toggle play/pause for active timer"""
        if self.pomodoro_running:
            self.pomodoro_pause()
        else:
            self.pomodoro_play()
    
    def pomodoro_play(self):
        """Resume/start the Pomodoro timer"""
        if self.pomodoro_active and not self.pomodoro_running:
            self.pomodoro_running = True
            self.update_pomodoro()
    
    def pomodoro_pause(self):
        """Pause the Pomodoro timer"""
        if self.pomodoro_running:
            self.pomodoro_running = False
            if self.pomodoro_timer_id:
                self.root.after_cancel(self.pomodoro_timer_id)
                self.pomodoro_timer_id = None
    
    def pomodoro_reset(self):
        """Reset the Pomodoro timer"""
        # Cancel any running timer
        if self.pomodoro_timer_id:
            self.root.after_cancel(self.pomodoro_timer_id)
            self.pomodoro_timer_id = None
        
        # Reset state
        self.pomodoro_active = False
        self.pomodoro_running = False
        self.pomodoro_is_break = False
        self.pomodoro_seconds = 25 * 60
        
        # Restore tomato icon with original font
        self.canvas.itemconfig(
            self.extra_button_icons[2], 
            text='🍅',
            font=('Segoe UI', 14)
        )
        
        # Restore original color
        self.canvas.itemconfig(self.extra_buttons[2], fill='#4facfe')
        
        # Hide control dots
        self.hide_pomodoro_controls()
    
    def on_button_click(self, event=None):
        # If we're dragging, don't trigger the action
        if self.is_dragging:
            self.is_dragging = False
            self.root.config(cursor='hand2' if self.is_hovered else '')  # Restore cursor
            return
        
        if event and (abs(event.x - self.drag_start_x) > 5 or abs(event.y - self.drag_start_y) > 5):
            return
        
        # Main button click - currently does nothing
        # The hover functionality expands the menu with the extra buttons
        # Text explanation functionality has been moved to the magnifier button
        print("Main mate button clicked - hover to see options")
        return
    
    def get_eli5_explanation(self, text):
        """Call Claude API to get ELI5 explanation"""
        # Build prompt from config template
        prompt = config.PROMPT_TEMPLATE.format(text=text)
        
        # Print prompt to terminal
        print("\n" + "="*60)
        print("PROMPT SENT TO CLAUDE:")
        print("="*60)
        print(prompt)
        print("="*60 + "\n")
        
        message = self.client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response = message.content[0].text
        
        # Print response to terminal
        print("="*60)
        print("RESPONSE FROM CLAUDE:")
        print("="*60)
        print(response)
        print("="*60 + "\n")
        
        return response
    
    def format_markdown_text(self, text_widget, markdown_text):
        """Format markdown text in a CTkTextbox widget"""
        # Configure text tags for different styles (smaller sizes)
        text_widget.tag_config("h1", font=("Segoe UI", 14, "bold"), spacing1=6, spacing3=3)
        text_widget.tag_config("h2", font=("Segoe UI", 12, "bold"), spacing1=5, spacing3=2)
        text_widget.tag_config("h3", font=("Segoe UI", 11, "bold"), spacing1=4, spacing3=2)
        text_widget.tag_config("bold", font=("Segoe UI", 10, "bold"))
        text_widget.tag_config("italic", font=("Segoe UI", 10, "italic"))
        text_widget.tag_config("code", font=("Consolas", 9), background="#f5f5f5", foreground="#d63384")
        text_widget.tag_config("link", font=("Segoe UI", 10, "underline"), foreground="#0066cc")
        text_widget.tag_config("bullet", font=("Segoe UI", 10))
        
        lines = markdown_text.split('\n')
        current_pos = "1.0"
        
        for line in lines:
            # Headers
            if line.startswith('# '):
                text = line[2:].strip() + '\n'
                text_widget.insert(current_pos, text, "h1")
            elif line.startswith('## '):
                text = line[3:].strip() + '\n'
                text_widget.insert(current_pos, text, "h2")
            elif line.startswith('### '):
                text = line[4:].strip() + '\n'
                text_widget.insert(current_pos, text, "h3")
            # Bullet points
            elif line.startswith('- ') or line.startswith('* '):
                text = '  • ' + line[2:].strip()
                self._insert_formatted_line(text_widget, text + '\n', current_pos)
            # Code blocks (simplified - just indent them)
            elif line.startswith('```'):
                continue  # Skip code block markers
            # Normal line with inline formatting
            else:
                self._insert_formatted_line(text_widget, line + '\n', current_pos)
            
            current_pos = text_widget.index("end-1c")
    
    def _insert_formatted_line(self, text_widget, line, pos):
        """Insert a line with inline markdown formatting (bold, italic, code, links)"""
        # Process inline markdown
        remaining = line
        current_index = pos
        
        # Pattern for **bold**, *italic*, `code`, and [links](url)
        pattern = r'(\*\*.*?\*\*|\*.*?\*|`.*?`|\[.*?\]\(.*?\))'
        
        parts = re.split(pattern, remaining)
        
        for part in parts:
            if not part:
                continue
                
            # Bold: **text**
            if part.startswith('**') and part.endswith('**'):
                text = part[2:-2]
                text_widget.insert(current_index, text, "bold")
            # Italic: *text*
            elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
                text = part[1:-1]
                text_widget.insert(current_index, text, "italic")
            # Code: `text`
            elif part.startswith('`') and part.endswith('`'):
                text = part[1:-1]
                text_widget.insert(current_index, text, "code")
            # Link: [text](url)
            elif part.startswith('[') and '](' in part:
                match = re.match(r'\[(.*?)\]\((.*?)\)', part)
                if match:
                    link_text = match.group(1)
                    text_widget.insert(current_index, link_text, "link")
                else:
                    text_widget.insert(current_index, part)
            # Normal text
            else:
                text_widget.insert(current_index, part)
            
            current_index = text_widget.index("end-1c")
    
    def show_explanation(self, text, loading=False):
        """Show explanation in a new window with CustomTkinter"""
        # Close existing explanation window if any
        if self.explanation_window and self.explanation_window.winfo_exists():
            self.explanation_window.destroy()
        
        # Create new explanation window with CustomTkinter
        self.explanation_window = ctk.CTkToplevel(self.root)
        self.explanation_window.title("")  # Empty title
        self.explanation_window.attributes('-topmost', True)
        
        # Remove title bar / top bar completely
        self.explanation_window.overrideredirect(True)
        
        # Calculate initial window size (will adjust to content)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Start with default size from config
        initial_width = config.WINDOW_MIN_WIDTH
        initial_height = config.WINDOW_MIN_HEIGHT
        
        # Position: calculated from bottom-right corner using config margins
        # x_position = screen_width - window_width - margin_from_right
        # y_position = screen_height - window_height - margin_from_bottom
        x_position = screen_width - initial_width - config.WINDOW_MARGIN_RIGHT
        y_position = screen_height - initial_height - config.WINDOW_MARGIN_BOTTOM
        
        self.explanation_window.geometry(
            f"{initial_width}x{initial_height}+{x_position}+{y_position}"
        )
        
        # Configure window with transparent background
        transparent_bg = '#010101'  # Color to make transparent
        self.explanation_window.configure(fg_color=transparent_bg)
        self.explanation_window.wm_attributes('-transparentcolor', transparent_bg)
        
        # Create main container with rounded corners (no header)
        main_container = ctk.CTkFrame(
            self.explanation_window,
            fg_color="white",
            corner_radius=15,
            border_width=2,
            border_color="#e0e0e0"
        )
        main_container.pack(fill='both', expand=True, padx=10, pady=10)  # Add padding to see rounded corners
        
        # Bind Escape key to close window
        self.explanation_window.bind('<Escape>', lambda e: self.explanation_window.destroy())
        
        # Create header with title and close button
        header_frame = tk.Frame(main_container, bg='white', cursor='fleur')
        header_frame.pack(fill='x', padx=20, pady=(10, 5))
        
        # Title on the left
        title_label = tk.Label(
            header_frame,
            text="mate explainer",
            font=("Segoe UI", 11, "bold"),
            fg="#333333",
            bg="white",
            cursor='fleur'
        )
        title_label.pack(side='left')
        
        # Close button (X) on the right
        close_button = tk.Button(
            header_frame,
            text="✕",
            font=("Segoe UI", 10),
            fg="#666666",
            bg="white",
            activebackground="#f0f0f0",
            activeforeground="#333333",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            command=self.explanation_window.destroy,
            padx=4,
            pady=2
        )
        close_button.pack(side='right')
        
        # Hover effects for close button
        close_button.bind('<Enter>', lambda e: close_button.config(fg="#333333", bg="#f0f0f0"))
        close_button.bind('<Leave>', lambda e: close_button.config(fg="#666666", bg="white"))
        
        # Make window draggable by header
        def start_drag(event):
            self.explanation_window._drag_start_x = event.x_root
            self.explanation_window._drag_start_y = event.y_root
            self.explanation_window._drag_start_window_x = self.explanation_window.winfo_x()
            self.explanation_window._drag_start_window_y = self.explanation_window.winfo_y()
        
        def on_drag(event):
            if hasattr(self.explanation_window, '_drag_start_x'):
                dx = event.x_root - self.explanation_window._drag_start_x
                dy = event.y_root - self.explanation_window._drag_start_y
                x = self.explanation_window._drag_start_window_x + dx
                y = self.explanation_window._drag_start_window_y + dy
                self.explanation_window.geometry(f"+{x}+{y}")
        
        def stop_drag(event):
            if hasattr(self.explanation_window, '_drag_start_x'):
                del self.explanation_window._drag_start_x
                del self.explanation_window._drag_start_y
                del self.explanation_window._drag_start_window_x
                del self.explanation_window._drag_start_window_y
        
        # Bind drag events to header frame and title
        header_frame.bind('<Button-1>', start_drag)
        header_frame.bind('<B1-Motion>', on_drag)
        header_frame.bind('<ButtonRelease-1>', stop_drag)
        
        title_label.bind('<Button-1>', start_drag)
        title_label.bind('<B1-Motion>', on_drag)
        title_label.bind('<ButtonRelease-1>', stop_drag)
        
        # Content frame for text widget
        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        # Use standard tkinter Text widget for markdown support (CustomTkinter doesn't support tag fonts)
        text_widget = tk.Text(
            content_frame,
            wrap="word",
            font=("Segoe UI", 10),
            bg="white",
            fg="#333333",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=15,
            pady=15,
            selectbackground='#667eea',
            selectforeground='white',
            width=50,
            height=15
        )
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(content_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        text_widget.pack(side='left', fill='both', expand=True)
        
        # Insert text with markdown formatting
        if loading:
            text_widget.insert('1.0', text)
        else:
            self.format_markdown_text(text_widget, text)
            text_widget.config(state='disabled')  # Make read-only
            
            # Update window to fit content
            self.explanation_window.update_idletasks()
            
            # Calculate required size based on text content
            text_widget.update_idletasks()
            
            # Get number of lines and adjust window size accordingly
            num_lines = int(text_widget.index('end-1c').split('.')[0])
            content_width = max(config.WINDOW_MIN_WIDTH, min(config.WINDOW_MAX_WIDTH, text_widget.winfo_reqwidth()))
            content_height = max(config.WINDOW_MIN_HEIGHT, min(config.WINDOW_MAX_HEIGHT, num_lines * 18 + 60))  # Line height + padding
            
            # Recalculate position with actual content size using config margins
            x_position = screen_width - content_width - config.WINDOW_MARGIN_RIGHT
            y_position = screen_height - content_height - config.WINDOW_MARGIN_BOTTOM
            
            self.explanation_window.geometry(f"{content_width}x{content_height}+{x_position}+{y_position}")
    
    def run(self):
        """Start the application"""
        # Set up Ctrl+C handler
        def signal_handler(sig, frame):
            print("\nShutting down Mate Overlay...")
            self.root.quit()
            self.root.destroy()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Use a polling loop instead of mainloop for better Ctrl+C handling on Windows
        def check_for_exit():
            try:
                self.root.after(100, check_for_exit)  # Check every 100ms
            except KeyboardInterrupt:
                print("\nShutting down Mate Overlay...")
                self.root.quit()
                sys.exit(0)
        
        try:
            check_for_exit()
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down Mate Overlay...")
            self.root.quit()
            sys.exit(0)

if __name__ == "__main__":
    try:
        # Show the study topic dialog
        study_topic = show_study_topic_dialog()
        
        # Save the study topic to environment variable
        if study_topic:
            os.environ['STUDY_TOPIC'] = study_topic
            print(f"Study topic set to: {study_topic}")
        else:
            os.environ['STUDY_TOPIC'] = "General Study"
            print("No study topic entered, using: General Study")
        
        # Verify environment variable is saved
        print(f"Environment variable STUDY_TOPIC = '{os.environ.get('STUDY_TOPIC', 'NOT SET')}'")
        print("")  # Empty line for readability
        
        # Start the main application
        app = ELI5Overlay()
        print("Mate Overlay is running. Press Ctrl+C to stop.")
        app.run()
    except KeyboardInterrupt:
        print("\nApplication stopped.")
        sys.exit(0)

