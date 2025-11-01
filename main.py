import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk
import pyperclip
import pyautogui
import time

import signal
import sys
import threading
from anthropic import Anthropic
import config
import ctypes
import re

# Import context retrieval service
from context_retrieval.ContextRetrievalService import ContextRetrievalService

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
        
        # Window size needs to accommodate canvas with extra space for hover and additional buttons
        # We need space for 3 buttons above the main button
        window_width = int(config.BUTTON_SIZE * 1.15)
        window_height = int(config.BUTTON_SIZE * 5)  # Space for 4 buttons total
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
        
        # Create circular button using Canvas - add extra space for hover growth and additional buttons
        canvas_width = int(config.BUTTON_SIZE * 1.15)
        canvas_height = int(config.BUTTON_SIZE * 5)
        self.canvas = tk.Canvas(
            self.root,
            width=canvas_width,
            height=canvas_height,
            bg=transparent_color,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Calculate positions - main button at bottom of canvas
        self.main_button_size = config.BUTTON_SIZE
        self.small_button_size = int(config.BUTTON_SIZE * 0.75)  # 75% of main button
        self.button_spacing = int(config.BUTTON_SIZE * 1.1)  # Space between buttons
        
        # Main button position (at bottom)
        main_button_y = canvas_height - int(config.BUTTON_SIZE * 1.15)
        padding = (int(config.BUTTON_SIZE * 1.15) - config.BUTTON_SIZE) // 2
        
        # Draw main circular button
        self.button_circle = self.canvas.create_oval(
            padding, main_button_y + padding, 
            canvas_width - padding, main_button_y + int(config.BUTTON_SIZE * 1.15) - padding,
            fill='#667eea',  # Modern purple-blue gradient
            outline='',
            width=0
        )
        
        # Add text centered in main button
        self.original_font_size = 12
        self.button_text = self.canvas.create_text(
            canvas_width // 2,
            main_button_y + int(config.BUTTON_SIZE * 1.15) // 2,
            text=config.BUTTON_TEXT,
            font=('Segoe UI', self.original_font_size, 'bold'),
            fill='white'
        )
        
        # Create 3 additional smaller buttons (initially hidden at main button position)
        self.extra_buttons = []
        self.extra_button_icons = []
        button_colors = ['#764ba2', '#f093fb', '#4facfe']  # Different gradient colors
        button_icons = ['📋', '🔍', '✨']  # Example icons
        
        for i in range(3):
            # Initially position at main button location
            small_padding = (canvas_width - self.small_button_size) // 2
            button = self.canvas.create_oval(
                small_padding,
                main_button_y + (self.main_button_size - self.small_button_size) // 2 + padding,
                small_padding + self.small_button_size,
                main_button_y + (self.main_button_size - self.small_button_size) // 2 + padding + self.small_button_size,
                fill=button_colors[i],
                outline='',
                width=0,
                state='hidden'  # Initially hidden
            )
            
            icon = self.canvas.create_text(
                canvas_width // 2,
                main_button_y + self.main_button_size // 2 + padding,
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
        
        # Bind events
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
        for button in self.extra_buttons:
            self.canvas.tag_bind(button, '<Enter>', self.cancel_leave)
            self.canvas.tag_bind(button, '<Leave>', self.check_leave)
        for icon in self.extra_button_icons:
            self.canvas.tag_bind(icon, '<Enter>', self.cancel_leave)
            self.canvas.tag_bind(icon, '<Leave>', self.check_leave)
        
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
        
        # Start context retrieval service in background
        self.start_context_retrieval_service()
    
    def start_context_retrieval_service(self):
        """Start context retrieval service in a background daemon thread"""
        try:
            print("Starting context retrieval service...")
            service = ContextRetrievalService()
            
            # Start service in daemon thread (will stop when main app exits)
            context_thread = threading.Thread(target=service.run, daemon=True)
            context_thread.start()
            
            print("Context retrieval service started successfully")
        except Exception as e:
            print(f"Warning: Could not start context retrieval service: {e}")
            print("Main app will continue without context retrieval")
    
    def ease_out_cubic(self, t):
        """Easing function for smooth deceleration"""
        return 1 - pow(1 - t, 3)
    
    def animate_extra_buttons(self, direction, frame=0, max_frames=20):
        """Animate extra buttons up or down with easing"""
        if frame == 0:
            self.animation_running = True
            self.animation_direction = direction
            
            # Make buttons visible if animating up
            if direction == 'up':
                for button in self.extra_buttons:
                    self.canvas.itemconfig(button, state='normal')
                    self.canvas.tag_raise(button)  # Bring to front when going up
                for icon in self.extra_button_icons:
                    self.canvas.itemconfig(icon, state='normal')
                    self.canvas.tag_raise(icon)  # Bring to front when going up
            elif direction == 'down':
                # Move extra buttons behind the main button when animating down
                for button in self.extra_buttons:
                    self.canvas.tag_lower(button, self.button_circle)
                for icon in self.extra_button_icons:
                    self.canvas.tag_lower(icon, self.button_circle)
        
        if frame >= max_frames:
            self.animation_running = False
            # Hide buttons if animating down and update state
            if direction == 'down':
                for button in self.extra_buttons:
                    self.canvas.itemconfig(button, state='hidden')
                for icon in self.extra_button_icons:
                    self.canvas.itemconfig(icon, state='hidden')
                self.buttons_visible = False
            elif direction == 'up':
                self.buttons_visible = True
            return
        
        # Calculate eased progress
        progress = self.ease_out_cubic(frame / max_frames)
        
        # Calculate movement distance for each button
        for i, (button, icon) in enumerate(zip(self.extra_buttons, self.extra_button_icons)):
            # Each button moves to a position above the previous one
            target_offset = -self.button_spacing * (i + 1)
            
            if direction == 'up':
                # Move from 0 to target_offset
                current_offset = target_offset * progress
            else:  # down
                # Move from target_offset to 0
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
        
        # Schedule leave check after a short delay
        self.leave_timer = self.root.after(50, self.on_leave)
    
    def on_hover(self, event):
        """Button hover effect - grow size and show extra buttons"""
        # Cancel any pending leave
        self.cancel_leave(event)
        
        if not self.is_hovered:
            self.is_hovered = True
            # Scale up the button by 10% from center
            canvas_width = int(config.BUTTON_SIZE * 1.15)
            canvas_height = int(config.BUTTON_SIZE * 5)
            main_button_y = canvas_height - int(config.BUTTON_SIZE * 1.15)
            center_x = canvas_width // 2
            center_y = main_button_y + int(config.BUTTON_SIZE * 1.15) // 2
            self.canvas.scale(self.button_circle, center_x, center_y, 1.1, 1.1)
            
            # Make text bigger by increasing font size
            new_font_size = int(self.original_font_size * 1.1)
            self.canvas.itemconfig(self.button_text, font=('Segoe UI', new_font_size, 'bold'))
            self.root.config(cursor='hand2')
            
            # Animate extra buttons up only if they're not already visible and not animating up
            if not self.buttons_visible and not self.animation_running:
                self.animate_extra_buttons('up')
    
    def on_leave(self):
        """Button leave effect - shrink back and hide extra buttons"""
        # Clear the timer reference
        self.leave_timer = None
        
        if self.is_hovered:
            self.is_hovered = False
            # Scale button back down to original size
            canvas_width = int(config.BUTTON_SIZE * 1.15)
            canvas_height = int(config.BUTTON_SIZE * 5)
            main_button_y = canvas_height - int(config.BUTTON_SIZE * 1.15)
            center_x = canvas_width // 2
            center_y = main_button_y + int(config.BUTTON_SIZE * 1.15) // 2
            self.canvas.scale(self.button_circle, center_x, center_y, 1/1.1, 1/1.1)
            
            # Restore text to original font size
            self.canvas.itemconfig(self.button_text, font=('Segoe UI', self.original_font_size, 'bold'))
            self.root.config(cursor='')
            
            # Animate extra buttons down only if they're visible and not animating down
            if self.buttons_visible and not self.animation_running:
                self.animate_extra_buttons('down')
    
    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = False
    
    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")
        self.is_dragging = True
    
    def on_button_click(self, event=None):
        # If we're dragging, don't trigger the action
        if self.is_dragging:
            self.is_dragging = False
            return
        
        if event and (abs(event.x - self.drag_start_x) > 5 or abs(event.y - self.drag_start_y) > 5):
            return
        
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
            return
        
        # If no text selected or clipboard unchanged, silently do nothing
        if not selected_text or selected_text.strip() == "" or selected_text == old_clipboard:
            print("No new text selected - ignoring click")
            return
        
        # Check if API key is set
        if not self.client or config.ANTHROPIC_API_KEY == "your-api-key-here":
            print("API key not configured - ignoring click")
            return
        
        # Show loading message
        self.show_explanation("Generating explanation...", loading=True)
        
        # Call Claude API
        try:
            explanation = self.get_eli5_explanation(selected_text)
            self.show_explanation(explanation)
        except Exception as e:
            self.show_explanation(f"Error calling Claude API: {str(e)}")
    
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
        app = ELI5Overlay()
        print("Mate Overlay is running. Press Ctrl+C to stop.")
        app.run()
    except KeyboardInterrupt:
        print("\nApplication stopped.")
        sys.exit(0)

